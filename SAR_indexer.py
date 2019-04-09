import re
import sys
from os import scandir
import json
import pickle
from operator import itemgetter


clean_re = re.compile('[_\W]+')
posting_list = dict()
news_table = dict()
dicDoc = dict()

def clean_text(text):
    return clean_re.sub(' ', text).lower()

def add_to_posting_list(termino, newsId, pos):
    #News id, identificador de noticia a la que pertence
    #pos, posición del término en la noticia
    dictNoticias = posting_list.get(termino, dict())
    listPosiciones = dictNoticias.get(newsId, list())
    listPosiciones.append(pos)
    dictNoticias[newsId] = listPosiciones
    posting_list[termino] = dictNoticias

def add_to_news_table(docId, pos, newsId):
    news_table[newsId] = (docId, pos)

def read_noticias(text):
    with open(text) as json_file:
        return json.load(json_file)

def indexar_noticias(dir_noticias, indice_fichero):
    docID = 0
    notID = 0
    #Lista de noticias que se encuentran en el directorio
    documentos = [arch.name for arch in scandir(dir_noticias) if arch.is_file()]
    #Recorremos todos los documentos eliminandolos de la lista
    while len(documentos) > 0:
        #Posicion de la noticia en el documento
        posNot = 0
        path = dir_noticias + '/' + documentos.pop(0)
        dicDoc[docID] = path
        noticias = read_noticias(path)
        #Recorremos todas las noticias eliminandolas de la lista
        while len(noticias) > 0:
            noticia = noticias.pop(0)
            text = clean_text(noticia['article']).split()
            notID = noticia['id']
            #Posicion del término en la noticia
            posTer = 0
            for termino in text:
                add_to_posting_list(termino, notID, posTer)
                posTer += 1
            add_to_news_table(docID, posNot, notID)
            posNot += 1
            docID += 1

def sorted_dict(diccionario, s):
    res = dict()
    if s == 0:
        keys = diccionario.keys()
        for key in keys:
            value = diccionario.get(key)
            for k in value.keys():
                v = value.get(k)
                v = sorted(v)
                value[k] = v
            res[key] = value    
    else:
        keys = diccionario.keys()
        for key in keys:
            value = diccionario.get(key)
            ordenado = sorted(value[0], key = itemgetter(0), reverse = False)
            res[key] = ordenado
    return res   
            
def save_object(object, filename):
    with open(filename, "wb") as fh:
        pickle.dump(object, fh)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        println('Formato: <SAR_indexer.py> <directorio_noticias> <índice_fichero>')
    else:
        dir_noticias = sys.argv[1]
        indice_fichero = sys.argv[2]
        indexar_noticias(dir_noticias, indice_fichero)
        posting_list = sorted_dict(posting_list, 0)
        news_table = sorted_dict(news_table, 1)
        objeto = (posting_list, news_table, dicDoc)
        save_object(objeto, "diccionarios.txt")

# mientras hay_documentos:
#     doc ← leer_siguiente_documento()
#     docid ← asignar_identificador_al_doc()
#     mientras hay_noticias_en_doc:
#         noticia ← extraer_siguiente_noticia()
#         newid ← asignar_identificador_a_la_noticia()
#         noticia_limpia ← procesar_noticia(noticia)
#         para termino en noticia_limpia:
#             añadir_noticia_al_postings_list_del_termino(termino, newid)
