# Repository Guidelines

## Project Structure & Module Organization

- `app.py` is the Streamlit entry point; keep UI layout, session state, and high-level flow here.
- Shared logic lives in `utils/azure_agent.py` (Azure agent management) and `utils/file_handler.py` (downloads and display helpers).
- Configuration comes from `.env` (copied from `.env.example`); runtime artifacts are written to `downloads/` and should not be committed.

## Build, Test, and Development Commands

- Create and activate a virtual environment:
  ```bash
  python -m venv .venv
  source .venv/bin/activate
  ```
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
- Run the app locally:
  ```bash
  streamlit run app.py
  ```
- When tests are added, prefer `pytest` and run with `pytest` from the repo root.

## Coding Style & Naming Conventions

- Follow PEP 8 with 4-space indentation and descriptive names (`snake_case` for functions/variables, `PascalCase` for classes).
- Keep Streamlit UI code in `app.py`; move reusable logic into `utils/` modules.
- Use docstrings and type hints for new public functions and classes, especially in `utils/`.

## Testing Guidelines

- Place tests in a `tests/` directory mirroring the `utils/` structure (e.g., `tests/test_file_handler.py`).
- Name tests by behavior (e.g., `test_download_files_handles_errors`).
- Include tests for new logic that touches Azure APIs or file handling; mock external services and the filesystem where possible.

## Commit & Pull Request Guidelines

- Use clear, imperative commit messages (e.g., `Add chart download button`); optional type prefixes like `feat:`, `fix:`, `refactor:` are encouraged.
- Keep commits focused and small; separate formatting-only changes from functional ones.
- PRs should include: a concise summary, motivation or linked issue, testing steps/results, and screenshots for notable UI changes.

## Security & Configuration Tips

- Never commit secrets or real `.env` values; update `.env.example` when adding new required settings.
- Treat Azure endpoints, project IDs, and deployment names as sensitive; redact them from shared logs and screenshots.
- Prefer using `DefaultAzureCredential` as already configured; avoid introducing alternative ad-hoc auth flows.

