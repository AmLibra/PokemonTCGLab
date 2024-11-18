from io import BytesIO
from typing import Tuple, Dict

import requests
import streamlit as st
from PIL import Image, ImageOps, ImageEnhance
from pokemontcgsdk import Card

from utils.deck import Deck
from utils.storage import save_deck_to_collection, remove_deck_from_collection


def show_add_deck():
    col1, col2 = st.columns([4, 1], vertical_alignment="bottom")
    with col1:
        deck_name = st.text_input("Empty", label_visibility="collapsed", placeholder="New Deck Name")

    with col2:
        if st.button("Save", use_container_width=True) or deck_name:
            if not deck_name:
                st.toast("Please enter a valid deck name.")
                return  # Exit early if the deck name is empty

            if deck_name in st.session_state.decks:
                st.toast(f"Deck '{deck_name}' already exists. Please choose a different name.")
            else:
                st.session_state.decks[deck_name] = Deck(deck_name, [])
                save_deck_to_collection(Deck(deck_name, []), st.session_state["name"])
                st.toast(f"Deck '{deck_name}' created successfully.")
                st.session_state.show_new_deck_input = False
                st.rerun()
        else:
            st.toast("Please enter a valid deck name.")


def show_decks():
    for deck in st.session_state.decks.values():
        col1, col2, col3 = st.columns([7, 1, 1])  # Adjust column proportions as needed
        with col1:
            st.subheader(f"{deck.name} ({len(deck)} cards)", anchor=False)  # Deck name on the left
        with col2:
            edit_button = st.button("Edit", key=f"edit_{deck.name}", use_container_width=True)
            if edit_button:
                st.session_state.view = "deck_builder"
                st.session_state.current_deck = deck.name
                st.rerun()  # Refresh the app to reflect the changes
        with col3:
            delete_button = st.button("Delete", key=f"delete_{deck.name}", use_container_width=True)
            if delete_button:
                del st.session_state.decks[deck.name]  # Remove the deck
                remove_deck_from_collection(deck.name, st.session_state["name"])
                st.toast(f"Deck '{deck.name}' deleted successfully.")
                st.rerun()  # Refresh the app to reflect the changes
        st.divider()

def display_modified_image(image_url, opacity=1.0, grayscale=False):
    # Fetch the image from the URL
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))

    if grayscale:
        # Convert image to grayscale
        image = ImageOps.grayscale(image)

    if opacity < 1.0:
        # Ensure the image has an alpha channel
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        # Create an alpha layer with the desired opacity
        alpha = image.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
        image.putalpha(alpha)

    # Display the modified image
    st.image(image, use_container_width=True)

def display_deck_cards(deck: Deck, num_columns: int):
    def display_cards(card_list: list[Tuple[Card, int]], header_text: str):
        count = sum(quantity for _, quantity in card_list)
        st.subheader(f"{header_text} ({count}): ", anchor=False)
        columns = st.columns(num_columns)
        for idx, (card, quantity) in enumerate(card_list):
            with columns[idx % num_columns]:
                # check if card is owned
                if card.id in st.session_state.cards:
                    quantity_owned = st.session_state.cards[card.id][1]
                    if quantity_owned < quantity:
                        st.image(card.images.small, use_container_width=True)
                        if st.button(
                                f"Remove 1 \n\n ({quantity_owned} owned, {quantity} left)",
                                key=f"remove_{deck.name}_{header_text}_{card.id}_{idx}",
                                use_container_width=True
                        ):
                            deck.remove_card(card)
                            st.session_state.decks[deck.name] = deck
                            st.toast(f"Successfully removed {card.name} from '{deck.name}'")
                            st.rerun()
                    else:
                        st.image(card.images.small, use_container_width=True)
                        if st.button(
                                f"Remove 1 ({quantity} left)",
                                key=f"remove_{deck.name}_{header_text}_{card.id}_{idx}",
                                use_container_width=True
                        ):
                            deck.remove_card(card)
                            st.session_state.decks[deck.name] = deck
                            st.toast(f"Successfully removed {card.name} from '{deck.name}'")
                            st.rerun()
                else:
                    display_modified_image(card.images.large, grayscale=True)
                    if st.button(
                            f"Remove 1 ({quantity} left)",
                            key=f"remove_{deck.name}_{header_text}_{card.id}_{idx}",
                            use_container_width=True
                    ):
                        deck.remove_card(card)
                        st.session_state.decks[deck.name] = deck
                        st.toast(f"Successfully removed {card.name} from '{deck.name}'")
                        st.rerun()

    # Display Pokémon cards
    pokemon = deck.get_pokemon_cards()
    display_cards(pokemon, "Pokemon")

    # Display Trainer cards
    trainers = deck.get_trainer_cards()
    display_cards(trainers, "Trainers")

    # Display Energy cards
    energies = deck.get_energy_cards()
    display_cards(energies, "Energy")


