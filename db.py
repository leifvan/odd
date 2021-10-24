from typing import List, Any, Dict
import streamlit as st
import pymongo
from dataclasses import dataclass, asdict

# client = pymongo.MongoClient("localhost:27017")
client = pymongo.MongoClient(st.secrets["DB_URL"])
db = client.get_database("odd")

players = db.get_collection("players")


def _remove_id(obj):
    return {k: v for k, v in obj.items() if k != '_id'}


@dataclass
class Confusion:
    guessed: str
    correct: str


@dataclass
class Player:
    name: str
    confusions: List[Confusion]
    game_data: Dict[str, Dict[str, Any]]

    def persist(self):
        players.replace_one({'name': self.name}, asdict(self))

    @staticmethod
    def get_by_name(name):
        p = players.find_one({'name': name})
        return Player(**_remove_id(p))

    @staticmethod
    def exists(name):
        p = players.find_one({'name': name})
        return p is not None

    @staticmethod
    def create(name):
        if not Player.exists(name):
            p = Player(name, [], {})
            players.insert_one(asdict(p))

    def add_confusion(self, guessed, correct):
        self.confusions.append(Confusion(guessed, correct))



def get_highscore_list(game_name):
    query = [
        {'$group': {'_id': '$name', 'score': {'$first': f'$game_data.{game_name}.highscore'}}},
        {'$sort': {'score': -1}},
        {'$limit': 3}
    ]
    highscore_list = players.aggregate(query)
    return [{"name": r['_id'], "score": r['score']} for r in highscore_list]

