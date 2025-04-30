import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import numpy as np

# Configura el acceso a Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("tu_credencial.json", scope)
client = gspread.authorize(creds)
sheet = client.open("eva_responses").sheet1

# Función para convertir EVA a color
def eva_to_color(eva):
    r = int(255 * (1 - eva / 10))
    g = int(255 * (eva / 10))
    return f"rgb({r},{g},0)"

# Interfaz
st.title("Evaluación EVA")
eva = st.slider("Indica tu nivel EVA (0-10)", 0, 10, 5)
if st.button("Enviar puntuación"):
    sheet.append_row([eva])
    st.success("Puntuación enviada correctamente")

# Cálculo de media
values = sheet.col_values(1)[1:]  # evita el encabezado si lo tienes
eva_values = [float(v) for v in values if v]
if eva_values:
    media = np.mean(eva_values)
    color = eva_to_color(media)
    st.markdown(
        f"<div style='background-color:{color}; padding:30px; text-align:center; color:white; font-size:30px;'>"
        f"Media EVA: {media:.2f}"
        f"</div>",
        unsafe_allow_html=True
    )
else:
    st.info("Aún no hay puntuaciones registradas.")

