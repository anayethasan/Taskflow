import re


def generate_slug(value: str) -> str:
    value = value.lower().strip()

    value = re.sub(
        r"[^a-z0-9]+",
        "-",
        value
    )

    value = value.strip("-")

    return value