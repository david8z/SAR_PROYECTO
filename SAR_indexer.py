import re

clean_re = re.compile('\W+')
posting_list = dict()

def clean_text(text):
    return clean_re.sub(' ', text).lower()

def add_to_posting_list(termino, newsId, pos):
    #News id, identificador de noticia a la que pertence
    dictNoticias = posting_list.get(termino, dict())
    listPosiciones = dictNoticias.get(newsId, list())
    listPosiciones.append(pos)
    dictNoticias[newsId] = listPosiciones
    posting_list[termino] = dictNoticias


# mientras hay_documentos:
#     doc ← leer_siguiente_documento()
#     docid ← asignar_identificador_al_doc()
#     mientras hay_noticias_en_doc:
#         noticia ← extraer_siguiente_noticia()
#         newid ← asignar_identificador_a_la_noticia()
#         noticia_limpia ← procesar_noticia(noticia)
#         para termino en noticia_limpia:
#             añadir_noticia_al_postings_list_del_termino(termino, newid)
