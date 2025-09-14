# Playwright Auto-POM Demo

Framework de pruebas automatizadas con **Pytest + Playwright + BDD** que incluye un **auto-POM generator**:  
cada vez que se navega a una nueva página, el framework lee el DOM, detecta elementos y crea/actualiza automáticamente el **Page Object Model (POM)**.  
👉 ¡Nunca más escribir locators manualmente!

---

## 🚀 Características principales
- **BDD con Pytest-BDD** → escenarios claros en archivos `.feature`.
- **Playwright** → automatización moderna, rápida y confiable.
- **Page Object Model (POM)** automático → generado a partir del DOM real.
- **Métodos genéricos** (`fill_input`, `click_button`, `get_text`, `is_visible`).
- **Métodos específicos** para páginas conocidas (`do_login`, `logout`).
- **Estructura modular** → los POM se guardan en subcarpetas según la URL (`/secure/secure_page.py`).
- **Alias para símbolos raros** → ej. `×` → `close_button`.

---

## 📂 Estructura del proyecto

```
playwright_auto_pom_demo/
│── features/
│   └── login.feature
│── tests/
│   ├── steps/
│   │   └── test_login_steps.py
│   └── pages/
│       ├── common/
│       │   └── login_page.py
│       └── secure/
│           └── secure_page.py
│── utils/
│   └── pom_generator.py
│── conftest.py
│── requirements.txt
```

---

## 🛠 Instalación

1. Crear entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Ejecución

Para correr todos los tests en modo headed:

```bash
pytest -v --headed
```

Cada vez que una prueba navega a una página nueva (`page.goto(...)`),  
se generará automáticamente un archivo de POM en `tests/pages/...`.

---

## 📖 Ejemplo de test

### Feature (`features/login.feature`)
```gherkin
Feature: Login
  Scenario: Successful login
    Given the user is on the login page
    When the user enters valid credentials
    Then the user should see the secure page
```

### Step definitions (`tests/steps/test_login_steps.py`)
```python
@when("the user enters valid credentials")
def enter_credentials(login_page):
    login_page.do_login("tomsmith", "SuperSecretPassword!")

@then("the user should see the secure page")
def verify_secure_page(secure_page):
    assert "Secure Area" in secure_page.get_text("header")
    assert secure_page.is_visible("logout_button")
```

---

## ✅ Resultado esperado

```
tests/steps/test_login_steps.py::test_successful_login PASSED
tests/steps/test_login_steps.py::test_logout_from_secure_page PASSED
```

---

## 💡 Ideas futuras
- Guardar **screenshots automáticos** junto a cada POM generado.
- Integración con **CI/CD** en GitHub Actions.
- Diccionario ampliable de **alias para iconografía** (🔍 → search_button, ➕ → add_button).
- Soporte para **DOM dinámico** con `page.wait_for_load_state("networkidle")`.

---

## 👩‍💻 Autor
Creado por **Erna Tercero Rodríguez** como parte de su portafolio en QA Automation.  
