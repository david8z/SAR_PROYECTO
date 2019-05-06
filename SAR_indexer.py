# -*- coding: utf-8 -*-
import re, sys, glob, os, json, pickle
from operator import itemgetter
from nltk.stem import SnowballStemmer



# Matching con alphanumericos
clean_re = re.compile('[_\W]+')
# dict(termino) -> dict(newsId) -> list(posTer)
posting_list = dict()
# dict(stem(termino)) -> dict(newsId) -> list(posTer)
posting_stem_list = dict()
# dict(newsId) -> tupla(docId, posNot)
news_table = dict()
# dict(docId) -> path_document
pathDoc = dict()

stemmer = SnowballStemmer('spanish')

def clean_text(text):
    """
    Eliminamos alfanuméricos y pasamos texto a minúsculas
    """
    return clean_re.sub(' ', text).lower()


def add_to_posting_list(termino, newsId, posTer):
    """
    Añadimos nueva aparición de término a la posting list
    ---
    newsId: identificador de noticia a la que pertence
    pos: posición del término en la noticia
    """
    dictNoticias = posting_list.get(termino, dict())
    listPosiciones = dictNoticias.get(newsId, list())
    listPosiciones.append(posTer)
    dictNoticias[newsId] = listPosiciones
    posting_list[termino] = dictNoticias

    # With stemming

    dictNoticiasStem = posting_stem_list.get(stemmer.stem(termino), dict())
    listPosicionesStem = dictNoticiasStem.get(newsId, list())
    listPosicionesStem.append(posTer)
    dictNoticiasStem[newsId] = listPosicionesStem
    posting_stem_list[stemmer.stem(termino)] = dictNoticiasStem



def add_to_news_table(docId, posNot, newsId):
    """
    Añadimos una nueva entrada al news table.
    """
    news_table[newsId] = (docId, posNot)


def read_noticias(path):
    with open(path) as json_file:
        return json.load(json_file)


def indexar_noticias(dir_noticias):
    """
    Recibimos el directorio donde se encuentran las noticias, para todos los términos
    de las noticias generamos la posting list y para todas las noticias la news table.
    """
    # Lista de noticias que se encuentran en el directorio
    documentos = [filename for filename in glob.iglob(
        os.getcwd() + "/" + dir_noticias + "/**/*.json", recursive=True)]
    # Recorremos todos los documentos eliminandolos de la lista
    while len(documentos) > 0:
        # Posicion de la noticia en el documento
        posNot = 0
        path = documentos.pop(0)
        docId = path
        # pathDoc[docId] = path
        # Noticias en formato list(dict())
        noticias = read_noticias(path)
        # Recorremos todas las noticias eliminandolas de la lista
        while len(noticias) > 0:
            noticia = noticias.pop(0)
            # Limpiamos texto y separamos por palabras
            text = clean_text(noticia['article']).split()
            # El identificador es uno de los campos del json
            newsId = noticia['id']
            # Posicion del término en la noticia
            posTer = 0
            for termino in text:
                add_to_posting_list(termino, newsId, posTer)
                posTer += 1
            add_to_news_table(docId, posNot, newsId)
            posNot += 1


def sorted_dict(posting_list):
    for key in posting_list.keys():
        # Transformamos el diccionario de newsId relacionado al termino  a list(tupla()) y lo ordenamos por newsId
        posting_list[key] = sorted(list(posting_list[key].items()))
    return posting_list


def save_object(object, filename):
    with open(filename, "wb") as fh:
        pickle.dump(object, fh)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Formato: <SAR_indexer.py> <directorio_noticias> <índice_fichero>')
    else:
        dir_noticias = sys.argv[1]
        ficheroPickle = sys.argv[2]
        indexar_noticias(dir_noticias)
        posting_list = sorted_dict(posting_list)
        posting_stem_list = sorted_dict(posting_stem_list)
        objeto = (posting_list,posting_stem_list, news_table)
        save_object(objeto, ficheroPickle)
