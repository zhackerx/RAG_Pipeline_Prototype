# Internal Guideline Repository

Place internal bank policy files here. Files are auto-indexed on app startup when AUTO_INDEX_GUIDELINES=true.

Current prototype scope:

- Industry: food_processing
- Standard: fssai

Folder convention:

- guidelines/food_processing/ -> FSSAI guideline files

Supported files:

- PDF: .pdf
- Markdown: .md, .markdown
- Excel: .xlsx, .xlsm, .xltx, .xltm

Example layout:

- guidelines/food_processing/fssai_guideline.pdf
- guidelines/food_processing/fssai_score_matrix.xlsx
- guidelines/food_processing/fssai_controls.md

Industry is inferred from the first folder under guidelines.
