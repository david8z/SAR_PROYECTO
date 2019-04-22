import re
import sys
import pickle
import json
def tokenize(query):
    query = re.split("(AND|OR)", query)
    return list(map(str.split, query))


def search(query):
    # Devuelve un término o una lista de listas que son newsID
    if (len(query)==1):
        return query[0]
    if (query[1] == "AND"):
        return search([sAnd(query[0], query[1])]+query[3:])
    else:
        return search([sOr(query[0], query[1])]+query[3:])

def retrieveList(w, posting_list, news_tables):
    #Obtiene la lista de newsID en los que aparece un término
    if not isinstance(w, str):
        # w es una lista de newsID
        return w
    if "NOT" in w:
        # Devolver complemento de lista de newsID de w.split()[1]
        # Quitamos de la lista de newsID en news_tables los newsID en los que aparezca w
        # Devuelve la lista de newsID
        return [k for k in news_tables.keys() if k not in [ x for x, y in posting_list[w.split()[1]] ]]
    else:
        # Devuelve la lista de newsID
        return [x for x,y in posting_list[w]]

def sAnd(a, b):
    a = retrieveList(a)
    b = retrieveList(b)
    posA = 0
    posB = 0
    res = []
    while(posA<len(a) and posB<len(b)):
        if ( a[posA] == b[posB] ):
            res.append(a[posA])
            posA+=1
            posB+=1
        elif ( a[posA] < b[posB] ):
            posA+=1
        elif ( a[posA] > b[posB] ):
            posB+=1
    return res

def sOr(a, b):
    a = retrieveList(a)
    b = retrieveList(b)
    posA = 0
    posB = 0
    res = []
    while(posA<len(a) and posB<len(b)):
        if ( a[posA][0] == b[posB][0] ):
            res.append(a[posA][0])
            posA+=1
            posB+=1
        elif ( a[posA][0] < b[posB][0] ):
            res.append(a[posA][0])
            posA+=1
        elif ( b[posB][0] < a[posA][0] ):
            res.append(b[posB][0])
            posB+=1
        for i in range(posA, len(a)):
            res.append(a[i][0])
        for i in range(posB, len(b)):
            res.append(b[i][0])

    return res

def retrieveNews(newsID, news_tables):
    res = []
    if len(newsID) > 1:
        with open(news_tables[newsID], "r") as fh:
            doc = json.load(fh)

def print_article(article):
    print("Fecha")

def print_results(results):
    if len(results) < 3:
        for noticia in results:
            print_article(noticia)

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