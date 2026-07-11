from typing import Any


class PromptBuilder:
    @staticmethod
    def build_prompt(context: str, question: str) -> str:
        return f"""==================================================

CONTEXT

{context}

==================================================

USER QUESTION

{question}

==================================================

INSTRUCTIONS

Answer only from context.

If answer not available say:

\"The uploaded documents do not contain sufficient information.\"

Provide:

### Answer

### Key Points

### Sources

==================================================
"""
