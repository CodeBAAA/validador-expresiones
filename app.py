import streamlit as st
from validador_expresiones import validate_expression, VALID_EXPRESSIONS, INVALID_EXPRESSIONS, probar_lista_expresiones

# ============================================
# CONFIGURACIÓN DE LA APP
# ============================================

st.set_page_config(
    page_title="Validador de Expresiones | Mini-Lenguaje",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 Validador de Expresiones Aritméticas")
st.write("Mini-lenguaje basado en gramática, autómata y pila. Compatible para compartir con otros.")

# ============================================
# SECCIÓN: INGRESAR EXPRESIÓN
# ============================================

st.header("✏️ Probar una expresión")

expr = st.text_input("Escribe una expresión:", placeholder="Ejemplo: (1+2)*3")

if st.button("Validar expresión"):
    valid, error, result = validate_expression(expr)

    if valid:
        st.success(f"✅ Expresión válida")
        st.info(f"📌 Resultado: **{result}**")
        VALID_EXPRESSIONS.append(expr)
    else:
        st.error(f"❌ Expresión inválida: {error}")
        INVALID_EXPRESSIONS.append((expr, error))


# ============================================
# SECCIÓN: RESULTADOS EN TIEMPO REAL
# ============================================
import pandas as pd

st.header("📊 Resultados acumulados")

col1, col2 = st.columns(2)

with col1:
    st.subheader("✨ Expresiones válidas")
    if VALID_EXPRESSIONS:
        df_valid = pd.DataFrame({"Expresión": VALID_EXPRESSIONS})
        st.dataframe(df_valid, use_container_width=True)
    else:
        st.info("Aún no hay expresiones válidas.")

with col2:
    st.subheader("❌ Expresiones inválidas")
    if INVALID_EXPRESSIONS:
        df_invalid = pd.DataFrame({
            "Expresión": [e for e, m in INVALID_EXPRESSIONS],
            "Error": [m for e, m in INVALID_EXPRESSIONS]
        })
        st.dataframe(df_invalid, use_container_width=True)
    else:
        st.info("Aún no hay expresiones inválidas.")

# ============================================
# PRUEBAS AUTOMÁTICAS
# ============================================

st.header("🧪 Ejecutar pruebas sugeridas")
if st.button("Correr casos de prueba"):
    validas = [
        "42",
        "(1+2)*3",
        "12 + (34 - 5)/6",
        "1+2*3",
        "((1+2)*3)/4",
    ]

    invalidas = [
        "+12",
        "1 2",
        "(1+2",
        "2*)3",
        "1++2",
        "1**2",
        "1+",
        "( )",
        "",
    ]

    st.write("Ejecutando pruebas...")

    probar_lista_expresiones(validas + invalidas)

    st.success("Pruebas ejecutadas correctamente. Revisa las tablas.")


# ============================================
# BOTÓN PARA LIMPIAR HISTORIAL
# ============================================

if st.button("Limpiar historial"):
    VALID_EXPRESSIONS.clear()
    INVALID_EXPRESSIONS.clear()
    st.success("Historial borrado.")
