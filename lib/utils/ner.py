# Named Entity Recognition utils using a supported spacy model.
# For most languages it is recommended to use 'xx_ent_wiki_sm' as the model.
from fuzzywuzzy import process as fuzzy


LABEL_PERSON = "PER"
MIN_SCORE = 80


def get_persons(model, text) -> list:
    """
    Using the given spacy model, returns a list of all persons in the text.
    A person can be a full name or an email.

    :param model: The spacy model to use (needs to support NER)
    :type model: spacy.lang
    :param text: The sentence to parse names from
    :type text: str
    """
    doc = model(text)
    persons = []

    for ent in doc.ents:
        if ent.label_ in [LABEL_PERSON]:
            persons.append(ent.text)

    for token in doc:
        if token.like_email and token.text not in persons:
            persons.append(token.text)

    return persons


def cross_check_names(tagged, persons) -> list:
    """
    Cross checks a list with tagged names and a list of persons.
    Uses fuzzywuzzy to see if the tagged names correspond to a name in the
    persons list. Returns a list of non-duplicated matches.

    :param tagged: List of names that have been tagged by the spacy parser
    :type tagged: list
    :param persons: List of persons to match against
    :type persons: list
    """
    ok = []

    for tag in tagged:
        try:
            value, score = fuzzy.extractOne(tag, persons)
            if score > MIN_SCORE and value not in ok:
                ok.append(value)
        except Exception:
            continue

    for tag in tagged:
        if not any(tag in name for name in ok):
            ok.append(tag)

    return ok
