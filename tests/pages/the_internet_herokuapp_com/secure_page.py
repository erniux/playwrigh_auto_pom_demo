class SecurePage:
    def __init__(self, page):
        self.page = page

        self.close_button = page.locator('a:has-text("×")')
        self.logout_button = page.locator('a:has-text("Logout")')
        self.elemental_selenium_button = page.locator('a:has-text("Elemental Selenium")')

    # --- Métodos genéricos ---
    def fill_input(self, locator_name, value):
        getattr(self, locator_name).fill(value)

    def click_button(self, locator_name):
        getattr(self, locator_name).click()

    def get_text(self, locator_name):
        return getattr(self, locator_name).inner_text()

    def is_visible(self, locator_name):
        return getattr(self, locator_name).is_visible()

    def logout(self):
        self.click_button("logout_button")
