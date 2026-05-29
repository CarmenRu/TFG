from dash import Dash, html, dcc, Input, Output, State

app = Dash(__name__)

app.layout = html.Div([

    dcc.Input(
        id='numero',
        type='number',
        placeholder='Escribe un número'
    ),

    html.Button(
        'Sumar 1',
        id='boton'
    ),

    html.Div(id='resultado')
])

@app.callback(
    Output('resultado', 'children'),

    Input('boton', 'n_clicks'),
    #No hace nada hasta que no se presiona el boton
    State('numero', 'value')
)
def sumar_uno(clicks, valor):

    if valor is None:
        return "Introduce un número"

    return f'Resultado: {valor + 1}'

if __name__ == "__main__":
    app.run(debug=True)