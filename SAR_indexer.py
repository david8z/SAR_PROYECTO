import re
clean_re = re.compile('\W+')

def clean_text(text):
    return clean_re.sub(' ', text)