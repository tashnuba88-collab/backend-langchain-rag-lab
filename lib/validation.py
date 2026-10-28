"""Request validation helpers for POST /api/ask."""

from lib.config import MAX_QUESTION_LENGTH, MIN_QUESTION_LENGTH


def _error(code, message):
    return {"error": code, "message": message}


def validate_question_payload(payload):
    """Validate the JSON body for POST /api/ask.

    Return:
        (question, None) when valid
        (None, error_dict) when invalid
    """

    if not isinstance(payload, dict):
        return None, _error("invalid_request", "Request body must be a JSON object.")

    if "question" not in payload:
        return None, _error("missing_question", "The request must include a question field.")

    question = payload["question"]

    if not isinstance(question, str):
        return None, _error("invalid_question", "The question must be a string.")

    question = question.strip()

    if not question:
        return None, _error("empty_question", "The question must not be blank.")

    if len(question) < MIN_QUESTION_LENGTH:
        return None, _error(
            "short_question",
            f"The question must be at least {MIN_QUESTION_LENGTH} characters long.",
        )

    if len(question) > MAX_QUESTION_LENGTH:
        return None, _error(
            "long_question",
            f"The question must be at most {MAX_QUESTION_LENGTH} characters long.",
        )

    return question, None