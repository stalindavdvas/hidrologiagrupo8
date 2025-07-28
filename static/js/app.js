  // Variables globales
        let map;
        let currentSlide = 0;
        const slides = document.querySelectorAll('.carousel-slide');
        const dots = document.querySelectorAll('.carousel-dot');

        // Función del carrusel
        function showSlide(index) {
            slides.forEach((slide, i) => {
                slide.classList.toggle('active', i === index);
            });
            dots.forEach((dot, i) => {
                dot.classList.toggle('active', i === index);
            });
        }

        function nextSlide() {
            currentSlide = (currentSlide + 1) % slides.length;
            showSlide(currentSlide);
        }

        // Auto-advance carousel cada 6 segundos
        setInterval(nextSlide, 6000);

        // Dot click handlers
        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => {
                currentSlide = index;
                showSlide(currentSlide);
            });
        });

        // Initialize main map
        function initializeMap() {
            map = L.map('map').setView([-0.562767, -78.182822], 11);

            // Add terrain layer
            L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenTopoMap contributors',
                maxZoom: 17
            }).addTo(map);

            const iconoPluvio = L.icon({
                iconUrl: '/static/img/pluvi.png', // Ícono para sensores pluviométricos
                iconSize: [32, 32],
                iconAnchor: [16, 32],
                popupAnchor: [0, -28]
            });

            const iconoHidro = L.icon({
                iconUrl: '/static/img/hidro.png', // Ícono para sensores hidrométricos
                iconSize: [32, 32],
                iconAnchor: [16, 32],
                popupAnchor: [0, -28]
            });

            // Coordenadas del sensor
            const sensores = [
                {
                    codigo: "P42",
                    nombre: "Antisana Ramón Huañuna",
                    tipo: "Pluviométrica",
                    lat: -0.6022867145410288,
                    lng: -78.1986689291808
                },
                {
                    codigo: "P43",
                    nombre: "Antisana Limboasi",
                    tipo: "Pluviométrica",
                    lat: -0.5934839659614135,
                    lng: -78.20825370752031
                },
                {
                    codigo: "P55",
                    nombre: "Antisana Diguchi",
                    tipo: "Pluviométrica",
                    lat: -0.5731364867736277,
                    lng: -78.262844542214
                },
                {
                    codigo: "P34",
                    nombre: "Papallacta",
                    tipo: "Pluviométrica",
                    lat: -0.3809496476812419,
                    lng: -78.1411372167858
                },
                {
                    codigo: "P63",
                    nombre: "La Virgen Papallacta",
                    tipo: "Pluviométrica",
                    lat: -0.32058993015514037,
                    lng: -78.19171352782969
                },
                {
                    codigo: "M5023",
                    nombre: "Papallacta",
                    tipo: "Pluviométrica",
                    lat: -0.3784621293075407,
                    lng: -78.14090447228763
                },
                {
                    codigo: "H44",
                    nombre: "Antisana DJ Diguchi",
                    tipo: "Hidrométrica",
                    lat: -0.5683880379564397,
                    lng: -78.2298390801277
                },
                {
                    codigo: "H55",
                    nombre: "Río Antisana AC",
                    tipo: "Hidrométrica",
                    lat: -0.5367672976823137,
                    lng: -78.22695270391573
                }
            ];

            // Añadir marcador con ícono
            sensores.forEach(sensor => {
                const icono = sensor.tipo.toLowerCase().includes('hidro') ? iconoHidro : iconoPluvio;

                L.marker([sensor.lat, sensor.lng], { icon: icono })
                    .bindPopup(`<b>${sensor.nombre}</b><br>Código: ${sensor.codigo}<br>Tipo: ${sensor.tipo}`)
                    .addTo(map);
            });

            // Load river coordinates
            fetch('/api/rio-coords')
            .then(response => response.json())
            .then(data => {
                if (data.rio_quijos) {
                    const riverPath = L.polyline(data.rio_quijos, {
                        color: '#3498db',
                        weight: 4,
                        opacity: 0.8
                    }).addTo(map);

                    L.marker(data.rio_quijos[0])
                        .bindPopup('<b>Inicio Río Quijos</b><br>' + data.rio_quijos[0].join(', '))
                        .addTo(map);

                    L.marker(data.rio_quijos[data.rio_quijos.length - 1])
                        .bindPopup('<b>Fin del Río Quijos, union con el rio Coca- Hidroeléctrica Coca Codo Sinclair' +
                            '</b><br>' + data.rio_quijos[data.rio_quijos.length - 1].join(', '))
                        .addTo(map);

                    map.fitBounds(riverPath.getBounds(), {padding: [20, 20]});
                }

                if (data.rio_papallacta) {
                    const papallactaPath = L.polyline(data.rio_papallacta, {
                        color: '#2ecc71',
                        weight: 4,
                        opacity: 0.8
                    }).addTo(map);

                    L.marker(data.rio_papallacta[0])
                        .bindPopup('<b>Inicio Río Papallacta</b><br>' + data.rio_papallacta[0].join(', '))
                        .addTo(map);

                    L.marker(data.rio_papallacta[data.rio_papallacta.length - 1])
                        .bindPopup('<b>Fin del Río Papallacta</b><br>' + data.rio_papallacta[data.rio_papallacta.length - 1].join(', '))
                        .addTo(map);
                }
            })
            .catch(error => {
                console.log('No se pudieron cargar las coordenadas de los ríos:', error);
                // El mapa funcionará sin los ríos si la API no está disponible
            });
        }

        // Smooth scrolling para navegación
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Header background on scroll
        window.addEventListener('scroll', () => {
            const header = document.querySelector('.header');
            if (window.scrollY > 100) {
                header.style.background = 'rgba(10, 14, 26, 0.95)';
            } else {
                header.style.background = 'rgba(10, 14, 26, 0.85)';
            }
        });

        // Crear partículas flotantes
        function createParticle() {
            const particle = document.createElement('div');
            particle.className = 'particle';

            // Tamaño aleatorio
            const size = Math.random() * 4 + 2;
            particle.style.width = size + 'px';
            particle.style.height = size + 'px';

            particle.style.left = Math.random() * 100 + 'vw';
            particle.style.animationDelay = Math.random() * 12 + 's';
            particle.style.animationDuration = (Math.random() * 6 + 8) + 's';

            document.body.appendChild(particle);

            setTimeout(() => {
                if (particle.parentNode) {
                    particle.remove();
                }
            }, 12000);
        }

        // Crear partículas periódicamente
        setInterval(createParticle, 500);

        // Intersection Observer para animaciones
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animation = 'slideInUp 1s ease-out forwards';
                    entry.target.style.opacity = '1';
                }
            });
        }, observerOptions);

        // Observar elementos para animaciones
        document.addEventListener('DOMContentLoaded', () => {
            document.querySelectorAll('.chart-card, .feature-card, .info-card').forEach(card => {
                card.style.opacity = '0';
                observer.observe(card);
            });

            // Inicializar mapa cuando el DOM esté listo
            setTimeout(() => {
                try {
                    initializeMap();
                } catch (error) {
                    console.log('Error inicializando el mapa:', error);
                }
            }, 1000);
        });

        // Agregar animación slideInUp
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideInUp {
                from {
                    opacity: 0;
                    transform: translateY(40px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        `;
        document.head.appendChild(style);

let precipitacionQuijosChart, caudalQuijosChart, nivelQuijosChart, summaryChart;
let precipitacionPapallactaChart, caudalPapallactaChart, nivelPapallactaChart;

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadStats();
    loadCharts();
});

// Load statistics
function loadStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            if (data.total_registros) {
                const totalRegistros = Object.values(data.total_registros).reduce((a, b) => a + b, 0);
                document.getElementById('total-registros').textContent = totalRegistros;

                const totalSensores = Object.values(data.sensores_activos).reduce((a, b) => a + b, 0);
                document.getElementById('sensores-activos').textContent = totalSensores;
            }
        })
        .catch(error => console.error('Error loading stats:', error));
}

// Load all charts
function loadCharts() {
    loadPrecipitacionQuijosChart();
    loadPrecipitacionPapallactaChart();
    loadCaudalQuijosChart();
    loadCaudalPapallactaChart();
    loadNivelQuijosChart();
    loadNivelPapallactaChart();
    loadSummaryChart();
}

// Load precipitación chart
function loadPrecipitacionQuijosChart() {
    fetch('/api/precipitacion')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('precipitacionQuijosChart').getContext('2d');

            if (precipitacionQuijosChart) {
                precipitacionQuijosChart.destroy();
            }

            precipitacionQuijosChart = new Chart(ctx, {
                type: 'line',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Precipitación por Sensor Quijos'
                        },
                        legend: {
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Precipitación (mm)'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Fecha'
                            }
                        }
                    },
                    interaction: {
                        intersect: false,
                        mode: 'index'
                    }
                }
            });
            window.precipitacionChart = precipitacionQuijosChart;
        })
        .catch(error => {
            console.error('Error loading precipitación Quijos data:', error);
            showNoDataMessage('precipitacionQuijosChart');
        });
}

// Load caudal chart
function loadCaudalQuijosChart() {
    fetch('/api/caudal')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('caudalQuijosChart').getContext('2d');

            if (caudalQuijosChart) {
                caudalQuijosChart.destroy();
            }

            caudalQuijosChart = new Chart(ctx, {
                type: 'line',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Caudal por Sensor'
                        },
                        legend: {
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Caudal (m³/s)'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Fecha'
                            }
                        }
                    },
                    interaction: {
                        intersect: false,
                        mode: 'index'
                    }
                }
            });
            window.caudalChart = caudalQuijosChart;
        })
        .catch(error => {
            console.error('Error loading caudal Quijos data:', error);
            showNoDataMessage('caudalChart');
        });
}

// Load nivel chart
function loadNivelQuijosChart() {
    fetch('/api/nivel')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('nivelQuijosChart').getContext('2d');

            if (nivelQuijosChart) {
                nivelQuijosChart.destroy();
            }

            nivelQuijosChart = new Chart(ctx, {
                type: 'line',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Nivel por Sensor'
                        },
                        legend: {
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Nivel (m)'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Fecha'
                            }
                        }
                    },
                    interaction: {
                        intersect: false,
                        mode: 'index'
                    }
                }
            });
            window.nivelChart = nivelQuijosChart;
        })
        .catch(error => {
            console.error('Error loading nivel Quijos data:', error);
            showNoDataMessage('nivelQuijosChart');
        });
}

function loadPrecipitacionPapallactaChart() {
    fetch('/api/precipitacion_papallacta')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('precipitacionPapallactaChart').getContext('2d');

            if (precipitacionPapallactaChart) {
                precipitacionPapallactaChart.destroy();
            }

            precipitacionPapallactaChart = new Chart(ctx, {
                type: 'line',
                data: data,
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Precipitación Papallacta por Sensor'
                        },
                        legend: { position: 'top' }
                    },
                    interaction: { intersect: false, mode: 'index' },
                    scales: {
                        x: { title: { display: true, text: 'Fecha' }},
                        y: { title: { display: true, text: 'Precipitación (mm)' }, beginAtZero: true }
                    }
                }
            });
             window.precipitacionPapallactaChart = precipitacionPapallactaChart;
        });
}

function loadCaudalPapallactaChart() {
    fetch('/api/caudal_papallacta')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('caudalPapallactaChart').getContext('2d');

            if (caudalPapallactaChart) {
                caudalPapallactaChart.destroy();
            }

            caudalPapallactaChart = new Chart(ctx, {
                type: 'line',
                data: data,
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Caudal Papallacta por Sensor'
                        },
                        legend: { position: 'top' }
                    },
                    interaction: { intersect: false, mode: 'index' },
                    scales: {
                        x: { title: { display: true, text: 'Fecha' }},
                        y: { title: { display: true, text: 'Caudal (m³/s)' }, beginAtZero: true }
                    }
                }
            });
             window.caudalPapallactaChart = caudalPapallactaChart;
        });
}

function loadNivelPapallactaChart() {
    fetch('/api/nivel_papallacta')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('nivelPapallactaChart').getContext('2d');

            if (nivelPapallactaChart) {
                nivelPapallactaChart.destroy();
            }

            nivelPapallactaChart = new Chart(ctx, {
                type: 'line',
                data: data,
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Nivel Papallacta por Sensor'
                        },
                        legend: { position: 'top' }
                    },
                    interaction: { intersect: false, mode: 'index' },
                    scales: {
                        x: { title: { display: true, text: 'Fecha' }},
                        y: { title: { display: true, text: 'Nivel (m)' }, beginAtZero: true }
                    }
                }
            });
            window.nivelPapallactaChart = nivelPapallactaChart;
        });
}

// Load summary chart
function loadSummaryChart() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('summaryChart').getContext('2d');

            if (summaryChart) {
                summaryChart.destroy();
            }

            const labels = ['Precipitación', 'Caudal', 'Nivel'];
            const registros = [
                data.total_registros?.precipitacion || 0,
                data.total_registros?.caudal || 0,
                data.total_registros?.nivel || 0
            ];

            summaryChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: registros,
                        backgroundColor: [
                            'rgba(54, 162, 235, 0.8)',
                            'rgba(255, 99, 132, 0.8)',
                            'rgba(75, 192, 192, 0.8)'
                        ],
                        borderColor: [
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 99, 132, 1)',
                            'rgba(75, 192, 192, 1)'
                        ],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Distribución de Registros'
                        },
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error loading summary data:', error);
        });
}

// Show no data message
function showNoDataMessage(canvasId) {
    const canvas = document.getElementById(canvasId);
    const ctx = canvas.getContext('2d');

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.font = '16px Arial';
    ctx.fillStyle = '#6c757d';
    ctx.textAlign = 'center';
    ctx.fillText('No hay datos disponibles', canvas.width / 2, canvas.height / 2);
}

// Resize maps when sections change
function showSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.style.display = 'none';
    });

    // Show selected section
    const targetSection = document.getElementById(sectionName + '-section');
    if (targetSection) {
        targetSection.style.display = 'block';

        // Resize maps if needed
        setTimeout(() => {
            if (sectionName === 'dashboard' && map) {
                map.invalidateSize();
            } else if (sectionName === 'mapa' && detailedMap) {
                detailedMap.invalidateSize();
            }
        }, 100);
    }
}

// Refresh data function
function refreshData() {
    loadStats();
    loadCharts();
}

// Auto refresh every 5 minutes
setInterval(refreshData, 300000);

// --- Añade este código JavaScript al final del bloque extra_js ---
console.log("Inicializando funcionalidad del Chatbot IA...");

// Variable para almacenar la referencia al gráfico actualmente en análisis
let graficoEnAnalisis = null;
let seccionEnAnalisis = null;

// Función para obtener los datos del gráfico de Chart.js
function obtenerDatosGrafico(nombreGrafico) {
    // Accede a la variable global del gráfico (definida en tu JS existente)
    let chartInstance = window[nombreGrafico];
    if (chartInstance && chartInstance.data) {
        // Devolvemos una copia serializable de los datos
        return {
            labels: chartInstance.data.labels,
            datasets: chartInstance.data.datasets.map(ds => ({
                label: ds.label,
                data: ds.data
                // Puedes añadir más propiedades si son relevantes para el análisis
            }))
        };
    } else {
        console.error(`No se encontró el gráfico con nombre: ${nombreGrafico}`);
        return null;
    }
}

// Función para mostrar mensajes en el modal del chat
function mostrarMensajeEnChat(mensaje, tipo='info') {
    const chatMessages = document.getElementById('chat-messages');
    const alertClass = tipo === 'error' ? 'alert-danger' : tipo === 'success' ? 'alert-success' : 'alert-info';
    const iconClass = tipo === 'error' ? 'fa-exclamation-triangle' : tipo === 'success' ? 'fa-check-circle' : 'fa-info-circle';

    const mensajeElemento = document.createElement('div');
    mensajeElemento.className = `alert ${alertClass} alert-dismissible fade show`;
    mensajeElemento.role = 'alert';
    mensajeElemento.innerHTML = `
        <i class="fas ${iconClass} me-2"></i>
        ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    chatMessages.appendChild(mensajeElemento);
    // Hacer scroll hacia abajo
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Función para solicitar análisis al backend
async function solicitarAnalisis(nombreGrafico, seccion) {
    console.log(`Solicitando análisis para el gráfico: ${nombreGrafico} en la sección: ${seccion}`);

    const datos = obtenerDatosGrafico(nombreGrafico);
    if (!datos) {
        mostrarMensajeEnChat('No se pudieron obtener los datos del gráfico seleccionado.', 'error');
        return;
    }

    // Guardar referencia para posibles interacciones futuras
    graficoEnAnalisis = nombreGrafico;
    seccionEnAnalisis = seccion;

    // Mostrar modal
    const chatModal = new bootstrap.Modal(document.getElementById('chatbotModal'));
    const chatMessages = document.getElementById('chat-messages');

    // Limpiar mensajes anteriores y mostrar mensaje de carga
    chatMessages.innerHTML = '';
    mostrarMensajeEnChat('Enviando datos al asistente IA... <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>', 'info');

    chatModal.show();

    try {
        const response = await fetch('/api/analizar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                grafico_id: nombreGrafico,
                seccion: seccion,
                datos: datos
                // contexto: "" // Se puede añadir un input para que el usuario dé contexto
            })
        });

        if (!response.ok) {
            // Manejar errores HTTP
            let errorMsg = 'Error desconocido al comunicarse con el servidor.';
            if (response.status === 503) {
                 errorMsg = 'El servicio de análisis IA no está disponible. ¿Se configuró correctamente la clave API?';
            } else if (response.status === 400) {
                errorMsg = 'Datos enviados al servidor incompletos o inválidos.';
            } else {
                errorMsg = `Error del servidor: ${response.status} - ${response.statusText}`;
            }
            throw new Error(errorMsg);
        }

        const data = await response.json();

        if (data.error) {
            // Manejar errores devueltos por el backend
            throw new Error(data.error);
        }

        if (data.analisis) {
            // Mostrar la respuesta exitosa en el chat
            mostrarMensajeEnChat(`<strong>Análisis para ${nombreGrafico}:</strong><br>${data.analisis.replace(/\n/g, '<br>')}`, 'success');
            // Opcional: Mostrar el input para más preguntas
            // document.getElementById('chat-input-group').classList.remove('d-none');
        } else {
             mostrarMensajeEnChat('El servidor respondió, pero no se recibió un análisis.', 'error');
        }


    } catch (error) {
        console.error('Error al solicitar análisis:', error);
        mostrarMensajeEnChat(`Error: ${error.message}`, 'error');
        // Opcional: Ocultar el input si hay error
        // document.getElementById('chat-input-group').classList.add('d-none');
    }
}

