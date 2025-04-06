import streamlit as st

st.set_page_config(page_title="Calculadora de UFC", layout="centered")

st.title("Calculadora de UFC/mL o g")
st.markdown("Ingresa los datos para calcular las Unidades Formadoras de Colonias (UFC) por mL o gramo de tu muestra.")

# Entradas del usuario
colonias = st.number_input("Número total de colonias contadas", min_value=0, step=1)
volumen = st.number_input("Volumen sembrado (mL)", min_value=0.0001, format="%.4f")
dilucion = st.text_input("Dilución utilizada (ejemplo: 10^-3)", value="10^-3")

# Cálculo
try:
    factor_dilucion = eval(dilucion.replace("^", "**"))
    if colonias > 0 and volumen > 0:
        ufc = colonias / (volumen * factor_dilucion)
        st.success(f"Resultado: {ufc:.2e} UFC/mL o g")
except:
    st.warning("Revisa que el formato de dilución sea válido (ejemplo: 10^-3 o 1e-3).")
