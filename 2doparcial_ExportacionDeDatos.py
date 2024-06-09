#Valentina Dominguez
#Fabrizio Chera
import pandas as pd
import os

# Define la carpeta de destino
nombre_carpeta = 'output_data'

# Crea la carpeta si no existe
os.makedirs(nombre_carpeta, exist_ok=True)

# Carga la base de datos sin modificar los indices
data2 = pd.read_csv('electricity-consumption-processed.csv')

# Agrupar por subestacion y linea
grouped = data2.groupby(['substation', 'feeder'])

# Crear y exportar un archivo CSV para cada subestacion y linea
for (substation, feeder), group in grouped:
    # Crear una copia del grupo para asegurar que el original no se modifique
    group_copy = group.copy()
    # Crear el nombre del archivo
    filename = f'{substation}_{feeder}.csv'
    # Generar la ruta completa del archivo
    file_path = os.path.join(nombre_carpeta, filename)
    # Exportar el grupo a un archivo CSV
    group_copy.to_csv(file_path, index=False)
    print(f"Archivo {file_path} generado y exportado.")

print("Exportacion completada.")