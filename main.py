from dataclasses import dataclass

import streamlit as st

from db import Player
from games.which_image import render_game as render_which_image_game
from games.which_breed import render_game as render_which_breed_game
from games.mosaic import render_game as render_mosaic_game
from background import background_base64
from highscores import render_highscores
from api import get_random_images

game_renderers = {
    'Which dog is that breed?': render_which_image_game,
    'Which breed is that dog?': render_which_breed_game,
    'Dog mosaics!': render_mosaic_game
}


# import base64


# @st.cache(allow_output_mutation=True)
# def get_base64_of_bin_file(bin_file):
#     with open(bin_file, 'rb') as f:
#         data = f.read()
#     return base64.b64encode(data).decode()


def set_png_as_page_bg(png_file):
    page_bg_img = '''
    <style>
    .stApp  {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % background_base64
    st.markdown(page_bg_img, unsafe_allow_html=True)


@dataclass
class MainState:
    selected_game: str = None


if 'main_state' not in st.session_state:
    st.session_state['main_state'] = MainState()

if 'player_name' not in st.session_state:
    st.session_state['player_name'] = ""


def on_game_select_button(name):
    player_name = st.session_state.player_name
    if len(player_name) > 0:
        if not Player.exists(player_name):
            Player.create(player_name)

        st.session_state.main_state.selected_game = name


def on_back_to_main_button():
    st.session_state.main_state.selected_game = None


if st.session_state.main_state.selected_game is None:
    st.set_page_config(layout='centered', page_icon=":dog2:", page_title="Dog Quiz - The quiz with dogs!")
    # st.title("Dog Quiz - the quiz with dogs!")
    st.image("images/header.png", use_column_width=True)

    _, col, _ = st.columns(3)

    player_name = col.text_input("What's your name?", st.session_state.player_name)
    st.session_state.player_name = player_name

    if len(player_name) > 0:
        if Player.exists(player_name):
            col.markdown(f"Welcome back, *{player_name}*!")
        else:
            col.markdown(f"Hi *{player_name}*, you are new!")

        col.markdown("##### Select a game mode:")
        for name in game_renderers:
            col.button(name, on_click=on_game_select_button, args=[name])

        st.markdown("  \n")
        st.markdown("  \n")
        st.markdown("  \n")
        render_highscores()
    else:
        col.markdown(
            "Welcome to **Dog Quiz - the quiz with dogs**! This is a collection of dog-themed "
            "quizzes, because dogs are the best! Enter your name above and enjoy!")

        col.caption("a random doggo")
        random_url = get_random_images(1)[0]
        col.image(random_url, use_column_width=True)

    col.markdown("<small>powered by https://dog.ceo/dog-api</small>", unsafe_allow_html=True)

else:
    if st.session_state.main_state.selected_game == 'Which dog is that breed?':
        st.set_page_config(layout='wide', page_icon=":dog2:", page_title="Dog Quiz - The quiz with dogs!")
    else:
        st.set_page_config(layout='centered', page_icon=":dog2:", page_title="Dog Quiz - The quiz with dogs!")

    st.button("Back to main menu", on_click=on_back_to_main_button)
    game_renderers[st.session_state.main_state.selected_game]()

set_png_as_page_bg('images/background_light.png')
