import streamlit as st
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from rasterio.io import MemoryFile
import datetime
# Configuración de la página
st.set_page_config(page_title="ThermiCAL", layout="wide")
# Estilos personalizados
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=PT+Serif:wght@400;700&display=swap');

        body {
            font-family: 'PT Serif', serif;
        }

        /* Estilo para Modo Claro */
        @media (prefers-color-scheme: light) {
            body {
                background: linear-gradient(to bottom right, #ffffff, #e6e6e6);
                color: #000000;
            }
            .main-header {
                background-color: #ffa500;
                color: white;
            }
            h2, h3, .stMarkdown {
                color: #000000;
            }
        }

        /* Estilo para Modo Oscuro */
        @media (prefers-color-scheme: dark) {
            body {
                background: linear-gradient(to bottom right, #1e3c72, #2a5298);
                color: white;
            }
            .main-header {
                background-color: #ffa500;
                color: white;
            }
            h2, h3, .stMarkdown {
                color: #f0f0f0;
            }
        }

        .stButton > button, .stDownloadButton > button {
            font-family: 'PT Serif', serif;
            font-weight: bold;
            border-radius: 10px;
            padding: 10px 20px;
        }

        .stButton > button {
            background-color: #ffa500;
            color: white;
        }

        .stDownloadButton > button {
            background-color: #28a745;
            color: white;
        }

        .stNumberInput input {
            background-color: #f0f0f0;
            color: #333;
            font-family: 'PT Serif', serif;
        }

        .stFileUploader {
            background-color: rgba(255, 255, 255, 0.1);
            padding: 10px;
            border-radius: 10px;
        }

        footer {
            text-align: center;
            margin-top: 50px;
            font-size: 14px;
            color: #ccc;
        }
    </style>
""", unsafe_allow_html=True)

# Encabezado con logos y título alineados horizontalmente
st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; background-color: #005792; padding: 10px 20px; border-radius: 10px;">
        <img src="https://raw.githubusercontent.com/JLHM1998/ThermiCAL_EcosmartRice/master/assets/Escudo.png" style="height: 80px;">
        <div style="text-align: center;">
            <h1 style="color: white; margin: 0;">🔥 ThermiCAL_EcosmartRice</h1>
            <p style="margin: 0; font-size: 14px; color: #e0e0e0;">Aplicativo Web para el procesamiento y Corrección Radiométrica</p>
        </div>
        <img src="https://raw.githubusercontent.com/JLHM1998/ThermiCAL_EcosmartRice/master/assets/logo_TyC.png" style="height: 80px;">
    </div>
""", unsafe_allow_html=True)
# --- Encabezado y descripción ---
st.markdown("""
### Bienvenido a la aplicación ThermiCAL
Esta aplicación permite cargar un ortomosaico térmico, aplicar una **ecuación de calibración** y visualizar los resultados.
La calibración indirecta de las imágenes térmicas obtenidas por la cámara H20T se realizó comparándolas con los datos medidos con un radiómetro en nueve coberturas. Para reescalar los valores de temperatura en las imágenes térmicas, se utilizó un radiómetro Apogee MI-210 (MI-210; Apogee Instruments, Inc., Logan, UT, USA). Este radiómetro se utilizó en nueve coberturas conocidas, incluyendo aluminio, hojas secas, hojas verdes, poliestireno expandido, tela amarilla, tela negra, tela roja, tela verde y suelo desnudo.
""")
# --- Menús desplegables jerárquicos ---
st.markdown("### 🗺️ Seleccionar información del monitoreo")
# Selección de región
region = st.selectbox("🌎 Seleccionar Región", ["Lambayeque", "Lima"])
# Inicializar variables
provincia = distrito = zona = None
# Opciones según la región seleccionada
if region == "Lambayeque":
    provincia = st.selectbox("📍 Seleccionar Provincia", ["Ferreñafe", "Chiclayo"])
    if provincia == "Ferreñafe":
        zona = st.selectbox("🗺️ Seleccionar Zona", ["Capote"])
    elif provincia == "Chiclayo":
        distrito = st.selectbox("🏙️ Seleccionar Distrito", ["Chongoyape", "Picsi"])
        if distrito == "Chongoyape":
            zona = st.selectbox("🗺️ Seleccionar Zona", ["Carniche", "Paredones"])
        elif distrito == "Picsi":
            zona = "Picsi"  # Selección directa
elif region == "Lima":
    zona = st.selectbox("📍 Seleccionar Zona", ["La Molina"])
# Mostrar la selección final
if zona:
    st.write(f"Zona seleccionada: {zona}")
# --- Selección de hora ---
st.markdown("### 🕒 Seleccionar hora del monitoreo")
horas_disponibles = [datetime.time(hour, 0) for hour in range(9, 16)]
hora = st.selectbox("🕒 Hora del monitoreo (9:00 AM a 3:00 PM)", horas_disponibles)
st.write(f"Hora seleccionada: {hora}")
# --- Diccionario de ecuaciones ---
ecuaciones = {
    # Capote (Ferreñafe)
    ("Capote", datetime.time(9, 0)): (0.8700, 9.500),
    ("Capote", datetime.time(10, 0)): (0.9000, 9.800),
    ("Capote", datetime.time(11, 0)): (0.9150, 9.950),
    ("Capote", datetime.time(12, 0)): (0.9244, 10.019),
    ("Capote", datetime.time(13, 0)): (0.9150, 9.950),
    ("Capote", datetime.time(14, 0)): (0.9000, 9.800),
    ("Capote", datetime.time(15, 0)): (0.8700, 9.500),
    # Paredones (Chongoyape)
    ("Paredones", datetime.time(9, 0)): (0.85, 10.5),
    ("Paredones", datetime.time(10, 0)): (0.88, 11.2),
    ("Paredones", datetime.time(11, 0)): (0.90, 9.8),
    ("Paredones", datetime.time(12, 0)): (0.87, 10.0),
    ("Paredones", datetime.time(13, 0)): (0.89, 10.3),
    ("Paredones", datetime.time(14, 0)): (0.92, 11.0),
    ("Paredones", datetime.time(15, 0)): (0.95, 11.5),
    # Carniche (Chongoyape)
    ("Carniche", datetime.time(9, 0)): (0.92, 12.1),
    ("Carniche", datetime.time(10, 0)): (0.95, 11.5),
    ("Carniche", datetime.time(11, 0)): (0.93, 12.0),
    ("Carniche", datetime.time(12, 0)): (0.91, 11.8),
    ("Carniche", datetime.time(13, 0)): (0.94, 11.9),
    ("Carniche", datetime.time(14, 0)): (0.96, 12.3),
    ("Carniche", datetime.time(15, 0)): (0.98, 12.7),
    # Picsi
    ("Picsi", datetime.time(9, 0)): (0.6980, 8.520),
    ("Picsi", datetime.time(10, 0)): (0.7050, 8.630),
    ("Picsi", datetime.time(11, 0)): (0.7100, 8.700),
    ("Picsi", datetime.time(12, 0)): (0.7139, 8.7325),
    ("Picsi", datetime.time(13, 0)): (0.7100, 8.700),
    ("Picsi", datetime.time(14, 0)): (0.7050, 8.630),
    ("Picsi", datetime.time(15, 0)): (0.6980, 8.520),
    # La Molina
    ("La Molina", datetime.time(9, 0)): (0.7130, 10.350),
    ("La Molina", datetime.time(10, 0)): (0.7180, 10.450),
    ("La Molina", datetime.time(11, 0)): (0.7240, 10.520),
    ("La Molina", datetime.time(12, 0)): (0.7291, 10.592),
    ("La Molina", datetime.time(13, 0)): (0.7240, 10.520),
    ("La Molina", datetime.time(14, 0)): (0.7180, 10.450),
    ("La Molina", datetime.time(15, 0)): (0.7130, 10.350),
}
# --- Obtener coeficientes ---
A, B = ecuaciones.get((zona, hora), (1.0, 0.0))

# --- Subida de imagen ---
st.markdown("### 📂 Subir tu imagen térmica (GeoTIFF)")
uploaded_file = st.file_uploader("Selecciona tu archivo:", type=["tif", "tiff"])
if uploaded_file is not None:
    with rasterio.open(uploaded_file) as src:
        profile = src.profile
        image = src.read(1).astype(np.float32)
    # Vista previa original
    st.markdown("### 🗾 Vista Previa - Imagen Original")
    image_clipped = np.clip(image, 0, 70)
    vmin, vmax = np.percentile(image_clipped, [2, 98])
    fig, ax = plt.subplots(figsize=(6, 4))
    im = ax.imshow(image_clipped, cmap='inferno', vmin=vmin, vmax=vmax)
    ax.axis('off')
    cbar = fig.colorbar(im, ax=ax, label='Temperatura (°C)')
    st.pyplot(fig)
    # Aplicar calibración
    calibrated = A * image + B
    calibrated = np.clip(calibrated, 0, 70)
    # Vista previa calibrada
    st.markdown("### 🗾 Vista Previa - Imagen Calibrada")
    vmin2, vmax2 = np.percentile(calibrated, [2, 98])
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    im2 = ax2.imshow(calibrated, cmap='inferno', vmin=vmin2, vmax=vmax2)
    ax2.axis('off')
    cbar2 = fig2.colorbar(im2, ax=ax2, label='Temperatura Calibrada (°C)')
    st.pyplot(fig2)
    # Guardar como GeoTIFF
    profile.update(dtype=rasterio.float32)
    with MemoryFile() as memfile:
        with memfile.open(**profile) as dst:
            dst.write(calibrated.astype(rasterio.float32), 1)
        mem_bytes = memfile.read()
    # Botón de descarga
    st.markdown("### 💾 Descargar Imagen Calibrada")
    st.download_button("📥 Descargar TIFF Calibrado", data=mem_bytes,
                       file_name=f"{zona}_{hora}_calibrada.tif", mime="image/tiff")
else:
    st.info("Por favor, sube una imagen térmica para comenzar.")

# --- Sección de Manual de Usuario ---
st.markdown("### 📘 Manual de Usuario")
st.markdown("""
Para conocer más sobre el funcionamiento de esta aplicación, puedes visualizar o descargar el manual completo que contiene instrucciones detalladas, flujogramas, requisitos y recomendaciones de uso.

- **Visualizar en línea**:  
  [Haz clic aquí para abrir el manual en una nueva pestaña](https://github.com/JLHM1998/ThermiCAL_EcosmartRice/blob/main/Manual_Usuario_ThermiCAL.pdf)

- **Descargar PDF**:
""")

with open("Manual_Usuario_ThermiCAL.pdf", "rb") as manual_file:
    st.download_button(
        label="📥 Descargar Manual de Usuario (PDF)",
        data=manual_file,
        file_name="Manual_Usuario_ThermiCAL.pdf",
        mime="application/pdf"
    )

# --- Sección de Financiamiento con estilo destacado ---
st.markdown("""
    <div style="margin-top: 30px; padding: 20px; background: linear-gradient(to right, #004e92, #000428); border-radius: 12px; color: white;">
        <h3 style="margin-top: 0;">💼 Financiamiento</h3>
        <p style="font-size: 15px; line-height: 1.6;">
            Esta aplicación ha sido desarrollada en el marco del proyecto EcosmartRice:
            <strong>"Nuevas herramientas tecnológicas de precisión con sensores remotos para un sistema de producción sostenible en arroz, con menor consumo de agua, menor emisión de gases y mayor rendimiento, en beneficio de los agricultores de Lambayeque"</strong>,
            financiado por el <strong>Programa Nacional de Investigación Científica y Estudios Avanzados (PROCIENCIA)</strong> del
            <strong>Consejo Nacional de Ciencia, Tecnología e Innovación Tecnológica (CONCYTEC)</strong>, mediante el
            <strong>Contrato No. PE501086540-2024-PROCIENCIA</strong>.
        </p>
    </div>
""", unsafe_allow_html=True)

# Pie de página
st.markdown("""
    <footer>
        © 2025 Universidad Nacional Agraria La Molina - Todos los derechos reservados.
    </footer>
""", unsafe_allow_html=True)
