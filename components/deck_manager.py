from io import BytesIO
from typing import Tuple, List

import requests
import streamlit as st
from PIL import Image, ImageOps
from pokemontcgsdk import Card

from utils.deck import Deck
from utils.storage import save_deck_to_collection, remove_deck_from_collection, save_card_to_collection


@st.cache_data
def fetch_image(image_url: str) -> Image.Image | None:
    """
    Fetches an image from a URL and returns it as a PIL Image object.

    Args:
        image_url (str): URL of the image to fetch.

    Returns:
        Image.Image: The fetched image.
    """
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        return image
    except requests.RequestException as e:
        st.error(f"Failed to fetch image: {e}")
        return None


def show_add_deck() -> None:
    """
    Display input fields and save functionality to add a new deck to the session state and storage.
    """
    col1, col2 = st.columns([4, 1], vertical_alignment="bottom")
    with col1:
        deck_name = st.text_input("Empty", label_visibility="collapsed", placeholder="New Deck Name")

    with col2:
        if st.button("Save", use_container_width=True) or deck_name:
            if not deck_name:
                st.toast("Please enter a valid deck name.")
                return

            if deck_name in st.session_state.decks:
                st.toast(f"Deck '{deck_name}' already exists. Please choose a different name.")
            else:
                new_deck = Deck(deck_name, [])
                st.session_state.decks[deck_name] = new_deck
                save_deck_to_collection(new_deck, st.session_state["name"])
                st.toast(f"Deck '{deck_name}' created successfully.")
                st.session_state.show_new_deck_input = False
                st.rerun()


def show_decks() -> None:
    """
    Display all decks with options to edit or delete them.
    """
    for deck in st.session_state.decks.values():
        col1, col2, col3 = st.columns([7, 1, 1])  # Adjust column proportions as needed
        with col1:
            st.subheader(f"{deck.name} ({len(deck)} cards)", anchor=False)
        with col2:
            if st.button("Edit", key=f"edit_{deck.name}", use_container_width=True):
                st.session_state.view = "deck_builder"
                st.session_state.current_deck = deck.name
                st.rerun()
        with col3:
            if st.button("Delete", key=f"delete_{deck.name}", use_container_width=True):
                del st.session_state.decks[deck.name]
                remove_deck_from_collection(deck.name, st.session_state["name"])
                st.toast(f"Deck '{deck.name}' deleted successfully.")
                st.rerun()
        st.divider()


def display_modified_image(image_url: str, opacity: float = 1.0, grayscale: bool = False) -> None:
    """
    Fetches an image from a URL, modifies it based on opacity and grayscale settings, and displays it.

    Args:
        image_url (str): URL of the image to fetch.
        opacity (float, optional): Opacity level of the image between 0.0 and 1.0. Defaults to 1.0.
        grayscale (bool, optional): Whether to convert the image to grayscale. Defaults to False.
    """
    image = fetch_image(image_url)
    if image is None:
        return

    if grayscale:
        image = ImageOps.grayscale(image)

    if opacity < 1.0:
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        r, g, b, a = image.split()
        a = a.point(lambda i: i * opacity)
        image.putalpha(a)

    st.image(image, use_container_width=True)


def display_deck_cards(deck: Deck, num_columns: int) -> None:
    """
    Display the cards in the deck categorized as Pokemon, Trainers, and Energy.

    Args:
        deck (Deck): The deck object containing the cards.
        num_columns (int): Number of columns to use for displaying cards.
    """

    def display_cards(card_list: List[Tuple[Card, int]], header_text: str) -> None:
        """
        Helper function to display a list of cards in a grid layout.

        Args:
            card_list (List[Tuple[Card, int]]): List of cards and their quantities.
            header_text (str): The header text for the card category.
        """
        count = sum(quantity for _, quantity in card_list)
        st.subheader(f"{header_text} ({count}): ", anchor=False)
        columns = st.columns(num_columns)
        for idx, (card, quantity) in enumerate(card_list):
            with columns[idx % num_columns]:
                card_owned = card.id in st.session_state.cards
                quantity_owned = st.session_state.cards[card.id][1] if card_owned else 0
                image_url = card.images.small if card_owned else card.images.large
                if card_owned and quantity_owned >= quantity:
                    st.image(image_url, use_container_width=True)
                else:
                    display_modified_image(image_url, grayscale=True)
                button_label = f"Remove 1 ({quantity} left)"
                if card_owned and quantity_owned < quantity:
                    button_label += f"\n\n ({quantity_owned} owned)"
                if st.button(
                        button_label,
                        key=f"remove_{deck.name}_{header_text}_{card.id}_{idx}",
                        use_container_width=True
                ):
                    deck.remove_card(card)
                    st.session_state.decks[deck.name] = deck
                    st.toast(f"Successfully removed {card.name} from '{deck.name}'")
                    st.rerun()
        st.write("")
        st.write("")
        st.write("")
    with st.container(border=True, height=600):
        # Display Pokémon cards
        pokemon = deck.get_pokemon_cards()
        display_cards(pokemon, "Pokemon")

        # Display Trainer cards
        trainers = deck.get_trainer_cards()
        display_cards(trainers, "Trainers")

        # Display Energy cards
        energies = deck.get_energy_cards()
        display_cards(energies, "Energy")


