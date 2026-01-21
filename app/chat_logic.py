from app.rag_pipeline import rag_tool

QUESTION_KEYWORDS = [
    "what", "when", "where", "who", "which", "how",
    "timing", "time", "doctor", "clinic", "services",
    "documents", "available"
]


def is_question(text):
    text = text.lower()
    return any(word in text for word in QUESTION_KEYWORDS)


def handle_user_message(user_input):
    # Only attempt RAG for likely questions
    if not is_question(user_input):
        return None

    rag_response = rag_tool(user_input)

    if rag_response:
        return (
            "📚 **Answer from uploaded documents:**\n\n"
            f"{rag_response}"
        )

    return None
