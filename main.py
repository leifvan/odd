import streamlit as st
from utils import get_unique_breed_images, get_breed_from_url, Round
import api
from random import randint
import numpy as np
import plotly.express as px

st.set_page_config(layout='wide')


# create cached api call wrappers

@st.cache
def get_all_breeds():
    return api.get_all_breeds()


# initialize state

if 'rounds' not in st.session_state:
    st.session_state['rounds'] = []

if 'confusion' not in st.session_state:
    num_breeds = len(get_all_breeds())
    st.session_state['confusion'] = np.zeros((num_breeds, num_breeds))

# get state data

last_round: Round = st.session_state.rounds[-1] if len(st.session_state.rounds) > 0 else None
round_num = len(st.session_state.rounds) + 1

# fetch data

if last_round is None or last_round.shown:
    urls = get_unique_breed_images(4)
    last_round = Round(urls=urls, solution_id=randint(0, 3))
    st.session_state.rounds.append(last_round)

urls = last_round.urls
solution_id = last_round.solution_id
breeds = [get_breed_from_url(url) for url in urls]
correct_breed = breeds[solution_id]


def choice_button_clicked(choice_id):
    last_round.choice_id = choice_id
    choice_breed_id = get_all_breeds().index(breeds[choice_id])
    solution_breed_id = get_all_breeds().index(breeds[solution_id])
    st.session_state.confusion[choice_breed_id, solution_breed_id] += 1
    st.session_state.confusion[solution_breed_id, choice_breed_id] += 1


def next_button_clicked():
    last_round.shown = True


# --------
#   PAGE
# --------

st.title(f"Dogquiz - Round {round_num}")

fig = px.imshow(
    st.session_state.confusion,
    labels=dict(x="good boys", y="good girls", color="#confused"),
    x=get_all_breeds(),
    y=get_all_breeds(),
    height=1000
)
fig.update_xaxes(side="top")
plotbox = st.expander("confusion matrix")
plotbox.plotly_chart(fig, use_container_width=True)

if last_round.choice_id is not None:
    st.button("Next Round", on_click=next_button_clicked)

if last_round.choice_id is None:
    st.markdown(f"Which one is the **{correct_breed}**?")

if last_round.choice_id is None:
    cols = st.columns(4)
else:
    cols = st.columns([2 if i == solution_id else 1 for i in range(4)])

captions = ('A', 'B', 'C', 'D')

for i, (col, url, caption, breed) in enumerate(zip(cols, urls, captions, breeds)):

    if last_round.choice_id is None:
        col.button("Choose " + caption, on_click=choice_button_clicked, args=[i])
    elif solution_id == i == last_round.choice_id:
        st.balloons()
        col.markdown(f"**correct: {breed}**")
    elif solution_id == i:
        col.markdown(f"**{breed}**")
    elif last_round.choice_id == i:
        col.markdown(f"wrong: {breed}")
    else:
        col.markdown(breed)

    col.image(url, use_column_width=True)
