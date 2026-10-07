# Academic Paper Talk

[![Validate skill](https://github.com/ooooooomygosh/academic-paper-talk/actions/workflows/validate.yml/badge.svg)](https://github.com/ooooooomygosh/academic-paper-talk/actions/workflows/validate.yml)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](scripts/install.py)
[![Code and docs MIT](https://img.shields.io/badge/code%20%26%20docs-MIT-green)](LICENSE)

**Turn a paper into a clear academic presentation: the problem, the mechanism, and the evidence.**

[中文](README.md) · [Quick start](#quick-start) · [Gallery](#gallery) · [FAQ](docs/faq.md) · [Contributing](CONTRIBUTING.md)

An installable Codex skill for paper reading and presentation production. It produces an editable PowerPoint deck, full speaker notes, a matching narration script, and a slide outline. Chinese narration is the default; ask for English or another language when needed.

![Reference title slide](skills/artifact-template-academic-paper-talk/assets/preview.png)

White backgrounds, navy text, restrained blue/teal accents, readable research figures, and native diagrams and tables. The retained Channel Deduction deck is a visual reference; each new talk is grounded in its own paper.

## Quick start

You need a Codex environment with **Presentations** capability and Python 3.10+.

```bash
git clone https://github.com/ooooooomygosh/academic-paper-talk.git
cd academic-paper-talk
python3 scripts/install.py
```

Attach a full paper PDF in Codex and ask:

> Use $artifact-template-academic-paper-talk to create a 20-minute academic presentation in English. Explain the central insight, the complete method, key equations, and experimental evidence. Write full speaker notes that I can read aloud.

You can specify a slide count, audience, existing deck, or advisor's template. With only a DOI or URL, the agent first needs access to the full paper. If the skill is not discovered in your current session, start a new session.

Installation defaults to `${CODEX_HOME:-~/.codex}/skills/artifact-template-academic-paper-talk`. Use `--skills-dir /path/to/skills` for another location. To update after pulling repository changes:

```bash
python3 scripts/install.py --force
```

Existing installations are preserved unless you use `--force`; forced updates first back up the old skill under `skill-backups/` beside the skills directory. You can also copy the complete skill folder manually.

Generation uses Codex's installed presentation runtime. The Python installer and audit tools use the standard library and require no API key; generation requires the host's model and presentation capabilities. Local checks were run on macOS; CI covers Ubuntu with Python 3.10 and 3.12. Windows compatibility has not been verified.

## How it works

Full paper → source and evidence review → slide outline → editable slides and narration → render and inspect every final slide.

| Stage | What the talk explains |
| --- | --- |
| Problem and insight | The concrete limitation and the observation that motivates the method |
| Contribution | What the closest prior approaches already do and what changes here |
| Method | Inputs, outputs, interfaces, timing, side information, and feedback |
| Equations and execution | Variables, assumptions, and one sample through the algorithm |
| Experiments | Baseline information and resource budgets, metrics, results, and scope |
| Research follow-up | A real remaining bottleneck and a small testable next experiment |

Speaker notes contain continuous narration. References belong in slide footers or an appendix. Slide count follows the paper, audience, and time budget.

## Gallery

| Overall flow | Module explanation |
| --- | --- |
| ![Overall flow](skills/artifact-template-academic-paper-talk/assets/examples/overall-flow.png) | ![Module explanation](skills/artifact-template-academic-paper-talk/assets/examples/module-detail.png) |

| Baseline protocol | Experimental interpretation |
| --- | --- |
| ![Baseline protocol](skills/artifact-template-academic-paper-talk/assets/examples/baseline-protocol.png) | ![Experimental interpretation](skills/artifact-template-academic-paper-talk/assets/examples/experiment-explanation.png) |

## Validate

```bash
python3 scripts/check_package.py
python3 -m unittest discover -s tests -v
python3 skills/artifact-template-academic-paper-talk/scripts/audit_pptx.py report.pptx --script script.md --out audit.json
```

The audit checks missing notes, script mismatches, presenter labels, and native object counts. Source review and visual inspection of every final slide remain required. For `--script`, use one Markdown level-two heading per slide, followed only by its narration.

## Documentation and contributions

Detailed guides are currently in Chinese:

- [Usage and script format](docs/usage.md)
- [Scientific and visual quality criteria](docs/quality.md)
- [Troubleshooting](docs/faq.md)
- [Contributing](CONTRIBUTING.md), [roadmap](docs/roadmap.md), and [changelog](CHANGELOG.md)

The self-contained skill is in `skills/artifact-template-academic-paper-talk/`, with instructions, assets, reference guides, and the audit utility. Repository-level `scripts/` contains installation and package checks; `tests/` contains regression tests.

Report reproducible issues through [GitHub Issues](https://github.com/ooooooomygosh/academic-paper-talk/issues). Contributions should include a source, expected behavior, and relevant validation.

## Credits and license

The workflow grew from repeated research-talk practice; see [provenance](skills/artifact-template-academic-paper-talk/references/provenance.md). Repository presentation takes inspiration from the installation clarity of [anthropics/skills](https://github.com/anthropics/skills), workflow navigation of [obra/superpowers](https://github.com/obra/superpowers), and quick-start organization of [Typer](https://github.com/fastapi/typer).

Original code and documentation use the [MIT License](LICENSE). Reference decks and images contain third-party scholarly material and are excluded from that grant; see [third-party notices](THIRD_PARTY_NOTICES.md).
