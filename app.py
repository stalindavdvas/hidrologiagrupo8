from flask import Flask, render_template, jsonify, request
import pandas as pd
import json
import os
from datetime import datetime
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score, mean_squared_error
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
            'M5023': 'rgba(40, 30, 209, 0.8)',
            'H31': 'rgba(35, 158, 184, 0.8)',
            'H32': 'rgba(11, 126, 24, 0.8)',
            'H33': 'rgba(153, 102, 255, 0.8)',
            'H34': 'rgba(133, 157, 23, 0.8)',
            'H36': 'rgba(53, 11, 142, 0.8)',
            'H45': 'rgba(192, 6, 167, 0.8)',
            'H46': 'rgba(201, 142, 5, 0.8)',
            'P34': 'rgba(35, 158, 184, 0.8)',
            'P38': 'rgba(11, 126, 24, 0.8)',
            'P42': 'rgba(133, 157, 23, 0.8)',
            'P43': 'rgba(153, 102, 255, 0.8)',
            'P46': 'rgba(53, 11, 142, 0.8)',
            'P55': 'rgba(192, 6, 167, 0.8)',
            'P57': 'rgba(201, 142, 5, 0.8)',

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
    df = safe_read_csv('precipitacion_quijos.csv')
    data = process_data_for_charts(df, 'Precipitación (mm)')
    return jsonify(data)


@app.route('/api/caudal')
def api_caudal():
    """API para datos de caudal"""
    df = safe_read_csv('caudal_quijos.csv')
    data = process_data_for_charts(df, 'Caudal (m³/s)')
    return jsonify(data)


@app.route('/api/nivel')
def api_nivel():
    """API para datos de nivel"""
    df = safe_read_csv('nivel_quijos.csv')
    data = process_data_for_charts(df, 'Nivel (m)')
    return jsonify(data)

@app.route('/api/precipitacion_papallacta')
def api_precipitacion_papallacta():
    df = safe_read_csv('precipitacion_papallacta.csv')
    data = process_data_for_charts(df, 'Precipitación Papallacta (mm)')
    return jsonify(data)

@app.route('/api/caudal_papallacta')
def api_caudal_papallacta():
    df = safe_read_csv('caudal_papallacta.csv')
    data = process_data_for_charts(df, 'Caudal Papallacta (m³/s)')
    return jsonify(data)

@app.route('/api/nivel_papallacta')
def api_nivel_papallacta():
    df = safe_read_csv('nivel_papallacta.csv')
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
        precipitacion_df = safe_read_csv('precipitacion_quijos.csv')
        caudal_df = safe_read_csv('caudal_quijos.csv')
        nivel_df = safe_read_csv('nivel_quijos.csv')
        precipitacionpapallacta_df = safe_read_csv('precipitacion_papallacta.csv')
        caudalpapallacta_df = safe_read_csv('caudal_papallacta.csv')
        nivelpapallacta_df = safe_read_csv('nivel_papallacta.csv')

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
                'nivel': (len([col for col in nivel_df.columns if col != 'Fecha']) if not nivel_df.empty else 0)
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

# === Funciones para análisis de correlación caudal-nivel ===

def load_level_flow_data():
    """Cargar datos de caudal y nivel para ambas estaciones"""
    try:
        caudal_papallacta = safe_read_csv('caudal_papallacta.csv')
        nivel_papallacta = safe_read_csv('nivel_papallacta.csv')
        caudal_quijos = safe_read_csv('caudal_quijos.csv')
        nivel_quijos = safe_read_csv('nivel_quijos.csv')
        return caudal_papallacta, nivel_papallacta, caudal_quijos, nivel_quijos
    except Exception as e:
        print(f"❌ Error cargando datos para correlación: {e}")
        return None, None, None, None

def prepare_station_data(caudal_data, nivel_data, station_name):
    """Preparar datos alineados por fecha para una estación"""
    try:
        # Procesar caudal - promedio de todas las estaciones
        caudal_cols = [col for col in caudal_data.columns if col != 'Fecha']
        if caudal_cols:
            caudal_data['Caudal_Prom'] = caudal_data[caudal_cols].mean(axis=1)
        else:
            # Si no hay columnas específicas, asumir que la segunda columna en adelante son datos
            caudal_data['Caudal_Prom'] = caudal_data.select_dtypes(include=[np.number]).mean(axis=1)

        # Procesar nivel - promedio de todas las estaciones
        nivel_cols = [col for col in nivel_data.columns if col != 'Fecha']
        if nivel_cols:
            nivel_data['Nivel_Prom'] = nivel_data[nivel_cols].mean(axis=1)
        else:
             # Si no hay columnas específicas, asumir que la segunda columna en adelante son datos
            nivel_data['Nivel_Prom'] = nivel_data.select_dtypes(include=[np.number]).mean(axis=1)

        # Asegurar que la columna 'Fecha' sea datetime
        if 'Fecha' in caudal_data.columns:
            caudal_data['Fecha'] = pd.to_datetime(caudal_data['Fecha'], errors='coerce')
        if 'Fecha' in nivel_data.columns:
            nivel_data['Fecha'] = pd.to_datetime(nivel_data['Fecha'], errors='coerce')

        # Eliminar filas con NaT en Fecha
        caudal_data = caudal_data.dropna(subset=['Fecha'])
        nivel_data = nivel_data.dropna(subset=['Fecha'])

        # Merge por fecha (inner join para fechas comunes)
        if 'Fecha' in caudal_data.columns and 'Fecha' in nivel_data.columns:
            merged_data = pd.merge(
                caudal_data[['Fecha', 'Caudal_Prom']],
                nivel_data[['Fecha', 'Nivel_Prom']],
                on='Fecha',
                how='inner'
            )
            # Ordenar por fecha
            merged_data = merged_data.sort_values('Fecha').reset_index(drop=True)
        else:
            # Si no hay fechas, alinear por índice (como en el script original)
            min_len = min(len(caudal_data), len(nivel_data))
            merged_data = pd.DataFrame({
                'Caudal_Prom': caudal_data['Caudal_Prom'].iloc[:min_len].reset_index(drop=True),
                'Nivel_Prom': nivel_data['Nivel_Prom'].iloc[:min_len].reset_index(drop=True)
            })

        # Eliminar filas con NaN en los valores promedio
        merged_data = merged_data.dropna(subset=['Caudal_Prom', 'Nivel_Prom'])

        print(f"📊 Datos alineados para {station_name}: {len(merged_data)} registros")
        return merged_data

    except Exception as e:
        print(f"❌ Error preparando datos para {station_name}: {e}")
        return pd.DataFrame() # Devolver DataFrame vacío en caso de error

