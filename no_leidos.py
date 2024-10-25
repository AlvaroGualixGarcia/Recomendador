import pandas as pd
from collections import defaultdict
import random

# Carga de datos (asumiendo que los datos se cargan correctamente)
usuarios = pd.read_csv('Users.csv')
calificaciones = pd.read_csv('Ratings.csv')
dtype_dict = {'ISBN': str,
              'Book-Title': str,
              'Book-Author': str,
              'Year-Of-Publication': str,
              'Publisher': str,
              'Image-URL-S': str,
              'Image-URL-M': str,
              'Image-URL-L': str}
libros = pd.read_csv("Books.csv", dtype=dtype_dict)

# Combinar los 3 csv primero utilizando como key el id de usuario, y luego con la que optenemos el ISBN de los libros
datos_combinados = pd.merge(pd.merge(usuarios, calificaciones, on='User-ID'), libros, on='ISBN')

# Usuario deseado, podria ser un imput dentro de una aplicacion
usuario_deseado = 67544  # Cambia esto al ID del usuario que desees verificar

# Recoger IDs únicos de usuarios en una lista
user_ids = datos_combinados['User-ID'].unique().tolist()

# Obtener 1000 usuarios aleatorios de la lista de usuarios
lista_usuarios_aleatorios = random.sample(user_ids, 1000)   # Ajusta este número según tu disponibilidad de memoria, que explota si se le meten 10000

# Comprueba si el usuario deseado no está entre los 1000 usuarios aleatorios
if usuario_deseado not in lista_usuarios_aleatorios:
    # y lo agrega
    lista_usuarios_aleatorios.append(usuario_deseado)

# Comprueba si el usuario deseado está entre los 1000 usuarios aleatorios
if usuario_deseado in lista_usuarios_aleatorios:
    
    # Filtra el conjunto de datos solo con los 1001 usuarios aleatorios recogidos anteriormente
    usuarios_filtrados = datos_combinados[datos_combinados['User-ID'].isin(lista_usuarios_aleatorios)]

    # Calcula una matriz de usuario-libro con las calificaciones
    matriz_calificaciones = usuarios_filtrados.pivot_table(index='User-ID', columns='ISBN', values='Book-Rating')
    matriz_calificaciones = matriz_calificaciones.fillna(0)

    # Verificación si el usuario objetivo está presente en los datos
    if usuario_deseado in matriz_calificaciones.index:
        
        # Obtener títulos de libros correspondientes a los ISBNs
        titulos = dict(zip(libros['ISBN'], libros['Book-Title']))
       
        #variable para guardar los libros
        libros_recomendados = defaultdict(int)

        # Buscar libros no calificados por el usuario objetivo
        libros_no_calificados = matriz_calificaciones.loc[usuario_deseado][matriz_calificaciones.loc[usuario_deseado] == 0]
        libros_no_calificados = libros_no_calificados.index.map(titulos)
        
        # Obtener los títulos de los primeros 10 libros recomendados
        for title in libros_no_calificados[:10]:
            libros_recomendados[title] = 0

        # Muestra los títulos de libros recomendados al usuario objetivo
        print("\nLibros recomendados para el usuario {}: ".format(usuario_deseado))
        for titulo in libros_recomendados:
            print("Título:", titulo)
        
    else:
        print(f"El usuario {usuario_deseado} no está presente entre los 1000 usuarios aleatorios.")
else:
    print(f"El usuario {usuario_deseado} no existe.")