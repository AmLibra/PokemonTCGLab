from typing import Tuple, Dict

import streamlit as st
from pokemontcgsdk import Card
from streamlit import container

from utils.deck import Deck
from utils.storage import save_deck_to_collection, remove_deck_from_collection


def show_add_deck():
    # Create a two-column layout for text input and button
    col1, col2 = st.columns([4, 1], vertical_alignment="bottom")
    with col1:
        deck_name = st.text_input("Empty", label_visibility="collapsed", placeholder="New Deck Name")

    with col2:
        if st.button("Save", use_container_width=True) or deck_name:
            if deck_name in st.session_state.decks:
                st.toast(f"Deck '{deck_name}' already exists. Please choose a different name.")
            else:
                st.session_state.decks[deck_name] = Deck(deck_name, [])
                save_deck_to_collection(Deck(deck_name, []))
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
                remove_deck_from_collection(deck.name)
                st.toast(f"Deck '{deck.name}' deleted successfully.")
                st.rerun()  # Refresh the app to reflect the changes
        st.divider()


def show_deck_builder(deck: Deck):
    col1, col2 = st.columns([5, 1], vertical_alignment="bottom")
    with col1:
        st.header(deck.name, anchor=False)
    with col2:
        if st.button("Save", use_container_width=True):
            st.session_state.view = "deck_manager"
            save_deck_to_collection(deck)
            st.toast(f"Deck '{deck.name}' saved successfully.")
            st.rerun()

    # Display the deck name or a text input for a new deck
    # Create a two-column layout for cards in deck on the left and card search on the right, with a divider in between
    st.divider()

    # Create a two-column layout
    left_col, right_col = st.columns([3, 2])

    # Left Column: Cards in the Deck
    with left_col:
        st.subheader("Cards in Deck", anchor=False)
        num_columns = 4
        columns = st.columns(num_columns)

        for idx, (card, quantity) in enumerate(deck.cards()):
            with columns[idx % num_columns]:
                st.image(card.images.large, caption=f"{quantity} x {card.name}", use_container_width=True)
                if st.button(f"Remove {card.name}", key=f"remove_{deck.name}_{card.id}_{idx}",
                             use_container_width=True):
                    deck.remove_card(card)
                    st.session_state.decks[deck.name] = deck
                    st.toast(f"Successfully removed {card.name} from '{deck.name}'")
                    st.rerun()

    # Right Column: Add New Cards to Deck
    with right_col:
        st.subheader("Owned cards", anchor=False)

        # Fetch cards from session state
        cards: Dict[str, Tuple[Card, int]] = st.session_state.cards.values()

        # Handle search query
        search_results = cards
        search_query = st.text_input("Search for Cards", placeholder="Enter card name")
        if search_query:
            search_results = [(card, quantity) for card, quantity in cards if search_query.lower() in card.name.lower()]

        # Display cards in a grid layout
        num_columns = 4
        with st.container(height=400):
            columns = st.columns(num_columns)
            for idx, (card, quantity_in_state) in enumerate(search_results):
                with columns[idx % num_columns]:
                    # Display card image and name
                    st.image(card.images.small, caption=f"{quantity_in_state} x {card.name}", use_container_width=True)

                    # Create a vertical block for inputs and buttons
                    st.write("")  # Add spacing if needed
                    if st.button(f"Add", key=f"add_{card.id}_{idx}", use_container_width=True):
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
