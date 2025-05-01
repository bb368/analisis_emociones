import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import numpy as np
from datetime import datetime, timezone

# 1. Cargar credenciales del panel de secrets
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["google_sheets"], scope
)
client = gspread.authorize(creds)
sheet = client.open("hoja-analisis-emociones").sheet1   # cámbialo si tu hoja se llama distinto

# 2. Conversión EVA→color
def eva_to_color(eva: float) -> str:
    r = int(255 * (1 - eva / 10))
    g = int(255 * (eva / 10))
    return f"rgb({r},{g},0)"





# 3. Interfaz
st.title("Como te sientes hoy?")
usuario = st.text_input("Tu nombre o alias:)")
eva = st.slider("Puntua cómo te sientes(0-10)", 0, 10, 5)

if st.button("Enviar puntuación"):
    if usuario.strip() == "":
        st.warning("Por favor, escribe tu nombre o alias.")
    else:
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        sheet.append_row([ts, usuario, eva])
        st.success("Puntuación enviada correctamente")


# 4. Mostrar media global
valores = sheet.col_values(1)
eva_vals = [float(v) for v in valores if v]   # evita celdas vacías
if eva_vals:
    media = np.mean(eva_vals)
    color = eva_to_color(media)
    st.markdown(
        f"<div style='background:{color};padding:30px;text-align:center;"
        f"color:white;font-size:30px;border-radius:8px;'>"
        f"Media EVA: {media:.2f}"
        f"</div>",
        unsafe_allow_html=True
    )
else:
    st.info("Aún no hay puntuaciones registradas.")

with st.expander("Ver últimos registros"):
    rows = sheet.get_all_values()[1:]
    st.dataframe(rows[-10:], use_container_width=True)