def show_export(deck: Deck) -> None:
    """
    Displays the export deck data interface.

    Args:
        deck (Deck): The deck to export.
    """
    st.subheader("Export Deck Data")
    deck_data = deck.export()
    if deck_data is None:
        st.error("Failed to export deck data.")
        st.session_state['show_export'] = False
        return
    st.code(deck_data, language='text')
    if st.button("Close Export", use_container_width=True, key="close_export"):
        st.session_state['show_export'] = False


def show_import(deck: Deck) -> None:
    """
    Displays the import deck data interface.

    Args:
        deck (Deck): The deck to import data into.
    """
    st.divider()
    st.subheader("Import Deck Data")
    import_data = st.text_area("Paste deck data here", height=200)
    if st.button("Import Deck", use_container_width=True, key="import_deck"):
            deck.import_from_string(import_data)
            st.success("Deck imported successfully")
            st.session_state['show_import'] = False
            st.rerun()

    if st.button("Close Import", use_container_width=True, key="close_import"):
        st.session_state['show_import'] = False
        st.rerun()


def show_owned_cards(deck: Deck) -> None:
    """
    Displays the interface for adding owned cards to the deck.

    Args:
        deck (Deck): The deck to add cards to.
    """
    with st.container(border=True, height=600):
        st.subheader("Owned cards", anchor=False)
        cards: List[Tuple[Card, int]] = list(st.session_state.cards.values())
        search_query = st.text_input("Search for a card", placeholder="Search for a card", label_visibility="collapsed")
        if search_query:
            search_results = [(card, quantity) for card, quantity in cards if search_query.lower() in card.name.lower()]
        else:
            search_results = cards

        num_columns = 4
        columns = st.columns(num_columns)
        for idx, (card, quantity_owned) in enumerate(search_results):
            with columns[idx % num_columns]:
                st.image(card.images.small, use_container_width=True)
                quantity_in_deck = deck.count_of(card)
                quantity_left = quantity_owned - quantity_in_deck
                if st.button(f"Add ({quantity_left} left)", key=f"add_{card.id}_{idx}", use_container_width=True):
                    if quantity_left > 0:
                        deck.add_card(card)
                        st.session_state.decks[deck.name] = deck
                        save_deck_to_collection(deck, st.session_state["name"])
                        st.toast(f"Successfully added {1} x {card.name} to '{deck.name}'")
                        st.rerun()
                    else:
                        st.toast(f"Cannot add more {card.name} to '{deck.name}'. Limit reached.")


def show_deck_builder(deck: Deck) -> None:
    """
    Displays the deck builder interface, allowing the user to modify the deck.

    Args:
        deck (Deck): The deck to display and edit.
    """
    if 'show_export' not in st.session_state:
        st.session_state['show_export'] = False
    if 'show_import' not in st.session_state:
        st.session_state['show_import'] = False

    col1, col2, col3, col4, col5 = st.columns([5, 1, 1, 1, 1], gap="small", vertical_alignment="bottom")
    with col1:
        is_legal, error = deck.legal()
        st.header(f"{deck.name} ({len(deck)} cards) {'✅' if is_legal else '❌\n\n' + error}", anchor=False)
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
    with col5:
        if st.button("Get missing cards", use_container_width=True):
            # iterate over all cards in the deck and check if they are in the collection, if not add them
            count = 0
            for card, quantity in deck.cards():
                unowned = card.id not in st.session_state.cards
                if unowned or st.session_state.cards[card.id][1] < quantity:
                    q_to_add = quantity - (0 if unowned else st.session_state.cards[card.id][1])
                    save_card_to_collection(card, q_to_add, st.session_state["name"])
                    st.session_state.cards[card.id] = (card, quantity)
                    count += q_to_add
            st.toast(f"Added {count} missing cards to your collection.")

    if st.session_state['show_export']:
        show_export(deck)

    if st.session_state['show_import']:
        show_import(deck)

    left_col, right_col = st.columns([3, 2])
    with left_col:
        display_deck_cards(deck, 5)
    with right_col:
        show_owned_cards(deck)


def view_decks() -> None:
    """
    Main function to manage and view decks. Handles the deck builder and deck manager views.
    """
    if st.session_state.view == "deck_builder":
        current_deck = st.session_state.get("current_deck")
        if current_deck in st.session_state.decks:
            deck = st.session_state.decks[current_deck]
            show_deck_builder(deck)
        else:
            st.error("Deck not found.")
        return

    col1, col2 = st.columns([5, 1], vertical_alignment="bottom")
    with col1:
        st.header("Deck Manager", anchor=False)
    with col2:
        if st.button("Create a New Deck", use_container_width=True):
            st.session_state.show_new_deck_input = True

    if st.session_state.get('show_new_deck_input', False):
        show_add_deck()

    st.divider()

    if not st.session_state.decks:
        st.warning("No decks available. Create a deck first.")
    else:
        show_decks()