// Añadir event listeners a los botones de análisis
document.addEventListener('DOMContentLoaded', function() {
    // Seleccionar todos los botones con la clase 'btn-analizar-ia'
    document.querySelectorAll('.btn-analizar-ia').forEach(boton => {
        boton.addEventListener('click', function() {
            // Obtener los atributos data del botón
            const graficoId = this.getAttribute('data-grafico-id');
            const seccion = this.getAttribute('data-seccion');
            if (graficoId && seccion) {
                solicitarAnalisis(graficoId, seccion);
            } else {
                console.error('Botón de análisis sin atributos data-grafico-id o data-seccion válidos.');
                alert('Error: No se pudo identificar el gráfico para el análisis.');
            }
        });
    });

    // Opcional: Lógica para el input de chat (enviar mensaje al presionar Enter o clic en enviar)
    const chatInput = document.getElementById('chat-input');
    const chatSendBtn = document.getElementById('chat-send-btn');

    if (chatInput && chatSendBtn) {
        const enviarMensaje = () => {
             const mensaje = chatInput.value.trim();
             if (mensaje) {
                 mostrarMensajeEnChat(`<strong>Tú:</strong> ${mensaje}`, 'info');
                 chatInput.value = '';
                 // Aquí iría la lógica para enviar el mensaje a Gemini y obtener una respuesta
                 // Por ahora, simulamos una respuesta
                 setTimeout(() => {
                     mostrarMensajeEnChat(`<strong>IA:</strong> Entendido. Esta funcionalidad de conversación continua está en desarrollo.`, 'success');
                 }, 1000);
             }
        };

        chatSendBtn.addEventListener('click', enviarMensaje);
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                enviarMensaje();
            }
        });
    }
});

