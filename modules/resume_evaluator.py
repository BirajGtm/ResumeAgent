from modules.llm_router import run_llm_task


def evaluate_resume(resume_text, jd_text, model="gpt-4o"):
    """
    Asks the selected LLM to act as a hiring manager and evaluate resume alignment.
    Returns score and detailed feedback.
    """
    system_prompt = (
        "You are a hiring manager reviewing a candidate's resume. "
        "Evaluate how well this resume fits the job description.\n"
        "Give a score out of 100 and explain what was strong or lacking.\n"
        "Do not assume or hallucinate details. Be honest but constructive."
    )

    user_prompt = f"""
Job Description:
---
{jd_text}

Candidate Resume:
---
{resume_text}

Please rate and review this candidate's resume for the job.
Start with a score out of 100 and detailed feedback on strengths and weaknesses.
Do not start with "As an AI" , "In my opinion" or similar phrases.
Just give the score and feedback directly.
"""

    response = run_llm_task(
        task="evaluation",
        prompt=user_prompt,
        context=None,
        model_preference=model,
        system_prompt=system_prompt
    )

    return response.get("output", "⚠️ No feedback returned.")
