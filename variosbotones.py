from dash import Dash, html, dcc
from dash import Input, Output, State

#Fallido por?

app = Dash(__name__)

app.layout = html.Div([

    # Entradas
    dcc.Input(
        id="farmaco1",
        type="text",
        placeholder="Primer fármaco"
    ),

    dcc.Input(
        id="farmaco2",
        type="text",
        placeholder="Segundo fármaco"
    ),

    # Botón principal
    html.Button(
        "Analizar",
        id="btn_analizar"
    ),

    html.Hr(),

    # Botones secundarios
    html.Button(
        "Efectos adversos",
        id="btn_efectos"
    ),

    html.Button(
        "Interacciones",
        id="btn_interacciones"
    ),

    html.Button(
        "Contraindicaciones",
        id="btn_contraindicaciones"
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

    Input("btn_analizar", "n_clicks"),

    State("farmaco1", "value"),
    State("farmaco2", "value")
)
def analizar_farmacos(n_clicks, farmaco1, farmaco2):

    if n_clicks is None:
        return {}

    if not farmaco1 or not farmaco2:
        return {}

    # AEjemplo
    datos = {
        "efectos": f"Efectos adversos de {farmaco1} y {farmaco2}",
        "interacciones": f"Interacciones entre {farmaco1} y {farmaco2}",
        "contraindicaciones": f"Contraindicaciones de {farmaco1} y {farmaco2}"
    }

    return datos

#VARIOS CALLBACK NECESARIOS EN ESTE CASO
@app.callback(
    Output("resultado", "children"),

    Input("btn_efectos", "n_clicks"),

    State("datos_analisis", "data")
)
def mostrar_efectos(n_clicks, datos):

    if n_clicks is None:
        return ""

    if not datos:
        return "Primero pulsa Analizar"

    return datos["efectos"]


@app.callback(
    Output("resultado", "children"),

    Input("btn_interacciones", "n_clicks"),

    State("datos_analisis", "data")
)
def mostrar_interacciones(n_clicks, datos):

    if n_clicks is None:
        return ""

    if not datos:
        return "Primero pulsa Analizar"

    return datos["interacciones"]


@app.callback(
    Output("resultado", "children"),

    Input("btn_contraindicaciones", "n_clicks"),

    State("datos_analisis", "data")
)
def mostrar_contraindicaciones(n_clicks, datos):

    if n_clicks is None:
        return ""

    if not datos:
        return "Primero pulsa Analizar"

    return datos["contraindicaciones"]



if __name__ == "__main__":
    app.run(debug=True)