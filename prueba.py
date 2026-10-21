from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    navegador = p.chromium.launch(headless=False)
    pagina = navegador.new_page()
    pagina.goto("https://registro.micuenta.metrogas.com.ar/index.html")

    input("Si se abrió el navegador, presioná ENTER para cerrar...")

    navegador.close()