from dataclasses import dataclass
from random import sample, shuffle
from typing import List

import streamlit as st

from api import get_all_breeds
from db import Player
from utils import get_unique_breed_images, get_breed_from_url


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
        if __name__ not in player.game_data:
            player.game_data[__name__] = dict()

        if 'highscore' not in player.game_data[__name__]:
            player.game_data[__name__]['highscore'] = 0

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
            if game_state.score > game_state.player.game_data[__name__]['highscore']:
                game_state.player.game_data[__name__]['highscore'] = game_state.score
                st.balloons()

        game_state.player.persist()

    def _on_next_round_button():
        st.session_state.game_state = game_state.next_round()

    def _on_new_game_button():
        st.session_state.game_state = GameState(game_state.player).next_round()

    st.title("Which breed game")
    left_col, center_col, right_col = st.columns([1, 1, 2])

    right_col.image(game_state.url, use_column_width=True)

    left_col.caption("Lives")
    left_col.markdown(":dog2:" * game_state.lives)
    left_col.metric("Round", game_state.round)
    combo_text = f"{game_state.combo}x combo!" if game_state.combo > 1 else ""
    left_col.metric("Score", game_state.score, combo_text)
    left_col.metric("Highscore", game_state.player.game_data[__name__]['highscore'])
    # left_col.markdown("---")

    center_col.markdown("---")
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

    # def _on_choose_button(button_id):
    #     game_state.selected_id = button_id
    #     if game_state.selected_id != game_state.correct_id:
    #         game_state.lives = game_state.lives - 1
    #         game_state.combo = 0
    #     else:
    #         game_state.combo = game_state.combo + 1
    #         game_state.score += game_state.combo
    #
    #     game_state.player.add_confusion(
    #         guessed=game_state.breeds[game_state.selected_id],
    #         correct=game_state.breeds[game_state.correct_id]
    #     )
    #
    #     if st.session_state.game_state.lives == 0:
    #         if game_state.score > game_state.player.game_data[__name__]['highscore']:
    #             game_state.player.game_data[__name__]['highscore'] = game_state.score
    #             st.balloons()
    #
    #     game_state.player.persist()
    #
    # def _on_next_round_button():
    #     st.session_state.game_state = game_state.next_round()
    #
    # def _on_new_game_button():
    #     st.session_state.game_state = GameState(game_state.player).next_round()
    #
    # # render
    #
    # col_left, col_right = st.columns(2)
    # col_left.title(f"Which image game")
    #
    # if game_state.lives > 0:
    #     correct_breed = game_state.breeds[game_state.correct_id]
    #     col_left.markdown(f"Which one is the *{correct_breed}*?")
    # else:
    #     col_left.markdown("Game Over :face_with_rolling_eyes:")
    #     col_left.button("New game", on_click=_on_new_game_button)
    #
    # col_right.markdown("Lives: "+":dog2: " * game_state.lives)
    # col_right.markdown(f"Round: {game_state.round}")
    # combo_text = f"({game_state.combo}x combo!)" if game_state.combo > 1 else ""
    # col_right.markdown(f"Score: {game_state.score} "+combo_text)
    # col_right.markdown(f"Highscore: {game_state.player.game_data[__name__]['highscore']}")
    #
    # st.markdown("---")
    #
    # if game_state.selected_id is None:
    #     letters = "ABCD"
    #     cols = st.columns(4)
    #     for i, (col, letter, url) in enumerate(zip(cols, letters, game_state.urls)):
    #         col.button(f"choose {letter}", on_click=_on_choose_button, args=[i])
    #         col.image(url, use_column_width=True)
    # else:
    #     if game_state.lives > 0:
    #         st.button("Next round", on_click=_on_next_round_button)
    #     cols = st.columns([2 if i == game_state.correct_id else 1 for i in range(4)])
    #     for i, (col, breed, url) in enumerate(zip(cols, game_state.breeds, game_state.urls)):
    #         if i == game_state.correct_id:
    #             col.markdown(f"**{breed}**")
    #         else:
    #             col.text(breed)
    #
    #         col.image(url, use_column_width=True)
