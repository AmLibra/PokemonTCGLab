from typing import Tuple

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from pokemontcgsdk import Card
from streamlit_authenticator import LoginError, Hasher
from streamlit_option_menu import option_menu
from yaml import SafeLoader

from components.card_shop import show_card_shop
from components.card_viewer import view_cards
from components.deck_manager import view_decks
from utils.deck import Deck  # For type hinting
from utils.pokemon_api import get_sets
from utils.storage import load_cards_from_collection, load_decks_from_collection

APP_TITLE = "Pokémon Card Manager"
SECTION_NAMES = ["Card Shop", "Deck Manager", "Owned Cards"]
SECTION_ICONS = ["plus-circle", "folder", "cards"]

# Set the page to wide mode and define the title
st.set_page_config(layout="wide", page_title=APP_TITLE, initial_sidebar_state="expanded")


@st.cache_data
def load_config() -> dict:
    """
    Load the configuration file for authentication and app settings.
    Returns:
        dict: Parsed configuration dictionary.
    """
    with open('config.yaml', 'r', encoding='utf-8') as f:
        return yaml.load(f, Loader=SafeLoader)


def save_config(config: dict) -> None:
    """
    Save the updated configuration back to the YAML file.
    Args:
        config (dict): Configuration dictionary to save.
    """
    Hasher([""]).hash_passwords(config['credentials'])
    with open('config.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(config, f)


def navbar() -> str:
    """
    Create the navigation menu at the top of the app.
    Returns:
        str: The name of the selected menu option.
    """
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
    return option_menu(
        menu_title=None,
        options=SECTION_NAMES,
        icons=SECTION_ICONS,
        menu_icon="cast",
        default_index=2,
        orientation="horizontal",
    )


def sidebar(authenticator: stauth.Authenticate) -> None:
    """
    Render the sidebar with user information and account options.
    Args:
        authenticator (stauth.Authenticate): Authentication controller instance.
    """
    with st.sidebar:
        st.title(APP_TITLE, anchor=False)
        st.write(f"Welcome to the Pokémon Card Manager, {st.session_state['name']}!")
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
                st.rerun()


def load_collections(user: str) -> (dict[str, Tuple[Card, int]], dict[str, Deck]):
    """
    Load card and deck collections for a user.
    Args:
        user (str): Username for which to load collections.
    Returns:
        Tuple[list, list]: Loaded cards and decks.
    """
    cards = load_cards_from_collection(user)
    decks = load_decks_from_collection(user)
    return cards, decks


def main():
    """
    Main function to run the Streamlit app.
    """
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

    if st.session_state.get('authentication_status'):
        # Lazy initialization of session state variables
        if 'cards' not in st.session_state or 'decks' not in st.session_state:
            st.session_state['cards'], st.session_state['decks'] = load_collections(st.session_state['name'])

        if "show_new_deck_input" not in st.session_state:
            st.session_state.show_new_deck_input = False

        if "view" not in st.session_state:
            st.session_state.view = "deck_manager"

        # Main app interface
        nav = navbar()
        if nav == SECTION_NAMES[0]:
            show_card_shop(get_sets())
        elif nav == SECTION_NAMES[1]:
            view_decks()
        elif nav == SECTION_NAMES[2]:
            view_cards()
        sidebar(authenticator)

    elif st.session_state.get('authentication_status') is False:
        st.error("Username/password is incorrect")
    elif st.session_state.get('authentication_status') is None:
        st.warning("Please enter your username and password")


if __name__ == "__main__":
    main()
