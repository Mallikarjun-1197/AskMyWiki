import re

def sanitize_id(value):
    value = re.sub(r'[^A-Za-z0-9_\-=]', '_', value)
    value = re.sub(r'^_+', '', value)
    return value