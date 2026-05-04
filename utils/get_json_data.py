import json
from pathlib import Path

class Jsondata:

    def __init__(self):

        pass

    def get_json_data(self):
        print("")
        # 1. Get the absolute path of the folder containing THIS file (utils)
        utils_path = Path(__file__).resolve().parent

        # 2. Go up one level to the project root, then into 'test_data'
        # Project Structure:
        # root/
        # ├── utils/json_retriever.py
        # └── test_data/person_details.json
        file_path = utils_path.parent / "testdata" / "person_details.json"


        with open(file_path, "r") as f:
            data = json.load(f)
            return data

# obj = Jsondata()
# data = obj.get_json_data()
# print(data)
# for d in data['person']:
#     print(d['name'])