console.log("Funcionalidad del Chatbot IA inicializada.");

   // --- Funciones para el Modal Personalizado del Chatbot ---
  // Añadir event listeners a los botones de análisis Y configurar el modal
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM completamente cargado. Configurando modal y botones de IA.");

    // --- 1. Configurar el Modal Personalizado ---
    setupModalCloseHandlers(); // <-- ESTA ES LA LÍNEA QUE FALTABA
     setupModalGraficoGrandeHandlers(); // Configura cómo se cierra el modal de gráfico grande
        setupBotonesVerGrande(); // Configura los botones para abrir el modal
        setupBotonAnalizarIAModal(); // Configura el botón de análisis del modal de gráfico grande
    console.log("Manejadores del modal personalizado configurados.");

    // --- 2. Configurar botones de análisis (asegurarse de usar la clase correcta) ---
    // Asegúrate de que los botones en tu HTML usen class="btn-analizar-ia-custom"
    // o cambia el selector aquí a la clase que uses.
    const botonesAnalisis = document.querySelectorAll('.btn-analizar-ia-custom'); // <-- Clase correcta
    console.log(`Encontrados ${botonesAnalisis.length} botones de análisis.`);

    botonesAnalisis.forEach(boton => {
        boton.addEventListener('click', function() {
            console.log("Botón de análisis clickeado.");
            // Obtener los atributos data del botón
            const graficoId = this.getAttribute('data-grafico-id');
            const seccion = this.getAttribute('data-seccion'); // Esto sigue siendo válido
            console.log(`Datos extraídos del botón: graficoId=${graficoId}, seccion=${seccion}`);

            if (graficoId && seccion) {
                solicitarAnalisis(graficoId, seccion); // Esta función ahora usa el modal personalizado
            } else {
                console.error('Botón de análisis sin atributos data-grafico-id o data-seccion válidos.');
                // Opcional: mostrar mensaje de error al usuario
                alert('Error: No se pudo identificar el gráfico para el análisis.');
            }
        });
    });

    // --- 3. Inicializar mapa, estadísticas y gráficos ---
    // Mueve estas llamadas aquí si aún no se llaman en otro lugar del DOMContentLoaded
    try {
        // initializeMap(); // Ya se llama dentro del otro DOMContentLoaded, pero puedes moverla aquí si es más claro
        refreshData(); // Esto llama a loadStats() y loadCharts()
        console.log("Datos iniciales cargados.");
    } catch (error) {
        console.error("Error al cargar datos iniciales:", error);
    }

    // --- 4. Opcional: Lógica para el input de chat (si decides implementarlo) ---
    // (Este código ya estaba, asegúrate de que los IDs sean correctos si usas el modal personalizado)
    const chatInput = document.getElementById('chat-input');
    const chatSendBtn = document.getElementById('chat-send-btn');
    if (chatInput && chatSendBtn) {
        const enviarMensaje = () => {
             const mensaje = chatInput.value.trim();
             if (mensaje) {
                 mostrarMensajeEnChat(`<strong>Tú:</strong> ${mensaje}`, 'info');
                 chatInput.value = '';
                 // Aquí iría la lógica para enviar el mensaje a Gemini y obtener una respuesta
                 // Por ahora, simulamos una respuesta
                 setTimeout(() => {
                     mostrarMensajeEnChat(`<strong>IA:</strong> Entendido. Esta funcionalidad de conversación continua está en desarrollo.`, 'success');
                 }, 1000);
             }
        };
        chatSendBtn.addEventListener('click', enviarMensaje);
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                enviarMensaje();
            }
        });
    }
    console.log("Configuración del DOM completada.");
});

        // Función para mostrar/ocultar el modal
        function toggleCustomModal(show = true) {
            const modal = document.getElementById('customChatbotModal');
            if (show) {
                modal.classList.add('active');
                modal.style.display = 'flex'; // Asegura que se muestre como flex
            } else {
                modal.classList.remove('active');
                // Espera a que termine la transición antes de ocultarlo completamente
                setTimeout(() => {
                    if (!modal.classList.contains('active')) {
                        modal.style.display = 'none';
                    }
                }, 300); // Coincide con la duración de la transición CSS
            }
        }

        // Función para cerrar el modal al hacer clic en el botón de cierre o fuera del contenido
        function setupModalCloseHandlers() {
            const modal = document.getElementById('customChatbotModal');
            const closeBtn = document.getElementById('closeModalBtn');
            const closeFooterBtn = document.getElementById('closeModalFooterBtn'); // Nuevo botón

            const closeModal = () => toggleCustomModal(false);

            if (closeBtn) {
                closeBtn.addEventListener('click', closeModal);
            }
            if (closeFooterBtn) {
                closeFooterBtn.addEventListener('click', closeModal);
            }

            // Opcional: Cerrar al hacer clic fuera del contenido del modal
            modal?.addEventListener('click', (e) => {
                if (e.target === modal) {
                    closeModal();
                }
            });
        }

            // Función para configurar el event listener del botón de análisis IA dentro del modal de gráfico grande
        function setupBotonAnalizarIAModal() {
            const btnAnalizarModal = document.getElementById('btnAnalizarIAModal');
            if (btnAnalizarModal) {
             // Importante: Eliminar cualquier listener previo para evitar duplicados
                btnAnalizarModal.replaceWith(btnAnalizarModal.cloneNode(true));
                const nuevoBtn = document.getElementById('btnAnalizarIAModal');

                nuevoBtn.addEventListener('click', function() {
                    // OPCIÓN 1: Usar atributos data almacenados previamente
                    // (Este método es más robusto si el botón se reutiliza)
                    const graficoId = this.getAttribute('data-grafico-id');
                    const seccion = this.getAttribute('data-seccion');

                    // OPCIÓN 2: Usar la variable global (alternativa)
                    // const graficoId = graficoGrandeActualId;
                    // const seccion = mapeoGraficoSeccion[graficoId];

                    if (graficoId && seccion) {
                        console.log(`Iniciando análisis desde modal grande para: ${graficoId}, seccion: ${seccion}`);
                        // Llamar a la función de análisis existente
                        solicitarAnalisis(graficoId, seccion);

                        // Opcional: Cerrar el modal de gráfico grande al iniciar el análisis
                        // cerrarModalGraficoGrande();

                    } else {
                        console.error('Botón "Analizar con IA" del modal sin atributos válidos o variable global no definida.');
                        // Usa el modal personalizado o uno de alerta simple
                        if (typeof toggleCustomModal !== 'undefined') {
                            mostrarMensajeEnChat('Error: No se pudo identificar el gráfico para el análisis desde el modal grande.', 'error');
                            toggleCustomModal(true); // Asegurarse de que el modal de chat esté visible para el mensaje
                        } else {
                             alert('Error: No se pudo identificar el gráfico para el análisis.');
                        }
                    }
                });
            } else {
                 console.warn('Botón "Analizar con IA" del modal de gráfico grande no encontrado en el DOM.');
            }
        }

        // Función modificada para mostrar mensajes en el modal personalizado
        function mostrarMensajeEnChat(mensaje, tipo = 'info') {
            const chatMessages = document.getElementById('chat-messages');
            if (!chatMessages) {
                console.error("Elemento #chat-messages no encontrado para el modal personalizado.");
                return;
            }

            // Usar clases personalizadas en lugar de las de Bootstrap
            const alertClass = tipo === 'error' ? 'custom-alert-danger' :
                               tipo === 'success' ? 'custom-alert-success' :
                                                    'custom-alert-info';

            const iconHTML = tipo === 'error' ? '⚠️' :
                             tipo === 'success' ? '✅' :
                                                  'ℹ️'; // Icono simple basado en texto

            const mensajeElemento = document.createElement('div');
            mensajeElemento.className = `custom-alert ${alertClass}`;
            mensajeElemento.innerHTML = `
                <span>${iconHTML}</span>
                ${mensaje}
                <!-- Botón de cierre simple (opcional, sin funcionalidad js aquí) -->
                <span style="float: right; cursor: pointer;" onclick="this.parentElement.remove();">&times;</span>
            `;
            chatMessages.appendChild(mensajeElemento);
            // Hacer scroll hacia abajo
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        // Función modificada para solicitar análisis y mostrar el modal personalizado
        async function solicitarAnalisis(nombreGrafico, seccion) {
            console.log(`Solicitando análisis para el gráfico: ${nombreGrafico} en la sección: ${seccion}`);
            const datos = obtenerDatosGrafico(nombreGrafico);
            if (!datos) {
                mostrarMensajeEnChat('No se pudieron obtener los datos del gráfico seleccionado.', 'error');
                return;
            }

            graficoEnAnalisis = nombreGrafico;
            seccionEnAnalisis = seccion;

            // --- Mostrar el modal personalizado ---
            const chatMessages = document.getElementById('chat-messages');
            if (chatMessages) {
                // Limpiar mensajes anteriores (excepto el de bienvenida si es la primera vez, o simplemente limpiar todo)
                // Para este ejemplo, limpiamos todo y mostramos el mensaje de carga.
                chatMessages.innerHTML = ''; // O puedes mantener el mensaje de bienvenida si lo prefieres
            }
            mostrarMensajeEnChat('Enviando datos al asistente IA... <span class="spinner-border" role="status" aria-hidden="true"></span>', 'info');
            toggleCustomModal(true); // Mostrar el modal

            try {
                const response = await fetch('/api/analizar', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        grafico_id: nombreGrafico,
                        seccion: seccion,
                        datos: datos
                    })
                });

                if (!response.ok) {
                    let errorMsg = 'Error desconocido al comunicarse con el servidor.';
                    if (response.status === 503) {
                        errorMsg = 'El servicio de análisis IA no está disponible. ¿Se configuró correctamente la clave API?';
                    } else if (response.status === 400) {
                        errorMsg = 'Datos enviados al servidor incompletos o inválidos.';
                    } else {
                        errorMsg = `Error del servidor: ${response.status} - ${response.statusText}`;
                    }
                    throw new Error(errorMsg);
                }

                const data = await response.json();
                if (data.error) {
                    throw new Error(data.error);
                }

                if (data.analisis) {
                    mostrarMensajeEnChat(`<strong>Análisis para ${nombreGrafico}:</strong><br>${data.analisis.replace(/\n/g, '<br>')}`, 'success');
                    // Opcional: Mostrar el input para más preguntas si el análisis fue exitoso
                    // document.getElementById('chat-input-group').style.display = 'flex';
                } else {
                    mostrarMensajeEnChat('El servidor respondió, pero no se recibió un análisis.', 'error');
                }
            } catch (error) {
                console.error('Error al solicitar análisis:', error);
                mostrarMensajeEnChat(`Error: ${error.message}`, 'error');
                // Opcional: Ocultar el input si hay error
                // document.getElementById('chat-input-group').style.display = 'none';
            }
        }

        // --- Fin de Funciones para el Modal Personalizado del Chatbot ---
          // --- Funciones para el Modal de Gráfico Grande ---
   // --- Variables globales adicionales para el modal de gráfico grande ---
        let graficoGrandeActualId = null; // Variable para almacenar el ID del gráfico actual
        // Mapeo de ID de canvas a data-seccion (debe coincidir con tus botones originales)
        // Asegúrate de que estos valores sean correctos según tu HTML original
        const mapeoGraficoSeccion = {
            'precipitacionChart': 'precipitacion',
            'precipitacionPapallactaChart': 'precipitacion_papallacta',
            'caudalChart': 'caudal',
            'caudalPapallactaChart': 'caudal_papallacta',
            'nivelChart': 'nivel',
            'nivelPapallactaChart': 'nivel_papallacta'
            // Añade más mapeos si tienes otros gráficos
        };
        // --- Fin de Variables globales adicionales ---

        let graficoGrandeInstance = null; // Variable para almacenar la instancia del gráfico grande

        // Función para mostrar/ocultar el modal de gráfico grande
        function toggleModalGraficoGrande(show = true) {
            const modal = document.getElementById('graficoGrandeModal');
            if (show) {
                modal.classList.add('active');
                modal.style.display = 'flex';
            } else {
                modal.classList.remove('active');
                setTimeout(() => {
                    if (!modal.classList.contains('active')) {
                        modal.style.display = 'none';
                    }
                }, 300);
            }
        }

        // Función para cerrar el modal de gráfico grande
        function cerrarModalGraficoGrande() {
            toggleModalGraficoGrande(false);
            // Destruir la instancia del gráfico grande al cerrar para liberar memoria
            if (graficoGrandeInstance) {
                graficoGrandeInstance.destroy();
                graficoGrandeInstance = null;
            }
        }

        // Función para configurar los manejadores de cierre del modal
        function setupModalGraficoGrandeHandlers() {
            const modal = document.getElementById('graficoGrandeModal');
            const cerrarBtn = document.getElementById('cerrarModalGrafico');
            const cerrarFooterBtn = document.getElementById('cerrarModalGraficoFooter');

            const cerrar = () => cerrarModalGraficoGrande();

            if (cerrarBtn) cerrarBtn.addEventListener('click', cerrar);
            if (cerrarFooterBtn) cerrarFooterBtn.addEventListener('click', cerrar);

            // Cerrar al hacer clic fuera del contenido del modal
            modal?.addEventListener('click', (e) => {
                if (e.target === modal) {
                    cerrar();
                }
            });
        }

        // Función principal para mostrar el gráfico en grande
        function mostrarGraficoEnGrande(graficoId) {
            console.log(`Mostrando gráfico en grande: ${graficoId}`);
            graficoGrandeActualId = graficoId;
            // 1. Obtener la instancia del gráfico original
            const graficoOriginal = window[graficoId]; // Accede usando window[nombre]

            if (!graficoOriginal || !graficoOriginal.data) {
                console.error(`No se encontró el gráfico con ID: ${graficoId}`);
                alert('Error: No se pudo encontrar el gráfico para mostrarlo en grande.');
                return;
            }

            // 2. Obtener el canvas del modal
            const canvasGrande = document.getElementById('graficoGrandeCanvas');
            const ctx = canvasGrande.getContext('2d');

            // 3. Destruir instancia anterior si existe
            if (graficoGrandeInstance) {
                graficoGrandeInstance.destroy();
            }

            // 4. Establecer el título del modal
            const tituloModal = document.getElementById('tituloGraficoGrande');
            // Intentar obtener el título del gráfico original
            const tituloOriginal = graficoOriginal.options?.plugins?.title?.text || graficoId;
            tituloModal.textContent = ` Vista Ampliada: ${tituloOriginal}`;

            // 5. Crear una nueva instancia de Chart.js en el canvas grande
            // Usamos structuredClone o JSON para copiar los datos y evitar mutaciones
            // structuredClone es más robusto pero puede no estar en todos los navegadores muy viejos
            let datosCopia;
            let opcionesCopia;
            try {
                 // Intentar copia profunda
                datosCopia = JSON.parse(JSON.stringify(graficoOriginal.data));
                opcionesCopia = JSON.parse(JSON.stringify(graficoOriginal.options));
            } catch (e) {
                console.error("Error al copiar datos del gráfico:", e);
                // Si falla, usar referencias directas (menos seguro pero puede funcionar)
                datosCopia = graficoOriginal.data;
                opcionesCopia = graficoOriginal.options;
            }

            // 6. Ajustar opciones para el tamaño grande (opcional)
            // Por ejemplo, aumentar el tamaño de fuente
            if (opcionesCopia) {
                 // Asegurar que sea responsive en el modal
                opcionesCopia.responsive = true;
                opcionesCopia.maintainAspectRatio = false; // Importante para el modal

                // Ajustar tamaños de fuente si existen
                const escalaFuente = 1.5; // Aumentar un 50%
                if (opcionesCopia.plugins?.title?.font?.size) {
                    opcionesCopia.plugins.title.font.size *= escalaFuente;
                }
                if (opcionesCopia.scales) {
                    for (const eje in opcionesCopia.scales) {
                        if (opcionesCopia.scales[eje].title?.font?.size) {
                             opcionesCopia.scales[eje].title.font.size *= escalaFuente;
                        }
                        if (opcionesCopia.scales[eje].ticks?.font?.size) {
                             opcionesCopia.scales[eje].ticks.font.size *= escalaFuente;
                        }
                    }
                }
                if (opcionesCopia.plugins?.legend?.labels?.font?.size) {
                     opcionesCopia.plugins.legend.labels.font.size *= escalaFuente;
                }
            }

            // 7. Crear el nuevo gráfico
            graficoGrandeInstance = new Chart(ctx, {
                type: graficoOriginal.config.type, // Mantener el mismo tipo
                data: datosCopia,
                options: opcionesCopia
            });
            // --- NUEVO: Configurar el botón de análisis IA del modal ---
            const btnAnalizarModal = document.getElementById('btnAnalizarIAModal');
            if (btnAnalizarModal) {
                // Obtener la sección correspondiente al graficoId
                const seccion = mapeoGraficoSeccion[graficoId];
                if (seccion) {
                    // Almacenar graficoId y seccion como atributos data del botón
                    btnAnalizarModal.setAttribute('data-grafico-id', graficoId);
                    btnAnalizarModal.setAttribute('data-seccion', seccion);
                    // Asegurarse de que el botón esté habilitado/visible si era necesario
                    btnAnalizarModal.disabled = false;
                } else {
                    console.warn(`No se encontró mapeo de sección para el gráfico: ${graficoId}`);
                    btnAnalizarModal.disabled = true; // O puedes ocultarlo
                }
            }
            // --- FIN NUEVO ---

            // 8. Mostrar el modal
            toggleModalGraficoGrande(true);
        }

        // Función para configurar los event listeners de los botones "Ver en Grande"
        function setupBotonesVerGrande() {
            document.querySelectorAll('.btn-ver-grande').forEach(boton => {
                boton.addEventListener('click', function(e) {
                    // Evitar que el clic se propague a la tarjeta si también es clicable
                    e.stopPropagation();
                    const graficoId = this.getAttribute('data-grafico-id');
                    if (graficoId) {
                        mostrarGraficoEnGrande(graficoId);
                    } else {
                        console.error('Botón "Ver en Grande" sin atributo data-grafico-id válido.');
                    }
                });
            });

            // Opcional: Hacer que toda la tarjeta sea clicable
            // document.querySelectorAll('.chart-card').forEach(card => {
            //     card.addEventListener('click', function() {
            //         const graficoId = this.getAttribute('data-grafico-id');
            //         if (graficoId) {
            //             mostrarGraficoEnGrande(graficoId);
            //         }
            //     });
            // });
        }

        // --- Fin de Funciones para el Modal de Gráfico Grande ---