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
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    ).strip()

    start_idx = text.find("{")
    end_idx = text.rfind("}")

    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        text = text[start_idx:end_idx + 1]

    try:
        return json.loads(text)
    except Exception as e:
        print(f"Error parsing comparison JSON response: {e}")
        return None


def compare_documents(
    document_a_text: str,
    document_b_text: str,
    document_a_name: str,
    document_b_name: str
):
    """
    Compare two enterprise documents using grounded LLM analysis.
    """

    prompt = f"""
You are an Enterprise Document Comparison system.

Compare the two documents provided below.

IMPORTANT RULES:
1. Use ONLY the information contained in the two documents.
2. Do not use outside knowledge or invent facts.
3. Clearly distinguish Document A and Document B.
4. Identify common information, key differences, and unique information for each document.
5. Return ONLY a valid JSON object matching this structure:

{{
    "document_a": {{
        "name": "{document_a_name}",
        "summary": "Detailed summary of Document A"
    }},
    "document_b": {{
        "name": "{document_b_name}",
        "summary": "Detailed summary of Document B"
    }},
    "common_information": ["Common point 1", "Common point 2"],
    "key_differences": ["Difference 1", "Difference 2"],
    "document_a_unique": ["Unique to Document A point 1"],
    "document_b_unique": ["Unique to Document B point 1"],
    "comparison_summary": "Overall comparison summary paragraph"
}}

DOCUMENT A
==================================================
Name: {document_a_name}

{document_a_text}

==================================================

DOCUMENT B
==================================================
Name: {document_b_name}

{document_b_text}

==================================================
"""

    try:
        client = get_groq_client()
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a reliable enterprise document "
                        "comparison system. You must output valid JSON."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0,
            max_completion_tokens=1800
        )

        content = response.choices[0].message.content
        result = clean_json_response(content)

        if result is not None:
            # Normalize document_a structure
            doc_a_val = result.get("document_a")
            if isinstance(doc_a_val, str):
                result["document_a"] = {
                    "name": document_a_name,
                    "summary": doc_a_val
                }
            elif isinstance(doc_a_val, dict):
                if not doc_a_val.get("name"):
                    doc_a_val["name"] = document_a_name
                if not doc_a_val.get("summary"):
                    doc_a_val["summary"] = ""
            else:
                result["document_a"] = {
                    "name": document_a_name,
                    "summary": ""
                }

            # Normalize document_b structure
            doc_b_val = result.get("document_b")
            if isinstance(doc_b_val, str):
                result["document_b"] = {
                    "name": document_b_name,
                    "summary": doc_b_val
                }
            elif isinstance(doc_b_val, dict):
                if not doc_b_val.get("name"):
                    doc_b_val["name"] = document_b_name
                if not doc_b_val.get("summary"):
                    doc_b_val["summary"] = ""
            else:
                result["document_b"] = {
                    "name": document_b_name,
                    "summary": ""
                }

            # Ensure lists and summary exist
            if not isinstance(result.get("common_information"), list):
                result["common_information"] = []
            if not isinstance(result.get("key_differences"), list):
                result["key_differences"] = []
            if not isinstance(result.get("document_a_unique"), list):
                result["document_a_unique"] = []
            if not isinstance(result.get("document_b_unique"), list):
                result["document_b_unique"] = []
            if not result.get("comparison_summary"):
                result["comparison_summary"] = "Comparison completed successfully."

            return result

    except Exception as e:
        print(f"Error calling Groq for document comparison: {e}")

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
        "comparison_summary": "Unable to generate a structured comparison."
    }