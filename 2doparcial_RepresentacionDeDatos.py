#Valentina Dominguez
#Fabrizio Chera

#LIBRERIAS
#pip install pandas
#pip install dash
#pip install plotly
 
###########################################################################################################################################################################

#  Code            Nombre                               Coords                    Nro de lineas o "feeders"
#   A    Estación Carlos Antonio López   –26.4404871349547   −54.7136488737980               2
#   B    Estación Campo Dos              –25.4132596331584   −55.5981466068710               6
#   C    Estación Itakyry                –24.9947877793220   –55.0748758141749               2
#   D    Subestación Paranambú           –25.8654409111292   –54.7673282080658               3
#   E    Estación Presidente Franco      –25.5242877755251   –54.6602730153911               7
#   F    Estación Salto del Guairá       –23.9859149118054   –54.3864868736447               2
#   G    Subestación Acaray              –25.4585684512157   –54.6236968644649               4
#   H    Subestación Alto Paraná         –25.5084506698273   –54.6322944725499               5
#   I    Subestación Catuete             −24.2581146985867   −54.7811690468161               5
#   J    Subestación Curuguaty           −24.4505596855661   −55.6825562061486               1
#   K    Subestación del Este            −25.5310680456045   −54.6175315957382               3           
#   L    Subestación Hernandarias        −25.4383964995769   −54.6333843509485               4
#   M    Subestación Km 30               −25.4783908524517   −54.8763969418319               7
#   N    Subestación Naranjal            −25.9884463723231   −55.0319767147661               4

#Ejemplos de la sintaxis del dataset: 3ra linea de la substacion 'M' = M3 ; 4ta linea de la subestacion 'N' = N4 ; 1ra linea de la subestacion 'D' = D1

###########################################################################################################################################################################

#DIRECCION PARA VER GRAFICOS(PEGAR EN EL NAVEGADOR) http://127.0.0.1:8050/

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
from datetime import datetime as dt

# Cargamos las bases de datos
data1 = pd.read_csv('meteorological-processed.csv', parse_dates = True, index_col='datetime')
data2 = pd.read_csv('electricity-consumption-with-predictions.csv', parse_dates = True, index_col='datetime')

print(data1.head())
print(data2.head())

# Busqueda de valores nulos en "data1"
valores_nulos_data1_Temp = data1['temperature'].isnull().sum()
valores_nulos_data1_Hu = data1['humidity'].isnull().sum()
valores_nulos_data1_Wind = data1['wind_speed'].isnull().sum()
valores_nulos_data1_Pr = data1['pressure'].isnull().sum()

print(f"Recuento de valores nulos en la columna 'temperature': {valores_nulos_data1_Temp}")
print(f"Recuento de valores nulos en la columna 'humidity': {valores_nulos_data1_Hu}")
print(f"Recuento de valores nulos en la columna 'wind_speed': {valores_nulos_data1_Wind}")
print(f"Recuento de valores nulos en la columna 'pressure': {valores_nulos_data1_Pr}")

# Busqueda de valores nulos en "data2"
valores_nulos_data2_substation = data2['substation'].isnull().sum()
valores_nulos_data2_feeder = data2['feeder'].isnull().sum()
valores_nulos_data2_consumption = data2['consumption'].isnull().sum()

print(f"Recuento de valores nulos en la columna 'substation': {valores_nulos_data2_substation}")
print(f"Recuento de valores nulos en la columna 'feeder': {valores_nulos_data2_feeder}")
print(f"Recuento de valores nulos en la columna 'consumption': {valores_nulos_data2_consumption}")

# Como vemos hay bastantes datos 'nulos' principalmente en el dataset de consumo de electricidad
# Vamos a filtrar los datos faltantes por subestacion y por linea para saber en donde tenemos mas datos faltantes

datos_faltantes_por_subestacion = data2.groupby('substation')['consumption'].apply(lambda x: x.isnull().sum())
datos_faltantes_por_alimentador = data2.groupby('feeder')['consumption'].apply(lambda x: x.isnull().sum())

print("Cantidad de datos faltantes por subestacion:")
print(datos_faltantes_por_subestacion)

print("\nCantidad de datos faltantes por linea:")
print(datos_faltantes_por_alimentador)


#Graficamos

app = Dash(__name__)

# Layout de la aplicación con ajustes de estilo
app.layout = html.Div([
    html.H1("Consumo de energia por linea"),
    dcc.Dropdown(
        id='feeder-dropdown',
        options=[{'label': feeder, 'value': feeder} for feeder in data2['feeder'].unique()],
        multi=True,
        value=[data2['feeder'].unique()[0]],  # Valor inicial con la primera linea
        placeholder="Selecciona los feeders a graficar"
    ),
    html.Div([
        dcc.DatePickerRange(
            id='date-picker-range',
            start_date=data2.index.min(),
            end_date=data2.index.max(),
            display_format='YYYY-MM-DD',
            clearable=True,
            persistence=True,
            persistence_type='session'
        )
    ], style={'margin-bottom': '20px'}),
    html.Div(
        dcc.Graph(id='consumption-graph'),
        style={'width': '100%', 'height': '90vh'}  # Ajusta el tamaño del gráfico
    )
])

# Callback para actualizar el grafico basado en la selección del dropdown y el rango de fechas

@app.callback(
    Output('consumption-graph', 'figure'),
    [Input('feeder-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_graph(selected_feeders, start_date, end_date):
    if not selected_feeders:  # Manejo de caso donde no se selecciona ninguna linea
        return {}

    if isinstance(selected_feeders, str):  # Convertir a lista si es una sola seleccion
        selected_feeders = [selected_feeders]

    filtered_data = data2[data2['feeder'].isin(selected_feeders)]
    filtered_data = filtered_data.sort_index()  # Ordenar el índice de fechas
    filtered_data = filtered_data.loc[start_date:end_date]  # Aplicar el filtro por rango de fechas

    if filtered_data.empty:  # Manejo de caso donde no hay datos para mostrar
        return {}

    fig = px.line(filtered_data, x=filtered_data.index, y='consumption', color='feeder',
                  title='Consumo de energia por linea en funcion del tiempo')
    fig.update_layout(xaxis_title='Fecha', yaxis_title='Consumo (A)', legend_title='Lineas')
    fig.update_xaxes(showgrid=True)  # Mostrar cuadrícula en el eje X
    fig.update_yaxes(showgrid=True)  # Mostrar cuadrícula en el eje Y
    return fig

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)