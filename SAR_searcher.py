import re


def tokenize(query):
    """
    Transformamos la query a una lista que realiza el split si encuentra un AND on un OR
    estos símbolos los matiene en la lista com otro elemento
    ---
    tokenike("a AND b") -> ["a ", "AND", " b"]
    """
    query = re.split("(AND|OR)", query)
    return list(map(str.split, query))


def search(query):
    """
    Función recursiva, vamos aplicando la operación necesaria (AND, OR) de izquierda a derecha
    y llamando otra vez a la fucnión search con el resultado de esta y el resto de la queryself.

    Anotar que los elementos de la query pueden tener 3 formatos que se trabajaran en el metodo retrieve list:
        1. Una lista de newsID
        2. Una string (termino) además del símbolo "NOT"
        3. Una string (termino)
    """
    # Caso base solo queda el resultado
    if (len(query) == 1):
        return query[0]
    # Si la length es mayor que 1 esto significa que al menos hay 3 elementos y el
    # segundo elemento en la lista ha de ser o un AND o un OR
    if (query[1] == "AND"):
        return search([sAnd(query[0], query[1])] + query[3:])
    else:
        return search([sOr(query[0], query[1])] + query[3:])


def retrieveList(w, posting_list, news_tables):
    """
    Hace que los contenidos de las querys todos tengan el mismo formato en el algoritmo.
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


/  # TODO: modificar las llamadas a retrieveList, faltan parametros


def sAnd(a, b):
    a = retrieveList(a)
    b = retrieveList(b)
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


def sOr(a, b):
    a = retrieveList(a)
    b = retrieveList(b)
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
