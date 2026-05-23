**Project Overview**:
- Browser chat app that connects to a database, converts natural language questions into SQL, executes them, and returns a concise answer using an LLM-powered chain.

**Why this structure**:
- Modular, testable code separated into `config`, `db`, `chain`, and `api` so each piece can be unit-tested and showcased clearly.

**Files of interest**:
- `app.py`: starts the FastAPI chat app.
- `cli.py`: optional demo runner. Pass `--question` to run arbitrary queries.
- `src/nl_to_sql/config.py`: typed settings and `.env` support.
- `src/nl_to_sql/db.py`: database connection helper.
- `src/nl_to_sql/chain.py`: builds the NL-to-SQL-to-answer pipeline.
- `src/nl_to_sql/api.py`: FastAPI and WebSocket backend for the chat UI.
- `static/`: browser chat interface.
- `.env.example`: example environment variables.
- `requirements.txt`: project dependencies.

Getting started (local):
1. Create a virtual environment and install requirements:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill credentials. You can also enter database details in the browser.

3. Run the chat app:

```powershell
python app.py
```

Open `http://127.0.0.1:8765`.

4. Optional CLI demo:

```powershell
python cli.py --question "How many employees have salary > 10000?"
```

Security and production cautions:
- Use a read-only database role for query execution where possible.
- Avoid exposing this directly to the internet without authentication, rate limiting, and query safeguards.
- Review generated SQL before enabling write permissions. This app is intended for read-oriented analysis.

Next steps:
- Add tests around the WebSocket message contract and chain payload shape.
- Pin dependency versions and add CI for repeatable installs.
