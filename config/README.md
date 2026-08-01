# Config

- `config.example.json` — committed template with placeholders (`<YOUR_…>`).
- `config.json` — local personal config (gitignored). Created automatically from the example on first run if missing.

## Setup on a new machine

1. Copy the example (or let the app create it):

   ```text
   copy config\config.example.json config\config.json
   ```

2. Edit `config.json`: replace `<YOUR_…>` placeholders with real paths.
3. Put API secrets under `api-keys/` (see `api-keys/README.md`); keep using `snippet:api-keys/…` keys in config.

Do not commit `config.json` — it contains machine-specific absolute paths.
