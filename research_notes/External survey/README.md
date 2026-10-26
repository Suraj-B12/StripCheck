# External survey drop folder

Put the files returned by the external research model here, exactly as the model produced them, named `<theme_key>__<model>__<YYYY-MM-DD>.md` (the brief and the shared page show the exact name for each theme).

Brief: `docs/prompts/literature_survey_brief.md` (paste-ready parts in `docs/prompts/brief/`; shareable page https://claude.ai/artifact/HTTGaW8JLaf9PzV3grL6xk, private until shared).

Intake, after adding files:
```
python docs/prompts/check_external_survey.py
```
It writes `_intake/INTAKE_REPORT.md` (format issues per file), one `_intake/<file>.bib` per input, and `_intake/new_sources.json` (sources not already in our verified bibliography). New sources then go through the same citation verification as our own survey before anything reaches `paper/references.bib`.
