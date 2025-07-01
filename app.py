from flask import Flask, render_template, jsonify
import pandas as pd
import json
import os
from datetime import datetime
import numpy as np

app = Flask(__name__)

# Configuración de la aplicación
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'

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

        stats = {
            'total_registros': {
                'precipitacion': len(precipitacion_df) if not precipitacion_df.empty else 0,
                'caudal': len(caudal_df) if not caudal_df.empty else 0,
                'nivel': len(nivel_df) if not nivel_df.empty else 0
            },
            'sensores_activos': {
                'precipitacion': len(
                    [col for col in precipitacion_df.columns if col != 'Fecha']) if not precipitacion_df.empty else 0,
                'caudal': len([col for col in caudal_df.columns if col != 'Fecha']) if not caudal_df.empty else 0,
                'nivel': len([col for col in nivel_df.columns if col != 'Fecha']) if not nivel_df.empty else 0
            }
        }

        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)