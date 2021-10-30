import numpy as np
import streamlit as st
from dataclasses import dataclass
from typing import List
from PIL import Image
import requests
from io import BytesIO
from api import get_random_images, get_all_breeds
from db import Player
from utils import get_breed_from_url, get_game_name
import matplotlib.pyplot as plt
from random import sample, shuffle

MOSAIC_LEVEL_ZOOMS = [16, 32, 48, 64, 96, 128]
MOSAIC_LEVEL_SCORES = [100, 50, 20, 10, 5, 1]
MOSAIC_LEVEL_NEW_ZOOMS = [2, 1, 0, 0, 0, 0]

GAME_NAME = get_game_name(__name__)


@dataclass
class GameState:
    player: Player
    round: int = 0
    url: str = None
    breeds: List[str] = None
    correct_breed: str = None
    chosen_breed: str = None
    mosaic_level: int = None
    score: int = 0
    zooms: int = 10

    def next_round(self):
        url = get_random_images(1)[0]
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
            mosaic_level=0,
            score=self.score,
            zooms=self.zooms
        )


def render_game():
    # prepare state

    if 'game_state' not in st.session_state or not isinstance(st.session_state.game_state, GameState):
        player = Player.get_by_name(st.session_state.player_name)
        if GAME_NAME not in player.game_data:
            player.game_data[GAME_NAME] = dict()

        if 'highscore' not in player.game_data[GAME_NAME]:
            player.game_data[GAME_NAME]['highscore'] = 0

        st.session_state['game_state'] = GameState(player).next_round()

    game_state = st.session_state.game_state

    def _on_enhance_button():
        game_state.mosaic_level += 1
        game_state.zooms -= 1

    def _on_choose_button(choice):
        game_state.chosen_breed = choice
        if game_state.chosen_breed == game_state.correct_breed:
            game_state.score += MOSAIC_LEVEL_SCORES[game_state.mosaic_level]
            game_state.zooms += MOSAIC_LEVEL_NEW_ZOOMS[game_state.mosaic_level]
        elif game_state.zooms == 0:
            game_state.zooms = -1
            if game_state.score > game_state.player.game_data[GAME_NAME]['highscore']:
                game_state.player.game_data[GAME_NAME]['highscore'] = game_state.score
                st.balloons()

        game_state.player.add_confusion(
            guessed=game_state.chosen_breed,
            correct=game_state.correct_breed
        )
        game_state.player.persist()

    def _on_next_round_button():
        st.session_state.game_state = game_state.next_round()

    def _on_new_game_button():
        st.session_state.game_state = GameState(game_state.player).next_round()

    st.title("Dog Mosaics!")
    st.markdown("  \n")
    st.markdown("  \n")
    st.markdown("  \n")

    response = requests.get(game_state.url)
    img = np.array(Image.open(BytesIO(response.content)))
    length = max(*img.shape)

    if game_state.chosen_breed is None:
        step = length // MOSAIC_LEVEL_ZOOMS[game_state.mosaic_level]
    else:
        step = 1

    plt.imshow(img[::step, ::step])
    plt.axis('off')
    left_col, right_col = st.columns([1, 2])

    if game_state.chosen_breed is None:
        if game_state.zooms > 0 and game_state.mosaic_level < len(MOSAIC_LEVEL_ZOOMS) - 1:
            right_col.button("Enhance!", on_click=_on_enhance_button)
        elif game_state.zooms == 0:
            right_col.markdown("No zooms left!")

    right_col.pyplot(fig=plt.gcf())

    if game_state.zooms == -1:
        if game_state.chosen_breed is not None:
            left_col.markdown("Game Over :face_with_rolling_eyes:")
            left_col.button("New game", on_click=_on_new_game_button)
    else:
        left_col.caption("Zooms")
        left_col.markdown(":mag:" * game_state.zooms)
    left_col.metric("Score", game_state.score)
    left_col.metric("Highscore", game_state.player.game_data[GAME_NAME]['highscore'])

    if game_state.chosen_breed is None:

        for breed in game_state.breeds:
            left_col.button(breed, on_click=_on_choose_button, args=[breed])

        left_col.markdown("---")

    else:
        left_col.markdown("---")

        if game_state.correct_breed == game_state.chosen_breed:
            left_col.markdown(f"Yes, it's a *{game_state.correct_breed}*")
        else:
            left_col.markdown(f"Nope, it's a *{game_state.correct_breed}*")

        if game_state.zooms > 0:
            left_col.button("Next round", on_click=_on_next_round_button)
