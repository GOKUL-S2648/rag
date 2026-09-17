import json
import re

from groq import Groq

from app.core.config import settings


client = Groq(
    api_key=settings.GROQ_API_KEY
)


def extract_topic_headings(text: str):
    """
    Extract explicit TOPIC headings from document text.
    """

    patterns = [
        r"TOPIC\s+\d+(?:\.\d+)*\s*:\s*(.+)",
        r"Topic\s+\d+(?:\.\d+)*\s*:\s*(.+)",
    ]

    topics = []

    for line in text.splitlines():

        line = line.strip()

        for pattern in patterns:

            match = re.search(
                pattern,
                line
            )

            if match:

                topic = match.group(1).strip()

                if topic and topic not in topics:
                    topics.append(topic)

    return topics


def analyze_document(
    document_text: str,
    filename: str,
    page_count: int,
    chunk_count: int
):
    """
    Generate structured intelligence for a document.
    """

    explicit_topics = extract_topic_headings(
        document_text
    )

    prompt = f"""
You are an Enterprise Document Intelligence system.

Analyze the document provided below.

Return ONLY valid JSON.

The JSON must have exactly these fields:

{{
    "title": "document title",
    "summary": "short summary of the document",
    "topics": [],
    "key_concepts": [],
    "important_terms": [],
    "discussion_questions": []
}}

Rules:

1. Use ONLY information from the document.
2. Do not invent information.
3. Preserve technical terminology from the document.
4. Topics should represent major topics explicitly supported
   by the document.
5. Key concepts should be important technical concepts.
6. Important terms should be important named terms or phrases.
7. Discussion questions should contain questions explicitly
   present in the document.
8. Keep the summary concise.
9. Return valid JSON only.
10. Do not include Markdown code fences.

Filename:
{filename}

Page Count:
{page_count}

Chunk Count:
{chunk_count}

Explicit Topic Headings Found:
{json.dumps(explicit_topics)}

DOCUMENT:
==================================================

{document_text}

==================================================
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a reliable enterprise "
                    "document intelligence system. "
                    "Return valid JSON only."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        max_completion_tokens=1500
    )

    content = response.choices[0].message.content

    if not content:
        return {
            "title": filename,
            "summary": "",
            "topics": explicit_topics,
            "key_concepts": [],
            "important_terms": [],
            "discussion_questions": []
        }

    content = content.strip()

    # Remove accidental Markdown code fences
    content = re.sub(
        r"^```json\s*",
        "",
        content,
        flags=re.IGNORECASE
    )

    content = re.sub(
        r"\s*```$",
        "",
        content
    )

    try:

        analysis = json.loads(content)

    except json.JSONDecodeError:

        analysis = {
            "title": filename,
            "summary": "",
            "topics": explicit_topics,
            "key_concepts": [],
            "important_terms": [],
            "discussion_questions": []
        }

    # Always preserve explicit headings found directly
    # from the document.
    if explicit_topics:

        analysis["topics"] = explicit_topics

    analysis["page_count"] = page_count
    analysis["chunk_count"] = chunk_count

    return analysis