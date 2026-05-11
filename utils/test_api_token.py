from playwright.sync_api import sync_playwright
import pytest
import config
import json
import os
import pathlib

class APIUtils:
    def __int__(self,get_token):
        pass

    def create_order(self,get_token:tuple):
        token, request_context = get_token
        root_path = pathlib.Path(__file__).resolve().parent.parent
        file_path = root_path / "testdata" / "create_order.json"
        with open(file_path) as f:
            json_req = json.load(f)
        response = request_context.post(url="https://rahulshettyacademy.com/api/ecom/order/create-order",
                                        headers={"Content-Type": "application/json", "Authorization": token},
                                        data=json_req)
        return response


