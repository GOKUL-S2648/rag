import re

from app.core.config import settings, get_groq_client



FALLBACK_ANSWER = (
    "I could not find this information in the provided documents."
)


# ============================================================
# TOPIC EXTRACTION
# ============================================================

def extract_topics(context: str):
    """
    Extract explicit TOPIC headings from retrieved
    document content.
    """

    patterns = [
        r"TOPIC\s+\d+(?:\.\d+)*\s*:\s*(.+)",
        r"Topic\s+\d+(?:\.\d+)*\s*:\s*(.+)",
    ]

    topics = []

    for line in context.splitlines():

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


# ============================================================
# QUESTION TYPE DETECTION
# ============================================================

def detect_question_type(question: str) -> str:

    question_lower = question.lower().strip()

    # Topic questions
    if any(
        phrase in question_lower
        for phrase in [
            "main topics",
            "what are the topics",
            "list the topics",
            "topics in this document",
            "topics in the document",
        ]
    ):
        return "topic"

    # Definition questions
    if any(
        phrase in question_lower
        for phrase in [
            "what is ",
            "what are ",
            "define ",
            "definition of ",
            "meaning of ",
        ]
    ):
        return "definition"

    # Comparison questions
    if any(
        phrase in question_lower
        for phrase in [
            "difference between",
            "differences between",
            "compare ",
            "comparison between",
            "distinguish between",
            "vs ",
            "versus ",
        ]
    ):
        return "comparison"

    # Reasoning questions
    if any(
        phrase in question_lower
        for phrase in [
            "why ",
            "why is",
            "why are",
            "why does",
            "why do",
            "reason for",
            "reason behind",
        ]
    ):
        return "reasoning"

    # List questions
    if any(
        phrase in question_lower
        for phrase in [
            "list ",
            "list all",
            "give me the list",
            "name all",
            "what are the important",
            "what are the key",
        ]
    ):
        return "list"

    # Summarization questions
    if any(
        phrase in question_lower
        for phrase in [
            "summarize",
            "summary",
            "give me a summary",
            "briefly explain the document",
            "give an overview",
            "overview of the document",
        ]
    ):
        return "summary"

    # Explanation questions
    if any(
        phrase in question_lower
        for phrase in [
            "explain ",
            "describe ",
            "how does",
            "how do",
            "how is",
            "how are",
        ]
    ):
        return "explanation"

    return "general"


# ============================================================
# ORDINAL TOPIC HANDLING
# ============================================================

def handle_ordinal_topic_question(
    question: str,
    topics: list[str]
):
    question_lower = question.lower()

    ordinal_map = {
        "first topic": 1,
        "second topic": 2,
        "third topic": 3,
        "fourth topic": 4,
        "fifth topic": 5,
        "sixth topic": 6,
        "seventh topic": 7,
        "eighth topic": 8,
        "ninth topic": 9,
        "tenth topic": 10,
    }

    for phrase, number in ordinal_map.items():

        if phrase in question_lower:

            ordinal_names = {
                1: "first",
                2: "second",
                3: "third",
                4: "fourth",
                5: "fifth",
                6: "sixth",
                7: "seventh",
                8: "eighth",
                9: "ninth",
                10: "tenth",
            }

            ordinal = ordinal_names[number]

            if len(topics) >= number:

                return (
                    f"The {ordinal} topic in the "
                    f"provided document is:\n\n"
                    f"{number}. {topics[number - 1]}"
                )

            return (
                f"I could not find a {ordinal} topic "
                f"in the provided document."
            )

    if "last topic" in question_lower:

        if topics:

            return (
                "The last topic in the provided "
                "document is:\n\n"
                f"{len(topics)}. {topics[-1]}"
            )

        return (
            "I could not find any topic in the "
            "provided document."
        )

    return None


# ============================================================
# MAIN RAG GENERATOR
# ============================================================

def generate_rag_answer(
    question: str,
    context: str
):
    """
    Generate an advanced enterprise RAG answer.

    Supports:
    - Topics
    - Definitions
    - Explanations
    - Comparisons
    - Lists
    - Reasoning
    - Summaries
    - General questions
    """

    question_type = detect_question_type(
        question
    )

    # ========================================================
    # TOPIC QUESTIONS
    # ========================================================

    topics = extract_topics(
        context
    )

    ordinal_result = handle_ordinal_topic_question(
        question,
        topics
    )

    if ordinal_result:

        return ordinal_result

    if question_type == "topic":

        if topics:

            if len(topics) == 1:

                return (
                    "The topic in the provided document is:\n\n"
                    f"1. {topics[0]}"
                )

            return (
                "The topics identified in the "
                "provided document are:\n\n"
                + "\n".join(
                    f"{index}. {topic}"
                    for index, topic
                    in enumerate(
                        topics,
                        start=1
                    )
                )
            )

    # ========================================================
    # ADVANCED LLM PROMPT
    # ========================================================

    question_instructions = {

        "definition": """
Answer as a definition question.

Start by clearly defining the requested concept
using information from the source material.

Then briefly explain its role or purpose if the
source provides that information.
""",

        "explanation": """
Answer as an explanation question.

Explain the requested concept or process clearly.
Use the source material to explain how it works,
what it does, or how it is used.
""",

        "comparison": """
Answer as a comparison question.

Identify the two or more concepts being compared.
Present the comparison clearly, preferably using
a structured format or table when appropriate.

Only compare information supported by the source.
""",

        "reasoning": """
Answer as a reasoning question.

Explain the reason, purpose, motivation, or benefit
only when it is supported by the source material.

Do not invent reasoning that is not present in
the source.
""",

        "list": """
Answer as a list question.

Extract the requested items from the source material.
Use a numbered or bulleted list.
Preserve the terminology used in the source.
""",

        "summary": """
Answer as a summarization question.

Provide a concise summary of the relevant document
content available in the source material.

Focus on the main ideas, concepts, and important facts.
""",

        "general": """
Answer the question directly and naturally.

Use the source material to determine the answer.
"""
    }

    instruction = question_instructions.get(
        question_type,
        question_instructions["general"]
    )

    prompt = f"""
You are an Advanced Enterprise Knowledge Assistant.

Your task is to answer the user's question using ONLY
the SOURCE MATERIAL provided below.

QUESTION TYPE:
{question_type}

QUESTION-SPECIFIC INSTRUCTIONS:
{instruction}

IMPORTANT RULES:

1. Carefully read the SOURCE MATERIAL before answering.
2. Use ONLY information supported by the SOURCE MATERIAL.
3. Never use outside knowledge.
4. Never invent facts.
5. Never assume information that is not present.
6. Preserve exact names, numbers, dates, definitions,
   and technical terminology when relevant.
7. If multiple items are requested, use a numbered list.
8. If a comparison is requested, clearly separate the
   compared concepts.
9. If the question is a follow-up question, use the
   previous conversation included in the SOURCE MATERIAL.
10. Give a concise but complete answer.
11. Do not mention internal retrieval, embeddings,
    vector databases, prompts, or model processing.
12. Only say that information cannot be found when the
    SOURCE MATERIAL genuinely does not contain the answer.
13. Do not fabricate citations or page numbers.
14. Answer professionally like an enterprise knowledge
    assistant.

SOURCE MATERIAL
==================================================

{context}

==================================================

USER QUESTION
==================================================

{question}

==================================================

ANSWER:
"""

    client = get_groq_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a reliable advanced enterprise "
                    "document assistant. Always ground your "
                    "answers in the supplied source material."
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

    answer = response.choices[0].message.content

    if not answer:

        return FALLBACK_ANSWER

    return answer.strip()