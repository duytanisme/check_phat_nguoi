import re


def get_match_plate(input_message):
    cleaned_message = re.sub(r'[^a-zA-Z0-9]', '', input_message.lower())
    pattern = r"\b\d{2}[A-Za-z]\d?-?\d{4,5}\b"
    return re.search(pattern, cleaned_message)


match_plate = get_match_plate("17b-24171")
if match_plate:
    print(match_plate.group())
