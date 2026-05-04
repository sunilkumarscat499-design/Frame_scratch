from pathlib import Path
import openpyxl

class Xldata:

    def __init__(self):
        # self.page = page
        pass


    def get_xl_data(self):
        # 1. Get the absolute path of the folder containing THIS file (utils)
        utils_path = Path(__file__).resolve().parent

        # 2. Go up one level to the project root, then into 'test_data'
        # Project Structure:
        # root/
        # ├── utils/json_retriever.py
        # └── test_data/person_details.json
        data=[]
        file_path = utils_path.parent / "testdata" / "logindata.xlsx"
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active
        for row in sheet.iter_rows(min_row=2, values_only=True):
            data.append(row)
