# routes/utils.py
import re
from bs4 import BeautifulSoup

def clean_llm_markdown_output(output_str: str) -> str:
    if not output_str: return ""
    cleaned_str = re.sub(r"^```(?:markdown)?\s*|\s*```$", "", output_str.strip(), flags=re.IGNORECASE | re.MULTILINE)
    return cleaned_str.strip()

def get_plain_text_from_html(html_content: str) -> str:
    if not html_content: return ""
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator='\n', strip=True)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text