import os
import re
from typing import List

import streamlit as st
from dotenv import load_dotenv
from pokemontcgsdk import RestClient, Card, Set

# Initialize the Pokémon TCG API client
load_dotenv()
RestClient.configure(os.getenv("POKEMON_API_KEY"))

# Function to process the card name to sanitize it and handle multi-word names
def process_card_name(card_name: str) -> str:
    # Split the input by whitespace, normalize case, and escape special characters
    words = [re.escape(word.lower()) for word in card_name.split()]
    # Join the words with regex lookahead for strict order matching
    return "*" + ".*".join(words) + "*"

# cache the API response
@st.cache_data
def get_sets() -> list[Set]:
    return Set.all()

@st.cache_data
def try_find_card_with_params(**kwargs) -> (List[Card], bool):
    try:
        cards = Card.where(**kwargs)
        if cards:
            return cards, True
        else:
            st.warning("No cards found with the provided parameters. Please try again.")
            return None, False
    except Exception:
        st.error(f"Error contacting Pokémon TCG API with the provided parameters")
        return None, False

# Function to import a card from a string input, such as "3 Regidrago V SIT 135"
def import_card_from_string(card_string: str) -> (int, Card | None):
    try:
        split_words = card_string.split()
        # Parse the quantity, card name, set code, and card number
        quantity = int(split_words[0])
        set_code = split_words[-2]
        card_number = split_words[-1]
        set_id = next((s.id for s in get_sets() if s.ptcgoCode == set_code), None)
        card = Card.find(set_id+"-"+card_number)
        if card:
            return card, quantity
        else:
            return None, 0
    except Exception:
        return None, 0