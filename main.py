from dataclasses import dataclass

import streamlit as st

from games.which_image import render_game as render_which_image_game
from games.which_breed import render_game as render_which_breed_game
from games.mosaic import render_game as render_mosaic_game

game_renderers = {
    'Which dog is that breed?': render_which_image_game,
    'Which breed is that dog?': render_which_breed_game,
    'Dog mosaics!': render_mosaic_game
}

import base64


@st.cache(allow_output_mutation=True)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    .stApp  {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)




@dataclass
class MainState:
    selected_game: str = None


if 'main_state' not in st.session_state:
    st.session_state['main_state'] = MainState()


def on_game_select_button(name):
    st.session_state.main_state.selected_game = name


if st.session_state.main_state.selected_game is None:
    st.title("Dog Quiz - the quiz with dogs!")

    """Select a game mode:"""

    for name in game_renderers:
        st.button(name, on_click=on_game_select_button, args=[name])

else:
    game_renderers[st.session_state.main_state.selected_game]()


set_png_as_page_bg('images/background_light.png')
