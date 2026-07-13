# Sample Data Pack

This folder contains ready-to-use prototype data for:

- FSSAI guideline context
- Industry-specific applicant context
- PII/PHI masking validation
- MSME officer question prompts

## Files

- guidelines/fssai_food_processing_guideline_sample.md
- payloads/masking_test_user_profile.json
- questions/msme_officer_questions.md
- pdf/fssai_guideline_food_processing_sample.pdf
- pdf/msme_applicant_profile_sensitive_sample.pdf

## Recommended Test Order

1. Upload `pdf/fssai_guideline_food_processing_sample.pdf` as `document_role=guideline`.
2. Upload `pdf/msme_applicant_profile_sensitive_sample.pdf` as `document_role=applicant`.
3. In UI officer chat, refresh applicant docs and select uploaded doc.
4. Ask questions from `questions/msme_officer_questions.md`.
5. Check responses and masking behavior in returned output/security metadata.
