from dataclasses import dataclass

import streamlit as st

# from utils import get_unique_breed_images, get_breed_from_url, Round
# import api
# from random import randint
# import numpy as np
# import plotly.express as px
from games.which_image import render_game as render_which_image_game
from games.which_breed import render_game as render_which_breed_game
from games.mosaic import render_game as render_mosaic_game

game_renderers = {
    'Which dog is that breed?': render_which_image_game,
    'Which breed is that dog?': render_which_breed_game,
    'Dog mosaics!': render_mosaic_game
}


@dataclass
class MainState:
    selected_game: str = None


if 'main_state' not in st.session_state:
    st.session_state['main_state'] = MainState()


def on_game_select_button(name):
    st.session_state.main_state.selected_game = name


st.set_page_config(layout='wide')

if st.session_state.main_state.selected_game is None:
    st.title("Dog Quiz - the quiz with dogs!")
    """Select a game mode:"""

    for name in game_renderers:
        st.button(name, on_click=on_game_select_button, args=[name])

else:
    game_renderers[st.session_state.main_state.selected_game]()
