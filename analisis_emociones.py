import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import numpy as np
from datetime import datetime, timezone

# 1. Cargar credenciales
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["google_sheets"], scope
)
client = gspread.authorize(creds)
sheet = client.open("hoja-analisis-emociones").sheet1  # cambia si tu hoja se llama distinto

# 2. Conversión EVA → color
def eva_to_color(eva: float) -> str:
    r = int(255 * (1 - eva / 10))
    g = int(255 * (eva / 10))
    return f"rgb({r},{g},0)"

# 3. Interfaz
st.title("¿Cómo te sientes hoy?")
usuario = st.text_input("Tu nombre o alias :)")
eva = st.slider("Puntúa cómo te sientes (0‑10)", 0, 10, 5)

if st.button("Enviar puntuación"):
    if usuario.strip() == "":
        st.warning("Por favor, escribe tu nombre o alias.")
    else:
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        sheet.append_row([ts, usuario, eva])
        st.success("Puntuación enviada correctamente")

# 4. Cargar datos de la hoja
rows = sheet.get_all_values()               # primera fila es cabecera
data = rows[1:]                             # resto son registros

if data:                                    # hay registros
    # índices de columnas (0‑based): 0=fecha, 1=usuario, 2=eva
    eva_vals_global = [float(r[2]) for r in data if r[2]]
    eva_vals_user   = [
        float(r[2]) for r in data
        if r[2] and r[1].strip().lower() == usuario.strip().lower()
    ]

    col_user, col_global = st.columns(2)    # tarjetas lado a lado

    # --- tarjeta personal ---
    with col_user:
        if eva_vals_user:
            media_user = np.mean(eva_vals_user)
            st.markdown(
                f"<div style='background:{eva_to_color(media_user)};"
                f"padding:30px;text-align:center;color:white;"
                f"font-size:24px;border-radius:8px;'>"
                f"Tu media EVA<br><b>{media_user:.2f}</b>"
                f"</div>",
                unsafe_allow_html=True
            )
        else:
            st.info("Aún no tienes puntuaciones propias.")

    # --- tarjeta global ---
    with col_global:
        media_global = np.mean(eva_vals_global)
        st.markdown(
            f"<div style='background:{eva_to_color(media_global)};"
            f"padding:30px;text-align:center;color:white;"
            f"font-size:24px;border-radius:8px;'>"
            f"Media global EVA<br><b>{media_global:.2f}</b>"
            f"</div>",
            unsafe_allow_html=True
        )
else:
    st.info("Aún no hay puntuaciones registradas.")

# 5. Últimos registros
with st.expander("Ver últimos registros"):
    st.dataframe(data[-10:], use_container_width=True)

