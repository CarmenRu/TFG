#Prueba de escribir un número y que me devuelva una suma
from dash import Dash, html, dcc, Input, Output

app = Dash(__name__)

app.layout = html.Div([

    dcc.Input(
        id='numero',
        type='number',
        placeholder='Introduce un número aqui'
    ),

    dcc.Input(
        id = 'numero2',
        type = 'number',
        placeholder = "Introduce aqui otro número"
    ),

    #Ejecuta el resultado como putput
     html.Div(id='resultado')
])

@app.callback(
    Output('resultado', 'children'),

    Input('numero', 'value'),
    Input('numero2','value')
)
#Van en el orden de inputs
#Si tengo mas de un input pero aqui solo quiero meter dos?
def suma(valor, valor2):
    if not valor or not valor2:
        return "Esperando"
    
    return f'Suma ambos valores: {valor+valor2}'

if __name__ == "__main__":
    app.run(debug=True)