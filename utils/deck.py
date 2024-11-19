import re
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from typing import Tuple

from pokemontcgsdk import Card

from utils.pokemon_api import import_card_from_string, get_sets


class Deck:
    def __init__(self, name: str, cards: list[Card]) -> None:
        """
        Initialize a new Deck object.

        :param name:    Name of the deck.
        :param cards:   List of Card objects to add to the deck.
        """
        self.name = name
        self.trainer_cards: dict[str, (Card, int)] = {}
        self.pokemon_cards: dict[str, (Card, int)] = {}
        self.energy_cards: dict[str, (Card, int)] = {}
        for card in cards:
            self._add_to_category(card, 1)

    def _get_card_category(self, card: Card) -> dict[str, (Card, int)] | None:
        """
        Get the category of the card.

        :param card:    The card to categorize.
        :return:        The cards of the same category as the input card.
        """

        if card.supertype == "Trainer":
            return self.trainer_cards
        elif card.supertype == "Pokémon":
            return self.pokemon_cards
        elif card.supertype == "Energy":
            return self.energy_cards
        return None

    def _add_to_category(self, card: Card, quantity: int) -> None:
        """
        Add a card to the appropriate category.

        :param card:        The card to add.
        :param quantity:    The quantity of the card to add.
        :return:
        """
        category = self._get_card_category(card)
        if category is not None:
            if card.id in category:
                category[card.id]["quantity"] += quantity
            else:
                category[card.id] = {"card": card, "quantity": max(1, quantity)}

    def add_card(self, card: Card) -> None:
        """
        Add a card to the deck.

        :param card:    The card to add.
        :return:        None
        """
        self._add_to_category(card, 1)

    def remove_card(self, card: Card) -> None:
        """
        Remove a card from the deck.

        :param card:    The card to remove.
        :return:        None
        """
        category = self._get_card_category(card)
        if category is not None and card.id in category:
            if category[card.id]["quantity"] > 1:
                category[card.id]["quantity"] -= 1
            else:
                del category[card.id]

    def cards(self) -> list[Tuple[Card, int]]:
        """
        Get all cards in the deck.

        :return:   A list of tuples containing the card and its quantity.
        """
        return [
            (category[card_id]["card"], category[card_id]["quantity"])
            for category in [self.trainer_cards, self.pokemon_cards, self.energy_cards]
            for card_id in category
        ]

    def get_pokemon_cards(self) -> list[Tuple[Card, int]]:
        """
        Get all Pokémon cards in the deck.

        :return:  A list of tuples containing the Pokémon card and its quantity.
        """
        return [(category[card_id]["card"], category[card_id]["quantity"]) for category in [self.pokemon_cards] for
                card_id in category]

    def get_trainer_cards(self) -> list[Tuple[Card, int]]:
        """
        Get all Trainer cards in the deck.

        :return: A list of tuples containing the Trainer card and its quantity.
        """
        return [(category[card_id]["card"], category[card_id]["quantity"]) for category in [self.trainer_cards] for
                card_id in category]

    def get_energy_cards(self) -> list[Tuple[Card, int]]:
        """
        Get all Energy cards in the deck.

        :return: A list of tuples containing the Energy card and its quantity.
        """
        return [(category[card_id]["card"], category[card_id]["quantity"]) for category in [self.energy_cards] for
                card_id in category]

    def count_of(self, card: Card) -> int:
        """
        Get the quantity of a specific card in the deck.

        :param card:    The card to count.
        :return:        The quantity of the card in the deck.
        """
        category = self._get_card_category(card)
        if category is not None and card.id in category:
            return category[card.id]["quantity"]
        return 0

    def legal(self) -> (bool, str):
        """
        Check if the deck is legal according to the official Pokémon TCG rules:
        1. A deck must contain exactly 60 cards.
        2. A deck can have a maximum of 4 copies of a single card with the same name (excluding basic energy).
        3. Basic energy cards have no limit.

        :return:   A tuple containing a boolean indicating legality and a message.
        """
        # Rule 1: Check total number of cards
        if len(self) != 60:
            return False, "Deck must contain exactly 60 cards."

        # Rule 2: Check for more than 4 copies of a single card (excluding basic energy)
        for category in [self.pokemon_cards, self.trainer_cards]:
            for card_id, card_info in category.items():
                if card_info["quantity"] > 4:
                    return False, f"Too many copies of {card_info['card'].name}. Maximum allowed is 4."

        # Rule 3: Basic energy cards have no limit, but ensure they are valid energy cards
        for card_id, card_info in self.energy_cards.items():
            if card_info["card"].supertype != "Energy":
                return False, f"Invalid energy card: {card_info['card'].name}."

        # If all rules pass
        return True, "Deck is legal."

    def __len__(self) -> int:
        """
        Get the total number of cards in the deck.

        :return:    The total number of cards in the deck.
        """
        return sum(
            sum(category[card_id]["quantity"] for card_id in category)
            for category in [self.trainer_cards, self.pokemon_cards, self.energy_cards]
        )

    def import_from_string(self, import_data: str) -> None:
        """
        Import a deck from a string input, containing lines of the format:
        <count> <card_name> <set_code> <card_number>

        Args:
            import_data (str): The string input containing the deck data.
        """
        category_lines = [
            line.strip()
            for line in import_data.split("\n")
            if line.strip() and ":" not in line
        ]
        sets = get_sets()  # Assuming get_sets() is defined and returns List[Set]

        # Use itertools.repeat to pass 'sets' to each call
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(import_card_from_string, category_lines, repeat(sets)))

        # Add fetched cards to the deck sequentially
        for card, qty in results:
            if card:
                for _ in range(qty):
                    self.add_card(card)

    def export(self) -> str:
        """
        Export the deck to a string format that can be imported later.

        :return:  The string representation of the deck.
        """

        def get_set_ptcgo_code(set_id: str) -> str:
            for s in get_sets():
                if s.id == set_id:
                    return s.ptcgoCode
            return "none"

        # remove anything between the parentheses in the card name
        def clean_card_name(card_name: str) -> str:
            return re.sub(r"\(.*\)", "", card_name).strip()

        return "\n".join(
            [
                f"{quantity} {clean_card_name(card.name)} {get_set_ptcgo_code(card.set.id)} {card.number}"
                for card, quantity in self.cards()
            ]
        )
