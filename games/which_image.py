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

    # prepare state

    if 'game_state' not in st.session_state or not isinstance(st.session_state.game_state, GameState):
        # get player
        player = Player.get_by_name(st.session_state.player_name)
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

    # _, col, _ = st.columns(3)
    # col.title(f"Which image game")

    cols = st.columns(7)

    if game_state.lives > 0:
        if game_state.selected_id is None:
            correct_breed = game_state.breeds[game_state.correct_id]
            cols[1].markdown(f"##### Which one is the")
            cols[1].markdown(f"### {correct_breed}?")
    else:
        cols[1].markdown("Game Over :face_with_rolling_eyes:")
        cols[1].button("New game", on_click=_on_new_game_button)

    cols[2].caption("Lives")
    cols[2].markdown(":dog2:" * game_state.lives)
    cols[3].metric("Round", game_state.round)
    combo_text = f"{game_state.combo}x combo!" if game_state.combo > 1 else ""
    cols[4].metric("Score", game_state.score, combo_text)
    cols[5].metric("Highscore", game_state.player.game_data[__name__]['highscore'])

    if game_state.selected_id is None:
        letters = "ABCD"
        cols = st.columns(4)
        for i, (col, letter, url) in enumerate(zip(cols, letters, game_state.urls)):
            col.button(f"choose {letter}", on_click=_on_choose_button, args=[i])
            col.image(url, use_column_width=True)
    else:
        #cols = st.columns([2 if i == game_state.correct_id else 1 for i in range(4)])
        cols = st.columns(4)
        for i, (col, breed, url) in enumerate(zip(cols, game_state.breeds, game_state.urls)):
            if i == game_state.correct_id:
                col.markdown(f"#### {breed}")
                if game_state.lives > 0:
                    col.button("Next round", on_click=_on_next_round_button)
            else:
                col.text(breed)

            col.image(url, use_column_width=True)

