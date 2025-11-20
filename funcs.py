from datetime import datetime, timedelta
import plotly.figure_factory as ff
import plotly.express as px
import pandas as pd
import numpy as np

def genDF():
    ruta_a = pd.read_csv("Data/SanJoseDesampa.csv")
    ruta_b = pd.read_csv("Data/SanJoseAlajuela.csv")
    ruta_c = pd.read_csv("Data/LaUrucaPavasEscazu.csv")
    ruta_d = pd.read_csv("Data/SanJoseCarpioUruca.csv")
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

def montecarlo_forecast(df, fecha_col, n_dias, n_simulaciones=1000):
    """
    Predice 1 año hacia el futuro (105,120 pasos de 5 min)
    usando Monte Carlo multivariado.
    """
    
    df = df.set_index(fecha_col)
    datos = df.select_dtypes(include=[np.number])

    # Cambios históricos (incrementos)
    cambios = datos.diff().dropna()
    
    mu  = cambios.mean().values            # media de cambios
    cov = cambios.cov().values            # covarianza multivariada

    pasos = 288 * 365                     # 1 año = 105120 pasos de 5 min
    x0 = datos.iloc[-1].values            # último registro real

    simulaciones_acumuladas = np.zeros((pasos + 1, datos.shape[1]))

    # Simulaciones
    for i in range(n_simulaciones):
        print (str(i*100/n_simulaciones)+"%")
        trayectoria = np.zeros((pasos + 1, datos.shape[1]))
        estado = x0.copy()
        trayectoria[0] = estado
        
        for i in range(1, pasos + 1):
            cambio = np.random.multivariate_normal(mu, cov)
            estado = estado + cambio
            trayectoria[i] = estado
        
        simulaciones_acumuladas += trayectoria
        
    
    # Promedio de simulaciones → predicción final
    prediccion_media = simulaciones_acumuladas / n_simulaciones

    # Crear fechas futuro
    fecha_inicio = df.index[-1]
    fechas_futuras = pd.date_range(
        start=fecha_inicio,
        periods=pasos + 1,
        freq='5min'
    )

    pred_df = pd.DataFrame(prediccion_media, index=fechas_futuras, columns=datos.columns)
    return pred_df