# Tech Setup

This file defines setup rules for the KinKeeper build.

## Workspace root

The Antigravity project root must be:

```text
/Users/shaliniguda213/Desktop/Kaggle BootCamp_SGP/KinKeeper
```

All playbook markdown files live directly in this folder unless a subfolder is specified.

## Required tools

Check these first:

```bash
python --version
uv --version
agents-cli --version
git --version
```

Python must be 3.11 or higher.

If `uv` is missing, tell the user to install it.

If `agents-cli` is missing, run:

```bash
uvx google-agents-cli setup
```

Then run:

```bash
agents-cli info
```

If ADK skills are missing, run:

```bash
agents-cli setup --skip-auth
```

## Environment file

Create `.env` only inside the generated project folder, not inside this playbook root unless needed for setup.

Use:

```text
GOOGLE_API_KEY=<paste_your_key_here>
GOOGLE_GENAI_USE_VERTEXAI=False
GEMINI_MODEL=gemini-2.5-flash
```

Tell the user to paste their own Gemini API key from Google AI Studio.

Never ask the user to paste the key into chat.

Never commit `.env`.

## Model rule

Use:

```text
gemini-2.5-flash
```

For tighter quota, allow:

```text
gemini-2.5-flash-lite
```

Never use retired `gemini-1.5-*` models.

## Scaffold rule

Use Agents CLI to scaffold the ADK project.

The final generated project folder should be named:

```text
kinkeeper
```

Use lowercase and hyphen-free or underscore-free Python package naming when needed.

Preferred project source package:

```text
kinkeeper_agent
```

If Agents CLI creates a different source folder, detect the actual folder containing `agent.py` and use that consistently.

Do not assume the source folder is named `app`.

## Required `.gitignore`

Ensure the generated project includes:

```gitignore
# Secrets
.env
*.env
.env.*

# Private user data
data/private/
private_exports/
real_exports/
*.zip
*.tar
*.gz

# Python
.venv/
__pycache__/
*.pyc
*.pyo
*.pyd
*.egg-info/
dist/
build/

# ADK local state
.adk/
*.db

# Caches
.pytest_cache/
.ruff_cache/

# OS
.DS_Store
Thumbs.db

# Terraform
.terraform/
terraform.tfstate
terraform.tfstate.backup
*.tfvars

# Artifacts that may include private traces
artifacts/private/
```

## Dependencies

Use pinned ranges where possible:

```toml
google-adk[gcp]>=2.0.0,<3.0.0
mcp>=1.0.0,<2.0.0
fastapi>=0.110,<1.0
uvicorn>=0.29,<1.0
python-dotenv>=1.0,<2.0
pydantic>=2.0,<3.0
pytest>=8.0,<9.0
```

## Makefile targets

Ensure the generated project includes:

```makefile
install
playground
run
test
eval
```

The `playground` target must use the real source directory containing `agent.py`.

## Quota protection

Do not run automated multi-turn LLM tests.

Do not repeatedly call the playground.

Start the local app and tell the user what manual test to run.
