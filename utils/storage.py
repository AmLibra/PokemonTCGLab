import pickle
import os

cards_path = "data/cards.pkl"  # Use a .pkl extension to indicate a pickle file
decks_path = "data/decks.pkl"

def save_deck_to_collection(deck_name, cards):
    # Check if the decks file exists and load it if so
    if os.path.exists(decks_path):
        with open(decks_path, "rb") as f:  # Open in binary read mode
            try:
                decks = pickle.load(f)
            except EOFError:
                decks = {}  # If the file is empty, start with an empty dictionary
    else:
        os.makedirs("data", exist_ok=True)  # Ensure the data directory exists
        decks = {}

    # Add or update deck information in the dictionary
    if deck_name in decks:
        decks[deck_name] += cards
    else:
        decks[deck_name] = cards

    # Save the updated decks back to the file
    with open(decks_path, "wb") as f:  # Open in binary write mode
        pickle.dump(decks, f)


def load_decks_from_collection():
    if os.path.exists(decks_path):
        with open(decks_path, "rb") as f:  # Open in binary read mode
            try:
                decks = pickle.load(f)
            except EOFError:
                decks = {}  # If the file is empty, start with an empty dictionary
    else:
        decks = {}
    return decks

def remove_deck_from_collection(deck_name):
    if os.path.exists(decks_path):
        with open(decks_path, "rb") as f:  # Open in binary read mode
            try:
                decks = pickle.load(f)
            except EOFError:
                decks = {}  # If the file is empty, start with an empty dictionary
    else:
        return

    if deck_name in decks:
        decks.pop(deck_name)

    with open(decks_path, "wb") as f:  # Open in binary write mode
        pickle.dump(decks, f)

def save_card_to_collection(card, quantity: int):
    # Check if the cards file exists and load it if so
    if os.path.exists(cards_path):
        with open(cards_path, "rb") as f:  # Open in binary read mode
            try:
                cards = pickle.load(f)
            except EOFError:
                cards = {}  # If the file is empty, start with an empty dictionary
    else:
        os.makedirs("data", exist_ok=True)  # Ensure the data directory exists
        cards = {}

    # Add or update card information in the dictionary
    card_id = card.id
    if card_id in cards:
        cards[card_id]["quantity"] += quantity
    else:
        cards[card_id] = {"card": card, "quantity": quantity}

    # Save the updated cards back to the file
    with open(cards_path, "wb") as f:  # Open in binary write mode
        pickle.dump(cards, f)

# Function to load cards from collection
def load_cards_from_collection():
    if os.path.exists(cards_path):
        with open(cards_path, "rb") as f:  # Open in binary read mode
            try:
                cards = pickle.load(f)
            except EOFError:
                cards = {}  # If the file is empty, start with an empty dictionary
    else:
        cards = {}
    return cards

def remove_card_from_collection(card_id):
    if os.path.exists(cards_path):
        with open(cards_path, "rb") as f:  # Open in binary read mode
            try:
                cards = pickle.load(f)
            except EOFError:
                cards = {}  # If the file is empty, start with an empty dictionary
    else:
        return

    if card_id in cards:
        if cards[card_id]["quantity"] > 1:
            cards[card_id]["quantity"] -= 1
        else:
            cards.pop(card_id)

    with open(cards_path, "wb") as f:  # Open in binary write mode
        pickle.dump(cards, f)
