import os
import cld2
import spacy
import re
import unicodedata


rootdir = '/Users/verlynfischer/Documents/ClusterLanguage'
nlp_es = spacy.load('es_core_news_sm')
nlp_en = spacy.load('en_core_web_sm')

# for subdir, dirs, files in os.walk(rootdir):
#     for file in files:
#         path = os.path.join(subdir, file)
#         f = open(path, "r")
#         contents = f.read()
#         # doc = nlp(contents)
#         # sents = list(doc.sents)
#         # for s in sents:
#         #     print(s)
#         isReliable, textBytesFound, details, langVector = cld2.detect(contents, returnVectors=True)
#         print('----------')
#         print('  File: %s' % file)
#         print('  reliable: %s' % (isReliable != 0))
#         print('  textBytes: %s' % textBytesFound)
#         print('  details: %s' % str(details))
#         print('  vectors: %s' % str(langVector))
#         # sentences = nltk.sent_tokenize(contents,language='english')
#         # print(sentences)
# The output looks like so:
#  reliable: True
#  textBytes: 24
#  details: (('ENGLISH', 'en', 95, 1736.0), ('Unknown', 'un', 0, 0.0), ('Unknown', 'un', 0, 0.0))

def getlanguageSpans(documentText):
    # Mimics what JANUS will do when detecting languages
    # Provides a span and it's language

    spanList = []

    isReliable, textBytesFound, details, langVector = cld2.detect(documentText, returnVectors=True)
    for offset, num_bytes, lang_name, lang_code in langVector:
        textSpan = documentText[offset:offset + num_bytes]
        spanList.append((lang_code, textSpan))

    return spanList

def getSentences(documentSpan):
    # Segments the document span based on the indicated language
    # For non-supported languages, it returns an empty list
    # For unsegmentable languages, it simply returns sets of 25 characters (e.g. CJK)
    doc_en = nlp_en(documentSpan)
    doc_es = nlp_es(documentSpan)
    sents_en = list(doc_en.sents)
    sents_es = list(doc_es.sents)
    return (sents_en, sents_es)

def eliminate_single_tokens_str(text):
    tokens = text.split(' ')
    ulist = []
    [ulist.append(x) for x in tokens if len(x) > 1]
    new_str = " ".join(ulist)
    return new_str

def eliminate_email_address(text):
    return re.sub('<\S+@\S+\\.\S+>', '<>', text)

def cleanup_email_header(text):
    lines = text.splitlines(True)
    ulist = []
    for x in lines:
        if x.strip().startswith("Sent:"):
            continue
        ulist.append(eliminate_email_address(x))

    new_text = "".join(ulist)
    return new_text

def eliminate_duplicate_words_str(text):
    tokens = text.split(' ')
    ulist = []
    [ulist.append(x) for x in tokens if x not in ulist]
    new_str = " ".join(ulist)
    return new_str

def eliminate_utf8_control_chars(text):
    return ''.join(x for x in text if (unicodedata.category(x) != 'Cc'))

def preProcess(documentText):
    documentText = eliminate_utf8_control_chars(documentText)
    documentText = eliminate_single_tokens_str(documentText)
    documentText = eliminate_duplicate_words_str(documentText)
    documentText = cleanup_email_header(documentText)
    return documentText

def main():
    # Iterate through documents - mimics JANUS ingest
    rootdir = '/Users/verlynfischer/Documents/ClusterLanguage'
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            path = os.path.join(subdir, file)
            f = open(path, "r")
            contents = f.read()
            languageSpans = getlanguageSpans(contents)
            for lang_code, textSpan in languageSpans:
                textSpanCleaned = preProcess(textSpan)
                print()
                print('------ SPAN BREAK -----')
                print('Language Code: ', lang_code)
                print()
                print(textSpanCleaned)
                print()
                print('------ END OF SPAN -----')
                print()
                if lang_code == 'en':
                    sentences_en, sentences_es = getSentences(textSpanCleaned)
                    for sentence in sentences_en:
                        print('>>>>  File: ',file, '   Language: ', lang_code, '  Sentence: ', sentence)
                if lang_code == 'es':
                    sentences_en, sentences_es = getSentences(textSpanCleaned)
                    for sentence in sentences_es:
                        print('>>>>  File: ',file, '   Language: ', lang_code, '  Sentence: ', sentence)

main()