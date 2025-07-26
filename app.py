from flask import Flask, render_template, jsonify, request
import pandas as pd
import json
import os
from datetime import datetime
import numpy as np
# --- Nuevas importaciones para el chatbot ---
from google import genai
from dotenv import load_dotenv # <-- Importar load_dotenv

app = Flask(__name__)

# --- Cargar variables de entorno desde .env ---
load_dotenv() # <-- Carga las variables del archivo .env
# ----------------------------------------------
# Configuración de la aplicación
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'

try:
    # Intenta obtener la clave API desde las variables de entorno
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("La variable de entorno GEMINI_API_KEY no está definida en el archivo .env")

    # Configura el cliente de Gemini con la clave obtenida
    genai_client = genai.Client(api_key=api_key)  # Se crea una instancia del cliente

    # Selecciona el modelo (verifica que esté disponible)
    MODEL_NAME = "gemini-2.0-flash"  # O el modelo que prefieras

    print("Cliente de Gemini configurado correctamente.")  # Log de confirmación

except ValueError as ve:
    # Error específico si la variable no está en .env
    print(f"ADVERTENCIA: {ve}. El análisis con IA no estará disponible.")
    genai_client = None
    MODEL_NAME = None
except Exception as e:
    # Otros errores de configuración
    print(f"ADVERTENCIA: Error al configurar el cliente de Gemini: {e}. El análisis con IA no estará disponible.")
    genai_client = None
    MODEL_NAME = None
# -------------------------------------------------------------------------------------

# Coordenadas del Rio Quijos (ejemplo extendido)
RIO_QUIJOS_COORDS = [
    [-0.562767, -78.182822],
    [-0.562689, -78.180687],
    [-0.562611, -78.178552],
    [-0.562533, -78.176417],
    [-0.562455, -78.174282],
    [-0.562377, -78.172147],
    [-0.562299, -78.170012],
    [-0.562221, -78.167877],
    [-0.562143, -78.165742],
    [-0.562065, -78.163607],
    [-0.561987, -78.161472],
    [-0.561909, -78.159337],
    [-0.561831, -78.157202],
    [-0.561753, -78.155067],
    [-0.561675, -78.152932]
]


def safe_read_csv(filename):
    """Lee un archivo CSV de forma segura, manejando errores"""
    try:
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            # Convertir fecha a datetime si existe la columna
            if 'Fecha' in df.columns:
                df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
            return df
        else:
            print(f"Archivo {filename} no encontrado")
            return pd.DataFrame()
    except Exception as e:
        print(f"Error leyendo {filename}: {str(e)}")
        return pd.DataFrame()


def process_data_for_charts(df, data_type):
    """Procesa los datos para los gráficos, manejando valores faltantes"""
    if df.empty:
        return {}

    try:
        # Remover filas con fechas inválidas
        df = df.dropna(subset=['Fecha'])

        # Preparar datos para Chart.js
        labels = df['Fecha'].dt.strftime('%Y-%m-%d').tolist()
        datasets = []

        # Colores para diferentes sensores
        colors = {
            'P42': 'rgba(54, 162, 235, 0.8)',
            'P43': 'rgba(255, 99, 132, 0.8)',
            'P55': 'rgba(75, 192, 192, 0.8)',
            'H44': 'rgba(153, 102, 255, 0.8)',
            'H55': 'rgba(255, 159, 64, 0.8)',
            'P34': 'rgba(54, 162, 235, 0.8)',
            'P63': 'rgba(255, 99, 132, 0.8)',
            'M5023': 'rgba(75, 192, 192, 0.8)',
            'H34': 'rgba(153, 102, 255, 0.8)',
            'H45': 'rgba(255, 159, 64, 0.8)'
        }

        for column in df.columns:
            if column != 'Fecha':
                # Manejar valores NaN
                data = df[column].fillna(0).tolist()

                datasets.append({
                    'label': f'{column} ({data_type})',
                    'data': data,
                    'borderColor': colors.get(column, 'rgba(128, 128, 128, 0.8)'),
                    'backgroundColor': colors.get(column, 'rgba(128, 128, 128, 0.2)'),
                    'borderWidth': 2,
                    'fill': False
                })

        return {
            'labels': labels,
            'datasets': datasets
        }
    except Exception as e:
        print(f"Error procesando datos para {data_type}: {str(e)}")
        return {}


@app.route('/')
def index():
    """Página principal del dashboard"""
    return render_template('index.html')


@app.route('/api/precipitacion')
def api_precipitacion():
    """API para datos de precipitación"""
    df = safe_read_csv('precipitacion.csv')
    data = process_data_for_charts(df, 'Precipitación (mm)')
    return jsonify(data)


@app.route('/api/caudal')
def api_caudal():
    """API para datos de caudal"""
    df = safe_read_csv('caudal.csv')
    data = process_data_for_charts(df, 'Caudal (m³/s)')
    return jsonify(data)


