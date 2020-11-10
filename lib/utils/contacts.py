from fuzzywuzzy import process as fuzzy

from lib.automate.google import Google, ContactBookInterruptedByUserError
from lib.settings import SETTINGS, load_local_contacts
from lib.utils.email import is_email
from lib import Error

MIN_SCORE = 75  # the minimum score needed to consider the fuzzy match


def get_emails(names, sender=None):
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
    google = None

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
            if sender:
                possible_receivers = []

                if not google:
                    settings = sender["email"]
                    username = settings.get("username")
                    google = Google(username).people()

                try:
                    possible_receivers = list(set(google.search([name])))
                except ContactBookInterruptedByUserError:
                    pass
                if len(possible_receivers) == 0:
                    unknown_contacts.append(name)
                elif len(possible_receivers) >= 1:
                    uncertain_contacts.append((name, possible_receivers))
            else:
                unknown_contacts.append(name)

    return {
        "emails": emails,
        "uncertain": uncertain_contacts,
        "unknown": unknown_contacts,
    }


def prompt_contact_choice(name: str, candidates) -> str:
    followup_str = ""
    if len(candidates) == 1:
        followup_str = f"Found a contact with the name {name}\n"
        c_name, c_email = candidates[0]
        followup_str += f"[1] {c_name} - {c_email}\n"
        followup_str += "\n[0] Not the right one \nPlease choose one (0-1)"
    else:
        followup_str = f"Found multiple contacts with the name {name}\n"
        for i in range(len(candidates)):
            c_name, c_email = candidates[i]
            followup_str += f"[{i+1}] {c_name} - {c_email}\n"
        followup_str += f"\n[0] None of the above \nPlease choose one (0-{len(candidates)})"
    return followup_str


def followup_contact_choice(module, answer):
    try:
        choice = int(answer) - 1
    except Exception:
        return module.prepare_processed(module.to, module.when, module.body, module.sender)
    name, candidates = module.uncertain_attendee
    if choice < 0:
        raise NoContactFoundError("No contact with name " + name + " was found")
    elif choice >= 0 and choice < len(candidates):
        module.to.remove(name)  # update to so recursive call continues resolving new attendees
        module.to.append(candidates[choice][1])  # add email of chosen attendee
    return module.prepare_processed(module.to, module.when, module.body, module.sender)


class NoContactFoundError(Error):
    pass
