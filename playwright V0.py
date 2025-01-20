import base64
from playwright.sync_api import sync_playwright
from openai import OpenAI
import csv
import os

client = OpenAI()

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def extraer_texto_captcha(imagen_path):

    base64_image = encode_image(imagen_path)

    response = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What is the text in this image? Help me only with the text in the image, I don't want extra text",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
    )

    choices = response.choices 
    if choices and len(choices) > 0:
        texto_extraido = choices[0].message.content  
        return texto_extraido.strip()
    else:
        raise ValueError("No se pudo extraer el texto del CAPTCHA.")

def extraer_informacion(page):
    try:

        identificacion = page.text_content('#formPrincipal\\:j_idt57')
        nombres = page.text_content('#formPrincipal\\:j_idt59')
        genero = page.text_content('#formPrincipal\\:j_idt62')
        nacionalidad = page.text_content('#formPrincipal\\:j_idt64')


        filas_titulos = page.locator('#formPrincipal\\:j_idt65\\:0\\:tablaAplicaciones_data > tr')
        titulos = []
        for fila in filas_titulos.all():
            columnas = fila.locator('td').all_inner_texts()
            titulos.append(columnas)

        return {
            "informacion_personal": {
                "Identificación": identificacion.strip(),
                "Nombres": nombres.strip(),
                "Género": genero.strip(),
                "Nacionalidad": nacionalidad.strip(),
            },
            "titulos_academicos": titulos,
        }
    except Exception as e:
        print(f"Error al extraer información: {e}")
        return None

def llenar_identificacion(cedula):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://www.senescyt.gob.ec/consulta-titulos-web/faces/vista/consulta/consulta.xhtml")
        page.wait_for_selector('input#formPrincipal\\:identificacion')

        page.fill('input#formPrincipal\\:identificacion', cedula)

        captcha_image_selector = 'img#formPrincipal\\:capimg'
        page.wait_for_selector(captcha_image_selector)
        captcha_image_element = page.locator(captcha_image_selector)
        captcha_image_path = "captcha_imagen.png"
        captcha_image_element.screenshot(path=captcha_image_path)

        texto_captcha = extraer_texto_captcha(captcha_image_path)
        print(f"Texto extraído del CAPTCHA: {texto_captcha}")

        if not texto_captcha or len(texto_captcha) < 4:
            print("CAPTCHA no válido. Intenta nuevamente.")
            browser.close()
            return

        page.fill('input#formPrincipal\\:captchaSellerInput', texto_captcha)
        page.click('button#formPrincipal\\:boton-buscar')

        try:
            page.wait_for_selector('#formPrincipal\\:j_idt65\\:0\\:tablaAplicaciones', timeout=60000)
        except Exception as e:
            print("No se pudieron cargar los datos. Verifica el CAPTCHA.")
            print(page.content())  
            browser.close()
            return

        informacion = extraer_informacion(page)

        if informacion is None:
            print("No se pudo extraer información de la página.")
            browser.close()
            return

        archivo = "informacion_titulos.csv"
        archivo_existe = os.path.exists(archivo) and os.path.getsize(archivo) > 0

        with open(archivo, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            if not archivo_existe:
                writer.writerow(["Campo", "Valor"])

            for key, value in informacion["informacion_personal"].items():
                writer.writerow([key, value])

            writer.writerow([])

            if not archivo_existe:
                writer.writerow(["Título", "Institución", "Tipo", "Reconocido Por", "Número de Registro", "Fecha de Registro", "Área", "Observación"])

            for titulo in informacion["titulos_academicos"]:
                writer.writerow(titulo)

        print("Información guardada en 'informacion_titulos.csv'.")
        browser.close()

if __name__ == "__main__":
    llenar_identificacion("Nro de cédula")