@app.route('/api/nivel')
def api_nivel():
    """API para datos de nivel"""
    df = safe_read_csv('nivel.csv')
    data = process_data_for_charts(df, 'Nivel (m)')
    return jsonify(data)

@app.route('/api/precipitacion_papallacta')
def api_precipitacion_papallacta():
    df = safe_read_csv('papallactaprecipitacion.csv')
    data = process_data_for_charts(df, 'Precipitación Papallacta (mm)')
    return jsonify(data)

@app.route('/api/caudal_papallacta')
def api_caudal_papallacta():
    df = safe_read_csv('caudalpapallacta.csv')
    data = process_data_for_charts(df, 'Caudal Papallacta (m³/s)')
    return jsonify(data)

@app.route('/api/nivel_papallacta')
def api_nivel_papallacta():
    df = safe_read_csv('nivelpapallacta.csv')
    data = process_data_for_charts(df, 'Nivel Papallacta (m)')
    return jsonify(data)





def leer_coords_txt(nombre_archivo):
    """Lee un archivo .txt de coordenadas lat, lon por línea y devuelve una lista de listas [lat, lon]"""
    coords = []
    try:
        with open(nombre_archivo, 'r') as archivo:
            for linea in archivo:
                partes = linea.strip().split(',')
                if len(partes) == 2:
                    try:
                        lat = float(partes[0].strip())
                        lon = float(partes[1].strip())
                        coords.append([lat, lon])
                    except ValueError:
                        print(f"Coordenada inválida en línea: {linea}")
    except Exception as e:
        print(f"Error leyendo {nombre_archivo}: {e}")
    return coords

@app.route('/api/rios')
def api_rios():
    """API que devuelve coordenadas de múltiples ríos desde archivos .txt"""
    rio_quijos = leer_coords_txt('coordquijos.txt')
    rio_papallacta = leer_coords_txt('coordpapallacta.txt')

    return jsonify({
        'quijos': rio_quijos,
        'papallacta': rio_papallacta
    })

@app.route('/api/rio-coords')
def api_rio_coords():
    """Devuelve coordenadas de ambos ríos desde archivos .txt"""
    return jsonify({
        'rio_quijos': leer_coords_txt('coordquijos.txt'),
        'rio_papallacta': leer_coords_txt('coordpapallacta.txt')
    })


@app.route('/api/stats')
def api_stats():
    """API para estadísticas generales"""
    try:
        precipitacion_df = safe_read_csv('precipitacion.csv')
        caudal_df = safe_read_csv('caudal.csv')
        nivel_df = safe_read_csv('nivel.csv')
        precipitacionpapallacta_df = safe_read_csv('papallactaprecipitacion.csv')
        caudalpapallacta_df = safe_read_csv('caudalpapallacta.csv')
        nivelpapallacta_df = safe_read_csv('nivelpapallacta.csv')

        stats = {
            'total_registros': {
                'precipitacion': (len(precipitacion_df) if not precipitacion_df.empty  else 0)+(len(precipitacionpapallacta_df) if not precipitacionpapallacta_df.empty  else 0),
                'caudal': (len(caudal_df) if not caudal_df.empty else 0)+(len(caudalpapallacta_df) if not caudalpapallacta_df.empty else 0),
                'nivel': (len(nivel_df) if not nivel_df.empty else 0)+(len(nivelpapallacta_df) if not nivelpapallacta_df.empty else 0)
            },
            'sensores_activos': {
                'precipitacion': (len(
                    [col for col in precipitacion_df.columns if col != 'Fecha']) if not precipitacion_df.empty else 0)+(len(
                    [col for col in precipitacionpapallacta_df.columns if col != 'Fecha']) if not precipitacionpapallacta_df.empty else 0),
                'caudal': (len([col for col in caudal_df.columns if col != 'Fecha']) if not caudal_df.empty else 0)+(len([col for col in caudalpapallacta_df.columns if col != 'Fecha']) if not caudalpapallacta_df.empty else 0),
                'nivel': (len([col for col in nivel_df.columns if col != 'Fecha']) if not nivel_df.empty else 0)+(len([col for col in nivelpapallacta_df.columns if col != 'Fecha']) if not nivelpapallacta_df.empty else 0)
            }
        }

        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)})


