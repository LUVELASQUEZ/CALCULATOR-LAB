import streamlit as st
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from datetime import datetime
import os
import plotly.graph_objs as go

st.set_page_config(page_title="Cálculos para Laboratorio", layout="centered")

st.title("🧪 CÁLCULOS PARA LABORATORIO")
st.markdown("Herramienta para apoyar los cálculos en microbiología y química básica del laboratorio agrícola.")

# Inicializa historial
if 'historial_ufc' not in st.session_state:
    st.session_state['historial_ufc'] = pd.DataFrame(columns=[
        "Fecha", "Colonias", "Volumen (mL)", "Dilución", "UFC/mL o g"
    ])

# PESTAÑAS
tabs = st.tabs(["🦠 UFC/mL o g", "📊 Curva de calibración", "📁 Historial de datos (ISO 17025)"])

# TAB 1: UFC
with tabs[0]:
    st.header("🦠 Cálculo de UFC/mL o g")
    st.markdown("Ingresa los datos de tu siembra microbiológica:")

    colonias = st.number_input("Número total de colonias contadas", min_value=0, step=1)
    volumen = st.number_input("Volumen sembrado (mL)", min_value=0.1, format="%.4f")
    dilucion = st.text_input("Dilución utilizada (ejemplo: 10^-3)", value="10^-3")

    try:
        factor_dilucion = eval(dilucion.replace("^", "**"))
        if colonias > 0 and volumen > 0:
            ufc = colonias / (volumen * factor_dilucion)
            st.success(f"Resultado: **{ufc:.2e} UFC/mL o g**")

            # Guarda en historial
            nuevo_registro = {
                "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Colonias": colonias,
                "Volumen (mL)": volumen,
                "Dilución": dilucion,
                "UFC/mL o g": f"{ufc:.2e}"
            }
            st.session_state['historial_ufc'] = pd.concat(
                [st.session_state['historial_ufc'], pd.DataFrame([nuevo_registro])],
                ignore_index=True
            )
    except:
        st.warning("⚠️ Revisa que el formato de dilución sea válido (ejemplo: 10^-3 o 1e-3).")

# TAB 2: Curva de calibración
with tabs[1]:
    st.header("📊 Determinación de concentración por absorbancia")
    st.markdown("1. Ingresa los datos de tu curva de calibración:")

    conc_input = st.text_area("**Concentraciones (mg/L o unidades apropiadas):**", value="0, 2, 4, 6, 8")
    abs_input = st.text_area("**Absorbancias correspondientes:**", value="0.05, 0.12, 0.23, 0.34, 0.45")

    if conc_input and abs_input:
        try:
            x = np.array([float(i.strip()) for i in conc_input.split(",")]).reshape(-1, 1)
            y = np.array([float(i.strip()) for i in abs_input.split(",")])

            model = LinearRegression()
            model.fit(x, y)
            pendiente = model.coef_[0]
            intercepto = model.intercept_
            y_pred = model.predict(x)
            r2 = r2_score(y, y_pred)

            st.success(f"**Ecuación de la recta:** A = {pendiente:.4f}·C + {intercepto:.4f}")
            st.success(f"**R² de la curva:** {r2:.4f}")

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x.flatten(), y=y, mode='markers', name='Datos experimentales'))
            fig.add_trace(go.Scatter(x=x.flatten(), y=y_pred, mode='lines', name='Recta de regresión'))
            fig.update_layout(title="Curva de Calibración", xaxis_title="Concentración", yaxis_title="Absorbancia", template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

            st.divider()
            st.markdown("2. Ingresa la absorbancia de la muestra:")
            absorbancia_muestra = st.number_input("Absorbancia de la muestra", min_value=0.0, format="%.4f")

            if absorbancia_muestra:
                concentracion_muestra = (absorbancia_muestra - intercepto) / pendiente
                st.success(f"**Concentración estimada:** {concentracion_muestra:.4f} unidades")
        except:
            st.warning("⚠️ Revisa que los datos de concentración y absorbancia sean numéricos y estén bien separados por comas.")

# TAB 3: Historial ISO 17025
with tabs[2]:
    st.header("📁 Historial de datos (ISO 17025) - UFC")
    st.markdown("Aquí encontrarás el historial de tus cálculos microbiológicos:")

    if not st.session_state['historial_ufc'].empty:
        st.dataframe(st.session_state['historial_ufc'])

        archivo = st.session_state['historial_ufc'].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar historial en CSV",
            data=archivo,
            file_name="historial_ufc.csv",
            mime="text/csv"
        )
    else:
        st.info("Aún no hay cálculos registrados.")
