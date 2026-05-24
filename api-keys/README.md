# API keys

Local secret files for harrix-swiss-knife. **Not committed to Git** (see root `.gitignore`).

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [Files](#files)
- [Setup](#setup)
- [Install zips and offline snapshots](#install-zips-and-offline-snapshots)

</details>

## Files

| File             | Config key                           | Purpose                                    |
| ---------------- | ------------------------------------ | ------------------------------------------ |
| `pypi-token.txt` | `pypi_token` in `config/config.json` | PyPI token for publishing Python libraries |

Paths in `config.json` use the `snippet:api-keys/...` prefix; `harrix_pylib` loads file contents at runtime.

## Setup

1. Copy `pypi-token.example.txt` to `pypi-token.txt` (or move an existing token here).
2. Replace the placeholder with your real token (one line, no quotes; PyPI tokens usually start with `pypi-`).
3. Do not commit `api-keys/*` except files listed in `.gitignore` exceptions.

Add new keys as separate `.txt` files and reference them from `config.json` with `snippet:api-keys/<filename>`.

## Install zips and offline snapshots

| Artifact                                                                           | Includes `api-keys/`?                                                                                                       |
| ---------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `install/install-harrix-swiss-knife.zip`, `install-offline-harrix-swiss-knife.zip` | **No** — only `install/` scripts and `install/dependencies/` (not the repo tree).                                           |
| `install/dependencies/repos/harrix-swiss-knife.zip` (`git archive HEAD`)           | **No** — whole `api-keys/` is excluded via `.gitattributes` `export-ignore`; secret `*.txt` files are never tracked anyway. |
