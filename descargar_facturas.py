



from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

URL_METROGAS = "https://registro.micuenta.metrogas.com.ar/index.html"
CARPETA = Path.home() / "Documents" / "Facturas-MetroGAS"


def main():
    CARPETA.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=False)
        pagina = navegador.new_page(accept_downloads=True)
        pagina.goto(URL_METROGAS)

        input(
            "Iniciá sesión y dejá visible el listado de facturas. "
            "Presioná ENTER para continuar..."
        )

        # Los botones que contienen un BDI son los candidatos a factura.
        facturas = pagina.locator("button.sapMBtn").filter(
    has=pagina.locator("bdi[id$='-BDI-content']")
)

        total = facturas.count()
        print(f"Botones de factura detectados: {total}")

        if total == 0:
            print("No se encontraron facturas.")
            navegador.close()
            return

        # Confirmar el listado antes de iniciar las descargas.
        
        import re

        todos = pagina.locator("button.sapMBtn").filter(
            has=pagina.locator("bdi[id$='-BDI-content']")
        )

        indices_facturas = []

        for i in range(todos.count()):
            texto = todos.nth(i).inner_text().strip()

            if re.fullmatch(r"\d{8,}", texto):
                indices_facturas.append(i)
                print(f"Factura {len(indices_facturas) - 1}: {texto}")

        print("Total de facturas:", len(indices_facturas))


        confirmacion = input(
            "\n¿Querés procesar todos estos botones? Escribí SI para continuar: "
        )

        if confirmacion.strip().upper() != "SI":
            navegador.close()
            return

        exitosas = 0
        errores = 0

        
        exitosas = 0
        errores = 0

        for posicion, indice_real in enumerate(indices_facturas):
            try:
                facturas = pagina.locator("button.sapMBtn").filter(
                    has=pagina.locator("bdi[id$='-BDI-content']")
                )

                boton_factura = facturas.nth(indice_real)
                numero = boton_factura.inner_text().strip()

                print(f"\nProcesando factura {posicion + 1}: {numero}")

                boton_factura.click()
                pagina.wait_for_timeout(1500)

                descargar = pagina.get_by_role(
                    "button", name="Descargar", exact=True
                )

                if descargar.count() == 0:
                    print("No se encontró el botón Descargar.")
                    errores += 1
                else:
                    try:
                        with pagina.expect_download(timeout=15000) as evento:
                            descargar.first.click()

                        archivo = evento.value
                        nombre = Path(archivo.suggested_filename).name

                        if not nombre.lower().endswith(".pdf"):
                            nombre = f"factura_{numero}.pdf"

                        destino = CARPETA / nombre

                        if destino.exists():
                            print(f"Ya existe, se omite: {nombre}")
                        else:
                            archivo.save_as(str(destino))
                            print(f"Descargada: {destino}")
                            exitosas += 1

                    except PlaywrightTimeoutError:
                        print("No se detectó una descarga directa.")
                        errores += 1

                volver = pagina.locator(
                    'button[aria-label="sys-cancel"]'
                )

                if volver.count() == 1:
                    volver.click()
                    pagina.wait_for_timeout(1500)
                else:
                    print("No se encontró el botón Volver. Se detiene.")
                    errores += 1
                    break

            except Exception as error:
                print(f"Error en factura {posicion + 1}: {error}")
                errores += 1
                break


        print("\nProceso terminado.")
        print(f"Descargas correctas: {exitosas}")
        print(f"Errores: {errores}")
        print(f"Carpeta de destino: {CARPETA}")

        input("Presioná ENTER para cerrar el navegador...")
        navegador.close()


if __name__ == "__main__":
    main()

