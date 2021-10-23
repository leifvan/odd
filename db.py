from typing import List, Any, Dict

import pymongo
from dataclasses import dataclass, asdict

client = pymongo.MongoClient("localhost:27017")
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

    def add_confusion(self, guessed, correct):
        self.confusions.append(Confusion(guessed, correct))