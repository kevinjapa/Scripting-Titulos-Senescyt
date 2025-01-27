# Script para Extracción de Información desde SENESCYT con Playwright y OpenAI

## Descripción

Este script automatiza la extracción de datos desde la página de consulta de títulos de SENESCYT, resolviendo CAPTCHAs con ayuda de OpenAI y organizando los resultados en un archivo CSV. Su propósito es facilitar el acceso y manejo de información académica registrada en el sitio web oficial.

---

## Requisitos

### Dependencias

Antes de ejecutar el script, asegúrate de tener instaladas las siguientes dependencias:

- **Python 3.9 o superior**  
- Librerías de Python:
  - [playwright](https://playwright.dev/python): Para la interacción con la página web.
  - [beautifulsoup4](https://pypi.org/project/beautifulsoup4/): Para procesar el contenido HTML.
  - [openai](https://pypi.org/project/openai/): Para la interacción con el modelo de lenguaje que resuelve el CAPTCHA.
  - [csv](https://docs.python.org/3/library/csv.html): Para manejar archivos CSV.
  - [os](https://docs.python.org/3/library/os.html): Para operaciones de sistema de archivos.

### Instalación de Librerías

Usa el siguiente comando para instalar todas las dependencias necesarias:


**Nota:** Recuerda instalar `playwright` y configurar el navegador:


---

## Archivos Requeridos

1. **Archivo de entrada (`ced.txt`)**:
   - Archivo CSV donde cada fila contiene una cédula de identidad. Ejemplo:

     ```
     0123456789
     9876543210
     1234567890
     ```

2. **Archivo de salida (`informacion_titulos.csv`)**:
   - Archivo generado automáticamente con la información extraída desde el sitio web.

---

## Funcionalidades del Script

### 1. Resolución Automática de CAPTCHAs
   - Toma una captura de pantalla del CAPTCHA y lo envía al modelo de lenguaje GPT para obtener el texto.
   - Convierte la imagen del CAPTCHA en Base64 antes de procesarla.

### 2. Extracción de Datos
   - Ingresa al sitio web oficial de SENESCYT.
   - Llena los campos de búsqueda usando cédulas.
   - Descarga y analiza la tabla de resultados con BeautifulSoup.

### 3. Unificación de Tablas
   - Combina los datos de múltiples tablas en un solo formato estructurado.
   - Guarda la información procesada en un archivo CSV.

### 4. Procesamiento de Varias Cédulas
   - Procesa un archivo de entrada con cédulas y extrae información de cada una en una sola ejecución.

---


## Cómo Ejecutar el Programa

### Pasos para la Ejecución

1. **Configura las credenciales de OpenAI**:
   - Asegúrate de tener una cuenta en OpenAI y genera una clave API.
   - Configura la clave API como variable de entorno:
     ```
     export OPENAI_API_KEY="tu_clave_api"
     ```

2. **Prepara el archivo de entrada**:
   - Crea un archivo llamado `ced.txt` en la misma carpeta del script. Cada línea del archivo debe contener una cédula de identidad. Ejemplo:
     ```
     0123456789
     9876543210
     1234567890
     ```

3. **Ejecuta el script**:
   - Abre la terminal, navega a la carpeta donde se encuentra el script y escribe:
     ```
     python Recopilacion por Vision.py
     ```

4. **Resultados**:
   - El programa procesará las cédulas del archivo `ced.txt`.
   - Extraerá la información desde SENESCYT y guardará los datos en un archivo llamado `informacion_titulos.csv`.


---

## Funciones Principales

### `encode_image(image_path)`
Convierte una imagen en Base64 para su uso en las solicitudes a OpenAI.

### `extraer_texto_captcha(imagen_path)`
Resuelve el CAPTCHA utilizando el modelo GPT para obtener el texto.

### `extraer_datos(page)`
Extrae información de las tablas en la página web y las procesa en un diccionario.

### `guardar_informacion_csv(datos_texto, archivo="informacion_titulos.csv")`
Guarda los datos procesados en un archivo CSV.

### `llenar_identificacion(cedula)`
Automatiza el llenado del formulario en la página de SENESCYT para buscar información.

### `procesar_cedulas(csv_entrada)`
Procesa un archivo con múltiples cédulas y ejecuta la extracción de información por cada una.

---

## Notas

1. **Modelos de OpenAI**:
   - Asegúrate de que tu cuenta de OpenAI tenga acceso al modelo `gpt-4o-mini` o realiza los ajustes necesarios si utilizas un modelo diferente.

2. **Timeouts**:
   - El script está configurado con un tiempo de espera de 60 segundos para la carga de resultados. Si la página no responde en este tiempo, el script reportará un error.

3. **Errores Comunes**:
   - CAPTCHA no resuelto: Si el modelo no puede resolver el CAPTCHA, verifica que el formato de la imagen sea correcto.
   - Cédula no válida: Si una cédula no produce resultados, revisa el archivo de entrada.

---

## Ejemplo de Archivo de Salida

El archivo `informacion_titulos.csv` tendrá un formato como este:

| Identificación | Nombres         | Títulos                            |
|----------------|-----------------|------------------------------------|
| 0123456789     | Juan Pérez      | Ingeniería en Sistemas            |
| 9876543210     | María González  | Medicina                          |
| 1234567890     | Ana Ramírez     | Derecho                           |

---

## Créditos

Este script fue desarrollado para automatizar la extracción de datos académicos desde la página web de SENESCYT utilizando tecnologías modernas como **Playwright** y **OpenAI GPT**.

Para consultas o problemas, contacta al desarrollador. 🚀
