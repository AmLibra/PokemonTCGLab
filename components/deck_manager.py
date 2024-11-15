import streamlit as st

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
        with col3:
            delete_button = st.button("Delete", key=f"delete_{deck.name}", use_container_width=True)
            if delete_button:
                del st.session_state.decks[deck.name]  # Remove the deck
                remove_deck_from_collection(deck.name)
                st.toast(f"Deck '{deck.name}' deleted successfully.")
                st.rerun()  # Refresh the app to reflect the changes

        if len(deck) == 0:
            st.divider()  # Add a divider between decks
            continue

        # Display cards in the deck
        num_columns = 5
        columns = st.columns(num_columns)
        for idx, card_data, quantity in enumerate(deck.cards()):
            card = card_data["card"]
            with columns[idx % num_columns]:
                st.image(card.images.small, caption=f"{quantity} x {card.name}", use_container_width=True)
                _, c, _ = st.columns([1, 2, 1])
                with c:
                    remove_button = st.button("Remove", key=f"{deck.name}/{card.id}/{idx}")
                    if remove_button:
                        if quantity > 1:
                            card_data["quantity"] -= 1
                        else:
                            st.session_state.decks[deck.name].remove(card_data)

                        st.toast(f"Successfully removed {card.name} from '{deck.name}'")
                        # Refresh the app to reflect the changes
                        st.rerun()


# Function to view decks with details
def view_decks():
    col1, col2 = st.columns([5, 1], vertical_alignment="bottom")
    with col1:
        st.header("Deck Manager", anchor=False)
    with col2:
        if st.button("Create a New Deck"):
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

    show_decks()
