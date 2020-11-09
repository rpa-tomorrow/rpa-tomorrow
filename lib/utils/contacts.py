from fuzzywuzzy import process as fuzzy
from lib.settings import SETTINGS, load_local_contacts
from lib.utils.email import is_email

MIN_SCORE = 75  # the minimum score needed to consider the fuzzy match


def get_emails(names):
    """
    Returns a dictionary containing three key-value pairs given a string list
    containing names or emails. The key-value pairs reflects the results of
    trying to resolve the names with known contacts. If one of the names is a
    valid email it will be added to the resulting email list directly.

    Returns a dictionary with the following key-value pairs:
        - emails: the emails of the names which could be found and resolved
        - uncertain: list of tuples containing the name and a list of
                     the candidates which share the same name. Should be used
                     in a follow-up to resolve the correct contact.
        - unknown: a list of names which could not be resolved from the known
                   contacts, any invalid emails will also be returned in this
                   list
    """
    load_local_contacts()
    emails = []
    uncertain_contacts = []
    unknown_contacts = []

    for name in names:
        # Assume valid recipient if input is already an email
        if is_email(name):
            emails.append(name)
            continue

        matches = fuzzy.extract(name, SETTINGS["contacts"].keys())
        matches = list(filter(lambda x: x[1] > MIN_SCORE, matches))
        if len(matches) > 1:
            candidates = []
            for candidate_name, score in matches:
                c = (
                    candidate_name,
                    SETTINGS["contacts"][candidate_name]["email"]["address"],
                )
                candidates.append(c)
            uncertain_contacts.append((name, candidates))
        elif len(matches) == 1:
            name, _ = matches[0]
            emails.append(SETTINGS["contacts"][name]["email"]["address"])
        else:
            unknown_contacts.append(name)

    return {
        "emails": emails,
        "uncertain": uncertain_contacts,
        "unknown": unknown_contacts,
    }
