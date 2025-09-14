from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import os
import re

OUTPUT_DIR = "tests/pages"


ALIASES = {
    "×": "close_button",
    "X": "close_button",
    "✕": "close_button",
    "→": "next_button",
    "←": "back_button",
}


def camel_to_snake(name: str) -> str:
    """Convierte CamelCase en snake_case."""
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def parse_existing_locators(file_path: str):
    """Lee el archivo POM existente y devuelve un set de locators ya definidos."""
    locators = set()
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if "self." in line and "page.locator" in line:
                    name = line.strip().split("=")[0].replace("self.", "").strip()
                    locators.add(name)
    return locators


def safe_name_from_text(text: str, suffix: str = "") -> str:
    """Convierte texto visible en un nombre seguro en snake_case."""
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", text).strip()
    if not cleaned:
        return "unnamed" + suffix
    return cleaned.replace(" ", "_").lower() + suffix


def build_file_path(page_name: str, url: str) -> str:
    """
    Construye la ruta del archivo según la URL.
    - Convierte la clase (LoginPage) en snake_case (login_page.py).
    - Usa la penúltima parte de la URL como subcarpeta (/secure/logout -> secure/).
    """
    parts = [p for p in url.split("/") if p]
    folder = parts[-2] if len(parts) > 1 else "common"
    folder = re.sub(r"[^a-zA-Z0-9_]", "_", folder.lower())
    
    file_name = f"{camel_to_snake(page_name)}.py"
    folder_path = os.path.join(OUTPUT_DIR, folder)
    os.makedirs(folder_path, exist_ok=True)
    return os.path.join(folder_path, file_name)


def generate_pom_from_html(html: str, page_name: str, url: str = ""):
    """Genera o actualiza un POM con métodos genéricos y específicos."""
    soup = BeautifulSoup(html, "lxml")
    elements = []

    # Inputs
    for inp in soup.find_all("input"):
        if inp.get("id"):
            elements.append((inp.get("id").lower(), f"#{inp.get('id')}"))
        elif inp.get("name"):
            elements.append((inp.get("name").lower(), f"[name='{inp.get('name')}']"))

    # Botones
    for btn in soup.find_all("button"):
        text = btn.text.strip()
        if btn.get("id"):
            elements.append((btn.get("id").lower() + "_button", f"#{btn.get('id')}"))
        elif text:
            safe_name = ALIASES.get(text, safe_name_from_text(text, "_button"))
            escaped_text = text.replace('"', '\\"')
            selector = f'button:has-text("{escaped_text}")'
            elements.append((safe_name, selector))

    # Links
    for a in soup.find_all("a"):
        text = a.text.strip()
        if a.get("id"):
            elements.append((a.get("id").lower() + "_button", f"#{a.get('id')}"))
        elif text:
            safe_name = ALIASES.get(text, safe_name_from_text(text, "_button"))
            escaped_text = text.replace('"', '\\"')
            selector = f'a:has-text("{escaped_text}")'
            elements.append((safe_name, selector))

    # Archivo destino
    file_path = build_file_path(page_name, url)
    existing_locators = parse_existing_locators(file_path)

    # Código base
    pom_code = ""
    if not os.path.exists(file_path):
        pom_code += f"class {page_name}:\n"
        pom_code += "    def __init__(self, page):\n"
        pom_code += "        self.page = page\n\n"

    # Agregar locators nuevos
    new_locators_added = False
    for name, selector in elements:
        if name not in existing_locators:
            # Forzamos comillas simples por fuera para evitar conflicto con comillas dobles internas
            pom_code += f"        self.{name} = page.locator('{selector}')\n"
            new_locators_added = True

    # Métodos genéricos
    generic_methods = """
    # --- Métodos genéricos ---
    def fill_input(self, locator_name, value):
        getattr(self, locator_name).fill(value)

    def click_button(self, locator_name):
        getattr(self, locator_name).click()

    def get_text(self, locator_name):
        return getattr(self, locator_name).inner_text()

    def is_visible(self, locator_name):
        return getattr(self, locator_name).is_visible()
"""
    # Métodos específicos según URL
    methods_code = ""
    if "/login" in url.lower():
        methods_code += """
    def do_login(self, user, pwd):
        self.fill_input("username", user)
        self.fill_input("password", pwd)
        self.click_button("login_button")
"""
    if "/secure" in url.lower():
        methods_code += """
    def logout(self):
        self.click_button("logout_button")
"""

    # Guardar archivo
    mode = "a" if os.path.exists(file_path) else "w"
    with open(file_path, mode, encoding="utf-8") as f:
        f.write(pom_code)
        content = open(file_path, encoding="utf-8").read()
        if "def fill_input" not in content:
            f.write(generic_methods)
        if methods_code and methods_code not in content:
            f.write(methods_code)

    if new_locators_added or methods_code:
        print(f"✅ {page_name} actualizado en {file_path}")
    else:
        print(f"⚡ No se detectaron cambios en {page_name}")


def generate_login_and_secure_pages():
    """Demo: genera login + secure page en un solo run."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=200)
        page = browser.new_page()

        # Login Page
        page.goto("https://the-internet.herokuapp.com/login")
        generate_pom_from_html(page.content(), "LoginPage", page.url)

        # Login válido
        page.fill("#username", "tomsmith")
        page.fill("#password", "SuperSecretPassword!")
        page.click("button[type='submit']")
        page.wait_for_url("**/secure")

        # Secure Page
        generate_pom_from_html(page.content(), "SecurePage", page.url)

        browser.close()


if __name__ == "__main__":
    generate_login_and_secure_pages()
