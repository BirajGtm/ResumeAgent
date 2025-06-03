from modules.llm_router import run_llm_task


def generate_cover_letter(resume_text, jd_text, model):
    """
    Uses an LLM to create a personalized cover letter based on the resume and job description.
    """
    system_prompt = (
        "You are a professional career assistant."
        "Generate a concise, personalized cover letter based on the candidate's resume and the job description.\n"
        "Do NOT invent facts.\n"
        "Use a professional but warm tone.\n"
        "Structure it in 3 short paragraphs:\n"
        "1. Why you're applying\n"
        "2. How your background fits\n"
        "3. Why you're excited to contribute"
    )

    user_prompt = f"""
Here is the resume:
---
{resume_text}

And here is the job description:
---
{jd_text}

Please generate a short, job-specific cover letter.
"""

    response = run_llm_task(
        task="cover_letter",
        prompt=user_prompt,
        context=None,
        model_preference=model,
        system_prompt=system_prompt
    )

    return response.get("output", "⚠️ No cover letter generated.")
