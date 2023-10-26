import re
from cleanText import clean_text_both

#Premier clean du text sans retirer les \n car ils seront utile pour decouper nos paragraphe pour les pdf 
def Remove_Special_Characters_In_Text(text):
    #Retirer certains titres 
    text = re.sub(r"(\d+\n\n)?[A-Z&,’: ]{10,}(\n)?",'',text)
    #retirer les fin de pages (les confidentiel et les numéro de page)
    text = re.sub(r"(?<=\n)Confidentiel(\n\n)?",' ',text)
    text = re.sub(r"page \d+",'',text)
    #retirer les titres de figure
    text = re.sub(r"(\n)?(\n)?Figure\s*\d+\s*[:-–]\s*[\s\S]*?(?=\n\n)",' ',text)
    #retirer les \f et \xa0
    text = re.sub(r"\x0c",'',text)
    text = re.sub(r"\xa0",'',text)
    #retirer les pattern \•\•\•\• qui viennent des bullets point mal extrait par pdf
    text = re.sub(r"(\n•)+",'',text)
    #retirer les Bibliographie des textes
    text = re.sub(r"(\n\d\.\d\n\n)?Bibliographie[\s\S]*?(?=\n\n\d)",'', text)
    #retirer les \n d'un \n\n\n on veut en garder que 2 \n
    text = re.sub(r"(?<=\n \n)\n",'',text)
    #nettoyer des accents, charatères spéciaux et espace 
    text = clean_text_both(text)
    return text