import csv
from pathlib import Path

class CSVdata:

    def __init__(self):
        # self.page = page
        pass


    def get_csv_data(self):
        util_path = Path(__file__).resolve().parent
        file_path = util_path.parent / "testdata" / "logindata.csv"
        list_data = []
        with open(file_path, newline='', encoding="utf-8") as f:
            csv_data = csv.DictReader(f)
            for row in csv_data:
                list_data.append(tuple(row.values()))
            print(list_data)
            return list_data

obj = CSVdata()
obj.get_csv_data()


