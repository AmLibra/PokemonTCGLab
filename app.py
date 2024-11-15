import streamlit as st
from streamlit_option_menu import option_menu
from components.card_shop import show_card_shop
from utils.pokemon_api import Set
from components.deck_manager import view_decks
from components.card_viewer import view_cards
from utils.storage import load_cards_from_collection, load_decks_from_collection

# Set the page to use wide mode
st.set_page_config(layout="wide", page_title="Pokémon Card Manager")

# cache the API response
@st.cache_data
def get_sets():
    return Set.all()

# Initialize session state to store cards and decks
if 'cards' not in st.session_state:
    st.session_state.cards = load_cards_from_collection()()

if 'decks' not in st.session_state:
    st.session_state.decks = load_decks_from_collection()

if "show_new_deck_input" not in st.session_state:
    st.session_state.show_new_deck_input = False

# Main app interface
st.title("Pokémon Card Manager", anchor=False)

# Top Navigation Menu using option_menu
menu_option = option_menu(
    menu_title=None,  # Hide the title for a cleaner look
    options=["Card Shop", "Decks", "Owned Cards"],  # Menu options
    icons=["plus-circle", "folder", "cards"],  # Optional icons for each menu option
    menu_icon="cast",  # Optional main menu icon
    default_index=0,  # Which option is selected by default
    orientation="horizontal",  # Horizontal to simulate a navigation bar
)

# Conditional display based on user selection
if menu_option == "Card Shop":
    show_card_shop(get_sets())
elif menu_option == "Decks":
    view_decks()
elif menu_option == "Owned Cards":
    view_cards()
