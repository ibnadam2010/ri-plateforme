import re
import numpy as np

#External py pages
import IsUppercaseOrNumber
import RemovePdfTabulation


def split_paragraph_pdf(text):       
    paragraphs = []
    paragraph_tmp = ""
    len_lines = []
    para_splits = re.split("(?<![:;])(?<=[.?A-Z])\n *\n(?=[A-Z1-9])", text) #On split les paragraphe identifiable facilement ceux avec retour a la ligne + ligne vide
    for para in para_splits:                                             #sans prendre ceux qui finissent par : ou ;
        lines_text = re.split("\n", para)
        #On récupère les longueurs des lignes d'une page pour calculer la moyenne des longueurs des lignes et decider d'un 
        #seuil ou les lignes de fin de paragraphe sont en dessous de ce seuil 
        #car c'est au plus plus petite que la moyenne des lignes d'un texte)
        for line_text in lines_text:
            if not IsUppercaseOrNumber.is_all_uppercase_or_number(line_text):len_lines.append(len(line_text))

        len_lines = [x for x in len_lines if x != 0]
        if len(len_lines) != 0 : lines_mean = np.mean(len_lines)
        else : lines_mean = 84 # valeur heuristique d'une ligne complète  ancien 84

        #On regarde ligne par ligne pour stocker d'éventuel paragraphe qui serait du type \n (retour a ligne sans ligne vide)
        for line_text in lines_text:
            if not IsUppercaseOrNumber.is_all_uppercase_or_number(line_text): paragraph_tmp += line_text+" "
            #print("LEN ligne : ",len(line_text),line_text)
            if len(line_text) != 0 and line_text[-1] in [".","?","]","»"] and len(line_text) < lines_mean : #On est dans un potentiel fin de paragraphe type \n
                if not IsUppercaseOrNumber.is_all_uppercase_or_number(paragraph_tmp): 
                    paragraphs.append(paragraph_tmp)
                paragraph_tmp = ""

        if not IsUppercaseOrNumber.is_all_uppercase_or_number(paragraph_tmp): paragraphs.append(paragraph_tmp)
        
    paragraphs = [RemovePdfTabulation.clean_text_pdf_second_step(paragraph) for paragraph in paragraphs if len(paragraph) > 145]  
    #145 bonne valeurs après tests empiriques 
    
    return paragraphs