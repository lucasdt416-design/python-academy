# Handoffs

One handoff per completed step, for the maintainer and for a chat assistant (ChatGPT or Claude chat) that has no repository access. Each follows the handoff template in `build.md` section 14. Upload the PDF together with `build.md` at the start of a chat session.

File names: `YYYY-MM-DD-NN-<short-step-name>.md`, with a matching `.pdf` beside it.

Make or refresh a PDF from the repository root:

```sh
uv run --no-project --with markdown python docs/handoffs/make_pdf.py docs/handoffs/<file>.md
```

This uses the frontend's Playwright Chromium (`cd frontend && npm ci && npx playwright install chromium`). Everything runs locally and is free.

The Markdown file is the source; edit it, then regenerate the PDF. A handoff summarizes evidence; the pull request diff and CI results remain the source of truth.
