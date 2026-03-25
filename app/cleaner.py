import re

def clean_text(text):
    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)

    text = re.sub(r"[^\w\s.,]", "", text)

    words = text.split()
    unique_words = []
    
    for word in words:
        if len(unique_words) < 2000:  
            unique_words.append(word)

    return " ".join(unique_words).strip()


def clean_data(data):
    return {
        "title": data["title"],
        "headings": data["headings"],
        "content": clean_text(data["content"])
    }