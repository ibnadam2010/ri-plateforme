

def is_all_uppercase_or_number(text):
    words = text.split()
    return all(word.isupper() for word in words) or text.isdigit()