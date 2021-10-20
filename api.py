import requests


def get_random_images(num):
    response = requests.get(f"https://dog.ceo/api/breeds/image/random/{num}")
    json = response.json()
    assert json['status'] == 'success'
    return json['message']


def get_all_breeds():
    response = requests.get("https://dog.ceo/api/breeds/list/all")
    json = response.json()
    assert json['status'] == 'success'
    breeds = []
    for name, sublist in json['message'].items():
        if len(sublist) > 0:
            breeds.extend(subname + " " + name for subname in sublist)
        else:
            breeds.append(name)
    return breeds
