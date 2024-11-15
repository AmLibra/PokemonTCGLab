import streamlit as st
from pokemontcgsdk import Card

from utils.storage import remove_card_from_collection


# Function to display multiple cards and allow adding them to collection
def view_collection(cards: list[Card], quantity: list[int], uids: list[str]) -> None:
    num_columns = 5
    columns = st.columns(num_columns)
    for idx, card in enumerate(cards):
        with columns[idx % num_columns]:
            st.image(card.images.large, caption=f"{quantity[idx]} x {card.name}", use_container_width=True)
            button = st.button("Remove", key=card.id + "/" + str(idx), use_container_width=True)
            if button:
                if quantity[idx] > 1:
                    quantity[idx] -= 1
                    st.session_state.cards[uids[idx]]["quantity"] -= 1
                else:
                    st.session_state.cards.pop(uids[idx])
                remove_card_from_collection(cards[idx].id)

                st.toast(f"Successfully removed {quantity[idx]} x '{card.name}'")
                # Refresh the page to reflect the changes
                st.rerun()
            st.title("", anchor=False)
            st.title("", anchor=False)


# Function to view cards
def view_cards() -> None:
    st.header("Your Cards", anchor=False)
    if not st.session_state.cards:
        st.warning("No cards available. Add some cards first!")
        return
    cards: list[Card] = [card["card"] for card in st.session_state.cards.values()]
    uids: list[str] = [uid for uid in st.session_state.cards]
    quantities: list[int] = [card["quantity"] for card in st.session_state.cards.values()]
    view_collection(cards, quantities, uids)
