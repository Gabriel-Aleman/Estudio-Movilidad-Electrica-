from datetime import datetime, timedelta
import plotly.figure_factory as ff
import plotly.express as px
import pandas as pd
import numpy as np

def genDF():
    ruta_a = pd.read_csv("Data\\SanJoseDesampa.csv")
    ruta_b = pd.read_csv("Data\\SanJoseAlajuela.csv")
    ruta_c = pd.read_csv("Data\\LaUrucaPavasEscazu.csv")
    ruta_d = pd.read_csv("Data\\SanJoseCarpioUruca.csv")

    df=pd.DataFrame()
    df["t_stamp"] = ruta_a["time"]
    df["Ruta: San Jose- Desamparados"]  = ruta_a["Trabajo grupal"]
    df["Ruta: San Jose- Alajuela"]      = ruta_b["Trabajo grupal"]
    df["Ruta: Uruca-Pavas-Escazu"]      = ruta_c["Trabajo grupal"]
    df["Ruta: San Jose-Carpio-Uruca"]   = ruta_d["Trabajo grupal"]
    df["Consumo total (kW)"] = df["Ruta: San Jose-Carpio-Uruca"]+df["Ruta: San Jose- Desamparados"]+df["Ruta: San Jose- Alajuela"]+df["Ruta: Uruca-Pavas-Escazu"]
    
    #Arreglar columna de t_stamp
    #..................................................................................................
    N = len(df)  # cantidad de elementos
    intervalo = timedelta(minutes=5)

    # Obtener lunes de esta semana a medianoche
    hoy = datetime.today()
    lunes = datetime.combine(hoy - timedelta(days=hoy.weekday()), datetime.min.time())

    # Crear lista de N t_stamps espaciadas 5 min
    t_stamps = [lunes + i * intervalo for i in range(N)]
    #..................................................................................................

    df["t_stamp"] = t_stamps

    return df

def genStad(df):
    estad = df[df.columns[1:]].describe()
    estad = estad.iloc[1:]
    return estad

def genPlot(df):
        
    fig = px.line(df, x="t_stamp", y=df.columns.drop(["t_stamp", "Consumo total (kW)"]), title="Consumo kw en función del tiempo")
    fig.update_layout(

        xaxis_title="Tiempo",
        yaxis_title="kW",


        xaxis=dict(showgrid=True, gridcolor="lightgray"),
        yaxis=dict(showgrid=True, gridcolor="lightgray")
    )
    return fig

def genDist(df):
    df = df.copy()
    df.drop(columns=["t_stamp"], inplace =True)
    df_num = df.select_dtypes(include='number')

    fig = px.histogram(df_num, barmode='overlay', opacity=0.5)
    return fig




import random  # <- usar random.choice en lugar de np.random.choice

def simular_consumo(df, intervalo_min=5, dias_simulados=100, agregar_ruido=True, sigma_rel=0.05, inicio_simulacion=None, random_seed=42):
    np.random.seed(random_seed)
    random.seed(random_seed)  # Semilla para random.choice
    
    # Fecha de inicio
    if inicio_simulacion is None:
        hoy = pd.Timestamp.today()
        inicio_simulacion = pd.Timestamp(year=hoy.year + 1, month=1, day=1)
    
    # Crear columna de fecha a partir de t_stamp
    df['Fecha'] = df['t_stamp'].dt.date
    dias = df['Fecha'].unique()
    
    # Guardar cada día como bloque
    bloques_dia = [df[df['Fecha'] == dia].copy() for dia in dias]
    
    simulacion = []
    for i in range(dias_simulados):
        dia_random = random.choice(bloques_dia)  # <- cambio aquí
        dia_copy = dia_random.copy()
        
        if agregar_ruido:
            columnas_consumo = [col for col in df.columns if col not in ['t_stamp', 'Fecha']]
            for col in columnas_consumo:
                ruido = np.random.normal(loc=0, scale=sigma_rel, size=len(dia_copy))
                dia_copy[col] = dia_copy[col] * (1 + ruido)
        
        simulacion.append(dia_copy)
    
    df_simulado = pd.concat(simulacion).reset_index(drop=True)
    
    # Ajustar fechas
    inicio = pd.Timestamp(inicio_simulacion)
    df_simulado['t_stamp'] = [inicio + pd.Timedelta(minutes=intervalo_min*i) for i in range(len(df_simulado))]
    
    df_simulado = df_simulado.drop(columns=['Fecha'])
    
    return df_simulado
