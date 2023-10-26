import regex as re

def clean_text_both(text):

    #normalization du texte lower + accent + caractères spéciaux 

    text = text.lower()
    text = re.sub(r"[éèêë]",'e',text)
    text = re.sub(r"[àâäáã]",'a',text)
    text = re.sub(r"[ùûüú]",'u',text)
    text = re.sub(r"ç",'c',text)
    text = re.sub(r"[’‘]","'",text)
    text = re.sub(r"ô","o",text)
    text = re.sub(r"œ","oe",text)
    text = re.sub(r"”","""''""",text)
    text = re.sub(r"[ïíî]","i",text)
    text = re.sub(r"\t","   ",text)
    text = re.sub(r"ﬁ","fi",text)
    text = re.sub(r"ﬂ","fl",text)
    text = re.sub(r"š","s",text)
    #retirer les \f et \xa0
    text = re.sub(r"\x0c",'',text)
    text = re.sub(r"\xa0",' ',text)
    text = re.sub(r"\u2002"," ",text) #petit espace utilisé pour l'anglais
    text = re.sub(r"\u202f"," ",text) #petit espace utilisé
    text = re.sub(r"\u2009"," ",text) #petit espace utilisé
    text = re.sub(r"\u200e"," ",text) #petit espace utilisé
    text = re.sub(r"\u200b"," ",text) #petit espace utilisé
    text = re.sub(r"\uf050","",text) #caractère 0
    text = re.sub(r"\uf04f","?",text) #caractère 
    text = re.sub(r"\uf074","?",text) #caractère 
    text = re.sub(r"[ ]+", " ", text)

    return text