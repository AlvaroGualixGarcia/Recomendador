import pandas as pd
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity
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

datos_combinados = pd.merge(pd.merge(usuarios, calificaciones, on='User-ID'), libros, on='ISBN')

def recomendar_libros(usuario_deseado):
    # Recoger IDs únicos de usuarios en una lista
    ids_usuarios = datos_combinados['User-ID'].unique().tolist()

    # Obtener 1000 usuarios aleatorios de la lista de usuarios
    lista_usuarios_aleatorios = random.sample(ids_usuarios, 1000)   # Ajusta este número según tu disponibilidad de memoria

    # Si el usuario deseado no está entre los 1000 usuarios aleatorios, agrégalo
    if usuario_deseado not in lista_usuarios_aleatorios:
        lista_usuarios_aleatorios.append(usuario_deseado)

    # Comprueba si el usuario deseado está entre los 1000 usuarios aleatorios
    if usuario_deseado in lista_usuarios_aleatorios:
        
        # Filtra el conjunto de datos solo con los 1001 usuarios aleatorios recogidos anteriormente
        usuarios_filtrados = datos_combinados[datos_combinados['User-ID'].isin(lista_usuarios_aleatorios)]

        # Calcula una matriz de usuario-libro con las calificaciones
        matriz_calificaciones = usuarios_filtrados.pivot_table(index='User-ID', columns='ISBN', values='Book-Rating')
        matriz_calificaciones = matriz_calificaciones.fillna(0)

        # Calcular similitud entre usuarios usando la medida del coseno segun las calificaciones del usuario
        similitud_usuarios = cosine_similarity(matriz_calificaciones)

        # Obtener el índice del usuario deseado en la lista de usuarios aleatorios
        indice_usuario = lista_usuarios_aleatorios.index(usuario_deseado)

        # Encuentra los usuarios más similares al usuario deseado
        similitudes_usuario_deseado = similitud_usuarios[indice_usuario]
        # Obtener los 5 usuarios más similares
        # Basicamente ordena el array de mayor a menor y recoge los 20 primeros
        indices_usuarios_similares = similitudes_usuario_deseado.argsort()[:-21:-1]
        # Encontrar libros no calificados por el usuario deseado
        libros_no_calificados = matriz_calificaciones.loc[usuario_deseado][matriz_calificaciones.loc[usuario_deseado] == 0]

        # Recomendar libros basados en las valoraciones de usuarios similares que el usuario objetivo no ha calificado
        libros_recomendados = defaultdict(int)
        for indice_usuario_similar in indices_usuarios_similares:
            #recoge los libros no valorados aun y los compara con los usuarios similares
            libros_usuario_similar = matriz_calificaciones.iloc[indice_usuario_similar]
            # Filtra los libros que el usuario similar ha calificado, identificando aquellos con una calificación de 10 y de 9.
            libros_calificados_usuario_similar = libros_usuario_similar[libros_usuario_similar >= 9]
            #los guardamos en la variable
            libros_recomendados.update(libros_calificados_usuario_similar)

    # Muestra los títulos, ISBN y enlaces a las imágenes de los libros recomendados
    titulos = dict(zip(libros['ISBN'], libros['Book-Title']))
    urls = dict(zip(libros['ISBN'], libros['Image-URL-L']))
    print("\nLibros recomendados para el usuario {}: ".format(usuario_deseado))
    for isbn, rating in list(libros_recomendados.items())[:10]:
        if isbn in titulos and isbn in urls:
            print("Título:", titulos[isbn], "| ISBN:", isbn)
            print("Enlace:", urls[isbn])

# Llamada a la función para diferentes usuarios
usuarios_a_recomendar = [2, 8, 11400, 67544]  # IDs de los usuarios a recomendar

for usuario in usuarios_a_recomendar:
    recomendar_libros(usuario)