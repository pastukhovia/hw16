import json


def read_from_json(filename):
    with open(filename, encoding='utf-8') as file:
        return json.load(file)
