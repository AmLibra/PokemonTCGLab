import os
import pickle
from typing import Dict, Tuple

from pokemontcgsdk import Card

from utils.deck import Deck

data_path = "data"
cards_file = "cards.pkl"
decks_file = "decks.pkl"


def save_deck_to_collection(deck: Deck, name: str) -> None:
    decks: Dict[str, Deck] = {}
    user_decks_path = os.path.join(data_path, name, decks_file)
    if os.path.exists(user_decks_path):
        with open(user_decks_path, "rb") as f:
            try:
                decks = pickle.load(f)
            except EOFError:
                pass
    else:
        os.makedirs("data", exist_ok=True)

    # Replace or add the deck in the dictionary
    decks[deck.name] = deck

    with open(user_decks_path, "wb") as f:
        pickle.dump(decks, f)  # type: ignore


def load_decks_from_collection(name: str) -> Dict[str, Deck]:
    decks: Dict[str, Deck] = {}
    user_decks_path = os.path.join(data_path, name, decks_file)
    # create the data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    os.makedirs(os.path.join(data_path, name), exist_ok=True)

    if os.path.exists(user_decks_path):
        with open(user_decks_path, "rb") as f:
            try:
                loaded_decks = pickle.load(f)
                decks = {deck.name: deck for deck in loaded_decks.values()}
            except EOFError:
                pass
    return decks


def remove_deck_from_collection(deck_name: str, name: str) -> None:
    decks: Dict[str, Deck] = {}
    user_decks_path = os.path.join(data_path, name, decks_file)
    if os.path.exists(user_decks_path):
        with open(user_decks_path, "rb") as f:
            try:
                decks = pickle.load(f)
            except EOFError:
                pass

    # Remove the deck if it exists
    if deck_name in decks:
        decks.pop(deck_name)

    with open(user_decks_path, "wb") as f:
        pickle.dump(decks, f)  # type: ignore


def save_card_to_collection(card: Card, quantity: int, name: str) -> None:
    cards: Dict[str, Tuple[Card, int]] = {}
    cards_path = os.path.join(data_path, name, cards_file)
    if os.path.exists(cards_path):
        with open(cards_path, "rb") as f:
            try:
                cards = pickle.load(f)
            except EOFError:
                pass
    else:
        os.makedirs("data", exist_ok=True)

    card_id = card.id
    if card_id in cards:
        cards[card_id] = (card, cards[card_id][1] + quantity)
    else:
        cards[card_id] = (card, quantity)

    with open(cards_path, "wb") as f:
        pickle.dump(cards, f)  # type: ignore


def load_cards_from_collection(name: str) -> Dict[str, Tuple[Card, int]]:
    cards: Dict[str, Tuple[Card, int]] = {}
    # create the data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    os.makedirs(os.path.join(data_path, name), exist_ok=True)

    cards_path = os.path.join(data_path, name, cards_file)
    if os.path.exists(cards_path):
        with open(cards_path, "rb") as f:
            try:
                cards = pickle.load(f)
            except EOFError:
                pass
    return cards


def remove_one_card_from_collection(card_id: str, name: str) -> None:
    cards_path = os.path.join(data_path, name, cards_file)
    if os.path.exists(cards_path):
        with open(cards_path, "rb") as f:
            try:
                cards = pickle.load(f)
            except EOFError:
                cards = {}

        if card_id in cards:
            if cards[card_id][1] > 1:
                cards[card_id] = (cards[card_id][0], cards[card_id][1] - 1)
            else:
                cards.pop(card_id)

        with open(cards_path, "wb") as f:
            pickle.dump(cards, f)  # type: ignore
