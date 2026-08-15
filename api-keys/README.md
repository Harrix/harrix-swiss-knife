# API keys

Local secret files for harrix-swiss-knife. **Not committed to Git** (see root `.gitignore`).

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [Files](#files)
- [Setup](#setup)
- [AI providers](#ai-providers)
- [Transfer to another machine](#transfer-to-another-machine)
- [Install zips and offline snapshots](#install-zips-and-offline-snapshots)

</details>

## Files

| File                     | Config key                                 | Purpose                                            |
| ------------------------ | ------------------------------------------ | -------------------------------------------------- |
| `pypi-token.txt`         | `pypi_token` in `config/config.json`       | PyPI token for publishing Python libraries         |
| `bothub-api-key.txt`     | `bothub_api_key` in `config/config.json`   | BotHub access token for AI features                |
| `openai-api-key.txt`     | `openai_api_key` in `config/config.json`   | OpenAI API key (chat + Whisper speech)             |
| `anthropic-api-key.txt`  | `anthropic_api_key` in `config/config.json`| Anthropic API key (Claude Messages)                |
| `gemini-api-key.txt`     | `gemini_api_key` in `config/config.json`   | Google Gemini API key                              |

AI keys are also read by the Android Gradle build (`android/app/build.gradle.kts`) for the **active** provider from `config.json` → `ai.provider` (override with env). See [`DEVELOPMENT.md`](../DEVELOPMENT.md#ai-api-keys-android).

For school/corporate Wi-Fi, set optional `ai.proxy` (or legacy `bothub.proxy`) in `config/config.json` (see [`DEVELOPMENT.md`](../DEVELOPMENT.md#bothub-food--finance-ai-on-restricted-networks)).

Paths in `config.json` use the `snippet:api-keys/...` prefix; `harrix_pylib` loads file contents at runtime.

## Setup

1. Copy `pypi-token.example.txt` to `pypi-token.txt` (or move an existing token here).
2. Replace the placeholder with your real token (one line, no quotes; PyPI tokens usually start with `pypi-`).
3. Do not commit `api-keys/*` except files listed in `.gitignore` exceptions.

Add new keys as separate `.txt` files and reference them from `config.json` with `snippet:api-keys/<filename>`.

## AI providers

Choose the backend in `config/config.json`:

```json
"ai": {
  "provider": "bothub",
  "speech_provider": "",
  "max_image_side": 1600,
  "proxy": ""
}
```

Supported `provider` values: `bothub`, `openai`, `anthropic`, `gemini`.

- `speech_provider` empty means the same as `provider`.
- Anthropic has no speech-to-text API: set `speech_provider` to `openai`, `gemini`, or `bothub` for voice features.
- Copy the matching `*-api-key.example.txt` → `*-api-key.txt` and paste the key (one line).

If `ai` is omitted, the app keeps the previous BotHub-only behavior.

## Transfer to another machine

Personal ZIP (gitignored): secrets from this folder plus exercise images from `{parent(sqlite_fitness)}/fitness_img`. Not part of the public install bundles.

Commands:

```text
# Source machine (config.json with real sqlite_fitness required)
.\install\pack-private-data.bat

# Copy install\private-data-harrix-swiss-knife.zip to the new machine

# Target machine: set sqlite_fitness in config.json first (or pass -FitnessImgDir)
.\install\install-private-data.bat
```

## Install zips and offline snapshots

| Artifact                                                                           | Includes `api-keys/`?                                                                                                       |
| ---------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `install/install-harrix-swiss-knife.zip`, `install-offline-harrix-swiss-knife.zip` | **No** — only `install/` scripts and `install/dependencies/` (not the repo tree).                                           |
| `install/dependencies/repos/harrix-swiss-knife.zip` (`git archive HEAD`)           | **No** — whole `api-keys/` is excluded via `.gitattributes` `export-ignore`; secret `*.txt` files are never tracked anyway. |
