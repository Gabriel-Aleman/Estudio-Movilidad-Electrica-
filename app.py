from datetime import date
from funcs import *

import streamlit as st
if 'simul' not in st.session_state:
    st.session_state.simul = False  # sim es tu DataFrame simulado

if 'resultadoSimulacion' not in st.session_state:
    st.session_state.resultadoSimulacion = None  # sim es tu DataFrame simulado


st.html("<h1 style='color:white;padding-left:20px;background: linear-gradient(to right, #8b0000, #ff0000, #ffa07a); border-radius:10px 50px 50px 10px'>Aplicación de estudio de movilidad eléctrica<h1>")
st.set_page_config(layout="wide")
df = genDF()


sim, mont = st.tabs(["Resultados simulación", "Estimación montecarlo"])

with sim:
    with st.expander("Filtros"):
        t_stamp = df["t_stamp"].to_list()
        min_datetime= (t_stamp[0])
        max_datetime= (t_stamp[-1])

        try:


            # Valores iniciales
            default_start = min_datetime
            default_end = max_datetime

            # ---- FECHA ----
            start_date = st.date_input(
                "Fecha inicio",
                value=default_start.date(),
                min_value=min_datetime.date(),
                max_value=max_datetime.date()
            )

            end_date = st.date_input(
                "Fecha fin",
                value=default_end.date(),
                min_value=min_datetime.date(),
                max_value=max_datetime.date()
            )

            # ---- HORA ----
            start_time = st.time_input(
                "Hora inicio",
                value=default_start.time()
            )

            end_time = st.time_input(
                "Hora fin",
                value=default_end.time()
            )

            # ---- Combinar ----
            start_datetime = datetime.combine(start_date, start_time)
            end_datetime = datetime.combine(end_date, end_time)
        except:
            st.spinner("Espere...")
        else:
            df = df.query("t_stamp >= @start_datetime and t_stamp <= @end_datetime")

        st.info(f"Datos filtrados {len(df)}")

    st.dataframe(df)
    st.header("Plot", divider=True)
    st.plotly_chart(genPlot(df))

    st.header("Estadísticas", divider=True)
    st.dataframe(genStad(df))


    st.header("Distribución", divider=True)
    st.plotly_chart(genDist(df))

with mont:
    with st.container(border=True):
        dias    = st.number_input( "Días a simular", value=10,       min_value=0)

    if st.button("Crear resultado simulación"):
        resultadoSimulacion=simular_consumo(df,  dias_simulados=dias)
        resultadoSimulacion.set_index("t_stamp", inplace=True)
        
        st.session_state.simul = True  # sim es tu DataFrame simulado
        st.session_state.resultadoSimulacion = resultadoSimulacion

    if(st.session_state.simul):
        # Graficar todas las columnas numéricas
        st.write( st.session_state.resultadoSimulacion)
        st.success(f"{len(st.session_state.resultadoSimulacion)} elementos")

        if st.button("Graficar simulación"):
            st.line_chart( st.session_state.resultadoSimulacion)


