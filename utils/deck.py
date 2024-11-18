import re
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple

from pokemontcgsdk import Card

from utils.pokemon_api import import_card_from_string, get_sets


class Deck:
    def __init__(self, name: str, cards: list[Card]) -> None:
        self.name = name
        self.trainer_cards = {}
        self.pokemon_cards = {}
        self.energy_cards = {}
        for card in cards:
            self._add_to_category(card, 1)

    def _get_card_category(self, card: Card) -> dict[str, (Card, int)] | None:
        if card.supertype == "Trainer":
            return self.trainer_cards
        elif card.supertype == "Pokémon":
            return self.pokemon_cards
        elif card.supertype == "Energy":
            return self.energy_cards
        return None

    def _add_to_category(self, card: Card, quantity: int) -> None:
        category = self._get_card_category(card)
        if category is not None:
            if card.id in category:
                category[card.id]["quantity"] += quantity
            else:
                category[card.id] = {"card": card, "quantity": max(1, quantity)}

    def add_card(self, card: Card) -> None:
        self._add_to_category(card, 1)

    def remove_card(self, card: Card) -> None:
        category = self._get_card_category(card)
        if category is not None and card.id in category:
            if category[card.id]["quantity"] > 1:
                category[card.id]["quantity"] -= 1
            else:
                del category[card.id]

    def cards(self) -> list[Tuple[Card, int]]:
        return [
            (category[card_id]["card"], category[card_id]["quantity"])
            for category in [self.trainer_cards, self.pokemon_cards, self.energy_cards]
            for card_id in category
        ]

    def get_pokemon_cards(self) -> list[Tuple[Card, int]]:
        return [(category[card_id]["card"], category[card_id]["quantity"]) for category in [self.pokemon_cards] for
                card_id in category]

    def get_trainer_cards(self) -> list[Tuple[Card, int]]:
        return [(category[card_id]["card"], category[card_id]["quantity"]) for category in [self.trainer_cards] for
                card_id in category]

    def get_energy_cards(self) -> list[Tuple[Card, int]]:
        return [(category[card_id]["card"], category[card_id]["quantity"]) for category in [self.energy_cards] for
                card_id in category]

    def count_of(self, card: Card) -> int:
        category = self._get_card_category(card)
        if category is not None and card.id in category:
            return category[card.id]["quantity"]
        return 0

    def legal(self) -> (bool, str):
        # Official Pokémon TCG Rules:
        # 1. A deck must contain exactly 60 cards.
        # 2. A deck can have a maximum of 4 copies of a single card with the same name (excluding basic energy).
        # 3. Basic energy cards have no limit.

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
        return sum(
            sum(category[card_id]["quantity"] for card_id in category)
            for category in [self.trainer_cards, self.pokemon_cards, self.energy_cards]
        )

    def __str__(self) -> str:
        total_cards = sum(
            sum(category[card_id]["quantity"] for card_id in category)
            for category in [self.trainer_cards, self.pokemon_cards, self.energy_cards]
        )
        return f"{self.name} ({total_cards} cards)"

    """
    Typical input format:
    <count> <card_name> <set_code> <card_number>
    
    Pokémon: 20
    3 Regidrago V SIT 135
    3 Regidrago VSTAR SIT 136
    3 Teal Mask Ogerpon ex TWM 25
    2 Dragapult ex TWM 130
    1 Hoothoot SCR 114
    1 Noctowl SCR 115
    1 Giratina VSTAR LOR 131
    1 Squawkabilly ex PAL 169
    1 Mew ex MEW 151
    1 Fezandipiti ex SFA 38
    1 Kyurem SFA 47
    1 Cleffa OBF 80
    1 Radiant Charizard CRZ 20
    
    Trainer: 30
    4 Professor's Research SVI 189
    2 Iono PAL 185
    2 Boss's Orders PAL 172
    4 Ultra Ball SVI 196
    4 Nest Ball SVI 181
    4 Energy Switch SVI 173
    3 Earthen Vessel PAR 163
    2 Super Rod PAL 188
    1 Canceling Cologne ASR 136
    1 Switch SVI 194
    1 Prime Catcher TEF 157
    1 Jamming Tower TWM 153
    1 Temple of Sinnoh ASR 155
    
    Energy: 10
    7 Grass Energy SVE 9
    3 Fire Energy SVE 10
    """

    def import_from_string(self, import_data: str) -> None:
        category_lines = [
            line.strip()
            for line in import_data.split("\n")
            if line.strip() and ":" not in line
        ]
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(import_card_from_string, category_lines))
        # Add fetched cards to the deck sequentially
        for card, qty in results:
            if card:
                for _ in range(qty):
                    self.add_card(card)

    def export(self) -> str:
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
