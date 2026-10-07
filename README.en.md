# Academic Paper Talk

[中文](README.md)

A Codex skill that turns a research paper into a clear academic presentation: the research question, central insight, complete method, key equations, experimental evidence, and useful follow-up questions.

![Reference preview](skills/artifact-template-academic-paper-talk/assets/preview.png)

## What you get

- An editable PPTX with a restrained white, navy, blue, and teal visual style.
- Complete speaker notes that can be read aloud, plus a matching Markdown script.
- A slide outline grounded in the paper's actual figures, equations, assumptions, and experiments.
- Explicit explanations of overall versus internal diagrams, training versus inference, and baseline information/resource budgets.

Chinese narration is the default; request another language when needed. Page count follows the paper and your time budget. The retained Channel Deduction deck supplies a visual reference, not scientific content for new papers.

## Install and use

Requires Python 3.10+. Download or clone this repository, then run:

```bash
python3 scripts/install.py
```

The skill installs into `${CODEX_HOME:-~/.codex}/skills`. Existing installations are preserved unless you pass `--force`; updates first create a backup beside the skills directory under `skill-backups/`.

Attach a full paper PDF in Codex and ask:

> Use $artifact-template-academic-paper-talk to create a 20-minute academic presentation. Explain the complete method and experimental evidence, and write full speaker notes in English.

Generation uses the currently installed Codex Presentations capability and its runtime. This repository does not bundle an AI service or standalone offline slide generator. The audit utility uses only Python's standard library.

## Validate

```bash
python3 scripts/check_package.py
python3 -m unittest discover -s tests -v
python3 skills/artifact-template-academic-paper-talk/scripts/audit_pptx.py report.pptx --script script.md
```

Structural checks cover missing notes, narration mismatches, presenter labels, and native object counts. They do not replace scientific source checking or visual inspection of every final slide.

See [usage](docs/usage.md), [quality criteria](docs/quality.md), and [contributing](CONTRIBUTING.md). Original code and documentation are MIT licensed; retained scholarly reference assets are excluded. See [third-party notices](THIRD_PARTY_NOTICES.md).
