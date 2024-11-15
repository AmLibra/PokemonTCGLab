import os

import streamlit as st
from pokemontcgsdk import RestClient, Card, Set
from dotenv import load_dotenv

# Initialize the Pokémon TCG API client
load_dotenv()
RestClient.configure(os.getenv("POKEMON_API_KEY"))

@st.cache_data
def try_find_card_with_params(**kwargs) -> (Card, bool):
    try:
        cards = Card.where(**kwargs)
        if cards:
            return cards, True
        else:
            st.warning("No cards found with the provided parameters. Please try again.")
            return None, False
    except Exception as e:
        st.error(f"Error contacting Pokémon TCG API with the provided parameters")
        return None, False