import time

import pytest
from page.landing_page import LandingPage
from playwright.sync_api import expect
import random

from page.landing_page import LandingPage


@pytest.mark.skip
def test_demo(page):
    print(" =>> this is Done")
    title = page.title()
    assert "Your Store" in title

def test_dropdown_currency(page):
    # page.locator(".btn btn-link dropdown-toggle").click()
    # page.locator("button[data-toggle='dropdown'] span[class = 'hidden-xs hidden-sm hidden-md']").click()
    # page.get_by_role("button", name="EUR").click()
    obj = LandingPage(page)
    obj.select_currency()
    expect(obj.get_currency_symbol).to_have_text("€")
