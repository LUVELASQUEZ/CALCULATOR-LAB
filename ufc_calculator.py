import streamlit as st
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from datetime import datetime
import plotly.graph_objs as go

st.set_page_config(page_title="Cálculos para Laboratorio", layout="centered")

# DESCRIPCIÓN 
st.markdown("### 👋 Bienvenido/a")

with st.expander("Conoce más sobre esta aplicación"):
    st.markdown("""
    Hola, soy **Luisa**, microbióloga industrial, y desarrollé esta aplicación como una herramienta sencilla de apoyo para cálculos comunes en el laboratorio,
    como el conteo de UFC y la determinación de concentraciones a partir de curvas de calibración por absorbancia.

    Más allá de facilitar cálculos, el objetivo principal de esta aplicación fue **poner en práctica y fortalecer mis conocimientos en herramientas tecnológicas**,
    entendiendo la importancia que tienen los **sistemas LIMS** en la gestión de datos, la trazabilidad y la calidad de la información en un laboratorio.

    Con esta aplicación también busco demostrar que, **entendiendo conceptos básicos de tecnología y programación**, es posible
    **facilitar el acceso, el alcance y la interpretación de los datos científicos**, permitiendo que más personas puedan comprender
    y trabajar con la información de forma clara, ordenada y confiable.

    El desarrollo se realizó utilizando **Python y Streamlit**, y estuvo acompañado por el uso de **inteligencia artificial como apoyo**,
    tanto para la estructuración del código como para la validación lógica de los cálculos y la mejora progresiva de la aplicación.

    Este proyecto representa un ejercicio práctico de integración entre ciencia, tecnología y gestión de datos,
    con un enfoque en buenas prácticas de laboratorio y trazabilidad, alineado con los principios de la norma **ISO/IEC 17025**.
    
    Gracias por usar esta aplicación y ser parte de este ejercicio de ciencia, datos y tecnología 😘😘😘.
    """)

# TÍTULO PRINCIPAL
st.title("🧪 CÁLCULOS PARA LABORATORIO")
st.markdown("Herramienta para apoyar los cálculos en microbiología y química básica del laboratorio agrícola.")


# Inicializar historial en la sesión
if 'historial_ufc' not in st.session_state:
    st.session_state['historial_ufc'] = pd.DataFrame(columns=[
        "Fecha", "Colonias", "Volumen (mL)", "Dilución", "UFC/mL o g"
    ])

# PESTAÑAS PARA SELECCIÓN DE CÁLCULO
if 'historial_concentracion' not in st.session_state:
    st.session_state['historial_concentracion'] = pd.DataFrame(columns=[
        "Fecha", "Absorbancia muestra", "Concentración estimada"
    ])

tabs = st.tabs(["🦠 UFC/mL o g", 
                "📊 Curva de calibración", 
                "📁 Historial (ISO 17025) UFC",
                "📁 Historial (ISO 17025) ABS",
               ])

# TAB 1: UFC

# TAB 1: UFC
with tabs[0]:
    st.header("🦠 Cálculo de UFC/mL o g")
    st.markdown("Ingresa los datos de tu siembra microbiológica:")

    colonias = st.number_input("Número total de colonias contadas", min_value=0, step=1)
    volumen = st.number_input("Volumen sembrado (mL)", min_value=0.1, format="%.4f")
    dilucion = st.text_input("Dilución utilizada (ejemplo: 10^-3)", value="10^-3")

    if st.button("Calcular UFC"):
        try:
            factor_dilucion = eval(dilucion.replace("^", "**"))
            if colonias > 0 and volumen > 0:
                ufc = colonias / (volumen * factor_dilucion)
                st.success(f"Resultado: **{ufc:.2e} UFC/mL o g**")

                # Guardar en el historial
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
            else:
                st.warning("⚠️ Por favor, ingresa valores mayores a cero.")
        except:
            st.warning("⚠️ Revisa que el formato de dilución sea válido (ejemplo: 10^-3 o 1e-3).")



# TAB 2: CURVA DE CALIBRACIÓN

with tabs[1]:
    st.header("📊 Determinación de concentración por absorbancia")
    st.markdown("1. Ingresa los datos de tu curva de calibración:")

    conc_input = st.text_area("**Concentraciones (mg/L o unidades apropiadas):**", value="0, 2, 4, 6, 8")
    abs_input = st.text_area("**Absorbancias correspondientes:**", value="0.05, 0.12, 0.23, 0.34, 0.45")

    if st.button("Calcular curva de calibración"):
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

            # Guardar valores de la curva en el estado para usarlos después
            st.session_state['pendiente'] = pendiente
            st.session_state['intercepto'] = intercepto

            # Gráfica interactiva
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x.flatten(), y=y, mode='markers', name='Datos experimentales'))
            fig.add_trace(go.Scatter(x=x.flatten(), y=y_pred, mode='lines', name='Recta de regresión'))

            fig.update_layout(
                title="Curva de Calibración",
                xaxis_title="Concentración",
                yaxis_title="Absorbancia",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.warning("⚠️ Revisa el formato de los datos. Usa números separados por comas.")

    st.divider()
    st.markdown("2. Ingresa la absorbancia de la muestra para calcular su concentración:")

    absorbancia_muestra = st.number_input("Absorbancia de la muestra", min_value=0.0, format="%.4f")

    if st.button("Calcular concentración"):
        if 'pendiente' in st.session_state and 'intercepto' in st.session_state:
            try:
                pendiente = st.session_state['pendiente']
                intercepto = st.session_state['intercepto']
                concentracion_muestra = (absorbancia_muestra - intercepto) / pendiente
                st.success(f"**Concentración estimada:** {concentracion_muestra:.4f} unidades")

                # Guardar en el historial
                nuevo_resultado = {
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Absorbancia muestra": absorbancia_muestra,
                    "Concentración estimada": round(concentracion_muestra, 4)
                }
                st.session_state['historial_concentracion'] = pd.concat(
                    [st.session_state['historial_concentracion'], pd.DataFrame([nuevo_resultado])],
                    ignore_index=True
                )
            except:
                st.warning("⚠️ Error al calcular la concentración. Verifica tus datos.")
        else:
            st.warning("⚠️ Primero debes calcular la curva de calibración.")


# TAB 3: HISTORIAL
with tabs[2]:
    st.header("📁 Historial de datos (ISO 17025)")
    st.markdown("Aquí encontrarás el historial de tus cálculos microbiológicos (UFC):")

    if not st.session_state['historial_ufc'].empty:
        st.dataframe(st.session_state['historial_ufc'], use_container_width=True)

        archivo = st.session_state['historial_ufc'].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar historial en CSV",
            data=archivo,
            file_name="historial_ufc.csv",
            mime="text/csv"
        )
    else:
        st.info("Aún no hay cálculos registrados.")

# TAB 4: Historial concentración por absorbancia
with tabs[3]:
    st.header("📁 Historial (ISO 17025) ABS")
    st.markdown("Este historial contiene los cálculos de concentración realizados a partir de absorbancia de muestra.")
    
    df_abs = st.session_state['historial_concentracion']

    if not df_abs.empty:
        st.dataframe(df_abs, use_container_width=True)

        # Botón de descarga
        csv = df_abs.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar historial en CSV",
            data=csv,
            file_name="historial_concentracion_abs.csv",
            mime='text/csv'
        )
    else:
        st.info("📭 Aún no se ha registrado ningún cálculo.")
