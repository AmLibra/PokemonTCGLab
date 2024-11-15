from pokemontcgsdk import Card


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

    def cards(self) -> list[dict[str, (Card, int)]]:
        return [
            {"card": category[card_id]["card"], "quantity": category[card_id]["quantity"]}
            for category in [self.trainer_cards, self.pokemon_cards, self.energy_cards]
            for card_id in category
        ]

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
