import re

clean_re = re.compile('\W+')

def clean_text(text):
    return clean_re.sub(' ', text).lower()

<<<<<<< HEAD

# mientras hay_documentos:
#     doc ← leer_siguiente_documento()
#     docid ← asignar_identificador_al_doc()
#     mientras hay_noticias_en_doc:
#         noticia ← extraer_siguiente_noticia()
#         newid ← asignar_identificador_a_la_noticia()
#         noticia_limpia ← procesar_noticia(noticia)
#         para termino en noticia_limpia:
#             añadir_noticia_al_postings_list_del_termino(termino, newid)
=======
>>>>>>> c0ca75009b61d5cc92def3dba918f6bc01ea8775
