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

        @staticmethod
        def build_risk_assessment_prompt(industry: str, applicant_text: str, guideline_context: str) -> str:
                return f"""You are a banking credit advisory assistant for MSME pre-screening.

Industry detected: {industry}

Applicant details:
{applicant_text}

Guideline context:
{guideline_context}

Instructions:
1) Use the guideline context as the primary reference.
2) Evaluate risk factors and assign a score from 0 to 100 (higher means riskier).
3) Map the score to risk level: LOW (0-34), MEDIUM (35-64), HIGH (65-100).
4) Provide manual-review advisory points with concise rationale.
5) If context is insufficient, state gaps clearly.

Return ONLY valid JSON using this schema:
{{
    "industry": "string",
    "risk_score": 0,
    "risk_level": "LOW|MEDIUM|HIGH",
    "summary": "string",
    "key_risk_factors": ["string"],
    "advisory_notes": ["string"],
    "missing_information": ["string"]
}}"""
