import pytest
from playwright.sync_api import sync_playwright
import re
import os
from utils.pom_generator import generate_pom_from_html, camel_to_snake

PAGES_DIR = os.path.join("tests", "pages")
os.makedirs(PAGES_DIR, exist_ok=True)


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def browser(playwright_instance):
    browser = playwright_instance.chromium.launch(
        headless=False,
        slow_mo=200
    )
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def context(browser):
    context = browser.new_context(
        viewport={"width": 1280, "height": 800},
        ignore_https_errors=True
    )
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context):
    page = context.new_page()
    original_goto = page.goto

    def auto_pom_goto(url: str, *args, **kwargs):
        response = original_goto(url, *args, **kwargs)

        # Convertir URL en nombre de clase
        page_name = url_to_class_name(page.url)

        # Extraer HTML y generar POM
        html = page.content()
        generate_pom_from_html(html, page_name)

        return response

    page.goto = auto_pom_goto
    yield page
    page.close()


def url_to_class_name(url: str) -> str:
    """
    Convierte la última parte de la URL en CamelCase para clase.
    Ej:
    /login  -> LoginPage
    /secure -> SecurePage
    /users/list -> UsersListPage
    """
    parts = [p for p in re.split(r"[\/\-_]", url.split("?")[0].split("#")[0]) if p]
    if not parts:
        return "HomePage"
    name = "".join(p.capitalize() for p in parts[-2:])  # usa las 2 últimas partes
    return name + "Page"