def analyze_flow_level_relationship_for_api(data):
    """Analizar relación caudal-nivel y preparar datos para API"""
    if len(data) < 5:
        return {"error": "Insuficientes datos para análisis"}

    caudal = data['Caudal_Prom'].values
    nivel = data['Nivel_Prom'].values
    fechas = data['Fecha'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist() # Convertir fechas a string

    # Correlaciones
    try:
        pearson_corr, pearson_p = stats.pearsonr(caudal, nivel)
        spearman_corr, spearman_p = stats.spearmanr(caudal, nivel)
    except Exception as e:
        print(f"⚠️ Error calculando correlaciones: {e}")
        pearson_corr, pearson_p, spearman_corr, spearman_p = None, None, None, None

    # Regresión Lineal
    try:
        X_linear = nivel.reshape(-1, 1)
        y_linear = caudal
        linear_model = LinearRegression().fit(X_linear, y_linear)
        linear_r2 = r2_score(y_linear, linear_model.predict(X_linear))
        linear_equation = f"Caudal = {linear_model.coef_[0]:.4f} * Nivel + {linear_model.intercept_:.2f}"

        # Preparar datos para la línea de regresión lineal (puntos extremos)
        nivel_min, nivel_max = np.min(nivel), np.max(nivel)
        caudal_linear_min = linear_model.predict(np.array([[nivel_min]]))[0]
        caudal_linear_max = linear_model.predict(np.array([[nivel_max]]))[0]
        linear_regression_line = {
            'x': [nivel_min, nivel_max],
            'y': [caudal_linear_min, caudal_linear_max]
        }
    except Exception as e:
        print(f"⚠️ Error en regresión lineal: {e}")
        linear_r2, linear_equation, linear_regression_line = None, None, None

    # Regresión Polinómica (Cuadrática)
    try:
        poly_features = PolynomialFeatures(degree=2)
        X_poly = poly_features.fit_transform(nivel.reshape(-1, 1))
        poly_model = LinearRegression().fit(X_poly, y_linear)
        poly_r2 = r2_score(y_linear, poly_model.predict(X_poly))
        # Crear puntos para la curva polinómica
        nivel_sorted = np.sort(nivel)
        X_poly_sorted = poly_features.transform(nivel_sorted.reshape(-1, 1))
        caudal_poly_pred = poly_model.predict(X_poly_sorted)
        polynomial_regression_curve = {
            'x': nivel_sorted.tolist(),
            'y': caudal_poly_pred.tolist()
        }
        # Formato simplificado de la ecuación (a*x^2 + b*x + c)
        # coef_ es [intercept, x, x^2] para PolynomialFeatures
        coefs = poly_model.coef_
        intercept = poly_model.intercept_
        poly_equation = f"Caudal = {coefs[2]:.4f}*Nivel² + {coefs[1]:.4f}*Nivel + {intercept:.2f}"
    except Exception as e:
        print(f"⚠️ Error en regresión polinómica: {e}")
        poly_r2, poly_equation, polynomial_regression_curve = None, None, None

    # Preparar datos para Chart.js
    chartjs_data = {
        "datasets": [
            {
                "label": "Datos Observados",
                "data": [{"x": float(n), "y": float(c)} for n, c in zip(nivel, caudal)],
                "backgroundColor": "rgba(54, 162, 235, 0.6)",
                "borderColor": "rgba(54, 162, 235, 1)",
                "borderWidth": 1,
                "pointRadius": 3,
                "showLine": False # Solo puntos para datos observados
            }
        ]
    }

    # Añadir línea de regresión lineal si existe
    if linear_regression_line:
         chartjs_data["datasets"].append({
            "label": f"Regresión Lineal (R²={linear_r2:.3f})",
            "data": [{"x": float(x), "y": float(y)} for x, y in zip(linear_regression_line['x'], linear_regression_line['y'])],
            "borderColor": "rgba(255, 99, 132, 1)",
            "borderWidth": 2,
            "fill": False,
            "showLine": True,
            "pointRadius": 0, # No mostrar puntos en la línea
             "borderDash": [] # Línea continua
        })

    # Añadir curva de regresión polinómica si existe
    if polynomial_regression_curve:
         chartjs_data["datasets"].append({
            "label": f"Regresión Polinómica (R²={poly_r2:.3f})",
            "data": [{"x": float(x), "y": float(y)} for x, y in zip(polynomial_regression_curve['x'], polynomial_regression_curve['y'])],
            "borderColor": "rgba(75, 192, 192, 1)",
            "borderWidth": 2,
            "fill": False,
            "showLine": True,
            "pointRadius": 0, # No mostrar puntos en la curva
            "tension": 0.4 # Suavizar la línea
        })


    # Preparar estadísticas para devolver
    stats_data = {
        "total_puntos": len(data),
        "correlacion_pearson": pearson_corr,
        "p_valor_pearson": pearson_p,
        "correlacion_spearman": spearman_corr,
        "p_valor_spearman": spearman_p,
        "regresion_lineal": {
            "r2": linear_r2,
            "ecuacion": linear_equation
        } if linear_r2 is not None else None,
        "regresion_polinomica": {
            "r2": poly_r2,
            "ecuacion": poly_equation
        } if poly_r2 is not None else None
    }

    return {
        "success": True,
        "estadisticas": stats_data,
        "chartjs_data": chartjs_data # Datos formateados para Chart.js
    }

# === Fin de Funciones para análisis de correlación caudal-nivel ===
@app.route('/api/correlacion/<estacion>')
def api_correlacion(estacion):
    """API para datos de correlación caudal-nivel"""
    estacion = estacion.lower()
    if estacion not in ['papallacta', 'quijos']:
        return jsonify({"error": "Estación no válida. Usa 'papallacta' o 'quijos'."}), 400

    try:
        # 1. Cargar datos
        caudal_papallacta, nivel_papallacta, caudal_quijos, nivel_quijos = load_level_flow_data()
        if caudal_papallacta is None or nivel_papallacta is None or \
           caudal_quijos is None or nivel_quijos is None:
            return jsonify({"error": "Error al cargar los datos de caudal o nivel."}), 500

        # 2. Seleccionar datos de la estación solicitada
        if estacion == 'papallacta':
            caudal_data = caudal_papallacta
            nivel_data = nivel_papallacta
            station_name = "Papallacta"
        else: # quijos
            caudal_data = caudal_quijos
            nivel_data = nivel_quijos
            station_name = "Quijos"

        # 3. Preparar datos (alinear por fecha)
        aligned_data = prepare_station_data(caudal_data, nivel_data, station_name)
        if aligned_data.empty:
            return jsonify({"error": f"No se encontraron datos alineados para {station_name}."}), 404

        # 4. Analizar y preparar para API
        result = analyze_flow_level_relationship_for_api(aligned_data)
        if "error" in result:
            return jsonify(result), 400 # Devolver error específico del análisis

        # 5. Añadir nombre de la estación al resultado
        result["estacion"] = station_name
        return jsonify(result)

    except Exception as e:
        print(f"Error en /api/correlacion/{estacion}: {e}")
        return jsonify({"error": f"Error interno del servidor al procesar {estacion}."}), 500


# === Funciones para análisis de correlación Precipitación-Nivel ===

def load_precip_level_data_for_api():
    """Cargar datos de precipitación y nivel para ambas estaciones"""
    try:
        precip_papallacta = safe_read_csv('precipitacion_papallacta.csv')
        nivel_papallacta = safe_read_csv('nivel_papallacta.csv')
        precip_quijos = safe_read_csv('precipitacion_quijos.csv')
        nivel_quijos = safe_read_csv('nivel_quijos.csv')
        return precip_papallacta, nivel_papallacta, precip_quijos, nivel_quijos
    except Exception as e:
        print(f"❌ Error cargando datos para correlación Precipitación-Nivel: {e}")
        return None, None, None, None


def prepare_precip_level_data_for_api(precip_data, nivel_data, station_name):
    """Preparar datos alineados por fecha para una estación (Precipitación-Nivel)"""
    try:
        # --- Procesar Precipitación ---
        # Sumar todas las columnas de precipitación para obtener el total
        precip_cols = [col for col in precip_data.columns if col != 'Fecha']
        if precip_cols:
            precip_data['Precip_Total'] = precip_data[precip_cols].sum(axis=1, skipna=True)
        else:
            print(
                f"⚠️ No se encontraron columnas de precipitación específicas para {station_name}. Usando todas las numéricas.")
            numeric_precip_cols = precip_data.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_precip_cols:
                precip_data['Precip_Total'] = precip_data[numeric_precip_cols].sum(axis=1, skipna=True)
            else:
                raise ValueError(f"No hay datos numéricos de precipitación para {station_name}")

        # --- Procesar Nivel ---
        # Promediar todas las columnas de nivel
        nivel_cols = [col for col in nivel_data.columns if col != 'Fecha']
        if nivel_cols:
            nivel_data['Nivel_Prom'] = nivel_data[nivel_cols].mean(axis=1, skipna=True)
        else:
            print(
                f"⚠️ No se encontraron columnas de nivel específicas para {station_name}. Usando todas las numéricas.")
            numeric_nivel_cols = nivel_data.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_nivel_cols:
                nivel_data['Nivel_Prom'] = nivel_data[numeric_nivel_cols].mean(axis=1, skipna=True)
            else:
                raise ValueError(f"No hay datos numéricos de nivel para {station_name}")

        # --- Asegurar que la columna 'Fecha' sea datetime ---
        if 'Fecha' in precip_data.columns:
            precip_data['Fecha'] = pd.to_datetime(precip_data['Fecha'], errors='coerce')
        if 'Fecha' in nivel_data.columns:
            nivel_data['Fecha'] = pd.to_datetime(nivel_data['Fecha'], errors='coerce')

        # --- Eliminar filas con NaT en Fecha ---
        precip_data = precip_data.dropna(subset=['Fecha']).reset_index(drop=True)
        nivel_data = nivel_data.dropna(subset=['Fecha']).reset_index(drop=True)

        # --- Merge por fecha (inner join para fechas comunes) ---
        if 'Fecha' in precip_data.columns and 'Fecha' in nivel_data.columns:
            merged_data = pd.merge(
                precip_data[['Fecha', 'Precip_Total']],
                nivel_data[['Fecha', 'Nivel_Prom']],
                on='Fecha',
                how='inner'
            )
            # Ordenar por fecha
            merged_data = merged_data.sort_values('Fecha').reset_index(drop=True)
        else:
            # Si no hay fechas, alinear por índice (menos ideal)
            min_len = min(len(precip_data), len(nivel_data))
            merged_data = pd.DataFrame({
                'Precip_Total': precip_data['Precip_Total'].iloc[:min_len].reset_index(drop=True),
                'Nivel_Prom': nivel_data['Nivel_Prom'].iloc[:min_len].reset_index(drop=True)
            })

        # --- Eliminar filas con NaN en los valores calculados ---
        initial_len = len(merged_data)
        merged_data = merged_data.dropna(subset=['Precip_Total', 'Nivel_Prom']).reset_index(drop=True)
        final_len = len(merged_data)
        if initial_len != final_len:
            print(f"ℹ️ Filas eliminadas por NaN en {station_name}: {initial_len - final_len}")

        print(f"📊 Datos alineados y limpios (Precip-Nivel) para {station_name}: {len(merged_data)} registros")
        return merged_data

    except Exception as e:
        print(f"❌ Error preparando datos (Precip-Nivel) para {station_name}: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()


def analyze_precip_level_relationship_for_api(data):
    """Analizar relación precipitación-nivel y preparar datos para API"""
    if len(data) < 5:
        return {"error": "Insuficientes datos para análisis de Precipitación-Nivel"}

    precip = data['Precip_Total'].values
    nivel = data['Nivel_Prom'].values
    fechas = data['Fecha'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist() if 'Fecha' in data.columns else None

    # Eliminar pares NaN/NaN
    mask = ~(np.isnan(precip) | np.isnan(nivel))
    precip_clean = precip[mask]
    nivel_clean = nivel[mask]

    if len(precip_clean) < 5:
        return {"error": "Insuficientes datos válidos para análisis después de limpieza"}

    try:
        # Correlaciones
        pearson_corr, pearson_p = stats.pearsonr(precip_clean, nivel_clean)
        spearman_corr, spearman_p = stats.spearmanr(precip_clean, nivel_clean)

        # Regresión Lineal
        linear_model = LinearRegression()
        linear_model.fit(precip_clean.reshape(-1, 1), nivel_clean)
        linear_r2 = r2_score(nivel_clean, linear_model.predict(precip_clean.reshape(-1, 1)))
        linear_rmse = np.sqrt(mean_squared_error(nivel_clean, linear_model.predict(precip_clean.reshape(-1, 1))))
        linear_equation = f"Nivel = {linear_model.coef_[0]:.4f} * Precip + {linear_model.intercept_:.2f}"

        # Regresión Polinómica (Grado 2, como es común para este tipo de relación)
        poly_features = PolynomialFeatures(degree=2)
        X_poly = poly_features.fit_transform(precip_clean.reshape(-1, 1))
        poly_model = LinearRegression()
        poly_model.fit(X_poly, nivel_clean)
        poly_r2 = r2_score(nivel_clean, poly_model.predict(X_poly))
        poly_rmse = np.sqrt(mean_squared_error(nivel_clean, poly_model.predict(X_poly)))

        # Crear puntos para las líneas de regresión
        precip_sorted = np.sort(precip_clean)

        # Línea lineal
        nivel_linear_pred = linear_model.predict(precip_sorted.reshape(-1, 1))

        # Curva polinómica
        X_poly_sorted = poly_features.transform(precip_sorted.reshape(-1, 1))
        nivel_poly_pred = poly_model.predict(X_poly_sorted)

        # Preparar datos para Chart.js
        chartjs_data = {
            "datasets": [
                {
                    "label": "Datos Observados",
                    "data": [{"x": float(p), "y": float(n)} for p, n in zip(precip_clean, nivel_clean)],
                    "backgroundColor": "rgba(54, 162, 235, 0.6)",
                    "borderColor": "rgba(54, 162, 235, 1)",
                    "borderWidth": 1,
                    "pointRadius": 3,
                    "showLine": False
                },
                {
                    "label": f"Regresión Lineal (R²={linear_r2:.3f})",
                    "data": [{"x": float(p), "y": float(n)} for p, n in zip(precip_sorted, nivel_linear_pred)],
                    "borderColor": "rgba(255, 99, 132, 1)",
                    "borderWidth": 2,
                    "fill": False,
                    "showLine": True,
                    "pointRadius": 0,
                    "borderDash": []
                },
                {
                    "label": f"Regresión Polinómica (R²={poly_r2:.3f})",
                    "data": [{"x": float(p), "y": float(n)} for p, n in zip(precip_sorted, nivel_poly_pred)],
                    "borderColor": "rgba(75, 192, 192, 1)",
                    "borderWidth": 2,
                    "fill": False,
                    "showLine": True,
                    "pointRadius": 0,
                    "tension": 0.4
                }
            ]
        }

        # Preparar estadísticas
        stats_data = {
            "total_puntos": len(precip_clean),
            "correlacion_pearson": pearson_corr,
            "p_valor_pearson": pearson_p,
            "correlacion_spearman": spearman_corr,
            "p_valor_spearman": spearman_p,
            "regresion_lineal": {
                "r2": linear_r2,
                "rmse": linear_rmse,
                "ecuacion": linear_equation
            },
            "regresion_polinomica": {
                "r2": poly_r2,
                "rmse": poly_rmse
                # Coeficientes si se necesitan detallar más
            }
        }

        return {
            "success": True,
            "estadisticas": stats_data,
            "chartjs_data": chartjs_data
        }

    except Exception as e:
        print(f"⚠️ Error en análisis Precipitación-Nivel: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"Error al analizar relación Precipitación-Nivel: {str(e)}"}


# === Fin de Funciones para análisis de correlación Precipitación-Nivel ===
@app.route('/api/correlacion_precip_nivel/<estacion>')
def api_correlacion_precip_nivel(estacion):
    """API para datos de correlación precipitación-nivel"""
    estacion = estacion.lower()
    if estacion not in ['papallacta', 'quijos']:
        return jsonify({"error": "Estación no válida. Usa 'papallacta' o 'quijos'."}), 400

    try:
        # 1. Cargar datos
        precip_papallacta, nivel_papallacta, precip_quijos, nivel_quijos = load_precip_level_data_for_api()
        if precip_papallacta is None or nivel_papallacta is None or \
           precip_quijos is None or nivel_quijos is None:
            return jsonify({"error": "Error al cargar los datos de precipitación o nivel."}), 500

        # 2. Seleccionar datos de la estación solicitada
        if estacion == 'papallacta':
            precip_data = precip_papallacta
            nivel_data = nivel_papallacta
            station_name = "Papallacta"
        else: # quijos
            precip_data = precip_quijos
            nivel_data = nivel_quijos
            station_name = "Quijos"

        # 3. Preparar datos (alinear por fecha)
        aligned_data = prepare_precip_level_data_for_api(precip_data, nivel_data, station_name)
        if aligned_data.empty:
            return jsonify({"error": f"No se encontraron datos alineados para {station_name}."}), 404

        # 4. Analizar y preparar para API
        result = analyze_precip_level_relationship_for_api(aligned_data)
        if "error" in result:
            return jsonify(result), 400

        # 5. Añadir nombre de la estación al resultado
        result["estacion"] = station_name
        return jsonify(result)

    except Exception as e:
        print(f"Error en /api/correlacion_precip_nivel/{estacion}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error interno del servidor al procesar {estacion}."}), 500

# === Funciones para análisis de correlación Precipitación-Caudal ===

def load_precip_flow_data_for_api():
    """Cargar datos de precipitación y caudal para ambas estaciones"""
    try:
        precip_papallacta = safe_read_csv('precipitacion_papallacta.csv')
        caudal_papallacta = safe_read_csv('caudal_papallacta.csv')
        precip_quijos = safe_read_csv('precipitacion_quijos.csv')
        caudal_quijos = safe_read_csv('caudal_quijos.csv')
        return precip_papallacta, caudal_papallacta, precip_quijos, caudal_quijos
    except Exception as e:
        print(f"❌ Error cargando datos para correlación Precipitación-Caudal: {e}")
        return None, None, None, None

def prepare_precip_flow_data_for_api(precip_data, caudal_data, station_name):
    """Preparar datos alineados por fecha para una estación (Precipitación-Caudal)"""
    try:
        # --- Procesar Precipitación ---
        # Sumar todas las columnas de precipitación para obtener el total
        precip_cols = [col for col in precip_data.columns if col != 'Fecha']
        if precip_cols:
            precip_data['Precip_Total'] = precip_data[precip_cols].sum(axis=1, skipna=True)
        else:
            print(f"⚠️ No se encontraron columnas de precipitación específicas para {station_name}. Usando todas las numéricas.")
            numeric_precip_cols = precip_data.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_precip_cols:
                precip_data['Precip_Total'] = precip_data[numeric_precip_cols].sum(axis=1, skipna=True)
            else:
                raise ValueError(f"No hay datos numéricos de precipitación para {station_name}")

        # --- Procesar Caudal ---
        # Promediar todas las columnas de caudal
        caudal_cols = [col for col in caudal_data.columns if col != 'Fecha']
        if caudal_cols:
            caudal_data['Caudal_Prom'] = caudal_data[caudal_cols].mean(axis=1, skipna=True)
        else:
            print(f"⚠️ No se encontraron columnas de caudal específicas para {station_name}. Usando todas las numéricas.")
            numeric_caudal_cols = caudal_data.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_caudal_cols:
                caudal_data['Caudal_Prom'] = caudal_data[numeric_caudal_cols].mean(axis=1, skipna=True)
            else:
                raise ValueError(f"No hay datos numéricos de caudal para {station_name}")

        # --- Asegurar que la columna 'Fecha' sea datetime ---
        if 'Fecha' in precip_data.columns:
            precip_data['Fecha'] = pd.to_datetime(precip_data['Fecha'], errors='coerce')
        if 'Fecha' in caudal_data.columns:
            caudal_data['Fecha'] = pd.to_datetime(caudal_data['Fecha'], errors='coerce')

        # --- Eliminar filas con NaT en Fecha ---
        precip_data = precip_data.dropna(subset=['Fecha']).reset_index(drop=True)
        caudal_data = caudal_data.dropna(subset=['Fecha']).reset_index(drop=True)

        # --- Merge por fecha (inner join para fechas comunes) ---
        if 'Fecha' in precip_data.columns and 'Fecha' in caudal_data.columns:
            merged_data = pd.merge(
                precip_data[['Fecha', 'Precip_Total']],
                caudal_data[['Fecha', 'Caudal_Prom']],
                on='Fecha',
                how='inner'
            )
            # Ordenar por fecha
            merged_data = merged_data.sort_values('Fecha').reset_index(drop=True)
        else:
            # Si no hay fechas, alinear por índice (menos ideal)
            min_len = min(len(precip_data), len(caudal_data))
            merged_data = pd.DataFrame({
                'Precip_Total': precip_data['Precip_Total'].iloc[:min_len].reset_index(drop=True),
                'Caudal_Prom': caudal_data['Caudal_Prom'].iloc[:min_len].reset_index(drop=True)
            })

        # --- Eliminar filas con NaN en los valores calculados ---
        initial_len = len(merged_data)
        merged_data = merged_data.dropna(subset=['Precip_Total', 'Caudal_Prom']).reset_index(drop=True)
        final_len = len(merged_data)
        if initial_len != final_len:
            print(f"ℹ️ Filas eliminadas por NaN en {station_name}: {initial_len - final_len}")

        print(f"📊 Datos alineados y limpios (Precip-Caudal) para {station_name}: {len(merged_data)} registros")
        return merged_data

    except Exception as e:
        print(f"❌ Error preparando datos (Precip-Caudal) para {station_name}: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

def analyze_precip_flow_relationship_for_api(data):
    """Analizar relación precipitación-caudal y preparar datos para API"""
    if len(data) < 5:
        return {"error": "Insuficientes datos para análisis de Precipitación-Caudal"}

    precip = data['Precip_Total'].values
    caudal = data['Caudal_Prom'].values
    # fechas = data['Fecha'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist() if 'Fecha' in data.columns else None

    # Eliminar pares NaN/NaN
    mask = ~(np.isnan(precip) | np.isnan(caudal))
    precip_clean = precip[mask]
    caudal_clean = caudal[mask]

    if len(precip_clean) < 5:
        return {"error": "Insuficientes datos válidos para análisis después de limpieza"}

    try:
        # Correlaciones
        pearson_corr, pearson_p = stats.pearsonr(precip_clean, caudal_clean)
        spearman_corr, spearman_p = stats.spearmanr(precip_clean, caudal_clean)

        # Regresión Lineal
        linear_model = LinearRegression()
        linear_model.fit(precip_clean.reshape(-1, 1), caudal_clean)
        linear_r2 = r2_score(caudal_clean, linear_model.predict(precip_clean.reshape(-1, 1)))
        linear_rmse = np.sqrt(mean_squared_error(caudal_clean, linear_model.predict(precip_clean.reshape(-1, 1))))
        linear_equation = f"Caudal = {linear_model.coef_[0]:.4f} * Precip + {linear_model.intercept_:.2f}"

        # Crear puntos para la línea de regresión
        precip_sorted = np.sort(precip_clean)
        caudal_linear_pred = linear_model.predict(precip_sorted.reshape(-1, 1))

        # Preparar datos para Chart.js
        chartjs_data = {
            "datasets": [
                {
                    "label": "Datos Observados",
                    "data": [{"x": float(p), "y": float(c)} for p, c in zip(precip_clean, caudal_clean)],
                    "backgroundColor": "rgba(153, 102, 255, 0.6)", # Color púrpura
                    "borderColor": "rgba(153, 102, 255, 1)",
                    "borderWidth": 1,
                    "pointRadius": 3,
                    "showLine": False
                },
                {
                    "label": f"Regresión Lineal (R²={linear_r2:.3f})",
                    "data": [{"x": float(p), "y": float(c)} for p, c in zip(precip_sorted, caudal_linear_pred)],
                    "borderColor": "rgba(255, 159, 64, 1)", # Color naranja
                    "borderWidth": 2,
                    "fill": False,
                    "showLine": True,
                    "pointRadius": 0,
                    "borderDash": []
                }
            ]
        }

        # Preparar estadísticas
        stats_data = {
            "total_puntos": len(precip_clean),
            "correlacion_pearson": pearson_corr,
            "p_valor_pearson": pearson_p,
            "correlacion_spearman": spearman_corr,
            "p_valor_spearman": spearman_p,
            "regresion_lineal": {
                "r2": linear_r2,
                "rmse": linear_rmse,
                "ecuacion": linear_equation
            }
        }

        return {
            "success": True,
            "estadisticas": stats_data,
            "chartjs_data": chartjs_data
        }

    except Exception as e:
        print(f"⚠️ Error en análisis Precipitación-Caudal: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"Error al analizar relación Precipitación-Caudal: {str(e)}"}

# === Fin de Funciones para análisis de correlación Precipitación-Caudal ===
@app.route('/api/correlacion_precip_caudal/<estacion>')
def api_correlacion_precip_caudal(estacion):
    """API para datos de correlación precipitación-caudal"""
    estacion = estacion.lower()
    if estacion not in ['papallacta', 'quijos']:
        return jsonify({"error": "Estación no válida. Usa 'papallacta' o 'quijos'."}), 400

    try:
        # 1. Cargar datos
        precip_papallacta, caudal_papallacta, precip_quijos, caudal_quijos = load_precip_flow_data_for_api()
        if precip_papallacta is None or caudal_papallacta is None or \
           precip_quijos is None or caudal_quijos is None:
            return jsonify({"error": "Error al cargar los datos de precipitación o caudal."}), 500

        # 2. Seleccionar datos de la estación solicitada
        if estacion == 'papallacta':
            precip_data = precip_papallacta
            caudal_data = caudal_papallacta
            station_name = "Papallacta"
        else: # quijos
            precip_data = precip_quijos
            caudal_data = caudal_quijos
            station_name = "Quijos"

        # 3. Preparar datos (alinear por fecha)
        aligned_data = prepare_precip_flow_data_for_api(precip_data, caudal_data, station_name)
        if aligned_data.empty:
            return jsonify({"error": f"No se encontraron datos alineados para {station_name}."}), 404

        # 4. Analizar y preparar para API
        result = analyze_precip_flow_relationship_for_api(aligned_data)
        if "error" in result:
            return jsonify(result), 400

        # 5. Añadir nombre de la estación al resultado
        result["estacion"] = station_name
        return jsonify(result)

    except Exception as e:
        print(f"Error en /api/correlacion_precip_caudal/{estacion}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error interno del servidor al procesar {estacion}."}), 500


# Asegúrate de tener estos imports al principio de tu app.py
# import pandas as pd
# import numpy as np
# from datetime import datetime # Si necesitas fechas

# ... (resto de tu código) ...

@app.route('/api/contribucion_afluentes')
def api_contribucion_afluentes():
    """API para obtener datos de contribución de afluentes al caudal mínimo."""
    try:
        CAUDAL_MINIMO_ECOLOGICO = 127.0

        # 1. Cargar datos de caudal (reutiliza tu función existente)
        caudal_papallacta_df = safe_read_csv('caudal_papallacta.csv')
        caudal_quijos_df = safe_read_csv('caudal_quijos.csv')

        if caudal_papallacta_df.empty or caudal_quijos_df.empty:
            return jsonify({"error": "No se pudieron cargar los datos de caudal de una o ambas estaciones."}), 500

        # 2. Procesar datos: Alinear por fecha y calcular promedios diarios si es necesario
        # Asumimos que los DataFrames tienen una columna 'Fecha' y columnas numéricas de sensores.

        # --- Procesar Papallacta ---
        pap_cols = [col for col in caudal_papallacta_df.columns if col != 'Fecha']
        if not pap_cols:
            return jsonify({"error": "No se encontraron columnas de datos de caudal para Papallacta."}), 500
        # Asegurar que 'Fecha' sea datetime
        caudal_papallacta_df['Fecha'] = pd.to_datetime(caudal_papallacta_df['Fecha'], errors='coerce')
        caudal_papallacta_df = caudal_papallacta_df.dropna(subset=['Fecha'])
        # Calcular promedio de las estaciones de Papallacta por fecha
        caudal_papallacta_df['Caudal_Prom_Papallacta'] = caudal_papallacta_df[pap_cols].mean(axis=1, skipna=True)
        caudal_papallacta_df = caudal_papallacta_df[['Fecha', 'Caudal_Prom_Papallacta']].dropna(
            subset=['Caudal_Prom_Papallacta'])

        # --- Procesar Quijos ---
        qui_cols = [col for col in caudal_quijos_df.columns if col != 'Fecha']
        if not qui_cols:
            return jsonify({"error": "No se encontraron columnas de datos de caudal para Quijos."}), 500
        # Asegurar que 'Fecha' sea datetime
        caudal_quijos_df['Fecha'] = pd.to_datetime(caudal_quijos_df['Fecha'], errors='coerce')
        caudal_quijos_df = caudal_quijos_df.dropna(subset=['Fecha'])
        # Calcular promedio de las estaciones de Quijos por fecha
        caudal_quijos_df['Caudal_Prom_Quijos'] = caudal_quijos_df[qui_cols].mean(axis=1, skipna=True)
        caudal_quijos_df = caudal_quijos_df[['Fecha', 'Caudal_Prom_Quijos']].dropna(subset=['Caudal_Prom_Quijos'])

        # 3. Alinear datos por fecha (inner join para fechas comunes)
        df_combined = pd.merge(caudal_papallacta_df, caudal_quijos_df, on='Fecha', how='inner')
        if df_combined.empty:
            return jsonify(
                {"error": "No hay fechas comunes entre los datos de Papallacta y Quijos para comparar."}), 500

        # 4. Calcular caudal total de afluentes
        df_combined['Caudal_Total_Afluentes'] = df_combined['Caudal_Prom_Papallacta'] + df_combined[
            'Caudal_Prom_Quijos']

        # 5. Calcular estadísticas agregadas
        registros_totales = len(df_combined)
        if registros_totales == 0:
            return jsonify({"error": "No hay registros válidos después de alinear las fechas."}), 500

        caudal_prom_total = df_combined['Caudal_Total_Afluentes'].mean()
        caudal_prom_papallacta = df_combined['Caudal_Prom_Papallacta'].mean()
        caudal_prom_quijos = df_combined['Caudal_Prom_Quijos'].mean()

        # 6. Calcular porcentajes respecto al mínimo ecológico
        total_percentage = (caudal_prom_total / CAUDAL_MINIMO_ECOLOGICO) * 100
        pap_percentage = (caudal_prom_papallacta / CAUDAL_MINIMO_ECOLOGICO) * 100
        qui_percentage = (caudal_prom_quijos / CAUDAL_MINIMO_ECOLOGICO) * 100

        # 7. Calcular registros por debajo del mínimo
        registros_debajo = len(df_combined[df_combined['Caudal_Total_Afluentes'] < CAUDAL_MINIMO_ECOLOGICO])
        porcentaje_tiempo_debajo = (registros_debajo / registros_totales) * 100 if registros_totales > 0 else 0

        # 8. Determinar clasificación de importancia (basado en el script)
        if total_percentage >= 100:
            clasificacion = "🟢 CRÍTICOS - SUFICIENTES"
            descripcion = "Los afluentes PUEDEN cubrir el mínimo requerido"
        elif total_percentage >= 80:
            clasificacion = "🟡 MUY IMPORTANTES"
            descripcion = "Los afluentes cubren la mayoría del caudal mínimo"
        elif total_percentage >= 50:
            clasificacion = "🟠 IMPORTANTES"
            descripcion = "Los afluentes cubren la mitad del caudal mínimo"
        elif total_percentage >= 20:
            clasificacion = "🔵 MODERADA"
            descripcion = "Los afluentes tienen una contribución MODERADA"
        else:
            clasificacion = "ℹ️ LIMITADA"
            descripcion = "Los afluentes tienen importancia LIMITADA para la operación"

        # 9. Confiabilidad (ejemplo simple: porcentaje de datos válidos usados)
        # Asumiendo que safe_read_csv ya maneja errores básicos, la confiabilidad
        # se puede estimar como la proporción de registros alineados vs. el promedio de registros originales
        registros_orig_pap = len(caudal_papallacta_df)
        registros_orig_qui = len(caudal_quijos_df)
        registros_orig_promedio = (registros_orig_pap + registros_orig_qui) / 2
        confiabilidad_datos = (registros_totales / registros_orig_promedio) if registros_orig_promedio > 0 else 0
        confiabilidad_datos = min(confiabilidad_datos, 1.0)  # Asegurar que no supere 1.0

        # 10. Conclusión principal
        if total_percentage >= 100:
            conclusion = "Los afluentes analizados pueden ser suficientes para cubrir el caudal mínimo ecológico en algunos períodos."
        elif total_percentage >= 50:
            conclusion = "Los afluentes son importantes pero no suficientes por sí solos para garantizar el caudal mínimo ecológico en todo momento."
        else:
            conclusion = "La contribución de los afluentes es limitada respecto al caudal mínimo ecológico requerido."

        # 11. Preparar datos para Chart.js (ejemplo: gráfico de barras)
        # Puedes enviar los datos numéricos y dejar que el frontend decida cómo graficarlos.
        # Aquí enviamos los porcentajes para un gráfico de barras simple.
        chartjs_data_barras = {
            "labels": ["Papallacta", "Quijos", "Total Afluentes"],
            "datasets": [{
                "label": "Contribución al Caudal Mínimo (%)",
                "data": [round(pap_percentage, 1), round(qui_percentage, 1), round(total_percentage, 1)],
                "backgroundColor": [
                    "rgba(75, 192, 192, 0.6)",  # Verde azulado para Papallacta
                    "rgba(255, 99, 132, 0.6)",  # Rojo para Quijos
                    "rgba(54, 162, 235, 0.6)"  # Azul para Total
                ],
                "borderColor": [
                    "rgba(75, 192, 192, 1)",
                    "rgba(255, 99, 132, 1)",
                    "rgba(54, 162, 235, 1)"
                ],
                "borderWidth": 1
            }]
        }

        # 12. Devolver JSON con todos los resultados
        return jsonify({
            "success": True,
            "caudal_minimo_ecologico": CAUDAL_MINIMO_ECOLOGICO,
            "caudal_promedio_papallacta": round(caudal_prom_papallacta, 2),
            "caudal_promedio_quijos": round(caudal_prom_quijos, 2),
            "caudal_total_afluentes_promedio": round(caudal_prom_total, 2),
            "porcentaje_papallacta_del_minimo": round(pap_percentage, 1),
            "porcentaje_quijos_del_minimo": round(qui_percentage, 1),
            "porcentaje_total_del_minimo": round(total_percentage, 1),
            "registros_analizados": registros_totales,
            "registros_por_debajo_del_minimo": registros_debajo,
            "porcentaje_del_tiempo_por_debajo": round(porcentaje_tiempo_debajo, 1),
            "confiabilidad_datos": round(confiabilidad_datos, 2),
            "clasificacion_importancia": clasificacion,
            "descripcion_importancia": descripcion,
            "conclusion_principal": conclusion,
            "chartjs_data_barras": chartjs_data_barras  # Datos para Chart.js
        })

    except Exception as e:
        print(f"Error en /api/contribucion_afluentes: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(
            {"error": "Error interno del servidor al procesar la contribución de afluentes.", "details": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)