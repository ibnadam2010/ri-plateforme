

def check_end_of_paragraph(text):

    #Permet de garder en un paragraphe les paragraphes où on a "...:\n..." ou "...;\n..."
    if len(text) != 0 and ":" in text[-3:] or ";" in text[-3:]:
        return True