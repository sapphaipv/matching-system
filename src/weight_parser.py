# src/weight_parser.py

import re


def parse_weight(text: str):
    """
    Trả về gram (int)
    200g → 200
    1kg → 1000
    500ml → 500
    """

    if not text:
        return None

    match = re.search(r"(\d+)\s?(g|kg|ml|l)\b", text)

    if not match:
        return None

    value = int(match.group(1))
    unit = match.group(2)

    if unit == "kg":
        value *= 1000
    elif unit == "l":
        value *= 1000

    return value