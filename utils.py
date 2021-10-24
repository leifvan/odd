from dataclasses import dataclass
from typing import List

import api

REQUEST_LIMIT = 3


@dataclass
class Round:
    urls: List[str]
    solution_id: int
    choice_id: int = None
    shown: bool = False


def get_breed_from_url(url: str):
    breed = url.rsplit("/", maxsplit=2)[1]
    if "-" in breed:
        main, sub = breed.split("-")
        return sub + " " + main
    return breed


def get_unique_breed_images(num):
    uniques = dict()
    num_requests_sent = 0

    while num_requests_sent < REQUEST_LIMIT and len(uniques) < num:
        urls = api.get_random_images(num - len(uniques))
        uniques.update({get_breed_from_url(url): url for url in urls})

    assert len(uniques) == num
    return list(uniques.values())


def get_game_name(name):
    return name.replace(".", "_")
