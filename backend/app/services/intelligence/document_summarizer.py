import re

from app.core.config import settings, get_groq_client



MODEL_NAME = "openai/gpt-oss-20b"


def clean_summary(text: str) -> str:
    """
    Clean unnecessary Markdown formatting
    from the generated summary.
    """

    if not text:
        return ""

    text = text.strip()

    text = re.sub(
        r"^```.*?\n",
        "",
        text
    )

    text = re.sub(
        r"\n```$",
        "",
        text
    )

    return text.strip()


def summarize_chunk_group(
    chunk_texts: list[str],
    group_number: int
) -> str:
    """
    Generate an intermediate summary for a group
    of document chunks.
    """

    combined_text = "\n\n".join(
        chunk_texts
    )

    prompt = f"""
You are an Enterprise Document Summarization system.

Summarize the following section of an enterprise
document.

This is summary group {group_number}.

IMPORTANT RULES:

1. Use ONLY the provided document content.
2. Do not use outside knowledge.
3. Do not invent facts.
4. Preserve important technical terminology.
5. Preserve important names, numbers, dates,
   definitions and concepts when relevant.
6. Focus on the main information.
7. Remove unnecessary repetition.
8. Write a clear and concise paragraph.
9. Do not use Markdown headings.
10. Return ONLY the summary.

DOCUMENT SECTION
==================================================

{combined_text}

==================================================

SUMMARY:
"""

    client = get_groq_client()
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a reliable enterprise "
                    "document summarization system."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        max_completion_tokens=800
    )

    content = response.choices[0].message.content

    if not content:
        return ""

    return clean_summary(
        content
    )


def generate_final_summary(
    partial_summaries: list[str],
    filename: str
) -> str:
    """
    Combine intermediate summaries into one
    final document-wide summary.
    """

    combined_summaries = "\n\n".join(
        f"Section {index + 1}:\n{summary}"
        for index, summary
        in enumerate(partial_summaries)
        if summary
    )

    prompt = f"""
You are an Enterprise Document Summarization system.

Create the final summary of the complete document
using the intermediate summaries provided below.

IMPORTANT RULES:

1. Use ONLY the information contained in the
   intermediate summaries.
2. Do not use outside knowledge.
3. Do not invent information.
4. Preserve important technical terminology.
5. Preserve important facts, names, numbers and
   dates when relevant.
6. Combine related information.
7. Remove repetition.
8. Make the result easy to understand.
9. The final summary should represent the document
   as a whole.
10. Return ONLY the final summary.
11. Do not use Markdown headings.

Filename:
{filename}

INTERMEDIATE SUMMARIES
==================================================

{combined_summaries}

==================================================

FINAL SUMMARY:
"""

    client = get_groq_client()
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a reliable enterprise "
                    "document summarization system."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        max_completion_tokens=1200
    )

    content = response.choices[0].message.content

    if not content:
        return ""

    return clean_summary(
        content
    )


def summarize_document(
    document_text: str,
    filename: str,
    group_size: int = 4
) -> str:
    """
    Generate a document-wide summary using
    chunk-group summarization followed by
    final synthesis.
    """

    if not document_text.strip():
        return ""

    # -------------------------------------------------
    # Split document into manageable sections
    # -------------------------------------------------

    paragraphs = [
        paragraph.strip()
        for paragraph in document_text.split("\n\n")
        if paragraph.strip()
    ]

    if not paragraphs:
        return ""

    # -------------------------------------------------
    # Create groups
    # -------------------------------------------------

    groups = []

    for index in range(
        0,
        len(paragraphs),
        group_size
    ):

        groups.append(
            paragraphs[
                index:index + group_size
            ]
        )

    # -------------------------------------------------
    # Summarize each group
    # -------------------------------------------------

    partial_summaries = []

    for index, group in enumerate(
        groups,
        start=1
    ):

        summary = summarize_chunk_group(
            chunk_texts=group,
            group_number=index
        )

        if summary:
            partial_summaries.append(
                summary
            )

    if not partial_summaries:
        return ""

    # -------------------------------------------------
    # If only one group exists, return it directly
    # -------------------------------------------------

    if len(partial_summaries) == 1:
        return partial_summaries[0]

    # -------------------------------------------------
    # Generate final document-wide summary
    # -------------------------------------------------

    final_summary = generate_final_summary(
        partial_summaries=partial_summaries,
        filename=filename
    )

    return final_summary