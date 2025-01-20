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

def extraer_informacion(page):
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

def guardar_informacion_csv(informacion, archivo="informacion_titulos.csv"):

    encabezados = ["Identificación", "Nombres y Apellidos", "Título", "Institución", "Tipo", "Número de Registro", "Fecha de Registro", "Área", "Observación"]
    archivo_existe = os.path.isfile(archivo)
    with open(archivo, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not archivo_existe:
            writer.writerow(encabezados)
        
        for titulo_raw in informacion["titulos"]:

            titulo = titulo_raw[0].replace("Título", "").strip()
            institucion = titulo_raw[1].replace("Institución de Educación Superior", "").strip()
            tipo = titulo_raw[2].replace("Tipo", "").strip()
            numero_registro = titulo_raw[4].replace("Número de Registro", "").strip()
            fecha_registro = titulo_raw[5].replace("Fecha de Registro", "").strip()
            area = titulo_raw[6].replace("Área o Campo de Conocimiento", "").strip()
            observacion = titulo_raw[7].replace("Observación", "").strip()

            writer.writerow([
                informacion["identificacion"],
                informacion["nombres"],
                titulo,
                institucion,
                tipo,
                numero_registro,
                fecha_registro,
                area,
                observacion
            ])

def llenar_identificacion(cedula):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
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
            informacion = extraer_informacion(page)
            if informacion and informacion["titulos"]:
                guardar_informacion_csv(informacion)
                print("Información extraída y guardada con éxito.")
            else:
                print("No se pudo extraer información.")
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

if __name__ == "__main__":
    #llenar_identificacion("NroCedula")
    procesar_cedulas("Cedulas.csv")

