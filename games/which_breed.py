from dataclasses import dataclass
from random import sample, shuffle
from typing import List

import streamlit as st

from api import get_all_breeds
from db import Player
from utils import get_unique_breed_images, get_breed_from_url, get_game_name

GAME_NAME = get_game_name(__name__)

@dataclass
class GameState:
    player: Player
    round: int = 0
    url: str = None
    breeds: List[str] = None
    correct_breed: str = None
    selected_breed: str = None
    lives: int = 3
    score: int = 0
    combo: int = 0

    def next_round(self):
        url = get_unique_breed_images(1)[0]
        correct_breed = get_breed_from_url(url)
        all_breeds = get_all_breeds()
        all_breeds.remove(correct_breed)
        breeds = [correct_breed] + sample(all_breeds, k=4)
        shuffle(breeds)

        return GameState(
            player=self.player,
            round=self.round + 1,
            url=url,
            breeds=breeds,
            correct_breed=correct_breed,
            selected_breed=None,
            lives=self.lives,
            score=self.score,
            combo=self.combo
        )


def render_game():
    # prepare state

    if 'game_state' not in st.session_state or not isinstance(st.session_state.game_state, GameState):
        # get player
        player = Player.get_by_name(st.session_state.player_name)
        if GAME_NAME not in player.game_data:
            player.game_data[GAME_NAME] = dict()

        if 'highscore' not in player.game_data[GAME_NAME]:
            player.game_data[GAME_NAME]['highscore'] = 0

        st.session_state['game_state'] = GameState(player).next_round()

    game_state = st.session_state.game_state

    def _on_choice_button(chosen_breed):
        game_state.selected_breed = chosen_breed
        if game_state.selected_breed != game_state.correct_breed:
            game_state.lives = game_state.lives - 1
            game_state.combo = 0
        else:
            game_state.combo = game_state.combo + 1
            game_state.score += game_state.combo

        game_state.player.add_confusion(
            guessed=game_state.selected_breed,
            correct=game_state.correct_breed
        )

        if st.session_state.game_state.lives == 0:
            if game_state.score > game_state.player.game_data[GAME_NAME]['highscore']:
                game_state.player.game_data[GAME_NAME]['highscore'] = game_state.score
                st.balloons()

        game_state.player.persist()

    def _on_next_round_button():
        st.session_state.game_state = game_state.next_round()

    def _on_new_game_button():
        st.session_state.game_state = GameState(game_state.player).next_round()

    st.title("Which breed game")
    st.markdown("  \n")
    st.markdown("  \n")
    st.markdown("  \n")
    left_col, center_col, right_col = st.columns([1, 1, 2])

    right_col.image(game_state.url, use_column_width=True)

    left_col.caption("Lives")
    left_col.markdown(":dog2:" * game_state.lives)
    left_col.metric("Round", game_state.round)
    combo_text = f"{game_state.combo}x combo!" if game_state.combo > 1 else ""
    left_col.metric("Score", game_state.score, combo_text)
    left_col.metric("Highscore", game_state.player.game_data[GAME_NAME]['highscore'])

    if game_state.selected_breed is None:
        for breed in game_state.breeds:
            center_col.button(breed, on_click=_on_choice_button, args=[breed])
    else:
        if game_state.selected_breed == game_state.correct_breed:
            center_col.markdown(f"Yes, it's a *{game_state.correct_breed}*")
        else:
            center_col.markdown(f"Nope, it's a *{game_state.correct_breed}*")

        if game_state.lives > 0:
            center_col.button("Next round", on_click=_on_next_round_button)
        else:
            center_col.markdown("Game Over :face_with_rolling_eyes:")
            center_col.button("New game", on_click=_on_new_game_button)
