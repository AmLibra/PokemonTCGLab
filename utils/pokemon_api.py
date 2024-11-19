import os
import re
from typing import List, Optional, Tuple

import streamlit as st
from dotenv import load_dotenv
from pokemontcgsdk import RestClient, Card, Set

# Initialize the Pokémon TCG API client
load_dotenv()
RestClient.configure(os.getenv("POKEMON_API_KEY"))


# Function to process the card name to sanitize it and handle multi-word names
def process_card_name(card_name: str) -> str:
    """
    Process the card name to sanitize it and handle multi-word names.

    :param card_name:   The card name to process.
    :return:            The processed card name.
    """
    # Split the input by whitespace, normalize case, and escape special characters
    words = [re.escape(word.lower()) for word in card_name.split()]
    # Join the words with regex lookahead for strict order matching
    return "*" + ".*".join(words) + "*"


# cache the API response
@st.cache_data
def get_sets() -> list[Set]:
    """
    Get all the sets from the Pokémon TCG API.
    :return:  A list of all the sets.
    """
    return Set.all()


@st.cache_data
def try_find_card_with_params(**kwargs) -> (List[Card], bool):
    """
    Try to find a card with the given parameters.
    :param kwargs:  The parameters to search for, common parameters include:
                    - name: The name of the card.
                    - set.id: The ID of the set.
    :return:       A tuple containing the list of cards found and a boolean indicating if the search was successful.
    """
    try:
        cards = Card.where(**kwargs)
        if cards:
            return cards, True
        else:
            return None, False
    except Exception:
        return None, False


def import_card_from_string(card_string: str, sets: List[Set]) -> Tuple[Optional[Card], int]:
    """
    Imports a card from a string input, such as "3 Regidrago V SIT 135".

    Args:
        card_string (str): The string input to parse.
        sets (List[Set]): The list of available sets.

    Returns:
        Tuple[Optional[Card], int]: A tuple containing the card object and the quantity.
    """
    split_words = card_string.strip().split()
    if len(split_words) < 3:
        return None, 0

    quantity = int(split_words[0])
    set_code = split_words[-2].strip().upper()
    card_number = split_words[-1].strip()

    # Normalize set_code and ptcgoCode for case-insensitive comparison
    matching_sets = [
        s for s in sets if s.ptcgoCode and s.ptcgoCode.strip().upper() == set_code
    ]
    if not matching_sets:
        return None, 0
    for s in matching_sets:
        set_id = s.id
        card_id = f"{set_id}-{card_number}"
        try:
            card = Card.find(card_id)
            if card:
                return card, quantity
        except Exception:  # Handle exceptions such as card not found
            continue

    print(f"No card found for set code '{set_code}' and card number '{card_number}'")
    return None, 0
