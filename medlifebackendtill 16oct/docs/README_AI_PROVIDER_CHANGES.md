# MedLife AI Provider Selection - Changed Files

This bundle contains only the changed files, preserving their paths relative to the backend root.

## Changes
- Set Ollama as the default AI provider and the local model default to `llama3.1:8b`.
- Added server-controlled model allowlists for Gemini, Claude, OpenAI, and Ollama.
- Expanded `GET /medlife/providers/` metadata with the default provider, configured provider models, and configuration flags. It does not expose API keys or claim that remote services are currently reachable.
- Added a `model` request field for provider-specific model selection; retained `local_model` as a backward-compatible field.
- Routed model selection through the service and provider adapters.
- Added tests for model discovery, allowlist validation, and missing cloud credentials.
- Cleaned `.env.example`: removed duplicate/conflicting AI provider declarations and documented optional keys and model allowlists.

## API usage
- Provider discovery: `GET /medlife/providers/`
- General prompt: `GET /medlife/prompt/?query=...&provider=local&model=llama3.1:8b`
- Member chat: `POST /medlife/chat/ask/` with JSON such as:
  `{"member_name":"member1","query":"Explain this reading","provider":"local","model":"llama3.1:8b"}`

Use a provider ID and model returned by the discovery endpoint. API keys remain server-side in `.env`.

## Validation
- Python source compilation passed.
- Django tests could not run in this environment because Django is not installed (`ModuleNotFoundError: No module named 'django'`). Run the included provider tests in the project's configured Python environment before merging.
