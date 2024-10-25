import csv
import json

# Nombre del archivo CSV
archivo_csv = 'users.csv'
# Nombre del archivo JSON de salida
archivo_json = 'users.json'

# Abrir el archivo CSV y leer sus datos
with open(archivo_csv, 'r') as csv_file:
    # Lee el archivo CSV
    csv_reader = csv.DictReader(csv_file)
    
    # Convierte cada fila del CSV a un diccionario y agrega a una lista
    datos = [fila for fila in csv_reader]

# Escribe los datos en formato JSON en un archivo de salida
with open(archivo_json, 'w') as json_file:
    # Escribe los datos como JSON en el archivo de salida
    json.dump(datos, json_file, indent=4)