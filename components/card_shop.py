import re

import streamlit as st
import uuid

from streamlit import button

from utils.pokemon_api import try_find_card_with_params
from utils.storage import save_card_to_collection

post_BW_set_ids = ["bw*", "xy*", "sm*", "swsh*", "sv*"]

# Function to display multiple cards and allow adding them to collection
def display_cards(cards):
    num_columns = 5
    columns = st.columns(num_columns)
    for idx, card in enumerate(cards):
        with columns[idx % num_columns]:
            st.image(card.images.small, caption=f"{card.name}", use_container_width=True)
            col1, col2 = st.columns([2, 1], vertical_alignment="bottom")
            with col1:
                quantity = st.number_input("Quantity", value=1, min_value=1, max_value=4, key=card.id + str(idx), label_visibility="collapsed")
            with col2:
                b = st.button("Add", key=card.id + "/" + str(idx))
                if b:
                    st.session_state.cards[str(uuid.uuid4())] = {"card": card, "quantity": quantity}
                    save_card_to_collection(card, quantity)
                    st.toast(f"Successfully added {quantity} x '{card.name}'")
            st.title("", anchor=False)
            st.title("", anchor=False)


# Function to add a new card
def show_card_shop(sets):
    st.header("Get a Card", anchor=False)
    col1, col2 = st.columns(2)
    with col1:
        card_name = st.text_input("Card Name")
    with col2:
        # Join patterns with regex OR operator and escape special characters
        regex_pattern = "|".join(re.escape(id).replace("\\*", ".*") for id in post_BW_set_ids)
        filtered_sets = ["-"] + [s.name for s in sets if re.match(regex_pattern, s.id)]
        set_name = st.selectbox("Select Set", filtered_sets)

    if card_name:
        set_id = next((s.id for s in sets if s.name == set_name), None)
        set_query = f"{'' if set_name == '-' else f' set.id:{set_id}'}"
        post_BW = f"(set.id:bw* or set.id:xy* or set.id:sm* or set.id:swsh* or set.id:sv*)"
        kwargs = {"q": f"name:{card_name}* {post_BW} {set_query}",
                  "pageSize": 100,
                  "page": 1}
        cards, found = try_find_card_with_params(**kwargs)
        # Handle no matches, multiple matches, or a single match
        if not found:
            st.warning("No cards found with that name. Please try again.")
            return
        st.warning("Multiple matches found.")
        display_cards(cards)
