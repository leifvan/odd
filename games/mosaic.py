import numpy as np
import streamlit as st
from dataclasses import dataclass
from typing import List
from PIL import Image
import requests
from io import BytesIO
from api import get_random_images, get_all_breeds
from utils import get_breed_from_url
import matplotlib.pyplot as plt
from random import sample, shuffle


MOSAIC_LEVEL_ZOOMS = [16, 32, 64, 128]


@dataclass
class GameState:
    round: int = 0
    url: str = None
    breeds: List[str] = None
    correct_breed: str = None
    chosen_breed: str = None
    mosaic_level: int = None

    def next_round(self):
        url = get_random_images(1)[0]
        correct_breed = get_breed_from_url(url)
        breeds = [correct_breed] + sample(get_all_breeds(), k=4)
        shuffle(breeds)

        return GameState(
            round=self.round + 1,
            url=url,
            breeds=breeds,
            correct_breed=correct_breed,
            mosaic_level=0
        )


def render_game():
    # prepare state

    if 'game_state' not in st.session_state or not isinstance(st.session_state.game_state, GameState):
        st.session_state['game_state'] = GameState().next_round()

    game_state = st.session_state.game_state

    def _on_enhance_button():
        game_state.mosaic_level += 1

    def _on_choose_button(choice):
        game_state.chosen_breed = choice

    def _on_next_round_button():
        st.session_state.game_state = game_state.next_round()

    st.title("MOSAICS!")

    response = requests.get(game_state.url)
    img = np.array(Image.open(BytesIO(response.content)))
    length = max(*img.shape)
    step = length // MOSAIC_LEVEL_ZOOMS[game_state.mosaic_level]

    plt.imshow(img[::step, ::step])
    plt.axis('off')
    cols = st.columns([1, 1, 1])
    cols[1].pyplot(fig=plt.gcf())

    if game_state.mosaic_level < len(MOSAIC_LEVEL_ZOOMS) - 1:
        cols[0].button("Enhance!", on_click=_on_enhance_button)

    if game_state.chosen_breed is None:
        for breed in game_state.breeds:
            cols[2].button(breed, on_click=_on_choose_button, args=[breed])
    else:
        cols[2].text(f"It's a {game_state.correct_breed}")
        cols[2].button("Next round", on_click=_on_next_round_button)
