import streamlit as st
from dataclasses import dataclass
from typing import List
from utils import get_unique_breed_images, get_breed_from_url
from random import randint


@dataclass
class GameState:
    round: int = 0
    urls: List[str] = None
    breeds: List[str] = None
    correct_id: int = None
    selected_id: int = None

    def next_round(self):
        urls = get_unique_breed_images(4)
        breeds = [get_breed_from_url(url) for url in urls]

        return GameState(
            round=self.round + 1,
            urls=urls,
            breeds=breeds,
            correct_id=randint(0, 3),
            selected_id=None
        )





def render_game():

    # prepare state

    if 'game_state' not in st.session_state or not isinstance(st.session_state.game_state, GameState):
        st.session_state['game_state'] = GameState().next_round()

    game_state = st.session_state.game_state

    def _on_choose_button(button_id):
        game_state.selected_id = button_id

    def _on_next_round_button():
        st.session_state.game_state = game_state.next_round()

    # render

    st.title(f"Which image game - Round {game_state.round}")

    correct_breed = game_state.breeds[game_state.correct_id]
    st.markdown(f"Which one is the {correct_breed}?")

    if game_state.selected_id is None:
        letters = "ABCD"
        cols = st.columns(4)
        for i, (col, letter, url) in enumerate(zip(cols, letters, game_state.urls)):
            col.button(f"choose {letter}", on_click=_on_choose_button, args=[i])
            col.image(url, use_column_width=True)
    else:
        st.button("Next round", on_click=_on_next_round_button)
        cols = st.columns([2 if i == game_state.correct_id else 1 for i in range(4)])
        for i, (col, breed, url) in enumerate(zip(cols, game_state.breeds, game_state.urls)):
            if i == game_state.correct_id:
                col.markdown(f"**{breed}**")
            else:
                col.text(breed)

            col.image(url, use_column_width=True)
