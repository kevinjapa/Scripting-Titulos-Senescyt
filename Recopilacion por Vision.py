from bs4 import BeautifulSoup
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

def extraer_datos(page):
    html_content = page.content()
    soup = BeautifulSoup(html_content, "html.parser")

    identificacion_label = soup.find("label", id="formPrincipal:j_idt45")
    identificacion = identificacion_label.text.strip() if identificacion_label else "No disponible"

    nombres_label = soup.find("label", id="formPrincipal:j_idt47")
    nombres = nombres_label.text.strip() if nombres_label else "No disponible"

    titulos = []
    tabla = soup.find("tbody", id="formPrincipal:j_idt52:0:tablaAplicaciones_data")
    if tabla:
        for fila in tabla.find_all("tr"):
            celdas = [celda.text.strip() for celda in fila.find_all("td")]
            titulos.append(celdas)

    return {"identificacion": identificacion, "nombres": nombres, "titulos": titulos}

def guardar_informacion_csv(datos_texto, archivo="informacion_titulos.csv"):
    if not datos_texto.strip():
        print("No hay datos para guardar en el CSV.")
        return

    try:
        print("Procesando datos para guardar en CSV...")
        lineas = datos_texto.split("\n")
        encabezados = []
        datos = []

        for linea in lineas:
            if not linea.strip() or all(char in "-| " for char in linea):
                continue

            columnas = [col.strip() for col in linea.split("|")]

            if len(columnas) > 0 and columnas[0] == "":
                columnas.pop(0)
            if len(columnas) > 0 and columnas[-1] == "":
                columnas.pop(-1)

            if not encabezados:
                encabezados = columnas
                print(f"Encabezados establecidos ({len(encabezados)}): {encabezados}")

            elif len(columnas) < len(encabezados):
                columnas.extend([""] * (len(encabezados) - len(columnas)))
                datos.append(columnas)
                print(f"Fila ajustada y agregada: {columnas}")
            
            elif len(columnas) == len(encabezados):
                datos.append(columnas)
                print(f"Fila válida agregada: {columnas}")
            else:
                print(f"Línea descartada por desajuste de columnas ({len(columnas)} != {len(encabezados)}): {columnas}")

        if encabezados and datos:
            escribir_csv(encabezados, datos, archivo)
        else:
            print("No se encontraron datos válidos para guardar.")
    except Exception as e:
        print(f"Error al procesar y guardar datos en el CSV: {e}")

def escribir_csv(encabezados, datos, archivo):
    try:
        archivo_existe = os.path.isfile(archivo)
        with open(archivo, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
           
            if not archivo_existe:
                writer.writerow(encabezados)
            writer.writerows(datos)  
        print(f"Datos guardados correctamente en {archivo}.")
    except Exception as e:
        print(f"Error al escribir datos en el archivo CSV: {e}")

def llenar_identificacion(cedula):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("https://www.senescyt.gob.ec/consulta-titulos-web/faces/vista/consulta/consulta.xhtml")

        page.wait_for_selector('input#formPrincipal\\:identificacion')

        page.fill('input#formPrincipal\\:identificacion', cedula)

        captcha_image_selector = 'img#formPrincipal\\:capimg'
        captcha_image_path = "captcha_image.png"
        page.locator(captcha_image_selector).screenshot(path=captcha_image_path)

        texto_captcha = extraer_texto_captcha(captcha_image_path)
        if not texto_captcha:
            print("Error al resolver el CAPTCHA.")
            browser.close()
            return

        print(f"Texto extraído del CAPTCHA: {texto_captcha}")
        page.fill('input#formPrincipal\\:captchaSellerInput', texto_captcha)
        page.click('button#formPrincipal\\:boton-buscar')

        try:
            page.wait_for_selector("//div[contains(@id, 'pnlListaTitulos')]", timeout=60000)

            page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            page.screenshot(path="captura_datos.png")

            datos= extraer_dato("captura_datos.png")
            guardar_informacion_csv(datos)

            

        except Exception as e:
            print(f"Error durante la extracción de información: {e}")
        finally:
            browser.close()

def procesar_cedulas(csv_entrada):

    with open(csv_entrada, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        cedulas = [row[0] for row in reader]

    for cedula in cedulas:
        try:
            print(f"Procesando cédula: {cedula}")
            llenar_identificacion(cedula)
        except Exception as e:
            print(f"Error al procesar la cédula {cedula}: {e}")

def extraer_dato(imagen_path):
    base64_image = encode_image(imagen_path)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "en base con los datos que se encuentran dentro de las dos toablas, ayudame en forma de una sola tabla unidos los datos de ambas tablas y devuelve solamente la tabla nno quiero texto aparte",
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
        raise ValueError("No se pudo extraer el texto.")

if __name__ == "__main__":
    # llenar_identificacion("NroCedula")
    procesar_cedulas("ced.txt")
