import streamlit as st
from dataclasses import dataclass
from typing import List


@dataclass
class GameState:
    rounds_played: int
    urls: List[str]
    correct_id: int
    selected_id: int = None


def render_game():
    st.title("Which breed game")
    st.text("~ work in progress ~")