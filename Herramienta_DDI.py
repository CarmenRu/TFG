from dash import Dash, html, dcc, dash_table, ctx
from dash import Input, Output, State
from textos import *
import pandas as pd

#Accedemos a los dos csv
DDI = pd.read_csv("DDI_sea.csv")
#Normalizamos los nombres
DDI["ppio_normalizado"] = DDI["Drug_name"].str.strip().str.casefold()
efectos = pd.read_csv("efectos_adversos.csv")


app = Dash(__name__)

app.layout = html.Div([

    # Entradas
    dcc.Input(
        id="ppio1",
        type="text",
        placeholder="Introduce el primer principio (en inglés)"
    ),

    dcc.Input(
        id="ppio2",
        type="text",
        placeholder="Introduce el segundo principio (en inglés)"
    ),

    # Botón principal
    html.Button(
        "Analizar",
        id="btn_analizar"
    ),

    html.Hr(),

    # Botones secundarios
    html.Button(
        "Explicacion enzimas",
        id="btn_enzimas"
    ),
    
    html.Button(
        "Efectos adversos",
        id="btn_efectos"
    ),

    html.Button(
        "Explicacion interacciones",   
        id="btn_interacciones"
    ),

    #Solo opciones?
    html.Button(
        "Opciones",
        id="btn_opciones"
    ),

    html.Hr(),

    # Almacenamiento interno
    dcc.Store(
        id="datos_analisis"
    ),
    # Salida que quiero que se quede siempre fija
    html.Div(
        id= "fijo"
    ),
    # Salida que va cambiando dependiendo en que boton se presione
    html.Div(
        id="resultado"
    )
    
])


@app.callback(
    Output("datos_analisis", "data"),
    Output("fijo", "children"),
    
    Input("btn_analizar", "n_clicks"),

    State("ppio1", "value"),
    State("ppio2", "value")
)

def analizar_farmacos(n_clicks, ppio1, ppio2):

    if n_clicks is None:
        return {}, ""

    if not ppio1 or not ppio2:
        return {}, "Introduce ambos principios activos"

    ppio1 = ppio1.strip().casefold()
    ppio2 = ppio2.strip().casefold()
    
    dic_resumen = interaccion (ppio1, ppio2, DDI)
    
    if not dic_resumen:
        return {}, html.Div([
            html.H3(f"Interacción {ppio1} - {ppio2}"),
            html.Pre(texto_principal(ppio1, ppio2, None, DDI))
        ])
    
    riesgo = dic_resumen["riesgo"]
    coincidentes = dic_resumen["interaccion"]
    enzimas1, enzimas2 = dic_resumen["enz1"], dic_resumen["enz2"]
    principales1, principales2 = dic_resumen["ppal1"], dic_resumen["ppal2"]
    
    cadena_texto = texto_principal(ppio1, ppio2, riesgo, DDI)
    
    intro_1 = texto_intro (ppio1, enzimas1, principales1, texto=False)
    intro_2 = texto_intro (ppio2, enzimas2, principales2, texto=False)
    
    texto_riesgo = calcular_riesgo (ppio1, ppio2,coincidentes, intro_1, intro_2, texto=True)
    
    return (dic_resumen, 
            
            html.Div([
                html.H3(f"Interacción {ppio1} - {ppio2}."),
                html.Pre(cadena_texto),
                html.Pre(texto_riesgo)
            ])
            
           )
    
@app.callback(
    Output("resultado", "children"),
    Input("btn_enzimas", "n_clicks"),
    Input("btn_efectos", "n_clicks"),
    Input("btn_interacciones", "n_clicks"),
    Input("btn_opciones", "n_clicks"),
    State("datos_analisis", "data")
)

