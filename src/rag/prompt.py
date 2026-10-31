from api.schemas import Source


SYSTEM_PROMPT = (
    "You answer questions using ONLY the numbered context passages provided.\n"
    "Rules:\n"
    "- End every sentence with the number of the passage it came from, e.g [1] or [2][3].\n"
    "- if the answer is not in the context, reply exactly: I dont know.\n"
    "- Do not use outside knowledge.\n"
    "- Never make assumptions"
)


def build_prompt(question: str, sources: list[Source]) -> str:
    context = "\n\n".join(
        f"[{i}] ({s.source}, p. {s.page + 1})\n{s.text}"
        for i, s in enumerate(sources, start=1)
    )

    return (
        f"Context:\n {context} \n\n"
        f"Question:\n {question} \n\n"
        "Answer with a citation like [1] after every sentence."
    )