def show_deck_builder(deck: Deck):
    # Initialize session state variables
    if 'show_export' not in st.session_state:
        st.session_state['show_export'] = False
    if 'show_import' not in st.session_state:
        st.session_state['show_import'] = False

    is_legal, error = deck.legal()
    if not is_legal:
        st.error(f"Deck is ILLEGAL ❌: {error}")

    # Create four columns for the header and buttons
    col1, col2, col3, col4 = st.columns([5, 1, 1, 1], gap="small", vertical_alignment="bottom")
    with col1:
        st.header(f"{deck.name} ({len(deck)} cards)", anchor=False)
    with col2:
        if st.button("Save", use_container_width=True):
            st.session_state.view = "deck_manager"
            save_deck_to_collection(deck, st.session_state["name"])
            st.toast(f"Deck '{deck.name}' saved successfully.")
            st.rerun()
    with col3:
        if st.button("Export", use_container_width=True):
            st.session_state['show_export'] = True
    with col4:
        if st.button("Import", use_container_width=True):
            st.session_state['show_import'] = True

    # Handle the Export functionality
    if st.session_state['show_export']:
        st.subheader("Export Deck Data")
        deck_data = deck.export()
        if deck_data is None:
            st.error("Failed to export deck data.")
            st.session_state['show_export'] = False
            return
        st.code(deck_data, language='text')
        if st.button("Close Export", use_container_width=True, key="close_export"):
            st.session_state['show_export'] = False

    # Handle the Import functionality
    if st.session_state['show_import']:
        st.divider()
        st.subheader("Import Deck Data")
        import_data = st.text_area("Paste deck data here", height=200)
        if st.button("Import Deck", use_container_width=True, key="import_deck"):
            try:
                deck.import_from_string(import_data)
                st.success("Deck imported successfully")
                st.session_state['show_import'] = False
                st.rerun()
            except Exception as e:
                st.error(f"Failed to import deck: {e}")
        if st.button("Close Import", use_container_width=True, key="close_import"):
            st.session_state['show_import'] = False
            st.rerun()

    st.divider()
    # Create a two-column layout
    left_col, right_col = st.columns([3, 2])
    # Left Column: Cards in the Deck
    with left_col:
        display_deck_cards(deck, 5)

    # Right Column: Add New Cards to Deck
    with right_col:
        st.subheader("Owned cards", anchor=False)
        cards: Dict[str, Tuple[Card, int]] = st.session_state.cards.values()
        # Handle search query
        search_results = cards
        search_query = st.text_input("Search for a card", placeholder="Search for a card", label_visibility="collapsed")
        if search_query:
            search_results = [(card, quantity) for card, quantity in cards if search_query.lower() in card.name.lower()]

        # Display cards in a grid layout
        num_columns = 4
        with st.container(border=True):
            columns = st.columns(num_columns)
            for idx, (card, quantity_in_state) in enumerate(search_results):
                with columns[idx % num_columns]:
                    # Display card image and name
                    st.image(card.images.small, use_container_width=True)
                    if st.button(f"Add ({quantity_in_state - deck.count_of(card)} left)", key=f"add_{card.id}_{idx}",
                                 use_container_width=True):
                        if quantity_in_state > deck.count_of(card):
                            deck.add_card(card)
                            st.toast(f"Successfully added {1} x {card.name} to '{deck.name}'")
                            st.rerun()
                        else:
                            st.toast(f"Cannot add more {card.name} to '{deck.name}'. Limit reached.")


# Function to view decks with details
def view_decks():
    if st.session_state.view == "deck_builder":
        current_deck = st.session_state.get("current_deck", None)
        deck = st.session_state.decks.get(current_deck) if current_deck else None
        show_deck_builder(deck)
        return

    col1, col2 = st.columns([5, 1], vertical_alignment="bottom")
    with col1:
        st.header("Deck Manager", anchor=False)
    with col2:
        if st.button("Create a New Deck", use_container_width=True):
            st.session_state.show_new_deck_input = True

    if st.session_state.show_new_deck_input:
        show_add_deck()

    # Separator between the header and the decks
    st.title("", anchor=False)
    st.title("", anchor=False)
    st.divider()

    if not st.session_state.decks:
        st.warning("No decks available. Create a deck first.")
        return

    if st.session_state.view == "deck_manager":
        show_decks()
