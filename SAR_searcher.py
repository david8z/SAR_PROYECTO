import re
import sys
import pickle
import json


def tokenize(query):
    """
    Transformamos la query a una lista que realiza el split si encuentra un AND on un OR
    estos símbolos los matiene en la lista com otro elemento
    ---
    tokenike("a AND b") -> ["a ", "AND", " b"]

    OJO: Este método no hace ningún tipo de limpieza sobre los tokens
    """

    return [x.strip() for x in re.split("(AND|OR)", query)]


def search(query, posting_list, news_table):
    """
    Función recursiva, vamos aplicando la operación necesaria (AND, OR) de izquierda a derecha
    y llamando otra vez a la fucnión search con el resultado de esta y el resto de la queryself.

    Anotar que los elementos de la query pueden tener 3 formatos que se trabajarán en el método retrieve_list:
        1. Una lista de newsID
        2. Una string (término) además del símbolo "NOT"
        3. Una string (término)

    OJO: Aquí se convierten las palabras a minúsculas
    """
    print(query)
    # La query no se satisface
    if (len(query) == 0):
        return []
    # Caso base solo queda el resultado
    if (len(query) == 1):
        # La query ha sido solo una palabra
        if query[0] not in news_table.keys():
            return retrieveList(query[0], posting_list, news_table)
        return query[0]
    # Si la length es mayor que 1 esto significa que al menos hay 3 elementos y el
    # segundo elemento en la lista ha de ser o un AND o un OR
    if (query[1] == ["AND"]):
        return search([sAnd(query[0].lower(), query[2].lower(), posting_list, news_table)] + query[3:], posting_list, news_table)
    elif (query[1] == ["OR"]):
        return search([sOr(query[0].lower(), query[2].lower(), posting_list, news_table)] + query[3:], posting_list, news_table)
    return query


def retrieveList(w, posting_list, news_table):
    """
    Hace que los contenidos de las queries todos tengan el mismo formato en el algoritmo. EL formato es list(newsID)
    """
    print(w)
    if w in news_table.keys():
        # w es una lista de newsID
        return w
    if "NOT" in w:
        # Devolver complemento de lista de newsID de w.split()[1]
        # Quitamos de la lista de newsID en news_table los newsID en los que aparezca w
        # Devuelve la lista de newsID
        return [k for k in news_table.keys() if k not in [x for x, y in posting_list[w.split()[1]]]]
    elif w in posting_list.keys():
        # Devuelve la lista de newsID
        return [x for x, y in posting_list[w]]
    else:
        # La palabra no está en el diccionario
        return []



# OPERACIONES LÓGICAS: Devuelven lista de newsID
def sAnd(a, b, posting_list, news_table):
    a = retrieveList(a, posting_list, news_table)
    b = retrieveList(b, posting_list, news_table)
    posA = 0
    posB = 0
    res = []
    while(posA < len(a) and posB < len(b)):
        if (a[posA] == b[posB]):
            res.append(a[posA])
            posA += 1
            posB += 1
        elif (a[posA] < b[posB]):
            posA += 1
        elif (a[posA] > b[posB]):
            posB += 1
    return res


def sOr(a, b, posting_list, news_table):
    a = retrieveList(a, posting_list, news_table)
    b = retrieveList(b, posting_list, news_table)
    posA = 0
    posB = 0
    res = []
    while(posA < len(a) and posB < len(b)):
        if (a[posA][0] == b[posB][0]):
            res.append(a[posA])
            posA += 1
            posB += 1
        elif (a[posA] < b[posB]):
            res.append(a[posA])
            posA += 1
        elif (b[posB] < a[posA]):
            res.append(b[posB])
            posB += 1
    for i in range(posA, len(a)):
        res.append(a[i])
    for i in range(posB, len(b)):
        res.append(b[i])
    return res

# Obtener noticias (como objeto json) que estén en la lista de newsID
def retrieveNews(newsList, news_table):
    """
    Se devuelve el contenido de las noticias que están en newsList.
    ---
    newsList: Lista de newsID que han hecho matching con la query
    news_table: dict(newsID)->list(tuple(docID, posDoc))
    """
    res = []
    docs = set() # Set de documentos (garantiza unicidad)
    # Necesario en caso de que no haya ninguna noticia que haga matching con la query
    if len(newsList) >= 1:
        for newsID in newsList:
            with open(news_table[newsID][0], "r") as fh:
                doc = json.load(fh)
                # Porque no utilizamos news_table[newID][1] que es la posición de la noticia en el doc
                for article in doc:
                    if article["id"] == newsID:
                        res.append(article)
                        docs.add(news_table[article["id"]][0])
    return (res, docs)



# Imprimir un artículo: muestra cuerpo entero o extracto,
# en caso de printLine=True lo imprime en una línea sin imprimir el cuerpo
def print_article(article, excerpt=False, keywords=[], printLine=False):
    if printLine:
        endL = " " # Seguir en misma línea
    else:
        endL = "\n" # Imprimir en nueva línea

    print("Fecha: " + article["date"], end=endL)
    print("Título: " + article["title"], end=endL)
    print("Palabras clave: " + article["keywords"])

    # printLine solo es True cuando hay más de 5 resultados
    if excerpt and not printLine:
        print("Cuerpo de la noticia: " + article["article"])
        #print("Fragmento: " + excerpt(article["article"], keywords))
    elif not printLine:
        print("Cuerpo de la noticia: " + article["article"])

# Procesar los resultados según su tamaño. Pide lista de resultados y docs
# (obtenida de retrieveNews) y lista de palabras clave positivas.
def print_results(results, keywords):
    docs = results[1]
    results = results[0]
    if len(results) < 3:
        for noticia in results:
            print_article(noticia)
    elif len(results) < 5:
        for noticia in results:
            print_article(noticia, True, keywords)
    else:
        for noticia in results[:10]:
            print_article(noticia, True, keywords, True)

    print("Se han encontrado " + str(len(results)) + " resultados en los documentos:", end=" ")
    for i in docs:
        print(i, end=", ")
    print()

# Cargar fichero pickle como objeto
def load_object(filename):
    with open(filename, "rb") as fh:
        obj = pickle.load(fh)
    return obj

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Formato: SAR_searcher.py <índice_fichero> [consulta]')
        exit(0)
    # Cargamos el objeto pickle
    #  objeto = (posting_list, news_table)
    pickle_object = load_object(sys.argv[1])
    posting_list = pickle_object[0]
    news_table = pickle_object[1]

    if (len(sys.argv)<3):
        query = input("> Consulta: ")
        while(query):
            # Nos devuelve la lista de noticias que cumplen la query, list(newsID)
            search_results = search(tokenize(query), posting_list, news_table)

            print_results(retrieveNews(search_results, news_table),[])
            query = input("> Consulta: ")
    else:
        print_results(retrieveNews(search(sys.argv(2)), news_table))
