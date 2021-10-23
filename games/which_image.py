import streamlit as st
from dataclasses import dataclass
from typing import List
from utils import get_unique_breed_images, get_breed_from_url
from random import randint
from db import Player


@dataclass
class GameState:
    player: Player
    round: int = 0
    urls: List[str] = None
    breeds: List[str] = None
    correct_id: int = None
    selected_id: int = None
    lives: int = 3
    score: int = 0
    combo: int = 0

    def next_round(self):
        urls = get_unique_breed_images(4)
        breeds = [get_breed_from_url(url) for url in urls]

        return GameState(
            player=self.player,
            round=self.round + 1,
            urls=urls,
            breeds=breeds,
            correct_id=randint(0, 3),
            selected_id=None,
            lives=self.lives,
            score=self.score,
            combo=self.combo
        )


def render_game():
    st.set_page_config(layout='wide')

    # prepare state

    if 'game_state' not in st.session_state or not isinstance(st.session_state.game_state, GameState):
        # get player
        player = Player.get_by_name("Leif")
        if __name__ not in player.game_data:
            player.game_data[__name__] = dict()

        if 'highscore' not in player.game_data[__name__]:
            player.game_data[__name__]['highscore'] = 0

        st.session_state['game_state'] = GameState(player).next_round()

    game_state = st.session_state.game_state

    def _on_choose_button(button_id):
        game_state.selected_id = button_id
        if game_state.selected_id != game_state.correct_id:
            game_state.lives = game_state.lives - 1
            game_state.combo = 0
        else:
            game_state.combo = game_state.combo + 1
            game_state.score += game_state.combo

        game_state.player.add_confusion(
            guessed=game_state.breeds[game_state.selected_id],
            correct=game_state.breeds[game_state.correct_id]
        )

        if st.session_state.game_state.lives == 0:
            if game_state.score > game_state.player.game_data[__name__]['highscore']:
                game_state.player.game_data[__name__]['highscore'] = game_state.score
                st.balloons()

        game_state.player.persist()

    def _on_next_round_button():
        st.session_state.game_state = game_state.next_round()

    def _on_new_game_button():
        st.session_state.game_state = GameState(game_state.player).next_round()

    # render

    col_left, col_right = st.columns(2)
    col_left.title(f"Which image game")

    if game_state.lives > 0:
        correct_breed = game_state.breeds[game_state.correct_id]
        col_left.markdown(f"Which one is the *{correct_breed}*?")
    else:
        col_left.markdown("Game Over :face_with_rolling_eyes:")
        col_left.button("New game", on_click=_on_new_game_button)

    col_right.markdown("Lives: "+":dog2: " * game_state.lives)
    col_right.markdown(f"Round: {game_state.round}")
    combo_text = f"({game_state.combo}x combo!)" if game_state.combo > 1 else ""
    col_right.markdown(f"Score: {game_state.score} "+combo_text)
    col_right.markdown(f"Highscore: {game_state.player.game_data[__name__]['highscore']}")

    st.markdown("---")

    if game_state.selected_id is None:
        letters = "ABCD"
        cols = st.columns(4)
        for i, (col, letter, url) in enumerate(zip(cols, letters, game_state.urls)):
            col.button(f"choose {letter}", on_click=_on_choose_button, args=[i])
            col.image(url, use_column_width=True)
    else:
        if game_state.lives > 0:
            st.button("Next round", on_click=_on_next_round_button)
        cols = st.columns([2 if i == game_state.correct_id else 1 for i in range(4)])
        for i, (col, breed, url) in enumerate(zip(cols, game_state.breeds, game_state.urls)):
            if i == game_state.correct_id:
                col.markdown(f"**{breed}**")
            else:
                col.text(breed)

            col.image(url, use_column_width=True)
