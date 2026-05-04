from page.actions_page import Actionspage
from config import Config
import pytest
import json
from utils.get_json_data import Jsondata
from utils.get_csv_data import CSVdata

obj = Jsondata()
json_data =  obj.get_json_data()

obj2 = CSVdata()
data = obj2.get_csv_data()

@pytest.mark.parametrize("person_info",json_data['person'])
def test_name_email_phone(page,person_info):
    page.goto(Config.Base_url1)
    obj_actions_page = Actionspage(page)
    obj_actions_page.enter_person_details(person_info['name'],person_info['email'],person_info['phone'])


@pytest.mark.parametrize("name,email,phone",data )
def test_name_email_phone_csv(page,name,email,phone):

    page.goto(Config.Base_url1)
    obj_actions_page = Actionspage(page)
    obj_actions_page.enter_person_details(name,email,phone)