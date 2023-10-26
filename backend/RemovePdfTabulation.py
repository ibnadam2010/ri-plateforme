import re


#Deuxieme clean pour retirer tout les \n restants des pdf 
def clean_text_pdf_second_step(text):
    #retirer les \n des pdf
    text = re.sub(r"\n",' ',text)
    return text