def mostrar_resultado(n1, n2, n3, n4, datos):
    boton = ctx.triggered_id

    if boton is None:
        return ""

    if not datos:
        return "Primero pulsa Analizar o introduce valores validos como principios"
    
    #Recogemos las variables necesarias
    ppio1, ppio2 = datos["p1"], datos["p2"]
    e1, e2 = datos["enz1"], datos["enz2"]
    ppal1, ppal2 = datos["ppal1"], datos["ppal2"]
    ATC1, ATC2 = datos["ATC1"], datos["ATC2"]
    ATC_ref1, ATC_ref2 = datos["ref1"], datos["ref2"]
    df1, df2 = pd.DataFrame(datos["df1"]), pd.DataFrame(datos["df2"])
    coincidentes = datos["interaccion"]

    if boton == "btn_enzimas":
        
        primero = texto_intro (ppio1, e1, ppal1, texto=True, primero=True)
        segundo = texto_intro (ppio2, e2, ppal2, texto=True)
            
        return html.Div([
                    html.H2(f"Explicacion {ppio1}.\n"),
                    html.Pre(primero),
                    html.H2(f"Explicacion {ppio2}.\n"),
                    html.Pre(segundo)]
                    )

    elif boton == "btn_efectos":

        componentes = []
        
        #Codigo
        componentes.append(html.H2(f'----{ppio1}-----'))
        
        if len(ATC_ref1) == 0:
            componentes.append(
                html.P(f"No se ha podido encontrar ninguna alternativa para {ppio1}")
            )
            
        else:
            
            for ref in ATC_ref1:
                df = texto_efectos (ATC1, ref, efectos, ppio1)

                if not df:
                    componentes.extend([
                        html.Pre(f'No hay datos de efectos secundarios registrados en SIDDER para los codigos ATC con codigo de referencia {ref}.\n')

                    ])

                else:
                    componentes.extend([
                        html.Pre(f"Para el ATC de referencia {ref} los 10 posibles efectos adversos mas comunes son:"),
                
                        dash_table.DataTable(data=df.to_dict("records"),
                            columns=[{"name": c, "id": c} for c in df.columns])
                    ])
            
        componentes.append(html.H2(f'----{ppio2}-----'))
        
        if len(ATC_ref2) == 0:
            componentes.append(
                html.P(f"No se ha podido encontrar ninguna alternativa para {ppio2}")
            )
            
        else:
            
            for ref in ATC_ref2:
            
                df = texto_efectos (ATC2, ref, efectos, ppio2)

                if not df:
                    componentes.extend([
                        html.Pre(f'No hay datos de efectos secundarios registrados en SIDDER para los codigos ATC con codigo de referencia {ref}.\n')
                    ])

                else:
                    componentes.extend([
                        html.Pre(f"Para el ATC de referencia {ref} los 10 posibles efectos adversos mas comunes son:"),
                
                        dash_table.DataTable(data=df.to_dict("records"),
                            columns=[{"name": c, "id": c} for c in df.columns])
                    ])
        
        return html.Div(componentes)

    elif boton == "btn_interacciones":
        

        #Si hay interaccion entre ellas se mostrará en coincidentes, sino, la lista será vacia
        if not coincidentes:
            
            return html.Div([html.H3("Interacciones"),
                            html.P("No existen enzimas coincidentes entre ambos principios activos.")
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
                        html.H4(f"Enzima {e}"),
                        html.Pre(cadena)
                    ])
                )

            #Devolvemos lo almacenado en la variable textos
            return html.Div([
                html.H2(f"Interacciones entre {ppio1} y {ppio2}"),
                *textos
            ])

    elif boton == "btn_opciones":
        
        componentes = []
        alternativas_1 = []
        alternativas_2 = []
        
        #Codigo
        componentes.append(html.H2(f'----{ppio1}-----'))
        if not ATC1:
            #Poner opcion de introducir codigo ATC?
            componentes.append(
                html.Pre(f"No ha sido posible buscar alternativas del principio activo: {ppio1} debido a que no hay datos de cual es su código ATC.\n\n")
            )
        elif len(ATC_ref1) == 0:
            componentes.append(
                html.Pre(f"No se ha podido encontrar ninguna alternativa para {ppio1}.\n")
            )
        else:
            for ref in ATC_ref1:
                principios_1 = DDI[DDI['Drug_ATC'].str.startswith(ref, na=False)]["Drug_name"].unique().tolist()
                if principios_1:
                    alternativas_1.extend(principios_1)
                    componentes.extend([
                        html.Pre(f'Alternativas con codigo ATC de referencia: {ref} para el principio {ppio1}.\n'),
                        html.P(principios_1)
                    ])
                else:
                    componentes.append(
                        html.Pre(f"No ha sido posible encontrar una opción factible para el principio: {ppio1} con el ATC de referencia: {ref}.\n\n")
                    )
            

        componentes.append(html.H2(f'----{ppio2}-----'))
        if not ATC2:
            #Poner opcion de introducir codigo ATC?
            componentes.append(
                html.Pre(f"No ha sido posible buscar alternativas del principio activo: {ppio2} debido a que no hay datos de cual es su código ATC.\n\n")
            )
        elif len(ATC_ref2) == 0:
            componentes.append(
                html.P(f"No se ha podido encontrar ninguna alternativa para {ppio2}")
            )
        else:
            for ref in ATC_ref2:
                principios_2 = DDI[DDI['Drug_ATC'].str.startswith(ref, na=False)]["Drug_name"].unique().tolist()
                if principios_2:
                    alternativas_2.extend(principios_2)
                    componentes.extend([
                        html.Pre(f'Alternativas con codigo ATC de referencia: {ref} para el principio {ppio2}.\n'),
                        html.P(principios_2)
                    ])
                else:
                    componentes.append(
                        html.Pre(f"No ha sido posible encontrar una opción factible para el principio: {ppio1} con el ATC de referencia: {ref}.\n\n")
                    )

        if alternativas_1 or alternativas_2:
            opciones = opciones_ATC(alternativas_1, alternativas_2, ppio1, ppio2, DDI)
            if opciones:
                componentes.extend([
                    html.Pre("Las combinaciones posibles son:\n"),
                    html.Ul([
                        html.Li(f"{a} - {b}")
                        for a,b in opciones
                    ])
                ])
                
            else:
                componentes.append(
                    html.Pre("No ha habido ninguna combinacion factible.\n")
                )
                #Es posible que aqui pueda volver a llamar a la funcion pero con un número menos de i???
        else:
            componentes.append(
                    html.Pre("No hay alternativas posibles.\n")
                )

            
        return html.Div([
                html.H2(f"Alternativas para {ppio1} y {ppio2}"),
                *componentes
            ])
    
    return "Ningun boton válido"

if __name__ == "__main__":
    app.run(debug=True)