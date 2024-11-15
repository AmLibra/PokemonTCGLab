import os
import pickle
from typing import List, Dict, Union

from pokemontcgsdk import Card

from utils.deck import Deck

cards_path = "data/cards.pkl"
decks_path = "data/decks.pkl"


def save_deck_to_collection(deck: Deck) -> None:
    decks: List[Deck] = []
    if os.path.exists(decks_path):
        with open(decks_path, "rb") as f:
            try:
                decks = pickle.load(f)
            except EOFError:
                pass
    else:
        os.makedirs("data", exist_ok=True)

    # Check for duplicate and replace if found
    existing_deck = next((d for d in decks if d.name == deck.name), None)
    if existing_deck:
        decks[decks.index(existing_deck)] = deck
    else:
        decks.append(deck)

    with open(decks_path, "wb") as f:
        pickle.dump(decks, f)  # type: ignore


def load_decks_from_collection() -> Dict[str, Deck]:
    decks: Dict[str, Deck] = {}
    if os.path.exists(decks_path):
        with open(decks_path, "rb") as f:
            try:
                loaded_decks: List[Deck] = pickle.load(f)
                decks = {deck.name: deck for deck in loaded_decks}
            except EOFError:
                pass
    return decks


def remove_deck_from_collection(deck_name: str) -> None:
    decks: List[Deck] = []
    if os.path.exists(decks_path):
        with open(decks_path, "rb") as f:
            try:
                decks = pickle.load(f)
            except EOFError:
                pass

    # Remove the deck if it exists
    decks = [deck for deck in decks if deck.name != deck_name]

    with open(decks_path, "wb") as f:
        pickle.dump(decks, f)  # type: ignore


def save_card_to_collection(card: Card, quantity: int) -> None:
    cards: Dict[str, Dict[str, Union[Card, int]]] = {}
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
        cards[card_id]["quantity"] += quantity
    else:
        cards[card_id] = {"card": card, "quantity": quantity}

    with open(cards_path, "wb") as f:
        pickle.dump(cards, f)  # type: ignore


def load_cards_from_collection() -> Dict[str, Dict[str, Union[Card, int]]]:
    cards: Dict[str, Dict[str, Union[Card, int]]] = {}
    if os.path.exists(cards_path):
        with open(cards_path, "rb") as f:
            try:
                cards = pickle.load(f)
            except EOFError:
                pass
    return cards


def remove_card_from_collection(card_id: str) -> None:
    if os.path.exists(cards_path):
        with open(cards_path, "rb") as f:
            try:
                cards = pickle.load(f)
            except EOFError:
                cards = {}

        if card_id in cards:
            if cards[card_id]["quantity"] > 1:
                cards[card_id]["quantity"] -= 1
            else:
                cards.pop(card_id)

        with open(cards_path, "wb") as f:
            pickle.dump(cards, f)  # type: ignore
