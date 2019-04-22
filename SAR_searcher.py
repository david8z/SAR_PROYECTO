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
    """
    query = re.split("(AND|OR)", query)
    return list(map(str.split, query))


def search(query, posting_list, news_tables):
    """
    Función recursiva, vamos aplicando la operación necesaria (AND, OR) de izquierda a derecha
    y llamando otra vez a la fucnión search con el resultado de esta y el resto de la queryself.

    Anotar que los elementos de la query pueden tener 3 formatos que se trabajarán en el método retrieve_list:
        1. Una lista de newsID
        2. Una string (término) además del símbolo "NOT"
        3. Una string (término)
    """
    # Caso base solo queda el resultado
    if (len(query) == 1):
        return query[0]
    # Si la length es mayor que 1 esto significa que al menos hay 3 elementos y el
    # segundo elemento en la lista ha de ser o un AND o un OR
    if (query[1] == "AND"):
        return search([sAnd(query[0], query[1])] + query[3:], posting_list, news_tables)
    else:
        return search([sOr(query[0], query[1])] + query[3:], posting_list, news_tables)


def retrieveList(w, posting_list, news_tables):
    """
    Hace que los contenidos de las queries todos tengan el mismo formato en el algoritmo.
    """
    if not isinstance(w, str):
        # w es una lista de newsID
        return w
    if "NOT" in w:
        # Devolver complemento de lista de newsID de w.split()[1]
        # Quitamos de la lista de newsID en news_tables los newsID en los que aparezca w
        # Devuelve la lista de newsID
        return [k for k in news_tables.keys() if k not in [x for x, y in posting_list[w.split()[1]]]]
    else:
        # Devuelve la lista de newsID
        return [x for x, y in posting_list[w]]


def sAnd(a, b, posting_list, news_tables):
    a = retrieveList(a, posting_list, news_tables)
    b = retrieveList(b, posting_list, news_tables)
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


def sOr(a, b, posting_list, news_tables):
    a = retrieveList(a, posting_list, news_tables)
    b = retrieveList(b, posting_list, news_tables)
    posA = 0
    posB = 0
    res = []
    while(posA < len(a) and posB < len(b)):
        if (a[posA][0] == b[posB][0]):
            res.append(a[posA][0])
            posA += 1
            posB += 1
        elif (a[posA][0] < b[posB][0]):
            res.append(a[posA][0])
            posA += 1
        elif (b[posB][0] < a[posA][0]):
            res.append(b[posB][0])
            posB += 1
        for i in range(posA, len(a)):
            res.append(a[i][0])
        for i in range(posB, len(b)):
            res.append(b[i][0])

    return res

# Obtener noticias (como objeto json) que estén en la lista de newsID
def retrieveNews(newsID, news_tables):
    res = []
    docs = {} # Set de documentos (garantiza unicidad)
    if len(newsID) >= 1:
        with open(news_tables[newsID][0], "r") as fh:
            doc = json.load(fh)
            for article in doc:
                if article["id"] in newsID:
                    res.append(article)
                    docs.add(news_tables[newsID][0])
        return (res, docs)



# Imprimir un artículo: muestra cuerpo entero o extracto,
# en caso de printLine=True lo imprime en una línea sin imprimir el cuerpo
def print_article(article, excerpt=False, keywords=[], printLine=False):
    if printLine:
        endL = " " # Seguir en misma línea
    else:
        endL = "\n" # Imprimir en nueva línea

    print("Fecha: ".article["date"], end=endL)
    print("Título: ".article["title"], end=endL)
    print("Palabras clave: ".article["keywords"])

    # printLine solo es True cuando hay más de 5 resultados
    if excerpt and not printLine:
        print("Fragmento: " + excerpt(article["article"], keywords))
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

    print("Se han encontrado " + len(results) + " resultados en los documentos:", end=" ")
    for i in docs:
        print(i, end=", ")

# Cargar fichero pickle como objeto
def load_object(filename):
    with open(filename, "r") as fh:
        obj = pickle.load(fh)
    return obj

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Formato: SAR_searcher.py <índice_fichero> [consulta]')
        exit(0)
    # Cargamos el objeto pickle
    #  objeto = (posting_list, news_table, dicDoc)
    oject = load_object(sys.argv[1])
    posting_list = object[0]
    news_tables = object[1]
    pathDoc = object[2]

    if len(sys.argv<3):
        query = input("> Consulta: ")
        while(query):
            print_results(retrieveNews(search(query), news_tables))
            query = input("> Consulta: ")
    else:
        print_results(retrieveNews(search(sys.argv(2)), news_tables))