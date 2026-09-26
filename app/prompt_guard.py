import re
from typing import Tuple


INJECTION_PATTERNS = [
    r"\bignore\s+(all\s+)?previous\s+instructions\b",
    r"\bdisregard\s+(all\s+)?previous\s+instructions\b",
    r"\bforget\s+(all\s+)?previous\s+instructions\b",
    r"\breveal\s+(the\s+)?system\s+prompt\b",
    r"\bshow\s+(me\s+)?the\s+system\s+message\b",
    r"\breveal\s+(the\s+)?secret\b",
    r"\bprint\s+(the\s+)?api\s*key\b",
    r"\bexpose\s+(the\s+)?password\b",
    r"\bjailbreak\b",
    r"\byou\s+are\s+now\s+(a|an)\b",
]


SECRET_PATTERNS = [
    (re.compile(r"(?i)(authorization\s*:\s*bearer\s+)[A-Za-z0-9._~+/=-]+"),
     r"\1[REDACTED]"),
    (re.compile(r"(?i)(\bbearer\s+)[A-Za-z0-9._~+/=-]+"),
     r"\1[REDACTED]"),
    (re.compile(r"(?i)(\bapi[_ -]?key\s*[:=]\s*)[^\s,;]+"),
     r"\1[REDACTED]"),
    (re.compile(r"(?i)(\bpassword\s*[:=]\s*)[^\s,;]+"),
     r"\1[REDACTED]"),
    (re.compile(r"(?i)(\bsecret\s*[:=]\s*)[^\s,;]+"),
     r"\1[REDACTED]"),
]


def redact_sensitive(text: str) -> str:
    redacted = text

    for pattern, replacement in SECRET_PATTERNS:
        redacted = pattern.sub(replacement, redacted)

    return redacted


def detect_prompt_injection(text: str) -> Tuple[bool, str]:
    lowered = text.lower()

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, lowered, flags=re.IGNORECASE):
            return True, pattern

    return False, ""


def validate_input(text: str) -> Tuple[bool, str]:
    injection_found, pattern = detect_prompt_injection(text)

    if injection_found:
        return False, f"prompt-injection detected: {pattern}"

    return True, ""
