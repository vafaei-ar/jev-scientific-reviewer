# JEV Scientific Reviewer

A Telegram-first assistant for evaluating scientific papers and research proposals with **JEV structured decisions**, plus optional narrative Q&A through an OpenAI-compatible reasoning model.

The design intentionally separates three things:

1. **Scientific judgment**: JEV evaluates narrow rubric questions and returns probability distributions/confidence.
2. **Understanding/explanation**: an optional reasoning LLM handles `/ask` questions because JEV is a decision model, not a prose generator.
3. **Writing integrity**: JEV evaluates formulaic-writing patterns while deterministic code inspects textual signals and document provenance. It does **not** claim to prove AI authorship.

## Features

- Upload `.pdf`, `.docx`, `.txt`, or `.md` directly in Telegram.
- `/paper`: manuscript rubric covering research question, design alignment, methods, statistics, evidence/conclusion alignment, novelty, and limitations.
- `/proposal`: proposal rubric covering significance, innovation, aim coherence, aim-method alignment, feasibility, analysis, risk mitigation, and expected impact.
- `/integrity`: AI-likeness/style audit plus basic DOCX/PDF provenance inspection.
- `/check <claim>`: evaluates whether a document supports a specific claim.
- `/ask <question>`: optional narrative document Q&A using an OpenAI-compatible API.
- `/whoami`: shows your Telegram numeric ID so you can restrict the bot to yourself.

## 1. Create a Telegram bot

Open Telegram and message `@BotFather`.

Use `/newbot`, choose a name, and copy the bot token.

## 2. Install

```bash
git clone https://github.com/vafaei-ar/jev-scientific-reviewer.git
cd jev-scientific-reviewer
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -e .
```

## 3. Configure

```bash
cp .env.example .env
```

Edit `.env`:

```dotenv
TELEGRAM_BOT_TOKEN=...
TYPESAFE_API_KEY=...
JEV_MODEL=jev-latest
```

Start once, send `/whoami`, then optionally restrict access:

```dotenv
TELEGRAM_ALLOWED_USER_IDS=123456789
```

### Optional narrative reasoning model

JEV is ideal for structured evaluation but does not generate free-form explanations. To use `/ask`, configure any OpenAI-compatible endpoint:

```dotenv
LLM_API_KEY=...
LLM_MODEL=...
LLM_BASE_URL=https://api.openai.com/v1
```

Leave these blank if you only want JEV evaluation.

## 4. Run

```bash
jev-reviewer
```

The bot uses Telegram long polling, so no public web server or webhook is needed. Your laptop must remain running while you use the bot.

## Telegram workflow

1. Send a manuscript or proposal file to your bot.
2. The bot sets it as the active document for your Telegram user session.
3. Run `/paper`, `/proposal`, or `/integrity`.
4. Use `/check The intervention reduced 30-day readmission.` to interrogate a specific claim.
5. If you configured a reasoning model, use `/ask Why is Aim 2 dependent on Aim 1?`.

## JEV integration

The client uses the current documented System One endpoint:

```text
POST https://api.typesafe.ai/v1/systemone
Authorization: Bearer <key>
```

Requests use `jev-latest` by default and send a shared `state` plus independent `choice` questions. In V1, ordinal scores are represented as explicit 1-5 choices. This keeps the request schema simple and makes every probability distribution visible.

## Important interpretation rule

The `/integrity` feature reports **AI-like writing patterns**, clarity problems, and file-provenance indicators. These findings are not equivalent to proof of AI authorship. A programmatic-generation marker such as a document library or converter is also not proof that an AI model authored the text.

## Current limitations

- V1 extracts text from text-based PDFs. It does not OCR scanned PDFs.
- The default JEV text cap is 90,000 characters to stay comfortably within context limits. The response reports whether input was truncated.
- Tables are flattened to text in DOCX extraction.
- Narrative `/ask` requires a separate reasoning-model API.
- Rubrics are initial scientific-review rubrics and should be validated on real reviewer-labeled examples before treating numeric outputs as calibrated scientific quality scores.

## Tests

```bash
pip install -e '.[dev]'
pytest -q
```

## Security

Do not commit `.env`. API keys and the Telegram token belong only in local environment configuration. If a credential is ever committed, revoke and rotate it.

## Planned V2

- Section-aware review with exact paragraph/page evidence.
- NIH-style criterion-specific proposal profiles.
- User-defined rubrics in YAML.
- JEV-vs-reasoning-model disagreement analysis.
- Baseline author-style continuity using user-provided prior writing.
- DOCX comments/track-change export for actionable writing revisions.
- Persistent local SQLite review history.
