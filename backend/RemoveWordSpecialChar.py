import re
from cleanText import clean_text_both

def clean_text_word(text):
    #clean les titres des images ou doc qui sont dans les words 
    text = re.sub(r"Figure\s*(\d+)?[:-–]\s*[\s\S]*",'',text)
    #retirer les \f et \xa0
    text = re.sub(r"\x0c",'',text)
    text = re.sub(r"\xa0",' ',text)
    #retirer les biblio ds word
    text = re.sub(r"Bibliographie(\n)?[\s\S]*(?=Contribution)",'',text)
    text = clean_text_both(text)
    return text