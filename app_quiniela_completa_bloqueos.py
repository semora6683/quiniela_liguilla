
import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Quiniela Liguilla MX", layout="wide")

st.title("🏆 Quiniela Liguilla MX")

# Fechas y horas límite
limite_ida = datetime(2025, 5, 7, 18, 55)
limite_vuelta = datetime(2025, 5, 10, 17, 0)
ahora = datetime.now()

puede_editar_ida = ahora < limite_ida
puede_editar_vuelta = ahora < limite_vuelta

# Partidos
ida = [
    "Pachuca vs América (Ida)", "Monterrey vs Toluca (Ida)",
    "León vs Cruz Azul (Ida)", "Necaxa vs Tigres (Ida)"
]

vuelta = [
    "América vs Pachuca (Vuelta)", "Toluca vs Monterrey (Vuelta)",
    "Cruz Azul vs León (Vuelta)", "Tigres vs Necaxa (Vuelta)",
    "Ganador 1 vs Ganador 4 (Semifinal Ida)", "Ganador 4 vs Ganador 1 (Semifinal Vuelta)",
    "Ganador 2 vs Ganador 3 (Semifinal Ida)", "Ganador 3 vs Ganador 2 (Semifinal Vuelta)",
    "Finalista 1 vs Finalista 2 (Final Ida)", "Finalista 2 vs Finalista 1 (Final Vuelta)"
]

PRED_FILE = "predicciones_capturadas.csv"

tab1, tab2 = st.tabs(["📝 Captura de Predicciones", "📊 Ranking y Resultados"])

with tab1:
    st.header("📝 Participa llenando tu Quiniela")
    with st.form("form_predicciones"):
        participante = st.text_input("👤 Tu nombre (único):")

        predicciones = {}

        if puede_editar_ida:
            with st.expander("📅 Partidos de IDA (hasta 7 mayo 6:55 PM)"):
                for partido in ida:
                    col1, col2 = st.columns(2)
                    with col1:
                        local = st.number_input(f"{partido} - Goles Local", min_value=0, max_value=20, key=f"{partido}-L")
                    with col2:
                        visita = st.number_input(f"{partido} - Goles Visitante", min_value=0, max_value=20, key=f"{partido}-V")
                    predicciones[f"{partido} - Local"] = local
                    predicciones[f"{partido} - Visitante"] = visita
        else:
            st.warning("⚠️ La captura de predicciones para partidos de IDA ha sido cerrada.")

        if puede_editar_vuelta:
            with st.expander("📅 Partidos de VUELTA (hasta 10 mayo 5:00 PM)"):
                for partido in vuelta:
                    col1, col2 = st.columns(2)
                    with col1:
                        local = st.number_input(f"{partido} - Goles Local", min_value=0, max_value=20, key=f"{partido}-L")
                    with col2:
                        visita = st.number_input(f"{partido} - Goles Visitante", min_value=0, max_value=20, key=f"{partido}-V")
                    predicciones[f"{partido} - Local"] = local
                    predicciones[f"{partido} - Visitante"] = visita
        else:
            st.warning("⚠️ La captura de predicciones para partidos de VUELTA ha sido cerrada.")

        submitted = st.form_submit_button("📥 Enviar Predicciones")

        if submitted:
            if not participante.strip():
                st.error("Por favor, escribe tu nombre.")
            else:
                row = {"Participante": participante}
                row.update(predicciones)
                new_df = pd.DataFrame([row])

                if os.path.exists(PRED_FILE):
                    existing = pd.read_csv(PRED_FILE)
                    existing = existing[existing["Participante"] != participante]
                    updated_df = pd.concat([existing, new_df], ignore_index=True)
                else:
                    updated_df = new_df

                updated_df.to_csv(PRED_FILE, index=False)
                st.success("¡Tus predicciones han sido guardadas correctamente!")

    if os.path.exists(PRED_FILE):
        st.subheader("📋 Predicciones capturadas")
        df = pd.read_csv(PRED_FILE)
        st.dataframe(df)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📤 Descargar predicciones", csv, "predicciones_capturadas.csv", "text/csv")

with tab2:
    st.header("📊 Ranking de Participantes")

    resultados_file = st.file_uploader("📄 Subir archivo de Resultados Oficiales (CSV)", type="csv")

    if resultados_file and os.path.exists(PRED_FILE):
        resultados_df = pd.read_csv(resultados_file)
        predicciones_df = pd.read_csv(PRED_FILE)

        resultados_df = resultados_df.dropna()
        resultados_df["Marcador"] = list(zip(resultados_df["Goles Local"].astype(int), resultados_df["Goles Visitante"].astype(int)))
        resultados_dict = dict(zip(resultados_df["Partido"], resultados_df["Marcador"]))

        ranking = {}

        for idx, row in predicciones_df.iterrows():
            participante = row["Participante"]
            puntos = 0
            for partido, real in resultados_dict.items():
                key_local = f"{partido} - Local"
                key_visita = f"{partido} - Visitante"
                if key_local in row and key_visita in row:
                    try:
                        pred = (int(row[key_local]), int(row[key_visita]))
                        if pred == real:
                            puntos += 3
                        elif (
                            (pred[0] > pred[1] and real[0] > real[1]) or
                            (pred[0] < pred[1] and real[0] < real[1]) or
                            (pred[0] == pred[1] and real[0] == real[1])
                        ):
                            puntos += 1
                    except:
                        pass
            ranking[participante] = puntos

        ranking_df = pd.DataFrame(list(ranking.items()), columns=["Participante", "Puntos"]).sort_values(by="Puntos", ascending=False)
        st.dataframe(ranking_df)

        csv = ranking_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Descargar Ranking", csv, "ranking_quiniela.csv", "text/csv")
