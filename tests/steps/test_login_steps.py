import pytest
from pytest_bdd import scenarios, given, when, then
from tests.pages.the_internet_herokuapp_com.login_page import LoginPage
from tests.pages.the_internet_herokuapp_com.secure_page import SecurePage

# Vincula el archivo feature
scenarios("../../features/login.feature")


# --- Fixtures ---
@pytest.fixture
def login_page(page):
    return LoginPage(page)

@pytest.fixture
def secure_page(page):
    return SecurePage(page)


# --- Escenario de login ---
@given("the user is on the login page")
def go_to_login(page):
    page.goto("https://the-internet.herokuapp.com/login")

@when("the user enters valid credentials")
def enter_credentials(login_page):
    login_page.do_login("tomsmith", "SuperSecretPassword!")

@then("the user should see the secure page")
def verify_secure_page(secure_page):
    assert "Secure Area" in secure_page.header.inner_text()
    assert "You logged into a secure area!" in secure_page.flash.inner_text()

@then("the user should see a logout button")
def verify_logout(secure_page):
    assert secure_page.logout_button.is_visible()


# --- Escenario de logout ---
@given("the user is logged in")
def user_logged_in(page, login_page):
    page.goto("https://the-internet.herokuapp.com/login")
    login_page.do_login("tomsmith", "SuperSecretPassword!")
    page.wait_for_url("**/secure")

@when("the user clicks logout")
def click_logout(secure_page):
    secure_page.logout()

@then("the user should return to the login page")
def back_to_login(page):
    assert page.url.endswith("/login")
    assert page.locator("h2").inner_text() == "Login Page"
