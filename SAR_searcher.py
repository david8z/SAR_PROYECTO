import re
import sys
import pickle
import json
import os
from nltk.stem import SnowballStemmer


def tokenize(query, stemming = False):
    """
    Transformamos la query a una lista que realiza el split si encuentra un AND on un OR
    estos símbolos los matiene en la lista com otro elemento además separá los parentesis
    y transforma los términos a sus stems si stemming = True
    ---
    tokenike("a AND b") -> ["a ", "and", " b"]

    OJO: Este método convierte a minúsculas TODOS los tokens
    """
    aux = [x.strip().lower() for x in re.split("(AND|OR|[(]|[)])", query)]
    if stemming:
        stemmer = SnowballStemmer('spanish')
        # Usamos map porque stemming de "not valencia" != stemming("not") + stemming("valencia")
        return [" ".join(list(map(stemmer.stem,i.split()))) for i in aux if i]
    else:
        return [i for i in aux if i]

def search_with_parenthesis(query, posting_list, news_table):
    # La query no se satisface
    if (len(query) == 0):
        return []
    # Caso base solo queda el resultado
    if (len(query) == 1):
        # La query ha sido solo una palabra
        if type(query[0]) is not list:
            return retrieveList(query[0], posting_list, news_table)
        return query[0]

    # No quedan paréntesis
    if "(" not in query:
        return search(query, posting_list, news_table)

    # Apuntará al último "(" visto
    pointer = 0

    for i in range(len(query)):

        # Avanzamos hasta que encontremos e primer "("
        if query[pointer] != '(':
            pointer+=1
        # Para actualizar el puntero en caso de parentesis anidados
        elif (query[i] == '(') and (i != pointer):
            pointer = i
        # Ha encontrado el parentesois que lo cierra
        elif query[i] == ')':
            # We pop ")" from the query
            query.pop(i)

            if (query[pointer+2] == "and"):
                auxValue = sAnd(query[pointer+1], query[pointer+3], posting_list, news_table)
                # Check if the element previous to pointer is a not
                try:
                    if query[pointer-1] == "not":
                        # Usamos sorted porque las keys no están ordenadas
                        auxValue = sorted([k for k in news_table.keys() if k not in auxValue])
                        # Delete not from query
                        query.pop(pointer-1)
                        # Update pos of '('
                        pointer= pointer - 1
                except:
                    pass
                return search_with_parenthesis(query[:pointer] + [ auxValue ]  + query[pointer+4:],posting_list, news_table)
            elif (query[pointer+2] == "or"):
                auxValue = sOr(query[pointer+1], query[pointer+3], posting_list, news_table)
                # Check if the element previous to pointer is a not
                try:
                    if query[pointer-1] == "not":
                        # Usamos sorted porque las keys no están ordenadas
                        auxValue = sorted([k for k in news_table.keys() if k not in auxValue])
                        # Delete not from query
                        query.pop(pointer-1)
                        # Update pos of '('
                        pointer= pointer - 1
                except:
                    pass
                return search_with_parenthesis(query[:pointer] + [ auxValue ]  + query[pointer+4:],posting_list, news_table)
    return query

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
    # La query no se satisface
    if (len(query) == 0):
        return []
    # Caso base solo queda el resultado
    if (len(query) == 1):
        # La query ha sido solo una palabra
        if type(query[0]) is not list:
            return retrieveList(query[0], posting_list, news_table)
        return query[0]
    # Si la length es mayor que 1 esto significa que al menos hay 3 elementos y el
    # segundo elemento en la lista ha de ser o un AND o un OR
    if (query[1] == "and"):
        return search([sAnd(query[0], query[2], posting_list, news_table)] + query[3:], posting_list, news_table)
    elif (query[1] == "or"):
        return search([sOr(query[0], query[2], posting_list, news_table)] + query[3:], posting_list, news_table)
    return query


def retrieveList(w, posting_list, news_table):
    """
    Hace que los contenidos de las queries todos tengan el mismo formato en el algoritmo. EL formato es list(newsID)
    """
    if type(w) == list:
        # w es una lista de newsID
        return w
    if "not" in w.split():
        # Devolver complemento de lista de newsID de w.split()[1]
        # Quitamos de la lista de newsID en news_table los newsID en los que aparezca w
        # Devuelve la lista de newsID
        # Hay que aplicar sorted ya que al seleccionar los elementos de news_table.keys estos están desordenados.
        return sorted([k for k in news_table.keys() if k not in [x for x, y in posting_list.get(w.split()[1], [])]])
    elif '"' in w:
        w = w.replace('"', '').split() # ["palabra", "palabra"]
        query = tokenize(' AND '.join(w)) # ["palabra", "AND", "palabra"] --> search() --> lista de news_id comunes
        #print(query)
        news_list = search(query, posting_list, news_table) # Tenemos lista de newsID comunes entre todas las palabras

        return merged_sentence(w, news_list, posting_list)
    else:
        # Devuelve la lista de newsID. Si no existe el término, devuelve lista vacía.
        return [x for x, y in posting_list.get(w, [])]

