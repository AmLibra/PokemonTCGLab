import streamlit as st
import streamlit_authenticator as stauth
import yaml
from streamlit_authenticator import LoginError, Hasher
from streamlit_option_menu import option_menu
from yaml import SafeLoader

from components.card_shop import show_card_shop
from components.card_viewer import view_cards
from components.deck_manager import view_decks
# noinspection PyUnresolvedReferences
from utils.deck import Deck  # required for type hinting correctly when loading decks from collection
from utils.pokemon_api import get_sets
from utils.storage import load_cards_from_collection, load_decks_from_collection

APP_TITLE = "Pokémon Card Manager"
SECTION_NAMES = ["Card Shop", "Deck Manager", "Owned Cards"]
SECTION_ICONS = ["plus-circle", "folder", "cards"]

# Set the page to use wide mode
st.set_page_config(layout="wide", page_title=APP_TITLE)


# Loading config file
@st.cache_data
def load_config():
    with open('config.yaml', 'r', encoding='utf-8') as f:
        c = yaml.load(f, Loader=SafeLoader)
    return c


def save_config(c):
    Hasher([""]).hash_passwords(c['credentials'])
    with open('config.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(c, f)


def navbar():
    # inject some CSS to hide the hamburger menu and reduce padding
    st.markdown(
        """
        <style>
        #MainMenu {visibility: hidden;}
        .st-emotion-cache-1jicfl2 {
            width: 100%;
            padding: 2rem 5rem 10rem;
            min-width: auto;
            max-width: initial;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    # Top Navigation Menu using option_menu
    menu_option = option_menu(
        menu_title=None,  # Hide the title for a cleaner look
        options=SECTION_NAMES,  # List of menu options
        icons=SECTION_ICONS,  # Icons for each option
        menu_icon="cast",  # Optional main menu icon
        default_index=2,  # Which option is selected by default
        orientation="horizontal",  # Menu orientation
    )
    return menu_option


def sidebar():
    with st.sidebar:
        st.title(APP_TITLE, anchor=False)
        st.write(f"Welcome to the Pokémon Card Manager, {st.session_state["name"]}!")
        col1, col2 = st.columns(2, vertical_alignment="top")
        with col1:
            st.button("Account", use_container_width=True)
        with col2:
            if st.button("Logout", use_container_width=True):
                authenticator.authentication_controller.logout()
                authenticator.cookie_controller.delete_cookie()
                st.session_state.decks = None
                st.session_state.cards = None
                st.session_state.view = "deck_manager"
                st.session_state.show_new_deck_input = False


config = load_config()

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

try:
    authenticator.login()
except LoginError as e:
    st.error(e)

if st.session_state['authentication_status']:
    if 'cards' not in st.session_state:
        st.session_state.cards = load_cards_from_collection(st.session_state["name"])

    if 'decks' not in st.session_state:
        st.session_state.decks = load_decks_from_collection(st.session_state["name"])

    if "show_new_deck_input" not in st.session_state:
        st.session_state.show_new_deck_input = False

    if "view" not in st.session_state:
        st.session_state.view = "deck_manager"

    # Main app interface
    nav = navbar()
    # Conditional display based on user selection
    if nav == SECTION_NAMES[0]:
        show_card_shop(get_sets())
    elif nav == SECTION_NAMES[1]:
        view_decks()
    elif nav == SECTION_NAMES[2]:
        view_cards()
    sidebar()

elif st.session_state['authentication_status'] is False:
    st.error("Username/password is incorrect")
elif st.session_state['authentication_status'] is None:
    st.warning("Please enter your username and password")
