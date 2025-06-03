import re

def clean_job_description(jd_text):
    """
    Cleans and normalizes a raw job description string.
    Returns cleaned text ready for processing by LLM.
    """
    # 1. Remove HTML tags if pasted from job boards
    jd_text = re.sub(r'<[^>]+>', '', jd_text)

    # 2. Remove duplicated whitespace and line breaks
    jd_text = re.sub(r'\s+', ' ', jd_text).strip()

    # 3. Normalize bullets
    jd_text = re.sub(r'[\u2022\u2023\u25E6\u2043\u2219\-]+', '-', jd_text)

    # 4. Remove sections like "About the Company", "EEO", etc.
    jd_text = re.sub(r'(about us|our mission|equal opportunity employer|who we are).*?(?=(responsibilities|qualifications|requirements|skills|apply|$))', '', jd_text, flags=re.IGNORECASE|re.DOTALL)

    # 5. Strip trailing fluff (e.g., "We thank all applicants...")
    jd_text = re.sub(r'thank you for applying.*$', '', jd_text, flags=re.IGNORECASE)

    return jd_text.strip()

# Optional test driver
if __name__ == "__main__":
    raw = open("input/job_description.txt", encoding="utf-8").read()
    print(clean_job_description(raw))
