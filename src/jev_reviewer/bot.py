from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from .config import Settings, get_settings
from .document import SUPPORTED, load_document
from .formatting import render_answers, render_integrity, split_message
from .models import Document
from .providers.jev import JevClient, JevError
from .providers.llm import LLMClient
from .review.engine import ReviewEngine

LOGGER = logging.getLogger(__name__)
DOC_KEY = "active_document"


def _authorized(update: Update, settings: Settings) -> bool:
    allowed = settings.allowed_user_ids
    if not allowed:
        return True
    return bool(update.effective_user and update.effective_user.id in allowed)


async def _guard(update: Update, settings: Settings) -> bool:
    if _authorized(update, settings):
        return True
    if update.effective_message:
        await update.effective_message.reply_text("This bot is private.")
    return False


def _document(context: ContextTypes.DEFAULT_TYPE) -> Document | None:
    return context.user_data.get(DOC_KEY)


async def _send(update: Update, text: str) -> None:
    if not update.effective_message:
        return
    for chunk in split_message(text):
        await update.effective_message.reply_text(chunk)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = get_settings()
    if not await _guard(update, settings):
        return
    await _send(update, HELP)


async def whoami(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user:
        await _send(update, f"Your Telegram user ID is {update.effective_user.id}")


async def receive_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = get_settings()
    if not await _guard(update, settings) or not update.message or not update.message.document:
        return
    doc = update.message.document
    suffix = Path(doc.file_name or "upload").suffix.lower()
    if suffix not in SUPPORTED:
        await _send(update, f"Unsupported type {suffix}. Send PDF, DOCX, TXT, or MD.")
        return
    tg_file = await context.bot.get_file(doc.file_id)
    tmpdir = Path(tempfile.mkdtemp(prefix="jev-reviewer-"))
    path = tmpdir / (doc.file_name or f"document{suffix}")
    await tg_file.download_to_drive(custom_path=path)
    try:
        parsed = load_document(path)
    except Exception as exc:
        LOGGER.exception("Document extraction failed")
        await _send(update, f"Could not read the document: {exc}")
        return
    context.user_data[DOC_KEY] = parsed
    await _send(
        update,
        f"Loaded {parsed.name}\nCharacters extracted: {len(parsed.text):,}\n\nUse /paper, /proposal, /integrity, /check <claim>, or /ask <question>.",
    )


async def _run_review(update: Update, context: ContextTypes.DEFAULT_TYPE, mode: str) -> None:
    settings = get_settings()
    if not await _guard(update, settings):
        return
    doc = _document(context)
    if not doc:
        await _send(update, "Send me a PDF, DOCX, TXT, or MD file first.")
        return
    jev = JevClient(settings.typesafe_api_key, settings.jev_endpoint, settings.jev_model)
    engine = ReviewEngine(jev, settings.jev_max_chars)
    await _send(update, f"Running {mode} review on {doc.name}...")
    try:
        if mode == "paper":
            result = await engine.paper(doc)
            text = render_answers("SCIENTIFIC PAPER REVIEW", result)
        elif mode == "proposal":
            result = await engine.proposal(doc)
            text = render_answers("RESEARCH PROPOSAL REVIEW", result)
        else:
            result, local = await engine.integrity(doc)
            text = render_integrity(result, local)
        await _send(update, text)
    except JevError as exc:
        await _send(update, f"JEV error: {exc}")


async def paper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _run_review(update, context, "paper")


async def proposal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _run_review(update, context, "proposal")


async def integrity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _run_review(update, context, "integrity")


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = get_settings()
    if not await _guard(update, settings):
        return
    doc = _document(context)
    claim = " ".join(context.args).strip()
    if not doc:
        await _send(update, "Send me a document first.")
        return
    if not claim:
        await _send(update, "Usage: /check <claim you want tested against the document>")
        return
    engine = ReviewEngine(JevClient(settings.typesafe_api_key, settings.jev_endpoint, settings.jev_model), settings.jev_max_chars)
    try:
        result = await engine.check_claim(doc, claim)
        await _send(update, render_answers(f"CLAIM CHECK\n{claim}", result))
    except JevError as exc:
        await _send(update, f"JEV error: {exc}")


async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = get_settings()
    if not await _guard(update, settings):
        return
    doc = _document(context)
    question = " ".join(context.args).strip()
    if not doc:
        await _send(update, "Send me a document first.")
        return
    if not question:
        await _send(update, "Usage: /ask <question about the document>")
        return
    if not settings.llm_enabled:
        await _send(update, "Narrative Q&A is optional and not configured. Set LLM_API_KEY and LLM_MODEL in .env. JEV reviews still work without it.")
        return
    client = LLMClient(settings.llm_api_key, settings.llm_base_url, settings.llm_model)
    try:
        answer = await client.ask(doc.text[: settings.jev_max_chars], question)
        await _send(update, answer)
    except Exception as exc:
        LOGGER.exception("LLM request failed")
        await _send(update, f"Reasoning-model error: {exc}")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = get_settings()
    if not await _guard(update, settings):
        return
    doc = _document(context)
    lines = [f"JEV model: {settings.jev_model}", f"Narrative LLM configured: {'yes' if settings.llm_enabled else 'no'}"]
    lines.append(f"Active document: {doc.name} ({len(doc.text):,} characters)" if doc else "Active document: none")
    await _send(update, "\n".join(lines))


async def forget(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop(DOC_KEY, None)
    await _send(update, "Active document cleared from this bot session.")


HELP = """JEV Scientific Reviewer

1. Send a PDF, DOCX, TXT, or MD file.
2. Then use:
/paper - structured manuscript review
/proposal - structured proposal review
/integrity - AI-likeness/style + file provenance audit
/check <claim> - probability-based claim support check
/ask <question> - narrative explanation using an optional reasoning LLM
/status - configuration/document status
/whoami - show your Telegram user ID
/forget - clear the active document

The integrity audit does not claim to determine AI authorship. It reports writing-pattern and provenance signals separately."""


def main() -> None:
    settings = get_settings()
    logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO), format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    app = Application.builder().token(settings.telegram_bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("whoami", whoami))
    app.add_handler(CommandHandler("paper", paper))
    app.add_handler(CommandHandler("proposal", proposal))
    app.add_handler(CommandHandler("integrity", integrity))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("ask", ask))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("forget", forget))
    app.add_handler(MessageHandler(filters.Document.ALL, receive_document))
    LOGGER.info("Starting Telegram polling")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
