# Dashboard Hidrológico - Grupo 8

## Descripción
Dashboard profesional para visualización de datos hidrológicos del Río Quijos. La aplicación permite monitorear datos de precipitación, caudal y nivel de agua a través de una interfaz web elegante e interactiva.

## Características
- 📊 Dashboard interactivo con gráficos en tiempo real
- 🗺️ Mapa del río con trayectoria y puntos de monitoreo
- 📈 Visualización de datos de precipitación, caudal y nivel
- 📱 Interfaz responsive y moderna
- 🔄 Manejo robusto de datos faltantes
- 🎨 Diseño profesional con sidebar y navegación intuitiva

## Estructura del Proyecto
```
dashboard-hidrologico/
│
├── app.py                 # Aplicación Flask principal
├── requirements.txt       # Dependencias
├── README.md             # Este archivo
│
├── templates/
│   ├── base.html         # Plantilla base
│   └── index.html        # Página principal
│
├── precipitacion.csv     # Datos de precipitación
├── caudal.csv           # Datos de caudal
└── nivel.csv            # Datos de nivel
```

## Instalación

### 1. Crear el entorno del proyecto
```bash
# Crear directorio del proyecto
mkdir dashboard-hidrologico
cd dashboard-hidrologico

# Crear directorio templates
mkdir templates
```

### 2. Crear los archivos
Crea los siguientes archivos con el contenido proporcionado:
- `app.py`
- `requirements.txt`
- `templates/base.html`
- `templates/index.html`
- `precipitacion.csv`
- `caudal.csv`
- `nivel.csv`

### 3. Instalar dependencias
```bash
# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt.txt
```

### 4. Ejecutar la aplicación
```bash
python app.py
```

La aplicación estará disponible en: `http://localhost:5000`

## Uso

### Dashboard Principal
- Vista general con estadísticas de los sensores
- Mapa interactivo del Río Quijos
- Gráfico resumen de distribución de datos

### Navegación
- **Dashboard**: Vista principal con resumen
- **Precipitación**: Gráficos de datos de lluvia (sensores P42, P43, P55)
- **Caudal**: Visualización de caudal (sensores H44, H55)
- **Nivel**: Datos de nivel de agua (sensores H44, H55)
- **Mapa del Río**: Vista detallada del trayecto

### Características Técnicas
- **Manejo de errores**: La aplicación maneja archivos CSV faltantes o corruptos
- **Datos faltantes**: Rellena automáticamente valores NaN con ceros
- **Responsive**: Se adapta a diferentes tamaños de pantalla
- **Interactivo**: Gráficos con zoom, hover y leyendas
- **Actualización automática**: Los datos se actualizan cada 5 minutos

## Personalización

### Agregar más coordenadas del río
Edita la variable `RIO_QUIJOS_COORDS` en `app.py`:
```python
RIO_QUIJOS_COORDS = [
    [-0.562767, -78.182822],
    [-0.562689, -78.180687],
    # Agregar más coordenadas aquí...
]
```

### Modificar colores de los gráficos
Edita el diccionario `colors` en la función `process_data_for_charts()`:
```python
colors = {
    'P42': 'rgba(54, 162, 235, 0.8)',  # Azul
    'P43': 'rgba(255, 99, 132, 0.8)',  # Rojo
    # Agregar más colores...
}
```

### Cambiar el puerto de la aplicación
Modifica la última línea de `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Cambiar puerto
```

## APIs Disponibles

La aplicación expone las siguientes APIs REST:

- `GET /api/precipitacion` - Datos de precipitación
- `GET /api/caudal` - Datos de caudal
- `GET /api/nivel` - Datos de nivel
- `GET /api/rio-coords` - Coordenadas del río
- `GET /api/stats` - Estadísticas generales

## Solución de Problemas

### Error: Archivo CSV no encontrado
- Asegúrate de que los archivos CSV estén en el directorio raíz del proyecto
- Verifica que los nombres coincidan exactamente: `precipitacion.csv`, `caudal.csv`, `nivel.csv`

### Error: Módulo no encontrado
```bash
pip install -r requirements.txt.txt
```

### El mapa no se carga
- Verifica tu conexión a internet (requiere cargar mapas de OpenTopoMap)
- Revisa la consola del navegador para errores de JavaScript

### Gráficos no aparecen
- Asegúrate de que los archivos CSV tienen el formato correcto
- Revisa que las fechas estén en formato YYYY-MM-DD

## Tecnologías Utilizadas

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Gráficos**: Chart.js
- **Mapas**: Leaflet.js con OpenTopoMap
- **Estilos**: Bootstrap 5 + CSS personalizado
- **Iconos**: Font Awesome

## Autor
Grupo 8 - Dashboard Hidrológico

## Licencia
Este proyecto es para uso académico.