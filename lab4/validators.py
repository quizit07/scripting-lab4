import re

SKU_RE = re.compile(r"^[A-Z]{3}-\d{4}$")
PHONE_RE = re.compile(r"^\+380\d{9}$")
EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")


def validate_sku(value: str) -> str:
    if not SKU_RE.match(value):
        raise ValueError("SKU must look like ABC-1234")
    return value
