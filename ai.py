import google.generativeai as genai
import json
import os

# Read API key from environment variable GEMINI_API_KEY
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize Gemini model
model = genai.GenerativeModel("gemini-2.5-flash")


def analyze_resume(resume_text, user_goal):
    prompt = f"""
You are a senior software engineer and hiring manager.

Evaluate the resume based on the user's target role.

User goal: "{user_goal}"

STRICT RULES:
- Extract only skills relevant to this goal.
- Remove irrelevant tools (for example, Excel for backend roles).
- Generate a roadmap only for missing skills.
- Make the output different based on the goal.
- Return valid JSON only.

Return JSON in exactly this format:
{{
  "skills": [],
  "missing_skills": [],
  "roadmap": [],
  "interview_questions": []
}}

Resume:
{resume_text}
"""

    try:
        response = model.generate_content(prompt)

        # Gemini may wrap JSON in markdown code fences, so clean it
        content = response.text.strip()

        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]

        if content.endswith("```"):
            content = content[:-3]

        content = content.strip()

        # Extract JSON safely
        start = content.find("{")
        end = content.rfind("}") + 1

        if start == -1 or end == 0:
            raise ValueError("No valid JSON found in model response.")

        return json.loads(content[start:end])

    except Exception as e:
        return {
            "skills": [],
            "missing_skills": [],
            "roadmap": [],
            "interview_questions": [],
            "error": str(e)
        }