import numpy as np
import streamlit as st
from dataclasses import dataclass
from typing import List
from PIL import Image
import requests
from io import BytesIO
from api import get_random_images, get_all_breeds
from db import Player
from utils import get_breed_from_url
import matplotlib.pyplot as plt
from random import sample, shuffle


MOSAIC_LEVEL_ZOOMS = [16, 32, 48, 64, 96, 128]
MOSAIC_LEVEL_SCORES = [100, 50, 20, 10, 5, 1]
MOSAIC_LEVEL_NEW_ZOOMS = [2, 1, 0, 0, 0, 0]


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
        breeds = [correct_breed] + sample(get_all_breeds(), k=4)
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
        player = Player.get_by_name("Leif")
        if __name__ not in player.game_data:
            player.game_data[__name__] = dict()

        if 'highscore' not in player.game_data[__name__]:
            player.game_data[__name__]['highscore'] = 0

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
            if game_state.score > game_state.player.game_data[__name__]['highscore']:
                game_state.player.game_data[__name__]['highscore'] = game_state.score
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
    right_col.pyplot(fig=plt.gcf())

    if game_state.zooms == 0:
        if game_state.chosen_breed is None:
            left_col.markdown("No zooms left!")
        else:
            left_col.markdown("Game Over :face_with_rolling_eyes:")
            left_col.button("New game", on_click=_on_new_game_button)
    else:
        left_col.markdown("Zooms:")
        left_col.markdown(":mag:"*game_state.zooms)
    left_col.markdown(f"Score: {game_state.score}")
    left_col.markdown(f"Highscore: {game_state.player.game_data[__name__]['highscore']}")

    if game_state.chosen_breed is None:
        if game_state.zooms > 0 and game_state.mosaic_level < len(MOSAIC_LEVEL_ZOOMS) - 1:
            left_col.button("Enhance!", on_click=_on_enhance_button)
        else:
            left_col.markdown("Fully enhanced!")

        left_col.markdown("---")

        for breed in game_state.breeds:
            left_col.button(breed, on_click=_on_choose_button, args=[breed])
    else:
        left_col.markdown("---")

        if game_state.correct_breed == game_state.chosen_breed:
            left_col.markdown(f"Yes, it's a *{game_state.correct_breed}*")
        else:
            left_col.markdown(f"Nope, it's a *{game_state.correct_breed}*")

        if game_state.zooms > 0:
            left_col.button("Next round", on_click=_on_next_round_button)
