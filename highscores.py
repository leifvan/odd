import streamlit as st
from db import get_highscore_list

def render_highscores():
    exp = st.expander("Highscores")

    game_names_db = ["games_which_image", "games_which_breed", "games_mosaic"]
    game_names_ui = ["Which image?", "Which breed?", "Mosaics!"]
    cols = exp.columns(len(game_names_db))

    for name_ui, name_db, col in zip(game_names_ui, game_names_db, cols):
        col.markdown(f"##### {name_ui}")
        highscores = get_highscore_list(name_db)
        col.table(highscores)
