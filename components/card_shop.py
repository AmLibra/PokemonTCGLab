import re
import streamlit as st
from pokemontcgsdk import Card, Set
from utils.pokemon_api import try_find_card_with_params, process_card_name
from utils.storage import save_card_to_collection

# Define constants
POST_BW_SET_IDS = ["bw*", "xy*", "sm*", "swsh*", "sv*"]

def display_cards(cards: list[Card], batch_size: int = 50) -> None:
    """
    Display cards in a grid layout with pagination. Show up to `batch_size` cards at a time,
    with an option to load more recursively.
    Args:
        cards (list[Card]): List of Card objects to display.
        batch_size (int): Number of cards to display per page (default is 50).
    """
    # Initialize the starting index in session state if not already set
    if "displayed_cards_idx" not in st.session_state:
        st.session_state.displayed_cards_idx = batch_size

    # Get the current index range to display
    start_idx = 0
    end_idx = st.session_state.displayed_cards_idx
    end_idx = min(end_idx, len(cards))  # Ensure we don't go out of bounds

    num_columns = 5  # Number of columns for card display
    columns = st.columns(num_columns)

    # Display cards within the current range
    for idx, card in enumerate(cards[start_idx:end_idx]):
        with columns[idx % num_columns]:
            st.image(card.images.large, use_container_width=True)

            # Quantity input and add button
            col1, col2 = st.columns([2, 1], vertical_alignment="bottom")
            with col1:
                quantity = st.number_input(
                    "Quantity", value=1, min_value=1, max_value=4,
                    key=f"quantity_{card.id}_{idx}", label_visibility="collapsed"
                )
            with col2:
                if st.button("Add", key=f"add_{card.id}_{idx}", use_container_width=True):
                    add_card_to_collection(card, quantity)
                    st.toast(f"Successfully added {quantity} x '{card.name}'")

            st.write(""); st.write("")

    # Display the "Show More" button if there are more cards to show
    if end_idx < len(cards):
        if st.button("Show More", key="show_more", use_container_width=True):
            # Increment the range of cards to display
            st.session_state.displayed_cards_idx += batch_size
            st.rerun()

def add_card_to_collection(card: Card, quantity: int) -> None:
    """
    Add a card to the user's collection and save it to persistent storage.
    Args:
        card (Card): Card object to add.
        quantity (int): Quantity of the card to add.
    """
    if card.id in st.session_state.cards:
        _, current_quantity = st.session_state.cards[card.id]
        st.session_state.cards[card.id] = (card, current_quantity + quantity)
    else:
        st.session_state.cards[card.id] = (card, quantity)

    save_card_to_collection(card, quantity, st.session_state["name"])


def filter_sets_by_pattern(sets: list[Set], patterns: list[str]) -> list[Set]:
    """
    Filter sets based on patterns (e.g., post-BW sets).
    Args:
        sets (list[Set]): List of sets to filter.
        patterns (list[str]): List of regex patterns to filter sets by.
    Returns:
        list[Set]: Filtered sets.
    """
    regex_pattern = "|".join(re.escape(pattern).replace("\\*", ".*") for pattern in patterns)
    return [s for s in sets if re.match(regex_pattern, s.id)]


def show_card_shop(sets: list[Set]) -> None:
    """
    Display the card shop interface, allowing users to search for and add cards.
    Args:
        sets (list[Set]): List of available sets.
    """
    st.header("Get a Card", anchor=False)

    # Input fields for card search
    col1, col2 = st.columns(2)
    with col1:
        card_name = st.text_input("Card Name")
    with col2:
        # Sort sets by release date (cached for performance)
        sorted_sets = sorted(sets, key=lambda s: s.releaseDate, reverse=True)
        filtered_sets = ["-"] + [
            f"{s.name} ({s.ptcgoCode})" for s in filter_sets_by_pattern(sorted_sets, POST_BW_SET_IDS)
        ]
        set_name = st.selectbox("Select Set", filtered_sets)

    if card_name or set_name:
        # Process set selection
        set_name_clean = re.sub(r"\(.*\)", "", set_name).strip()
        set_id = next((s.id for s in sets if s.name == set_name_clean), None)
        set_query = f" set.id:{set_id}" if set_name != "-" else ""
        post_bw_filter = "(set.id:bw* or set.id:xy* or set.id:sm* or set.id:swsh* or set.id:sv*)"

        # Fetch cards with the given parameters
        kwargs = {
            "q": f"name:{process_card_name(card_name)} {post_bw_filter} {set_query}",
            "pageSize": 300,
            "page": 1,
            "orderBy": "set.releaseDate,number",
        }
        cards, found = try_find_card_with_params(**kwargs)

        # Handle search results
        if not found:
            st.warning("No cards found with that name. Please try again.")
        else:
            st.success(f"Found {len(cards)} cards")
            display_cards(cards[::-1])  # Reverse card list for display
