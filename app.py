import streamlit as st
import pandas as pd
from datetime import datetime
import altair as alt
import os

st.set_page_config(page_title="Calculadora de Seguimiento de Tilapias", layout="wide")

st.title("🐟 Calculadora de Seguimiento de Tilapias")

# Campo de fecha
fecha = st.date_input("Fecha del registro", value=datetime.today())

# Entradas de usuario
volumen_agua = st.number_input("Volumen de agua del estanque (litros)", min_value=0.0, value=1000.0)
numero_tilapias_inicial = st.number_input("Número inicial de tilapias", min_value=1, value=50)
peso_promedio = st.number_input("Peso promedio por tilapia (gramos)", min_value=0.0, value=300.0)
temperatura_agua = st.number_input("Temperatura promedio del agua (°C)", min_value=0.0, value=28.0)
temperatura_ambiente = st.number_input("Temperatura promedio del ambiente (°C)", min_value=0.0, value=26.0)
frecuencia = st.number_input("Frecuencia de alimentación diaria (veces por día)", min_value=1, value=2)
tilapias_muertas = st.number_input("Número de tilapias muertas esta semana", min_value=0, value=3)

# Botones
col_guardar, col_borrar = st.columns([2, 1])

with col_guardar:
    guardar = st.button("✅ Calcular y Guardar")

with col_borrar:
    borrar = st.button("🗑️ Borrar todos los registros")

# Borrar registros
if borrar:
    if os.path.exists("registro_tilapia.csv"):
        os.remove("registro_tilapia.csv")
        st.success("🗑️ Todos los registros se han borrado correctamente.")
    else:
        st.info("No hay registros para borrar.")

# Guardar nuevo registro
if guardar:
    numero_tilapias_final = numero_tilapias_inicial - tilapias_muertas
    mortalidad_porcentaje = (tilapias_muertas / numero_tilapias_inicial) * 100
    peso_total_kg = (peso_promedio * numero_tilapias_final) / 1000
    alimento_diario = peso_total_kg * 0.03

    estado_temp_agua = "✅ Adecuada" if 26 <= temperatura_agua <= 30 else "⚠️ FUERA del rango (26–30 °C)"
    estado_temp_ambiente = "✅ Adecuada" if 22 <= temperatura_ambiente <= 32 else "⚠️ FUERA del rango (22–32 °C)"

    nuevo_registro = pd.DataFrame({
        "Fecha": [fecha.strftime("%Y-%m-%d")],
        "Volumen Agua (L)": [volumen_agua],
        "N° Inicial Tilapias": [numero_tilapias_inicial],
        "Tilapias Muertas": [tilapias_muertas],
        "Mortalidad (%)": [mortalidad_porcentaje],
        "Peso Promedio (g)": [peso_promedio],
        "Peso Total (kg)": [peso_total_kg],
        "Alimento Diario (kg)": [alimento_diario],
        "Temp Agua (°C)": [temperatura_agua],
        "Temp Ambiente (°C)": [temperatura_ambiente],
        "Frecuencia Alimentación": [frecuencia]
    })

    try:
        historial = pd.read_csv("registro_tilapia.csv")
        historial = pd.concat([historial, nuevo_registro], ignore_index=True)
    except FileNotFoundError:
        historial = nuevo_registro

    historial.to_csv("registro_tilapia.csv", index=False)

    st.success("✅ Registro guardado correctamente en CSV.")

# Mostrar historial si existe
if os.path.exists("registro_tilapia.csv"):
    historial = pd.read_csv("registro_tilapia.csv")

    st.subheader("📊 Historial de registros")
    st.dataframe(historial)

    historial["Fecha"] = historial["Fecha"].astype(str)

    columnas_numericas = [
        "Mortalidad (%)",
        "Peso Total (kg)",
        "Temp Agua (°C)",
        "Temp Ambiente (°C)",
        "Frecuencia Alimentación"
    ]
    for col in columnas_numericas:
        historial[col] = pd.to_numeric(historial[col], errors="coerce").fillna(0)

    historial_agrupado = historial.groupby("Fecha", as_index=False).mean()

    st.subheader("📈 Gráficas de evolución")

    if historial_agrupado.empty:
        st.info("No hay datos registrados todavía.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            chart1 = alt.Chart(historial_agrupado).mark_bar().encode(
                x=alt.X('Fecha', title='Fecha'),
                y=alt.Y('Mortalidad (%)', scale=alt.Scale(domain=[0, 100])),
                tooltip=['Fecha', 'Mortalidad (%)']
            ).properties(title="Mortalidad Semanal (%)", height=250)
            st.altair_chart(chart1, use_container_width=True)

        with col2:
            chart2 = alt.Chart(historial_agrupado).mark_bar().encode(
                x=alt.X('Fecha', title='Fecha'),
                y=alt.Y('Peso Total (kg)', scale=alt.Scale(domain=[0, 50])),
                tooltip=['Fecha', 'Peso Total (kg)']
            ).properties(title="Peso Total de Tilapias (kg)", height=250)
            st.altair_chart(chart2, use_container_width=True)

        col3, col4 = st.columns(2)

        with col3:
            chart3 = alt.Chart(historial_agrupado).mark_bar().encode(
                x=alt.X('Fecha', title='Fecha'),
                y=alt.Y('Temp Agua (°C)', scale=alt.Scale(domain=[0, 40])),
                tooltip=['Fecha', 'Temp Agua (°C)']
            ).properties(title="Temperatura Promedio del Agua", height=250)
            st.altair_chart(chart3, use_container_width=True)

        with col4:
            chart4 = alt.Chart(historial_agrupado).mark_bar().encode(
                x=alt.X('Fecha', title='Fecha'),
                y=alt.Y('Temp Ambiente (°C)', scale=alt.Scale(domain=[0, 40])),
                tooltip=['Fecha', 'Temp Ambiente (°C)']
            ).properties(title="Temperatura Promedio del Ambiente", height=250)
            st.altair_chart(chart4, use_container_width=True)

        st.subheader("📈 Frecuencia de Alimentación Diaria")
        chart5 = alt.Chart(historial_agrupado).mark_bar().encode(
            x=alt.X('Fecha', title='Fecha'),
            y=alt.Y('Frecuencia Alimentación', scale=alt.Scale(domain=[0, 5])),
            tooltip=['Fecha', 'Frecuencia Alimentación']
        ).properties(title="Frecuencia de Alimentación", height=250)
        st.altair_chart(chart5, use_container_width=True)
else:
    st.info("No hay registros almacenados.")
