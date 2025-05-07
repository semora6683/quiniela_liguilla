
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Quiniela Liguilla MX", layout="wide")

st.title("🏆 Quiniela Liguilla MX - Ranking en Vivo")

st.markdown("""
Esta aplicación permite cargar resultados reales y predicciones de los participantes
para las etapas de **Cuartos de Final, Semifinales y Final** (Ida y Vuelta).  
El sistema calcula automáticamente los puntos y muestra un ranking en tiempo real.

**Puntos:**
- 🎯 3 puntos si acierta el marcador exacto
- ✅ 1 punto si acierta el ganador o empate
- ❌ 0 puntos si falla completamente
""")

# Subir archivos
resultados_file = st.file_uploader("📄 Subir archivo de Resultados (CSV)", type="csv")
predicciones_file = st.file_uploader("📄 Subir archivo de Predicciones (CSV)", type="csv")

if resultados_file and predicciones_file:
    resultados_df = pd.read_csv(resultados_file)
    predicciones_df = pd.read_csv(predicciones_file)

    # Crear diccionario de resultados reales
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

    st.subheader("📊 Ranking Actualizado")
    ranking_df = pd.DataFrame(list(ranking.items()), columns=["Participante", "Puntos"]).sort_values(by="Puntos", ascending=False)
    st.dataframe(ranking_df)

    # Descargar Ranking
    csv = ranking_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Descargar Ranking en CSV", csv, "ranking_quiniela.csv", "text/csv")

    with st.expander("📋 Resultados cargados"):
        st.dataframe(resultados_df)

    with st.expander("📝 Predicciones cargadas"):
        st.dataframe(predicciones_df)
