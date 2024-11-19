import os
import pickle
from typing import Any, Dict, Tuple

from pokemontcgsdk import Card

from utils.deck import Deck

DATA_PATH = "data"
CARDS_FILE = "cards.pkl"
DECKS_FILE = "decks.pkl"


def ensure_directory(path: str) -> None:
    """
    Ensures that the specified directory exists.

    Args:
        path (str): The directory path to ensure.
    """
    os.makedirs(path, exist_ok=True)


def load_pickle_file(file_path: str) -> Any:
    """
    Loads data from a pickle file.

    Args:
        file_path (str): The path to the pickle file.

    Returns:
        Any: The data loaded from the pickle file, or an empty dictionary if the file does not exist or is empty.
    """
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            try:
                return pickle.load(f)
            except EOFError:
                return {}
    return {}


def save_pickle_file(data: Any, file_path: str) -> None:
    """
    Saves data to a pickle file.

    Args:
        data (Any): The data to save.
        file_path (str): The path to the pickle file.
    """
    with open(file_path, "wb") as f:
        pickle.dump(data, f) #type: ignore


def get_user_path(name: str) -> str:
    """
    Constructs the user-specific data path.

    Args:
        name (str): The user's name.

    Returns:
        str: The user-specific data path.
    """
    return os.path.join(DATA_PATH, name)


def save_deck_to_collection(deck: Deck, name: str) -> None:
    """
    Saves a deck to the user's collection.

    Args:
        deck (Deck): The deck to save.
        name (str): The user's name.
    """
    user_path = get_user_path(name)
    ensure_directory(user_path)
    user_decks_path = os.path.join(user_path, DECKS_FILE)
    decks: Dict[str, Deck] = load_pickle_file(user_decks_path)
    decks[deck.name] = deck
    save_pickle_file(decks, user_decks_path)


def load_decks_from_collection(name: str) -> Dict[str, Deck]:
    """
    Loads all decks from the user's collection.

    Args:
        name (str): The user's name.

    Returns:
        Dict[str, Deck]: A dictionary of deck names to Deck objects.
    """
    user_path = get_user_path(name)
    ensure_directory(user_path)
    user_decks_path = os.path.join(user_path, DECKS_FILE)
    decks_data: Dict[str, Deck] = load_pickle_file(user_decks_path)
    decks = {deck_name: deck for deck_name, deck in decks_data.items()}
    return decks


def remove_deck_from_collection(deck_name: str, name: str) -> None:
    """
    Removes a deck from the user's collection.

    Args:
        deck_name (str): The name of the deck to remove.
        name (str): The user's name.
    """
    user_path = get_user_path(name)
    user_decks_path = os.path.join(user_path, DECKS_FILE)
    decks: Dict[str, Deck] = load_pickle_file(user_decks_path)
    if deck_name in decks:
        decks.pop(deck_name)
        save_pickle_file(decks, user_decks_path)


def save_card_to_collection(card: Card, quantity: int, name: str) -> None:
    """
    Saves a card to the user's collection, updating the quantity if it already exists.

    Args:
        card (Card): The card to save.
        quantity (int): The quantity of the card to add.
        name (str): The user's name.
    """
    user_path = get_user_path(name)
    ensure_directory(user_path)
    cards_path = os.path.join(user_path, CARDS_FILE)
    cards: Dict[str, Tuple[Card, int]] = load_pickle_file(cards_path)
    card_id = card.id
    if card_id in cards:
        existing_quantity = cards[card_id][1]
        cards[card_id] = (card, existing_quantity + quantity)
    else:
        cards[card_id] = (card, quantity)
    save_pickle_file(cards, cards_path)


def load_cards_from_collection(name: str) -> Dict[str, Tuple[Card, int]]:
    """
    Loads all cards from the user's collection.

    Args:
        name (str): The user's name.

    Returns:
        Dict[str, Tuple[Card, int]]: A dictionary of card IDs to tuples of Card objects and quantities.
    """
    user_path = get_user_path(name)
    ensure_directory(user_path)
    cards_path = os.path.join(user_path, CARDS_FILE)
    cards: Dict[str, Tuple[Card, int]] = load_pickle_file(cards_path)
    return cards


def remove_one_card_from_collection(card_id: str, name: str) -> None:
    """
    Removes one instance of a card from the user's collection.

    Args:
        card_id (str): The ID of the card to remove.
        name (str): The user's name.
    """
    user_path = get_user_path(name)
    cards_path = os.path.join(user_path, CARDS_FILE)
    cards: Dict[str, Tuple[Card, int]] = load_pickle_file(cards_path)
    if card_id in cards:
        card, quantity = cards[card_id]
        if quantity > 1:
            cards[card_id] = (card, quantity - 1)
        else:
            cards.pop(card_id)
        save_pickle_file(cards, cards_path)
