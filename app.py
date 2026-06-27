from dash import Dash, html, dcc,  ctx
from dash import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from textos import *
import pandas as pd

#Accedemos a los dos csv
DDI = pd.read_csv("DDI_sea.csv")
#Normalizamos los nombres
DDI["ppio_normalizado"] = DDI["Drug_name"].str.strip().str.casefold()
efectos = pd.read_csv("efectos_adversos.csv")
efectos["Freq_media"] = efectos["Freq_media"]*100
#Estilo base
recortar = {"whiteSpace": "pre-wrap", "overflowWrap": "break-word", "width": "100%"}


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

#Definimos esilos
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "18rem",
    "padding": "1rem",
    "backgroundColor": "#f8f9fa",
    "borderRight": "1px solid #dee2e6",
}

CONTENT_STYLE = {
    "marginLeft": "20rem",
    "marginRight": "2rem",
    "padding": "1rem",
}

sidebar = html.Div([
    html.Div([
        html.H3("Drug Analysis"),
        # Inputs
        dcc.Input(
            id="ppio1",
            type="text",
            placeholder="Enter the first active ingredient"
        ),
        html.Br(),
        html.Br(),

        dcc.Input(
            id="ppio2",
            type="text",
            placeholder="Enter the second active ingredient"
        ),
        html.Br(),
        html.Br(),

        # Botón principal
        dbc.Button(
            "Search interaction",
            id="btn_analizar",
            color = "primary",
            style={"width": "100%"}
        ),
        html.Hr(),

        dbc.Nav([
                dbc.NavLink("Enzyme explanation", id="btn_enzimas", active="exact"),
                dbc.NavLink("Adverse effects", id="btn_efectos", active="exact"),
                dbc.NavLink("Interaction explanation", id="btn_interacciones", active="exact"),
                dbc.NavLink("Options", id="btn_opciones", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
        # Almacenamiento interno
        dcc.Store(id="datos_analisis"),

    ], style=SIDEBAR_STYLE
    )
])


contenido = html.Div(
    [
        #Logo de la imagen
        html.Img(
            src="assets/interaccion.png",
            style={
                "width": "30%",
                "marginBottom": "10px"
            }
        ),
        html.Hr(),
        html.Div(id="fijo"),
        html.Br(),
        html.Div(id="resultado")
    ],
    style=CONTENT_STYLE
)

#layout
app.layout = html.Div([sidebar,contenido])

@app.callback(
    Output("datos_analisis", "data"),
    Output("fijo", "children"),

    Input("btn_analizar", "n_clicks"),

    State("ppio1", "value"),
    State("ppio2", "value")
)

def analizar_farmacos(n_clicks, ppio1, ppio2):

    if not n_clicks :
        txt = texto_intro(texto=True, primero=True)
        return {}, html.Pre(txt,
                            style=recortar)

    if not ppio1 or not ppio2:
        return {}, "Enter both active ingredients"

    ppio1 = ppio1.strip().casefold()
    ppio2 = ppio2.strip().casefold()
    
    dic_resumen = interaccion (ppio1, ppio2, DDI)
    
    if not dic_resumen:
        txt = texto_principal(ppio1, ppio2, DDI)
        return {}, html.Div([
            html.H1(f"Interaction {ppio1} - {ppio2}"),
            html.Pre(txt, style = recortar)
        ])
    
    riesgo = dic_resumen["riesgo"]
    coincidentes = dic_resumen["interaccion"]
    enzimas1, enzimas2 = dic_resumen["enz1"], dic_resumen["enz2"]
    principales1, principales2 = dic_resumen["ppal1"], dic_resumen["ppal2"]
    
    cadena_texto = texto_principal(ppio1, ppio2, DDI)
    
    intro_1 = texto_intro (ppio1, enzimas1, principales1, texto=False)
    intro_2 = texto_intro (ppio2, enzimas2, principales2, texto=False)
    
    texto_riesgo = calcular_riesgo (ppio1, ppio2,coincidentes, intro_1, intro_2, texto=True)

    if riesgo == "Alta":
        riesgo_ingles = "High"
        color_riesgo = "#f9051d"   
    elif riesgo == "Media":
        riesgo_ingles = "Medium"
        color_riesgo = "#ffff07"     
    else:
        riesgo_ingles = "low"
        color_riesgo = "#00FF48"   
    
    cajacolor_riesgo = html.Span(
        riesgo_ingles.upper(),
        style={
            "backgroundColor": color_riesgo,
            "color": "white",
            "padding": "5px 12px",
            "borderRadius": "8px",
            "fontWeight": "bold",
            "marginLeft": "10px"
        }
    )
        
    return (dic_resumen, 
            
            html.Div([
                html.H1(f"Interaction {ppio1} - {ppio2}."),
                html.Div(cajacolor_riesgo),
                html.Br(),
                html.Pre(cadena_texto, style = recortar),
                html.Details([
                    html.Summary("?",
                        style={
                            "cursor": "pointer",
                            "fontWeight": "bold",
                            "color": "#320ee8"}
                    ),
                    html.Pre(texto_riesgo,
                        style={
                            "whiteSpace": "pre-wrap",
                            "wordBreak": "break-word",
                            "marginTop": "10px",
                            "backgroundColor": "#0dfdfd",
                            "padding": "10px",
                            "borderRadius": "5px"}
                    )
                    
                ])
                
            ])
            
        )
    
@app.callback(
    Output("resultado", "children"),
    Input("btn_analizar", "n_clicks"),
    Input("btn_enzimas", "n_clicks"),
    Input("btn_efectos", "n_clicks"),
    Input("btn_interacciones", "n_clicks"),
    Input("btn_opciones", "n_clicks"),
    State("datos_analisis", "data")
)

def mostrar_resultado(n1, n2, n3, n4, n5, datos):
    boton = ctx.triggered_id

    if boton is None:
        return ""

    if not datos:
        return "First enter valid values as active ingredients, then press Search Ineractions. Later press one of the options"
    
    #Recogemos todas las variables 
    ppio1, ppio2 = datos["p1"], datos["p2"]
    e1, e2 = datos["enz1"], datos["enz2"]
    ppal1, ppal2 = datos["ppal1"], datos["ppal2"]
    ATC1, ATC2 = datos["ATC1"], datos["ATC2"]
    ATC_ref1, ATC_ref2 = datos["ref1"], datos["ref2"]
    df1, df2 = pd.DataFrame(datos["df1"]), pd.DataFrame(datos["df2"])
    coincidentes = datos["interaccion"]

    if boton == "btn_analizar":
        return ""

    elif boton == "btn_enzimas":
        
        primero = texto_intro (ppio1, e1, ppal1, texto=True)
        segundo = texto_intro (ppio2, e2, ppal2, texto=True)
            
        return html.Div([
                    html.H3(f"Enzymes {ppio1}.\n"),
                    html.Pre(primero, style = recortar),
                            
                    html.H3(f"Enzymes {ppio2}.\n"),
                    html.Pre(segundo, style = recortar)
                    ])

    elif boton == "btn_efectos":

        componentes = []
        
        #Código
        componentes.append(html.H2(f'----{ppio1}-----'))
        
        if not ATC_ref1:
            componentes.append(
                html.P(f"No alternatives could be found for {ppio1}")
            )
            
        else:
            
            for ref in ATC_ref1:
                df = texto_efectos (ATC1, ref, efectos, ppio1)

                if df is None or df.empty:
                    componentes.extend([
                        html.Pre(f'No adverse effect data recorded in SIDDER for ATC codes with reference code {ref}.\n')

                    ])

                else:
                    fig = go.Figure(
                        data=[go.Bar(
                                x=df["Side_effect"],
                                y=df["Freq_media"]
                                )
                            ]
                        )

                    fig.update_layout(
                        title=f"Most common adverse effects for reference {ref}",
                        xaxis_title="Adverse effect",
                        yaxis_title="Frequency",
                        height=500
                    )

                    componentes.extend([
                        dcc.Graph(
                            figure=fig,
                            config={"displayModeBar": False}
                        )
                    ])
            
        componentes.append(html.H2(f'----{ppio2}-----'))
        
        if not ATC_ref2:
            componentes.append(
                html.P(f"No alternatives could be found for {ppio2}")
            )
            
        else:
            
            for ref in ATC_ref2:
            
                df = texto_efectos (ATC2, ref, efectos, ppio2)

                if df is None or df.empty:
                    componentes.extend([
                        html.Pre(f'No adverse effect data recorded in SIDDER for ATC codes with reference code {ref}.\n')
                    ])

                else:
                    fig = go.Figure(
                        data=[go.Bar(
                                x=df["Side_effect"],
                                y=df["Freq_media"]
                                )
                            ]
                        )

                    fig.update_layout(
                        title=f"Most common adverse effects for reference {ref}",
                        xaxis_title="Adverse effect",
                        yaxis_title="Frequency",
                        height=500
                    )

                    componentes.extend([
                        dcc.Graph(
                            figure=fig,
                            config={"displayModeBar": False}
                        )
                    ])
        
        return html.Div(componentes)

    elif boton == "btn_interacciones":
        

        #Si hay interaccion entre ellas se mostrará en coincidentes, sino, la lista será vacia
        if not coincidentes:
            
            return html.Div([html.H3("Interactions"),
                            html.P("No coincident enzymes exist between both active ingredients.")
                            ])
            
        else:
            #Donde se almacena el texto que quiero sacar
            textos = []
            
            #Sacar las acciones y el texto sera para cada enzima por separado
            for e in coincidentes:
                #La fila q contiene la enzima que se quiere ver
                fila_1 = df1[df1["Gene_name"] == e]
                #Separamos por si tiene | (no da error si no lo tiene)
                separado_1 = fila_1["Accion"].str.split(r"\|")
                #Nos quedamos con los distintos
                acciones_1 = set(separado_1.explode().tolist())
        
                #Lo mismo pero con el otro principio consultado
                fila_2 = df2[df2["Gene_name"]==e]
                separado_2 = fila_2["Accion"].str.split(r"\|")
                acciones_2 = set(separado_2.explode().tolist())

                #Funcion que contiene el texto
                cadena = texto_acciones(ppio1,acciones_1,ppio2,acciones_2,e) #PARA CADA ENZIMA EN COINCIDENTES
                
                textos.append(
                    html.Div([
                        html.H4(f"Enzyme {e}"),
                        html.Pre(cadena, style = recortar)
                    ])
                )

            #Devolvemos lo almacenado en la variable textos
            return html.Div([
                html.H3(f"Interactions between {ppio1} and {ppio2}"),
                *textos
            ])


    elif boton == "btn_opciones":

        componentes = []
        alternativas_1 = []
        alternativas_2 = []

        #Ppio1
        contenido_ppio1 = []

        if not ATC1:
            contenido_ppio1.append(
                dbc.Alert(
                    f"No ATC code data available for {ppio1}",
                    color="danger"
                )
            )

        elif len(ATC_ref1) == 0:
            contenido_ppio1.append(
                dbc.Alert(
                    f"No alternatives found for {ppio1}",
                    color="warning"
                )
            )

        else:
            for ref in ATC_ref1:
                principios_1 = DDI[
                    DDI['Drug_ATC'].str.startswith(ref, na=False)
                ]["Drug_name"].unique().tolist()

                if principios_1:
                    alternativas_1.extend(principios_1)

                    contenido_ppio1.append(
                        dbc.Card([
                            dbc.CardHeader(f"ATC Ref: {ref}"),
                            dbc.CardBody(
                                html.Ul([
                                    html.Li(ppio) for ppio in principios_1
                                ])
                            )
                        ], className="mb-2")
                    )
                else:
                    contenido_ppio1.append(
                        dbc.Alert(
                            f"No options for ATC {ref}",
                            color="secondary"
                        )
                    )

        componentes.append(
            dbc.Card([
                dbc.CardHeader(html.H4(ppio1)),
                dbc.CardBody(contenido_ppio1)
            ], className="mb-4")
        )

        #Ppio2
        contenido_ppio2 = []

        if not ATC2:
            contenido_ppio2.append(
                dbc.Alert(
                    f"No ATC code data available for {ppio2}",
                    color="danger"
                )
            )

        elif len(ATC_ref2) == 0:
            contenido_ppio2.append(
                dbc.Alert(
                    f"No alternatives found for {ppio2}",
                    color="warning"
                )
            )

        else:
            for ref in ATC_ref2:
                principios_2 = DDI[
                    DDI['Drug_ATC'].str.startswith(ref, na=False)
                ]["Drug_name"].unique().tolist()

                if principios_2:
                    alternativas_2.extend(principios_2)

                    contenido_ppio2.append(
                        dbc.Card([
                            dbc.CardHeader(f"ATC Ref: {ref}"),
                            dbc.CardBody(
                                html.Ul([
                                    html.Li(ppio) for ppio in principios_2
                                ])
                            )
                        ], className="mb-2")
                    )
                else:
                    contenido_ppio2.append(
                        dbc.Alert(
                            f"No options for ATC {ref}",
                            color="secondary"
                        )
                    )

        componentes.append(
            dbc.Card([
                dbc.CardHeader(html.H4(ppio2)),
                dbc.CardBody(contenido_ppio2)
            ], className="mb-4")
        )

        # Combinaciones
        if alternativas_1 or alternativas_2:

            opciones = opciones_ATC(alternativas_1, alternativas_2, ppio1, ppio2, DDI)

            if opciones:

                principales_1 = [
                    html.Li(f"{a} - {b}")
                    for a, b in opciones if a == ppio1
                ]

                principales_2 = [
                    html.Li(f"{a} - {b}")
                    for a, b in opciones if b == ppio2
                ]

                otras = [
                    html.Li(f"{a} - {b}")
                    for a, b in opciones if (a != ppio1 or b != ppio2)
                ]

                componentes.append(
                    dbc.Card([
                        dbc.CardHeader(html.H4("Possible combinations")),

                        dbc.CardBody([

                            dbc.Row([

                                dbc.Col(
                                    dbc.Card([
                                        dbc.CardHeader(f"For {ppio1}"),
                                        dbc.CardBody(html.Ul(principales_1))
                                    ]),
                                    width=6
                                ),

                                dbc.Col(
                                    dbc.Card([
                                        dbc.CardHeader(f"For {ppio2}"),
                                        dbc.CardBody(html.Ul(principales_2))
                                    ]),
                                    width=6
                                )

                            ], className="mb-3"),

                            html.H5("Other alternatives"),
                            html.Ul(otras)

                        ])
                    ])
                )

            else:
                componentes.append(
                    dbc.Alert(
                        "No feasible combination found",
                        color="danger"
                    )
                )

        else:
            componentes.append(
                dbc.Alert(
                    "No possible alternatives",
                    color="secondary"
                )
            )

        return dbc.Container([
            html.H2(
                f"Alternatives for {ppio1} and {ppio2}",
                className="mb-4"
            ),
            *componentes
        ], fluid=True)
    
    return "No valid button"

if __name__ == "__main__":
    app.run(debug=True)
