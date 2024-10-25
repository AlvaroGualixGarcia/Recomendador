import pandas as pd
from collections import defaultdict
import random
from sklearn.metrics.pairwise import cosine_similarity
from tabulate import tabulate

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

# Combinar los 3 csv
datos_combinados = pd.merge(pd.merge(usuarios, calificaciones, on='User-ID'), libros, on='ISBN')

# Usuario deseado, *podria ser un imput en una aplicacion*.
usuario_deseado = 85526 # Cambia esto al ID del usuario que desees comprobar

#fase1- Recopilar los libros mejor valorados por el usuario----------------------------------------------------------------------------------------------------------------------

# Filtrar los datos solo para el usuario deseado
datos_usuario_deseado = datos_combinados[datos_combinados['User-ID'] == usuario_deseado]
#comprobador de si existe el usuario antes de nada
if not datos_usuario_deseado.empty:
    
    # Calcular una matriz de usuario-libro con las calificaciones del usuario deseado
    matriz_calificaciones_usuario_deseado = datos_usuario_deseado.pivot_table(index='User-ID', 
                                                                              columns='ISBN', 
                                                                              values='Book-Rating').fillna(0)

    # Obtener las calificaciones del usuario deseado, usamos iloc porque loc sera usando las keys de las columnas(mejor para codificación, más eficaz)
    calificaciones_usuario_deseado = matriz_calificaciones_usuario_deseado.iloc[0]

    # Filtrar los libros con calificaciones 
    libros_altamente_valorados = calificaciones_usuario_deseado[calificaciones_usuario_deseado >= 0]

    # Ordenar las calificaciones de mayor a menor
    calificaciones_ordenadas_usuario = libros_altamente_valorados.sort_values(ascending=False)

    # Obtener los 10 libros mejor valorados por el usuario (si hay más de 10)
    top_10_libros_mejor_valorados_usuario = calificaciones_ordenadas_usuario.head(10)

    # variable para ostrar los títulos de los libros mejor valorados
    titulos_autores = dict(zip(libros['ISBN'],
                               libros[['Book-Title', 'Book-Author']]))
    
    # variable para mostrar las url a las imagenes de los libros (para cuando haga una aplicacion web que se puedan ver)
    urls = dict(zip(libros['ISBN'],
                    libros['Image-URL-L']))

    # Crear un diccionario con ISBN como clave y tupla de título y autor como valor
    titulos_autores = {}
    for index, row in libros.iterrows():
        titulos_autores[row['ISBN']] = (row['Book-Title'], row['Book-Author'])

    # Mostrar los títulos de los libros mejor valorados en forma de tabla
    headers = ["Título", "Autor", "ISBN", "Calificación"]
    datos = []
    for isbn, rating in top_10_libros_mejor_valorados_usuario.items():
        if isbn in titulos_autores and isbn in urls:
            titulo_autor = titulos_autores[isbn]
            titulo = titulo_autor[0]
            autor = titulo_autor[1]
            datos.append([titulo, autor, isbn, rating])

    print("\nTop 10 libros mejor valorados por el usuario {}: ".format(usuario_deseado))
    print(tabulate(datos, headers=headers, tablefmt="pretty"))

    print("\n")



    #fase2-Recomendar libros nuevos en base a usuarios similares que los hayan valorado bien----------------------------------------------------

    # Recoger IDs únicos de usuarios en una lista
    ids_usuarios = datos_combinados['User-ID'].unique().tolist()

    # Obtener 1000 usuarios aleatorios de la lista de usuarios
    lista_usuarios_aleatorios = random.sample(ids_usuarios, 1000)   # Ajusta este número según tu disponibilidad de memoria

    # Si el usuario deseado no está entre los 1000 usuarios aleatorios, lo agrega
    if usuario_deseado not in lista_usuarios_aleatorios:
        lista_usuarios_aleatorios.append(usuario_deseado)

    # Comprueba si el usuario deseado está entre los 1000 usuarios aleatorios
    if usuario_deseado in lista_usuarios_aleatorios:
        
        # Filtra el conjunto de datos solo con los 1001 usuarios aleatorios recogidos anteriormente
        usuarios_filtrados = datos_combinados[datos_combinados['User-ID'].isin(lista_usuarios_aleatorios)]

        # Calcula una matriz de usuario-libro con las calificaciones
        matriz_calificaciones = usuarios_filtrados.pivot_table(index='User-ID', columns='ISBN', values='Book-Rating')
        #rellenar los valores nulos de la matriz con 0
        matriz_calificaciones = matriz_calificaciones.fillna(0)

        #ALGORITMO
        # Calcular similitud entre usuarios usando la medida del coseno segun las calificaciones del usuario
        similitud_usuarios = cosine_similarity(matriz_calificaciones)

        # Obtener el índice del usuario deseado en la lista de usuarios aleatorios
        indice_usuario = lista_usuarios_aleatorios.index(usuario_deseado)

        # Encuentra los usuarios más similares al usuario deseado
        similitudes_usuario_deseado = similitud_usuarios[indice_usuario]
        
        # Obtener los 15 usuarios más similares
        # Basicamente ordena el array de mayor a menor y recoge los 15 primeros
        indices_usuarios_similares = similitudes_usuario_deseado.argsort()[:-16:-1]
        
        # Encontrar libros no calificados por el usuario deseado
        #libros_no_calificados = matriz_calificaciones.loc[usuario_deseado][matriz_calificaciones.loc[usuario_deseado] == 0]

        # Recomendar libros basados en las valoraciones de usuarios similares que el usuario objetivo no ha calificado
        libros_recomendados = defaultdict(int)
        for indice_usuario_similar in indices_usuarios_similares:
            
            #recoge los libros no valorados aun y los compara con los usuarios similares
            libros_usuario_similar = matriz_calificaciones.iloc[indice_usuario_similar]
            
            # Filtra los libros que el usuario similar ha calificado, identificando aquellos con una calificación de 10,9 y 8.
            libros_calificados_usuario_similar = libros_usuario_similar[libros_usuario_similar >= 8]
            
            #los guardamos en la variable
            libros_recomendados.update(libros_calificados_usuario_similar)
            
        # Obtener los títulos de libros recomendados al usuario objetivo
        titulos = dict(zip(libros['ISBN'], libros['Book-Title']))
        
        # Obtener enlaces a las imágenes de los libros
        urls = dict(zip(libros['ISBN'], libros['Image-URL-L']))
        
        # Obtener los títulos de libros recomendados al usuario objetivo con sus autores
        autores = dict(zip(libros['ISBN'], libros['Book-Author']))
        
        # Limitar la cantidad de libros recomendados a mostrar (por ejemplo, los primeros 10 ordenados de mayor a menor)
        libros_recomendados_ordenados = dict(sorted(libros_recomendados.items(), key=lambda x: x[1], reverse=True)[:10])

        # Mostrar los libros recomendados en forma de tabla
        data_recomendados = []
        for isbn, rating in libros_recomendados_ordenados.items():
            if isbn in titulos and isbn in urls and isbn in autores:
                data_recomendados.append([titulos[isbn], autores[isbn], isbn, rating])

        print("\nLibros recomendados para el usuario {} por otros usuarios que han valorado similarmente (ordenados por valoración):".format(usuario_deseado))
        print(tabulate(data_recomendados, headers=headers, tablefmt="pretty"))
        print("\n")
    #comprobador de que esta el usuario en la lista de 1001
    else:
        print(f"El usuario {usuario_deseado} no existe.")
        
        
        
    #fase 3- Recomendar libros en funcion a autores similares que no haya leido el usuario--------------------------------------------------------------------------------------
    
    # Obtener los autores de los libros mejor valorados por el usuario
    autores_libros_valorados = [autor for isbn, (titulo, autor) in titulos_autores.items() if isbn in top_10_libros_mejor_valorados_usuario.index]

    # Filtrar datos para encontrar otros libros del mismo autor bien valorados por otros usuarios
    otros_libros_recomendados = defaultdict(int)
    # Iterar sobre autores únicos de los libros bien valorados
    for autor in set(autores_libros_valorados):  
        # Filtrar libros del mismo autor
        libros_mismo_autor = libros[libros['Book-Author'] == autor]  
        # Iterar sobre los libros del mismo autor
        for isbn in libros_mismo_autor['ISBN']:  
            # Verificar si el ISBN está en la matriz de calificaciones
            if isbn in matriz_calificaciones.columns:  
                calificaciones_libro = matriz_calificaciones[isbn]
                calificaciones_altas = calificaciones_libro[calificaciones_libro >= 6]
                if len(calificaciones_altas) > 0:
                    otros_libros_recomendados[isbn] = calificaciones_altas.mean()

    # Ordenar los libros recomendados por valoración
    otros_libros_recomendados_ordenados = dict(sorted(otros_libros_recomendados.items(), key=lambda x: x[1], reverse=True)[:10])

    # Obtener los ISBN de los libros leídos por el usuario
    isbn_libros_leidos = set(top_10_libros_mejor_valorados_usuario.index)

    # Filtrar libros recomendados por autores similares que el usuario no ha leído
    otros_libros_recomendados_filtrados = {
        isbn: rating for isbn, rating in otros_libros_recomendados.items() if isbn not in isbn_libros_leidos
    }

    # Ordenar los libros recomendados filtrados por valoración
    otros_libros_recomendados_ordenados = dict(sorted(otros_libros_recomendados_filtrados.items(), key=lambda x: x[1], reverse=True)[:10])

    # Mostrar los otros libros recomendados filtrados en forma de tabla
    data_otros_libros_recomendados_filtrados = []
    for isbn, rating in otros_libros_recomendados_ordenados.items():
        if isbn in titulos and isbn in urls and isbn in autores:
            data_otros_libros_recomendados_filtrados.append([titulos[isbn], autores[isbn], isbn, rating])

    print("\nOtros libros recomendados por autores similares que no ha leido el usuario (ordenados por valoración):")
    print(tabulate(data_otros_libros_recomendados_filtrados, headers=headers, tablefmt="pretty"))
    print("\n")
else:
    print("El usuario no existe.")