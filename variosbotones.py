from dash import Dash, html, dcc
from dash import Input, Output, State
from textos import *
import pandas as pd

#Accedemos a los dos csv
DDI = pd.read_csv("DDI_sea.csv")
efectos = pd.read_csv("efectos_adversos.csv")

#Para integrar el código que tengo en dash tengo que separar mas las funciones

app = Dash(__name__)

app.layout = html.Div([

    # Entradas
    dcc.Input(
        id="ppio1",
        type="text",
        placeholder="Primer fármaco"
    ),

    dcc.Input(
        id="ppio2",
        type="text",
        placeholder="Segundo fármaco"
    ),

    # Botón principal
    html.Button(
        "Analizar interacción",
        id="btn_interaccion"
    ),

    html.Hr(),

    # Botones secundarios
    html.Button(
        "Efectos adversos",
        id="btn_efectos"
    ),

    html.Button(
        "Descripcion metabolismo",
        id="btn_enzimas"
    ),

    html.Button(
        "Descripcion interacciones",
        id="btn_acciones"
    ),

    html.Hr(),

    # Almacenamiento interno
    dcc.Store(
        id="datos_analisis"
    ),

    # Zona de salida
    html.Div(
        id="resultado"
    )
])


@app.callback(
    Output("datos_analisis", "data"),

    Input("btn_interaccion", "n_clicks"),

    State("ppio1", "value"),
    State("ppio2", "value")
)
#Analizo la interaccion
def analizar_farmacos(n_clicks, ppio1, ppio2):

    if n_clicks is None:
        return {}

    if not ppio1 or not ppio2:
        return {}

    #La funcion interacción sin riesgo me devuelve el nivel de interaccion que tengan
    riesgo = interaccion(ppio1, ppio2, DDI)

    return riesgo

#VARIOS CALLBACK NECESARIOS EN ESTE CASO
@app.callback(
    Output("resultado", "children"),

    Input("btn_efectos", "n_clicks"),

    State("datos_analisis", "data")
)
#Mostramos los efectos, solo si hay interaccion....funcion
def mostrar_efectos(n_clicks, datos):

    if n_clicks is None:
        return ""

    if not datos:
        return "Primero pulsa Analizar"

    return datos["efectos"]


@app.callback(
    Output("resultado", "children"),

    Input("btn_enzimas", "n_clicks"),

    State("datos_analisis", "data")
)
#Mostramos la descripcion de enzimas: funcion
def mostrar_descr_enz(n_clicks, datos):

    if n_clicks is None:
        return ""

    if not datos:
        return "Primero pulsa Analizar"

    return datos["interacciones"]


@app.callback(
    Output("resultado", "children"),

    Input("btn_acciones", "n_clicks"),

    State("datos_analisis", "data")
)
#Mostramos la descripcion de las acciones. otra funcion
def mostrar_descr_acciones(n_clicks, datos):

    if n_clicks is None:
        return ""

    if not datos:
        return "Primero pulsa Analizar"

    return datos["contraindicaciones"]



if __name__ == "__main__":
    app.run(debug=True)