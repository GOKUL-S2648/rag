import json
import re

from app.core.config import settings, get_groq_client



MODEL_NAME = "openai/gpt-oss-20b"


def clean_json_response(text: str):
    """
    Remove Markdown code fences and parse JSON.
    """

    if not text:
        return None

    text = text.strip()

    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        return None


def compare_documents(
    document_a_text: str,
    document_b_text: str,
    document_a_name: str,
    document_b_name: str
):
    """
    Compare two enterprise documents using
    grounded LLM analysis.
    """

    prompt = f"""
You are an Enterprise Document Comparison system.

Compare the two documents provided below.

IMPORTANT RULES:

1. Use ONLY the information contained in the two documents.
2. Do not use outside knowledge.
3. Do not invent facts.
4. Clearly distinguish Document A and Document B.
5. Identify information that is common to both documents.
6. Identify important differences.
7. Identify unique information in each document.
8. Preserve important names, terminology, numbers and dates.
9. If something cannot be determined from the documents,
   say so.
10. Return ONLY valid JSON.
11. Do not use Markdown code fences.

The JSON must have exactly these fields:

{{
    "document_a": {{
        "name": "",
        "summary": ""
    }},
    "document_b": {{
        "name": "",
        "summary": ""
    }},
    "common_information": [],
    "key_differences": [],
    "document_a_unique": [],
    "document_b_unique": [],
    "comparison_summary": ""
}}

DOCUMENT A
==================================================

Name:
{document_a_name}

{document_a_text}

==================================================

DOCUMENT B
==================================================

Name:
{document_b_name}

{document_b_text}

==================================================

COMPARISON:
"""

    client = get_groq_client()
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a reliable enterprise document "
                    "comparison system. Return valid JSON only."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        max_completion_tokens=1800
    )

    content = response.choices[0].message.content

    result = clean_json_response(
        content
    )

    if result is not None:
        return result

    return {
        "document_a": {
            "name": document_a_name,
            "summary": ""
        },
        "document_b": {
            "name": document_b_name,
            "summary": ""
        },
        "common_information": [],
        "key_differences": [],
        "document_a_unique": [],
        "document_b_unique": [],
        "comparison_summary": (
            "Unable to generate a structured comparison."
        )
    }