import re
import os
from logger import logger

    
def process_tat(start, end):
    tat=(end - start)
    return tat


def extract_name_number_designation(text_content: str) -> dict:
    logger.info(f"text:{text_content}")
    result = {"email": None, "number": None, "website": None}

    # Email
    email_match = re.search(r'[a-z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', text_content)
    if email_match:
        result["email"] = email_match.group()

    # Phone number: must have at least 10 digits total
    for match in re.finditer(r'(?:\+?\d[\s\-.]?)?(?:\(?\d{2,4}\)?[\s\-.]?)?\d{3,5}[\s\-.]?\d{4,6}', text_content):
        if len(re.sub(r'\D', '', match.group())) >= 10:
            result["number"] = match.group().strip()
            break

    # Website
    website_match = re.search(
        r'https?://[a-zA-Z0-9\-]+(?:\.[a-zA-Z0-9\-]+)+(?:/[^\s]*)?|(?:www\.)[a-zA-Z0-9\-]+(?:\.[a-zA-Z0-9\-]+)+(?:/[^\s]*)?',
        text_content
    )
    if website_match:
        result["website"] = website_match.group()

    return result

