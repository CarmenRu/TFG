from dash import Dash, html, dcc
from dash import Input, Output, State
from textos import *
import pandas as pd

#Accedemos a los dos csv
DDI = pd.read_csv("DDI_sea.csv")
efectos = pd.read_csv("efectos_adversos.csv")


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

    State("ppio1", "value"),
    State("ppio2", "value")
)
def analizar_farmacos(n_clicks, farmaco1, farmaco2):

    if n_clicks is None:
        return {}

    if not ppio1 or not ppio2:
        return {}

    DDI["ppio_normalizado"] = DDI["Drug_name"].str.strip().str.casefold()
    ppio1 = ppio1.strip().casefold()
    ppio2 = ppio2.strip().casefold()
    dic_resumen = interaccion (ppio1, ppio2, DDI)

    return dic_resumen

#VARIOS CALLBACK NECESARIOS EN ESTE CASO
@app.callback(
    Output("resultado", "children"),

    Input("btn_efectos", "n_clicks"),

    State("datos_analisis", "data")
)
#Ver primero como saco los ATC de referencia
def mostrar_efectos(n_clicks, datos):

    if n_clicks is None:
        return ""

    if not dic_resumen:
        return "Primero pulsa Analizar"

    return 


@app.callback(
    Output("resultado", "children"),

    Input("btn_interacciones", "n_clicks"),

    State("datos_analisis", "data")
)
def mostrar_interacciones(n_clicks, datos):

    if n_clicks is None:
        return ""

    if not dic_resumen:
        return "Primero pulsa Analizar"

    df_1 = dic_resumen[ppio1][0]
    df_2 = dic_resumen[ppio2][0]
    coincidentes = dic_resumen["interaccion"]
    #Si hay interaccion entre ellas se mostrará en coincidentes, sino, la lista será vacia
    if coincidentes:
        #Sacar las acciones y el texto sera para cada enzima por separado
        if texto:
            for e in coincidentes:
                #La fila q contiene la enzima que se quiere ver
                fila_1 = df_1[df_1["Gene_name"]==e]
                #Separamos por si tiene | (no da error si no lo tiene)
                separado_1 = fila_1["Accion"].str.split(r"\|")
                #Nos quedamos con los distintos
                acciones_1 = set(separado_1.explode().tolist())
    
                #Lo mismo pero con el otro principio consultado
                fila_2 = df_2[df_2["Gene_name"]==e]
                separado_2 = fila_2["Accion"].str.split(r"\|")
                acciones_2 = set(separado_2.explode().tolist())
    
                #Funcion que contiene el texto
                texto_acciones(ppio_1,acciones_1,ppio_2,acciones_2,e) #PARA CADA ENZIMA
                
    return 


@app.callback(
    Output("resultado", "children"),

    Input("btn_contraindicaciones", "n_clicks"),

    State("datos_analisis", "data")
)
def mostrar_opciones(n_clicks, datos):

    if n_clicks is None:
        return ""

    if not dic_resumen:
        return "Primero pulsa Analizar"

    riesgo = dic_resumen["riesgo"]
    df_1 = dic_resumen[ppio1][0]
    df_2 = dic_resumen[ppio2][0]
    if riesgo=="Alta" or riesgo=="Media":   
        ATC_1 = df_1["Drug_ATC"].unique().tolist()
        ATC_2 = df_2["Drug_ATC"].unique().tolist()
        opciones = opciones_ATC(DDI, efectos, ATC_1, ATC_2, ppio1, ppio2)
        
    return opciones



if __name__ == "__main__":
    app.run(debug=True)