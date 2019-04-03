import re

clean_re = re.compile('\W+')

def clean_text(text):
    return clean_re.sub(' ', text).lower()

<<<<<<< HEAD
def add_to_posting_list(termino, newsId):
    #News id, identificador de noticia a la que pertence



=======
p
>>>>>>> 5ee5e2e20c4f693877a7092c89db128f10b106b6
# mientras hay_documentos:
#     doc ← leer_siguiente_documento()
#     docid ← asignar_identificador_al_doc()
#     mientras hay_noticias_en_doc:
#         noticia ← extraer_siguiente_noticia()
#         newid ← asignar_identificador_a_la_noticia()
#         noticia_limpia ← procesar_noticia(noticia)
#         para termino en noticia_limpia:
#             añadir_noticia_al_postings_list_del_termino(termino, newid)
