# MedLife AI provider selection

The frontend chooses a provider per request. API credentials and provider URLs are configured only on the Django backend and must never be sent to Vite/browser code.

## Discover configured choices

`GET /medlife/providers/`

Example response (only providers configured on the server are listed):

```json
{
  "providers": [
    {"id": "gemini", "label": "Google Gemini"},
    {"id": "claude", "label": "Anthropic Claude"},
    {"id": "openai", "label": "ChatGPT (OpenAI)"},
    {"id": "local", "label": "Local model (Ollama)", "models": ["llama3.1:8b"]}
  ]
}
```

The exact list depends on server configuration. It contains no API keys. The frontend should render provider choices from this response rather than hard-coding unavailable vendors.

## Send the selected provider

For the authenticated member chat endpoint, send the selected provider in the JSON body:

```json
{
  "member_name": "member1",
  "query": "Can you explain this blood pressure reading?",
  "provider": "claude"
}
```

For a local model, use the `local` provider and a model name listed in the `models` array:

```json
{
  "member_name": "member1",
  "query": "Can you explain this reading?",
  "provider": "local",
  "local_model": "llama3.1:8b"
}
```

The legacy general endpoint accepts `provider` and `local_model` as query parameters:
`GET /medlife/prompt/?query=...&provider=gemini`.

Supported provider IDs are `gemini`, `claude`, `openai`, and `local`. `mock` is for development/test fallback and is not intended as a production AI choice. Each request must include the user's current selection; the backend does not silently change a user's selection.

## Backend environment

- `GEMINI_API_KEY`, optional `GEMINI_MODEL` (default `gemini-2.0-flash`)
- `ANTHROPIC_API_KEY` or `CLAUDE_API_KEY`, optional `CLAUDE_MODEL`
- `OPENAI_API_KEY` or legacy `AI_API_KEY`, optional `OPENAI_MODEL`
- `OLLAMA_BASE_URL`, and comma-separated `OLLAMA_MODELS` (e.g. `llama3.1:8b,qwen2.5:7b`)
- `AI_TIMEOUT_SECONDS`, `AI_RATE_LIMIT_PER_MINUTE`

Install/pull each Ollama model on the host running Ollama. Listing a model in `OLLAMA_MODELS` only makes it selectable; it does not install the model or guarantee the Ollama service is online.

## Safety and privacy

All provider keys remain server-side. The selected family member's profile context is passed only after the authenticated account/member ownership check. Hosted providers receive the user's question and the selected member profile context; use this only with appropriate consent and privacy disclosures. AI responses are general health information, not a diagnosis or prescription.
