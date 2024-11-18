import re

import streamlit as st
from pokemontcgsdk import Card, Set

from utils.pokemon_api import try_find_card_with_params, process_card_name
from utils.storage import save_card_to_collection

post_BW_set_ids = ["bw*", "xy*", "sm*", "swsh*", "sv*"]


# Function to display multiple cards and allow adding them to collection
def display_cards(cards: list[Card]) -> None:
    num_columns = 5
    columns = st.columns(num_columns)
    for idx, card in enumerate(cards):
        with columns[idx % num_columns]:
            st.image(card.images.small, caption=f"{card.name}", use_container_width=True)
            col1, col2 = st.columns([2, 1], vertical_alignment="bottom")
            with col1:
                quantity = st.number_input("Quantity", value=1, min_value=1, max_value=4, key=card.id + str(idx),
                                           label_visibility="collapsed")
            with col2:
                b = st.button("Add", key=card.id + "/" + str(idx), use_container_width=True)
                if b:
                    if card.id in st.session_state.cards:
                        _, current_quantity = st.session_state.cards[card.id]
                        st.session_state.cards[card.id] = (card, current_quantity + quantity)
                    else:
                        st.session_state.cards[card.id] = (card, quantity)
                    save_card_to_collection(card, quantity, st.session_state["name"])
                    st.toast(f"Successfully added {quantity} x '{card.name}'")
            st.title("", anchor=False)
            st.title("", anchor=False)


# Function to add a new card
def show_card_shop(sets: list[Set]) -> None:
    st.header("Get a Card", anchor=False)
    col1, col2 = st.columns(2)
    with col1:
        card_name = st.text_input("Card Name")
    with col2:
        # Join patterns with regex OR operator and escape special characters
        regex_pattern = "|".join(re.escape(sid).replace("\\*", ".*") for sid in post_BW_set_ids)
        filtered_sets = ["-"] + [s.name + f" ({s.ptcgoCode})" for s in sets if re.match(regex_pattern, s.id)]
        set_name = st.selectbox("Select Set", filtered_sets)

    if card_name:
        set_id = next((s.id for s in sets if s.name == set_name), None)
        set_query = f"{'' if set_name == '-' else f' set.id:{set_id}'}"
        post_BW = f"(set.id:bw* or set.id:xy* or set.id:sm* or set.id:swsh* or set.id:sv*)"
        kwargs = {"q": f"name:{process_card_name(card_name)} {post_BW} {set_query}",
                  "pageSize": 200,
                  "page": 1}
        cards, found = try_find_card_with_params(**kwargs)
        # Handle no matches, multiple matches, or a single match
        if not found:
            st.warning("No cards found with that name. Please try again.")
            return
        st.success("Multiple matches found.")
        display_cards(cards)
