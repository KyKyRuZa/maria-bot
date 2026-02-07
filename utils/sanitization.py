import html
import re

def sanitize_html(text: str) -> str:
    if text is None:
        return ""
    return html.escape(str(text))

def sanitize_user_data(data: dict) -> dict:
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_html(value)
        elif isinstance(value, (int, float, type(None))):
            sanitized[key] = value
        else:
            sanitized[key] = sanitize_html(str(value))
    return sanitized