def merged_sentence(words, news_list, posting_list):
    pos_list = []
    f_news_list = []
    for news in news_list:
        f_word = posting_list[words[0]]
        pos_list = [y for x,y in f_word if x == news][0] # Obtenemos la lista de posiciones de la primera palabra
        for i in range(1,len(words)):
            i_word = posting_list.get(words[i])
            i_word = [y for x, y in i_word if x == news][0] # Obtenemos la lista de posiciones de la palabra i-ésima
            pos_list = [x for x in pos_list if x+i in i_word] # Si  posición_primera_palabra+i = posición_palabra_i entonces conservamos esa posición, sino la borramos de la lista
        # Aquí ya tenemos una lista de posiciones a partir de la cual podemos encontrar la secuencia de palabras
        if len(pos_list)>0: # Si la lista tiene algún elemento, entonces la noticia contiene la frase
            f_news_list.append(news)
    return f_news_list


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
        if (a[posA] == b[posB]):
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
def print_article(article, excerpt=False, keywords = [], printLine=False):
    if printLine:
        endL = " " # Seguir en misma línea
    else:
        endL = "\n" # Imprimir en nueva línea

    print("\033[1m Título: " + article["title"]+"\033[0m", end=endL)
    print("\033[1m Fecha: \033[0m" + article["date"], end=endL)
    print("\033[1m Palabras clave: \033[0m" + article["keywords"])
    # Casos en el que hay más de 10 noticias
    if not excerpt and not printLine:
        print("\033[1m Cuerpo de la noticia: \033[0m" + article["article"])
    # printLine solo es True cuando hay más de 5 resultados
    elif excerpt and not printLine:
        print("\033[1m Fragmento: \033[0m" + get_excerpt(article["article"], keywords))

    print()

# Obtener fragmento de texto que contenga las palabras clave
def get_excerpt(text, keywords):
    #Obtenemos lista del texto para que sea más fácil obtener extracto

    lower_text = text.lower()
    len_text = len(text)
    result = ""
    for word in keywords:
        len_word = len(word.strip('"'))
        fi = lower_text.index(word.strip('"'))
        print(fi)
        if len(text[:fi].split()) < 6:
            result = result + text[:fi]+ text[fi:fi+len_word] +" ".join(text[fi+len_word:].split()[:6]) + "..."
        else:
            result = result + "..."+ " ".join(text[:fi-1].split()[-6:]) + text[fi-1:fi+len_word+1] +" ".join(text[fi+len_word+1:].split()[:6]) + "..."

    return result

# Procesar los resultados según su tamaño. Pide lista de resultados y docs
# (obtenida de retrieveNews) y lista de palabras clave positivas.
def print_results(results, keywords):
    docs = results[1]
    # Ordenamos las noticias en base al número de ocurrencias de las keywords
    results = sorted(results[0], key=lambda noticia:sum([noticia["article"].split().count(x) for x in keywords]), reverse=True)
    if len(results) < 3:
        for noticia in results:
            print_article(noticia)
    elif len(results) <= 5:
        for noticia in results:
            print_article(noticia, True, keywords)
    else:
        for noticia in results[:10]:
            print_article(noticia, False, keywords, True)

    print("Se han encontrado \033[1m" + str(len(results)) + " resultados \033[0m en los documentos:", end=" ")
    for i in docs:
        print(os.path.basename(i), end=", ")
    print()
    print("Se han encontrado " + str(len(results)) + " resultados.")

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
    # Objeto = (posting_list, posting_stem_list, news_table)
    pickle_object = load_object(sys.argv[1])
    posting_list = pickle_object[0]
    posting_stem_list = pickle_object[1]
    news_table = pickle_object[2]

    if (len(sys.argv) < 3):
        query = input("> Consulta: ")
        while(query):
            # Nos devuelve la lista de noticias que cumplen la query, list(newsID)
            tokens = tokenize(query)
            # Obtenemos lista de palabras clave (no son AND, OR o contienen NOT)
            # limpiamos con el sub para eliminar ""
            keywords = [x for x in tokens if x not in ["and", "or"] and "not" not in x]
            print(keywords)
            search_results = search_with_parenthesis(tokens, posting_list, news_table)
            #print(search_results)
            print_results(retrieveNews(search_results, news_table),keywords)
            query = input("> Consulta: ")
    else:
        if "-s" in sys.argv:
            query = sys.argv[3:]
            # Nos devuelve la lista de noticias que cumplen la query, list(newsID)
            tokens = tokenize(" ".join(query), True)
            # Obtenemos lista de palabras clave (no son AND, OR o contienen NOT)
            # limpiamos con el sub para eliminar ""
            keywords = [x for x in re.compile('[_\W]+').sub("","".join(tokens)) if x not in ["and", "or"] and "not" not in x]
            search_results = search_with_parenthesis(tokens, posting_stem_list, news_table)
        else:
            query =sys.argv[2:]
            # Nos devuelve la lista de noticias que cumplen la query, list(newsID)
            tokens = tokenize(" ".join(query))
            # Obtenemos lista de palabras clave (no son AND, OR o contienen NOT)
            # limpiamos con el sub para eliminar ""
            keywords = [x for x in tokens if x not in ["and", "or"] and "not" not in x]

            search_results = search_with_parenthesis(tokens, posting_list, news_table)
        print_results(retrieveNews(search_results, news_table), keywords)
