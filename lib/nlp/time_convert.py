import spacy
import time

from datetime import datetime, timedelta
from word2number import w2n


def parse_time(when_list):
    """
    Parses strings of time to datetime, it is assumed that the words in the list
    is ordered. I.e. ["two", "hours"] not ["hours", "two"] or ["13.00"]. If the time
    has already passed, it will assume it is for the next day.
    Should it fail to parse, None will be returned.

    :param when_list A list of strings
    :type list
    :return The date
    :rtype datetime.datetime
    """
    datetime = None

    if len(when_list) == 0:
        return None

    if len(when_list) == 1:
        try:
            datetime = parse_24h_time(when_list[0])
        except:
            pass
        try:
            datetime = parse_word_time(when_list[0])
        except:
            pass
    else:
        try:
            datetime = parse_unit_time(when_list[0], when_list[1])
        except:
            pass
        try:
            _time = when_list[0] + " " + when_list[1]
            datetime = parse_12h_time(_time)
        except:
            pass

    if datetime is not None:
        datetime = increment_24h_if_passed(datetime)

    return datetime


def increment_24h_if_passed(time):
    when_delta = (time - datetime.now()).total_seconds()

    # Check if the time has already happened
    if when_delta < 0.0:
        time = time + timedelta(hours=24)

    return time


def parse_word_time(word):
    """
    Parses a single word to a datetime. I.e. "seven" -> 07:00 or 19:00
    depening on which hasn't occured yet.
    """
    time = datetime.now()
    number = w2n.word_to_num(word)
    time = time.replace(hour=number, minute=0, second=0)

    when_delta = (time - datetime.now()).total_seconds()

    # Check if the time has already happened
    if when_delta < 0.0:
        td = timedelta(hours=12)
        time = time + td

    return time


def parse_unit_time(word, unit):
    """
    Parses a word and a unit to datetime. Works on the following formats
    <NUMBER> <UNIT>
    E.g. ["2", "hours"]
    
    :param words The list of words to parse
    :type list
    :return A datetime
    :rtype datetime.datetime
    """
    number = 1
    time_multiplier = 1

    if word in ["a", "an"]:
        number = 1
    else:
        number = w2n.word_to_num(word)

    time_multiplier = unit_to_sec(unit)

    offset = number * time_multiplier
    ret_time = time.time() + offset

    return datetime.fromtimestamp(ret_time)


def parse_24h_time(time):
    """
    Parses a string to datetime in the following 24h formats
    13:00, 1.50 or 7
    
    :param time String to parse
    :type string
    :return A datetime of the string
    :rtype datetime.datetime
    """
    ret_time = datetime.now()
    t = format_24h_time(time)

    ret_time = ret_time.replace(hour=t.hour, minute=t.minute, second=0)
    return ret_time


def format_24h_time(time):
    t = None
    formats = ["%H:%M", "%H.%M", "%H"]

    for _format in formats:
        try:
            t = datetime.strptime(time, _format)
        except:
            pass

    return t


def parse_12h_time(time):
    """
    Parses a list of strings to datetime in the following 12h formats
    1:00 pm, 03.50 am or 7 pm
    
    :param time String to parse
    :type string
    :return A datetime of the string
    :rtype datetime.datetime
    """
    ret_time = datetime.now()
    t = format_12h_time(time)

    ret_time = ret_time.replace(hour=t.hour, minute=t.minute, second=0)
    return ret_time


def format_12h_time(time):
    t = None
    formats = ["%I:%M %p", "%I.%M %p", "%I %p"]

    for _format in formats:
        try:
            t = datetime.strptime(time, _format)
        except:
            pass

    return t


def unit_to_sec(unit):
    """
    Takes a time unit and tries to convert it into seconds.
    E.g. "hours" => 3600
    
    :param unit The unit to convert to seconds
    :type string

    :return An integer representing the seconds of the time unit
    :rtype int
    """
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(unit)

    lemma = doc[0].lemma_

    if lemma in ["hour", "h"]:
        return 3600
    elif lemma in ["minute", "mins", "min", "m"]:
        return 60
    elif lemma in ["second", "secs", "sec", "s"]:
        return 1
    elif lemma in ["moment"]:
        return 90
    elif lemma in [
        "day",
        "d",
    ]:
        return 86400
    elif lemma in ["week", "w"]:
        return 604800
    else:
        raise Exception("Could not convert time type.")
