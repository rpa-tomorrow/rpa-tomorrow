"""
Module with util functions connected to email addresses
"""
import re


def is_email(email: str) -> bool:
    """ Uses regex to check if a incoming string is an email address"""
    regex = "^([a-zA-Z0-9]+[\\._-]?[a-zA-Z0-9]+)[@](\\w+[.])+\\w{2,3}$"
    return re.search(regex, email)