# --- Añade/Reemplaza esta nueva ruta al final del archivo, antes de if __name__ == '__main__': ---
@app.route('/api/analizar', methods=['POST'])
def api_analizar():
    """
    API para analizar datos de gráficos usando Gemini.
    Recibe datos JSON del frontend, los procesa y devuelve un análisis.
    """
    # Verificar si el cliente de Gemini está configurado
    if not genai_client or not MODEL_NAME:
        return jsonify({
                           'error': 'Servicio de análisis IA no disponible. Clave API no configurada o cliente no inicializado.'}), 503

    try:
        # Obtener los datos JSON del cuerpo de la solicitud
        data = request.get_json()
        if not genai_client or not MODEL_NAME:
            return jsonify({'error': 'No se recibieron datos en el cuerpo de la solicitud.'}), 400

        # Extraer información del JSON
        grafico_id = data.get('grafico_id')  # Ej: 'precipitacionChart'
        seccion = data.get('seccion')  # Ej: 'precipitacion'
        datos = data.get('datos')  # Datos del gráfico { labels: [...], datasets: [...] }
        contexto = data.get('contexto', '')  # Información adicional opcional del usuario

        if not grafico_id or not seccion or not datos:
            return jsonify({'error': 'Datos incompletos. Se requieren grafico_id, seccion y datos.'}), 400

        # 1. Formatear los datos para el prompt
        # Creamos una representación de texto estructurada de los datos del gráfico
        datos_texto = f"Datos del gráfico '{grafico_id}' (Sección: {seccion}):\n"
        datos_texto += f"Fechas (Eje X): {datos.get('labels', [])}\n"
        datos_texto += "Series de Datos (Eje Y):\n"
        for dataset in datos.get('datasets', []):
            datos_texto += f"  - {dataset.get('label', 'Serie sin nombre')}: {dataset.get('data', [])}\n"

        # 2. Crear el prompt para Gemini
        prompt = f"""
        Eres un experto hidrólogo analizando datos de un dashboard sobre el Volcán Antisana.

        CONTEXTUALIZACIÓN:
        - El Volcán Antisana es una fuente crucial de agua para la región.
        - Se monitorean parámetros como Precipitación (mm), Caudal (m³/s) y Nivel (m) de los ríos.
        - Los datos provienen de sensores distribuidos en la zona.

        DATOS A ANALIZAR:
        {datos_texto}

        INSTRUCCIONES:
        Proporciona un análisis conciso y profesional de estos datos en español. Tu análisis debe incluir:
        1. Tendencias principales observadas (aumento, disminución, estabilidad, ciclos).
        2. Valores máximos y mínimos destacados, si los hay, y en qué fechas aproximadamente.
        3. Comparaciones relevantes entre diferentes series de datos (sensores), si aplica.
        4. Posibles correlaciones o patrones interesantes.
        5. Una breve conclusión sobre el estado actual del parámetro monitoreado.

        IMPORTANTE:
        - Sé objetivo y basa tu análisis únicamente en los datos proporcionados.
        - No hagas predicciones a largo plazo.
        - Si los datos son insuficientes o no muestran patrones claros, indícalo.
        - Responde en español latinoamericano.
        - No uses formato markdown ni HTML en tu respuesta.
        - Tu respuesta debe ser un texto plano informativo.
        - Debes relacionar estos datos a como afecta a la central Hidroeléctric Coca Codo Sinclair.
        _ Tu respuesta debe tambien relacionar en como afecta a la poblacion cercana a estos sectores y con respecto a la entrega de agua para la ciudad de Quito.

        CONTEXTO ADICIONAL DEL USUARIO (si aplica):
        {contexto if contexto else 'Ninguno proporcionado.'}
        """

        # 3. Llamar a la API de Gemini usando la nueva sintaxis
        # Usamos models.generate_content en lugar de model.generate_content
        response = genai_client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt  # El texto del prompt va aquí
        )

        # 4. Extraer el texto de la respuesta
        # La estructura de la respuesta también puede ser ligeramente diferente
        if hasattr(response, 'text') and response.text:
            analisis_texto = response.text.strip()
        else:
            # Manejar el caso de una respuesta vacía o inesperada
            # Puede que la respuesta tenga una estructura como response.candidates[0].content.parts[0].text
            # o simplemente no tenga texto. Es mejor manejarlo con cuidado.
            # print(f"Respuesta inesperada de Gemini: {response}") # Para depuración
            candidate = getattr(response, 'candidates', [None])[0]
            content = getattr(candidate, 'content', None)
            part = getattr(content, 'parts', [None])[0]
            analisis_texto = getattr(part, 'text', None)

            if not analisis_texto:
                analisis_texto = "Lo siento, el modelo de IA no pudo generar un análisis para estos datos en este momento, o la respuesta no contenía texto. Por favor, inténtalo de nuevo más tarde."
            else:
                analisis_texto = analisis_texto.strip()

        # 5. Devolver la respuesta al frontend
        return jsonify({'analisis': analisis_texto})

    except genai.api_types.ApiError as api_err:  # Capturar errores específicos de la API
        app.logger.error(f"Error de API de Gemini en /api/analizar: {api_err}")
        return jsonify({
                           'error': f'Error al comunicarse con la API de Gemini: {str(api_err)}'}), 502  # Bad Gateway indica problema upstream
    except Exception as e:
        # Registrar el error en el servidor para depuración
        app.logger.error(f"Error en /api/analizar: {e}")
        # Devolver un mensaje de error genérico al usuario
        return jsonify({'error': 'Ocurrió un error interno en el servidor al procesar la solicitud de análisis.'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)