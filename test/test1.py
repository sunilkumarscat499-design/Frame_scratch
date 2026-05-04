import json
import csv
from pathlib import Path
import os
import openpyxl

current_file_path = Path(__file__).resolve().parent
data_file = current_file_path.parent / "testdata" / "logindata.xlsx"


workbook = openpyxl.load_workbook(data_file)
sheet = workbook.active
list1 = []
for row in sheet.iter_rows(min_row=2,values_only=True):
    print(row)
    list1.append(tuple(row))
    print(list1)



