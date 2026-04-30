
class LandingPage:

    def __init__(self,page):
        self.page = page
        self.currency_dropdown = self.page.locator("button[data-toggle='dropdown'] span[class = 'hidden-xs hidden-sm hidden-md']")
        self.select_Eur = self.page.get_by_role("button", name="EUR")
        self.get_currency_symbol = self.page.locator("button[class='btn btn-link dropdown-toggle'] strong")


    def select_currency(self):
        self.page.wait_for_load_state(timeout=2000)
        self.currency_dropdown.click()
        self.select_Eur.click()