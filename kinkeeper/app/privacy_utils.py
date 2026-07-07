import re

# Regex patterns for PII redaction
PHONE_PATTERN = re.compile(
    r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
)
EMAIL_PATTERN = re.compile(
    r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
)
ADDRESS_PATTERN = re.compile(
    r'\d+\s+(?:[A-Za-z0-9#\-\.]+[\s,]+){1,4}(?:Street|St|Avenue|Ave|Road|Rd|Highway|Hwy|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Circle|Cir|Way|Pkwy|Parkway|Plaza|Pl)\b',
    re.IGNORECASE
)
SECRET_PATTERN = re.compile(
    r'(?:AIzaSy[a-zA-Z0-9-_]{33})|(?:sk-[a-zA-Z0-9]{32,})|(?:\b[a-fA-F0-9]{32,}\b)'
)
URL_PATTERN = re.compile(
    r'https?://[a-zA-Z0-9./?=&_%+-]+'
)

def redact_pii(text: str) -> str:
    """Redacts phone numbers, emails, addresses, secrets, and URLs from text."""
    if not text:
        return ""
    
    text = PHONE_PATTERN.sub("[PHONE_REDACTED]", text)
    text = EMAIL_PATTERN.sub("[EMAIL_REDACTED]", text)
    text = ADDRESS_PATTERN.sub("[ADDRESS_REDACTED]", text)
    text = SECRET_PATTERN.sub("[SECRET_REDACTED]", text)
    text = URL_PATTERN.sub("[URL_REDACTED]", text)
    
    return text

def detect_prompt_injection(text: str) -> list[str]:
    """Scans for potential prompt injection phrases and returns matching phrases."""
    injection_phrases = [
        "ignore previous instructions",
        "ignore all instructions",
        "system prompt",
        "developer message",
        "reveal secrets",
        "print the api key",
        "disable security",
        "send this message automatically",
        "buy flowers automatically",
        "delete all files"
    ]
    
    matches = []
    for phrase in injection_phrases:
        if phrase in text.lower():
            matches.append(phrase)
            
    return matches
