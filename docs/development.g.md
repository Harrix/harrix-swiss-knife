---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# ⚙️ Development

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [💻 CLI commands](#-cli-commands)
  - [BotHub (Food / Finance AI) on restricted networks](#bothub-food--finance-ai-on-restricted-networks)
- [📦 Building Windows installer EXEs](#-building-windows-installer-exes)
  - [Before you start](#before-you-start)
  - [Steps (checkbox dialog / CLI flags)](#steps-checkbox-dialog--cli-flags)
- [VS Code extension: Harrix Notes Explorer (HSK)](#vs-code-extension-harrix-notes-explorer-hsk)
  - [Format and check (Biome)](#format-and-check-biome)
  - [Install (local, copy folder)](#install-local-copy-folder)
  - [Install via tray (Windows)](#install-via-tray-windows)
  - [Troubleshooting (extension missing in VS Code / Insiders)](#troubleshooting-extension-missing-in-vs-code--insiders)
  - [hsk boundary](#hsk-boundary)
  - [Usage](#usage)
  - [Customization](#customization)
- [Android app (Harrix Swiss Knife)](#android-app-harrix-swiss-knife)
  - [Requirements](#requirements)
  - [AI API keys (Android)](#ai-api-keys-android)
  - [Optional SDK setup](#optional-sdk-setup)
  - [Build APK](#build-apk)
  - [Workflow](#workflow)
  - [Phone setup (Samsung Galaxy S24 Ultra)](#phone-setup-samsung-galaxy-s24-ultra)
- [➕ Add a new action](#-add-a-new-action)
  - [Example action with CLI command](#example-action-with-cli-command)
- [📁 Add file to a resource file](#-add-file-to-a-resource-file)
- [📝 Add a new Markdown template (for 📝 Add Markdown from template)](#-add-a-new-markdown-template-for--add-markdown-from-template)
  - [🚀 Quick start](#-quick-start)
  - [📋 Supported Field Types](#-supported-field-types)

</details>

## 💻 CLI commands

CLI commands after installation:

- `.venv\Scripts\Activate.ps1` — activate virtual environment
- `ruff check --select I --fix` — sort imports.
- `winget upgrade OpenJS.NodeJS`: upgrade `Node.js` (tray action **Update `Node.js`**).
- `pyside6-designer` — Qt Widgets Designer.
- Convert `.ui` to PY (also rewrites UTF-16 emoji surrogates from `pyside6-uic`, which crash `QCoreApplication.translate` on Python 3):
  - `python -c "from harrix_swiss_knife.apps.common.uic_compile import compile_app_ui; compile_app_ui('finance')"`
  - `python -c "from harrix_swiss_knife.apps.common.uic_compile import compile_app_ui; compile_app_ui('fitness')"`
  - `python -c "from harrix_swiss_knife.apps.common.uic_compile import compile_app_ui; compile_app_ui('food')"`
  - `python -c "from harrix_swiss_knife.apps.common.uic_compile import compile_app_ui; compile_app_ui('habits')"`
- `ruff check --fix` — lint and fix the project's Python files.
- `ruff check` — lint the project's Python files.
- `ruff format` — format the project's Python files.
- `ty check` — check Python types in the project's Python files.
- `uv python install 3.13` + `uv python pin 3.13` + `uv sync` — switch to a different Python version.
- `uv python upgrade` — upgrade Python to the latest patch release.
- `uv self update` — update uv itself.
- `uv sync --upgrade` — update all project libraries (sometimes you need to call twice).
- `vermin src` — determine the minimum Python version using [vermin](https://github.com/netromdk/vermin). However, if the version is below 3.10, we stick with 3.10 because Python 3.10 annotations are used.

### BotHub (Food / Finance AI) on restricted networks

BotHub HTTPS uses `certifi` and optional `SSL_CERT_FILE` (corporate root CA). Proxy resolution order: `ai.proxy` (or legacy `bothub.proxy`) in `config/config.json` (empty = auto), Qt system proxy (PAC/WPAD on Windows), `HTTPS_PROXY` / `HTTP_PROXY`, then Windows/urllib proxy settings. Example: `"ai": { "proxy": "http://proxy.school.local:3128", ... }`.

Choose the AI backend with `"ai": { "provider": "bothub" }` (`openai`, `anthropic`, `gemini`). Keys live in `api-keys/` — see `api-keys/README.md`.

## 📦 Building Windows installer EXEs

The **builder** that fills `install\dependencies\` and packs the two distributable EXEs is Python (tray **Dev** → **Build installer EXEs**, or `hsk dev build-install-zips`). Target PCs need **no Python**. Each EXE is a frozen PySide6 wizard with an appended zip payload (`HSK1` trailer). After install, the app still runs via repos + `uv` + `pythonw`.

### Before you start

1. From the tray the pipeline logs in the same place as other actions and opens the result window when it finishes. **uv cache** installs a throwaway CPython and project venvs under `%TEMP%`, so the live `.venv` can stay locked.
2. Ensure sibling repos exist next to this checkout when you snapshot sources or warm the uv cache: `harrix-pylib`, `harrix-pyssg` (same parent folder as `harrix-swiss-knife`).
3. Install **PyInstaller** with the Windows dev group: `uv sync --group dev` (first stub freeze is slow; later packs reuse `install\.installer-stub\`).
4. **Optional GitHub token** for media binaries and installer downloads: copy `api-keys/github-token.example.txt` → `api-keys/github-token.txt` and paste a read-only PAT. Raises GitHub REST API limits from 60/hour per IP to 5000/hour per account (helps avoid HTTP 403 on shared networks). Env `GITHUB_TOKEN` also works. Form fields: [`api-keys/README.md`](https://github.com/Harrix/harrix-swiss-knife/blob/main/api-keys/README.md#fine-grained-token-preferred).

### Steps (checkbox dialog / CLI flags)

| Step       | Tray checkbox / CLI                                     | Purpose                                                                                         |
| ---------- | ------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Wipe       | Wipe `install/dependencies` first (`--no-wipe` to skip) | Delete `install\dependencies\` so downloads rebuild from scratch.                               |
| Binaries   | Media binaries (`--skip-binaries`)                      | ffmpeg / avifenc / avifdec → `install\dependencies\`.                                           |
| Installers | Installers (`--skip-installers`)                        | Git, uv, VS Code installers → `install\dependencies\`.                                          |
| Repos      | Repo snapshots (`--skip-repos`)                         | `git archive` → `install\dependencies\repos\`.                                                  |
| uv cache   | uv cache (`--skip-uv-cache`)                            | Warm `uv-python-cache\` and `uv-cache\` (isolated Python/venv; safe while the tray is running). |
| EXEs       | Build installer EXEs (`--no-exes`)                      | Writes `harrix-swiss-knife-online.exe` and `harrix-swiss-knife-offline.exe`.                    |
| Open       | Open `install/` (`--no-open`)                           | Open Explorer on `install\` when finished.                                                      |
| Logs       | Clean `*.log` (`--clean-logs`)                          | Optional top-level logs under `install\` and `install\dependencies\`.                           |

All steps except log cleanup are on by default. Example partial rebuild (reuse dependencies, only re-pack EXEs):

```text
hsk dev build-install-zips --no-wipe --skip-binaries --skip-installers --skip-repos --skip-uv-cache
```

After packing, copy the two EXEs from `install\` for distribution (not an `install\` folder zip).

- **Online EXE** — wizard installs tools as needed, clones repos from GitHub, `uv sync`.
- **Offline EXE** — same wizard; extracts bundled `repos\` + uv caches; prefers bundled installers/binaries.

Local unpackaged test (no freeze): `python -m harrix_swiss_knife.installer --online` (or `--offline`) with `install\dependencies\` already populated.

Personal private-data transfer is one tray action **Dev** → **Transfer private data** (choose Export or Import, then which parts), or CLI `hsk dev private-data export` / `hsk dev private-data import`. Parts are API keys and/or exercise catalog plus `fitness_img` (`{English name}.avif`) from `sqlite_fitness` (not `process`/`weight` workouts). Import upserts the catalog by English name and overlays missing/updated images next to existing files without wiping local-only rows, extra images, or workout history. Output defaults to `install\private-data-harrix-swiss-knife.zip` (gitignored). It is **not** part of the public online/offline installer EXE pipeline above. See `api-keys/README.md` (section Transfer to another machine).

## VS Code extension: Harrix Notes Explorer (HSK)

Local VS Code extension is bundled in this repo:

- Folder: `vscode/harrix-notes-explorer-hsk/`
- Entry point: `vscode/harrix-notes-explorer-hsk/extension.js`
- Manifest: `vscode/harrix-notes-explorer-hsk/package.json`

### Format and check (Biome)

Requires Node.js and npm on PATH. From the repo root:

```text
hsk vscode format
hsk vscode check
```

Equivalent from `vscode/harrix-notes-explorer-hsk/`:

```text
npm install
npm run format
npm run check
```

`node_modules` is gitignored and is not copied into editor extension folders on install.

### Install (local, copy folder)

Current VS Code / Insiders / Cursor track unpacked extensions in **`extensions.json`** next to the extension folders (not only by scanning directories). Copying only the `harrix-notes-explorer-hsk` tree can leave the UI empty until that file lists **`local.harrix-notes-explorer-hsk`**.

The tray action (**Dev** → **Install or update Harrix Notes Explorer (HSK) extension**) copies the tree **and** upserts that ID into each target **`extensions.json`**. The GUI installer does **not** install the extension into editors. If you copy by hand with `Copy-Item` only, either merge the same entry yourself or use **Developer: Install Extension from Location** once (see troubleshooting).

From the repo root in PowerShell: remove any existing `harrix-notes-explorer-hsk` folder under that editor’s `extensions` directory, then copy the bundled extension tree (ordinary directory; no symlinks).

VS Code Insiders:

```powershell
$src = (Resolve-Path ".\vscode\harrix-notes-explorer-hsk").Path
$dst = "$env:USERPROFILE\.vscode-insiders\extensions\harrix-notes-explorer-hsk"
if (Test-Path -LiteralPath $dst) { Remove-Item -LiteralPath $dst -Force -Recurse }
Copy-Item -LiteralPath $src -Destination $dst -Recurse
```

VS Code Stable:

```powershell
$src = (Resolve-Path ".\vscode\harrix-notes-explorer-hsk").Path
$dst = "$env:USERPROFILE\.vscode\extensions\harrix-notes-explorer-hsk"
if (Test-Path -LiteralPath $dst) { Remove-Item -LiteralPath $dst -Force -Recurse }
Copy-Item -LiteralPath $src -Destination $dst -Recurse
```

Cursor:

```powershell
$src = (Resolve-Path ".\vscode\harrix-notes-explorer-hsk").Path
$dst = "$env:USERPROFILE\.cursor\extensions\harrix-notes-explorer-hsk"
if (Test-Path -LiteralPath $dst) { Remove-Item -LiteralPath $dst -Force -Recurse }
Copy-Item -LiteralPath $src -Destination $dst -Recurse
```

### Install via tray (Windows)

From the tray app: **Dev** → **Update/Install Harrix Notes Explorer extensions for VSCode**. When **`path_harrix_notes_explorer`** is set, the action first rebuilds the public extension into that Git repo (everything except `.git/` is replaced), then opens a checkbox dialog for VS Code-family editors. It **copies** `vscode/harrix-notes-explorer-hsk` into `harrix-notes-explorer-hsk` under each selected editor’s extensions folder and **updates** **`extensions.json`**. Optionally installs public **`harrix-notes-explorer`** from the synced repo into the same editors. No UAC is required for a normal user profile.

Restart the editor or run **Developer: Reload Window** after installing.

### Troubleshooting (extension missing in VS Code / Insiders)

1. **Confirm `extensions.json` lists the extension**

Open `%USERPROFILE%\.vscode-insiders\extensions\extensions.json` (or `.vscode\extensions` / `.cursor\extensions` for the editor you use) and search for **`local.harrix-notes-explorer-hsk`**. If the folder exists but this ID is missing, the editor may not show the extension until you register it (tray action, or **Developer: Install Extension from Location**). 2. **Uninstalled earlier via the Extensions UI (`.obsolete`)**

Uninstalling in the editor writes `local.harrix-notes-explorer-hsk-0.0.1` (publisher.name-version) into `%USERPROFILE%\…\extensions\.obsolete`. While that key is `true`, copying the folder and updating **`extensions.json`** is not enough — the extension stays hidden. The tray install action clears matching keys; or edit/remove them manually, then reload. 3. **Confirm the editor sees the install**

Run `code-insiders --list-extensions` (or `code --list-extensions` / `cursor --list-extensions`) and check for **`local.harrix-notes-explorer-hsk`**. 4. **Custom extensions directory**

Open `%USERPROFILE%\.vscode-insiders\argv.json` (or the matching `argv.json` for stable VS Code / Cursor) and check for **`--extensions-dir`**. If set, the extension folder and **`extensions.json`** live under that directory instead of the default `%USERPROFILE%\.vscode-insiders\extensions`. 5. **Copy failed or old files remain**

Close the corresponding editor (file locks), delete `%USERPROFILE%\…\extensions\harrix-notes-explorer-hsk` if needed, then run the tray action or `Copy-Item` again. 6. **Manual copy without tray or script**

Command Palette → **Developer: Install Extension from Location** → select the repo folder `vscode\harrix-notes-explorer-hsk` (or the copied `harrix-notes-explorer-hsk` folder). Then **Developer: Reload Window**. 7. **Logs**

**Developer: Show Logs…** → **Window** or **Extension Host** for manifest or path errors.

### hsk boundary

Commands that call `hsk` live in [`vscode/harrix-notes-explorer-hsk/harrix-cli.js`](https://github.com/Harrix/harrix-swiss-knife/blob/main/vscode/harrix-notes-explorer-hsk/harrix-cli.js). The **HSK** extension keeps this layer; the **public** extension does not.

The public build is **`OnSyncHarrixNotesExplorer`** / `hsk vscode sync-notes-explorer` (also run automatically by **Update/Install Harrix Notes Explorer extensions** and `hsk dev install-harrix-notes-explorer-hsk <editor>` when **`path_harrix_notes_explorer`** is configured):

- Reads **`path_harrix_notes_explorer`** and **`harrix_notes_explorer_publisher`** from `config/config.json` (defaults: `D:/GitHub/harrix-notes-explorer`, `harrix`).
- Builds from [`vscode/harrix-notes-explorer-hsk`](https://github.com/Harrix/harrix-swiss-knife/tree/main/vscode/harrix-notes-explorer-hsk): renames `harrixNotesExplorerHsk.*` → `harrixNotesExplorer.*`, strips CLI files and manifest entries (see [`HARRIX_CLI.md`](https://github.com/Harrix/harrix-swiss-knife/blob/main/vscode/harrix-notes-explorer-hsk/HARRIX_CLI.md)).
- **Deletes everything in the target repo except `.git/`**, then copies the build to the repo root (`package.json` at top level).
- Refuses to sync into the harrix-swiss-knife project root.
- Install CLI: add **`--with-public`** to also install `harrix-notes-explorer` from that repo into the editor profile (e.g. `dev install-harrix-notes-explorer-hsk insiders --with-public`).

Manual checklist (if not using the action): [`HARRIX_CLI.md`](https://github.com/Harrix/harrix-swiss-knife/blob/main/vscode/harrix-notes-explorer-hsk/HARRIX_CLI.md) and [`package.harrix-cli.contributes.json`](https://github.com/Harrix/harrix-swiss-knife/blob/main/vscode/harrix-notes-explorer-hsk/package.harrix-cli.contributes.json). Git discard, local add file/folder, and merged-note open stay in `extension.js`.

### Usage

- Open your notes folder as a workspace in VS Code.
- In **Explorer**, open the **Harrix Notes (HSK)** view.

Commands:

- **Refresh Harrix Notes (HSK):** `harrixNotesExplorerHsk.refresh`
- **Reveal in File Explorer:** `harrixNotesExplorerHsk.revealInOS`

### Customization

**Note labels in the tree** (`harrixNotesExplorerHsk.showNoteTitleFromContent`, default `true`): each note row uses YAML frontmatter `title:` if present, otherwise the first `#` heading, otherwise the file name without `.md`. Set to `false` to always show only the file name (previous behavior). When the label differs from the file name, `harrixNotesExplorerHsk.showNoteFileNameBesideTitle` (default `true`) controls whether the file name is shown as a gray description beside the title; set to `false` to show only the title.
Fenced code blocks in the built-in **Markdown preview** (including notes opened via **Harrix Notes (HSK)** with `openNotesInPreview`) can show **Copy** buttons (see `harrixNotesExplorerHsk.previewCopy.*` settings: enable buttons, top/bottom visibility, hover zone, colors). Defaults: top always visible, bottom on hover in the last 80px, background `#fefefe`, border/icon `#7f7f7f`. Preview scripts run only in a **trusted** workspace; if buttons are missing, check workspace trust and **Markdown: Preview Security Settings**. After changing colors or visibility, the preview refreshes automatically.

Example:

```json
{
  "harrixNotesExplorerHsk.previewCopy.backgroundColor": "#fefefe",
  "harrixNotesExplorerHsk.previewCopy.borderColor": "#7f7f7f",
  "harrixNotesExplorerHsk.previewCopy.topAlwaysVisible": true
}
```

If you previously used `notesExplorer.*` settings or `notesExplorer.gFile` under `workbench.colorCustomizations`, rename them to `harrixNotesExplorerHsk.*` and `local.harrix-notes-explorer-hsk.gFileHsk` (the extension contributes color ID `gFileHsk` for optional `*.g.md` theming).

Example user settings:

```json
{
  "workbench.colorCustomizations": {
    "local.harrix-notes-explorer-hsk.gFileHsk": "#C586C0"
  }
}
```

## Android app (Harrix Swiss Knife)

Optional Android companion app in this monorepo (Gallery Cleaner, Video Cleaner, Photo Editor, Speech to Text with AI). Markdown notes browsing lives in the separate [harrix-notes-android](https://github.com/Harrix/harrix-notes-android) app (**Harrix Notes**). Not part of the Windows installer EXE pipeline.

- Folder: `android/`
- Package / applicationId: `dev.harrix.hsk` (reverse DNS for <https://harrix.dev>)
- UI: Kotlin + Jetpack Compose
- Utilities: **Gallery Cleaner**, **Video Cleaner**, **Photo Editor**, **Speech to Text with AI**
- App name (launcher): **Harrix Swiss Knife**
- Icon: from `src/harrix_swiss_knife/assets/logo.svg` / `app.ico`

### Requirements

- JDK 17 (`JAVA_HOME`)
- Android SDK with `ANDROID_HOME` (or `ANDROID_SDK_ROOT`)
- SDK packages: `platform-tools`, `platforms;android-35`, `build-tools;35.0.0`
- `android/local.properties` with `sdk.dir=...` (gitignored; created by **Android** → **Install JDK and Android SDK**)
- For AI utilities (Speech to Text with AI): API key at build time (see [AI API keys (Android)](#ai-api-keys-android))

User `Path` should include `%JAVA_HOME%\bin` and `%ANDROID_HOME%\platform-tools` (and optionally `%ANDROID_HOME%\emulator`, `%ANDROID_HOME%\cmdline-tools\latest\bin`).

### AI API keys (Android)

The APK embeds the **active** AI provider settings via `BuildConfig` at compile time. Secrets are **not** committed to Git.

Provider selection (same as desktop `config/config.json` → `ai.provider`):

1. Env `AI_PROVIDER`
2. `android/local.properties` → `ai.provider`
3. `config/config.json` → `ai.provider`
4. Default: `bothub`

Supported providers: `bothub`, `openai`, `anthropic`, `gemini`. Optional `ai.speech_provider` (empty = same as chat). Anthropic has no STT — set speech to `openai`, `gemini`, or `bothub`.

API key resolution for the active provider:

1. Provider env (`BOTHUB_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`)
2. `local.properties` → `bothub.api_key` / `openai.api_key` / …
3. `config/config.json` key (`bothub_api_key`, …) including `snippet:api-keys/…`
4. File under `api-keys/` (same as desktop)

Optional overrides: `AI_BASE_URL` / `ai.base_url`, `AI_MODEL` / `ai.model`, `AI_SPEECH_MODEL` / `ai.speech_model`.

Setup example (OpenAI):

1. In `config/config.json`: `"ai": { "provider": "openai" }`
2. Copy `api-keys/openai-api-key.example.txt` → `api-keys/openai-api-key.txt` and paste the key
3. Rebuild the APK

If the key is missing, the project still builds; Speech to Text / Medicine Search show an in-app error until a key is provided. The key ends up inside the APK binary (decompilation can extract it) — acceptable for personal sideload, not for distributing a secret publicly.

Prompt Markdown for fix/rewrite is copied from `config/prompts/` into generated app assets on every `preBuild`.

### Optional SDK setup

Android tooling is **not** required to use the Windows tray app. For developers who work on the Android module, run once:

- Tray: **Android** → **Install JDK and Android SDK**
- CLI: `hsk android setup`
- Optional Android Studio: `hsk android setup --android-studio`

What the action does (idempotent):

1. Ensures JDK 17 (existing `JAVA_HOME`, Microsoft JDK, or portable Temurin under `%LOCALAPPDATA%\Java`; usually no UAC)
2. Installs Android command-line tools under `%LOCALAPPDATA%\Android\Sdk`
3. Accepts licenses and installs platform-tools, android-35, build-tools 35.0.0
4. Sets user env: `ANDROID_HOME`, `ANDROID_SDK_ROOT`, `JAVA_HOME`, and updates `Path`
5. Writes `android/local.properties`
6. Optionally installs Android Studio via winget (emulator / Layout Inspector; not required to build an APK)

Restart the tray app (and open a **new** terminal) after setup so env vars apply.

### Build APK

From `android\` with Gradle wrapper:

```powershell
cd android
.\gradlew.bat assembleDebug
.\gradlew.bat assembleRelease
```

Outputs:

| Variant | Command           | APK path                                                             |
| ------- | ----------------- | -------------------------------------------------------------------- |
| Debug   | `assembleDebug`   | `android\app\build\outputs\apk\debug\HarrixSwissKnife-debug.apk`     |
| Release | `assembleRelease` | `android\app\build\outputs\apk\release\HarrixSwissKnife-release.apk` |

Release is signed with the **debug** keystore so it can be sideloaded like debug. Use a dedicated release keystore before publishing to Play Store.

Via Harrix Swiss Knife (tray **Android** → **Build Android APK in …**, or CLI):

```text
hsk android format android
hsk android check android
hsk android build android
hsk android build android debug
hsk android build android release
hsk android build debug
hsk android build --all
hsk android build --all debug
```

`hsk android format` / `check` / `build` take an Android project folder (directory with `gradlew.bat`). Tray actions show a folder dialog from `paths_android_projects` in `config/config.json`. For **Build Android APK in …**, the dialog has folders on the left (plus checkboxes to build all listed projects sequentially and **Release**), and a single install target on the right: connected `adb` devices and installed AVDs (`emulator -list-avds`). **Release** is initially checked when `android_build_variant` in `config/config.json` is `release` (default). Selecting a stopped AVD starts the emulator, waits for boot, then runs `adb install -r`. `hsk android build --all` builds all configured projects from the CLI. `hsk android format` runs Spotless (`spotlessApply`). `hsk android check` runs `qualityCheck` (Spotless check + Detekt + `lintDebug`). CLI may omit the variant (same config key) or pass `debug`/`release` to override; a lone `debug`/`release` argument still means variant with FOLDER defaulting to `.`. CLI installs on the first authorized adb device. After a successful build the result dialog can open the APK folder. If no device is available, the APK is still produced.

Manual install (optional):

```powershell
adb install -r android\app\build\outputs\apk\debug\HarrixSwissKnife-debug.apk
```

### Workflow

- Edit Kotlin/Gradle in **Cursor**; format with `hsk android format android`, check with `hsk android check android`, build with tray **Android** → **Build Android APK in …** or `hsk android build android …`
- Quality stack: Spotless (ktlint), Detekt + Compose rules, Android Lint (`./gradlew qualityCheck` from `android/`)
- Android Studio is optional (File → Open → `android/`) for emulator / Layout Inspector — **not** required and **not** opened during APK build

### Phone setup (Samsung Galaxy S24 Ultra)

Do this once so auto-install / `adb install` works over USB Type-C:

1. **Settings → About phone → Software information** — tap **Build number** seven times (Developer options unlock).
2. **Settings → Developer options:**
   - **USB debugging** — on.
   - **Install via USB** and/or **USB debugging (Security settings)** — on (on Samsung, `adb install` often fails without these).
3. Connect the phone with a **USB Type-C** data cable (not charge-only).
4. On first connect, accept **Allow USB debugging** for this PC on the phone (optional: Always allow).
5. On the PC, verify:

```powershell
adb devices
```

You need a line like `XXXXXXXX    device` (not `unauthorized` or `offline`). If `unauthorized`, accept the prompt on the phone again. Windows drivers usually install automatically; if not, use Samsung USB Driver or the Google USB Driver from the Android SDK.

## ➕ Add a new action

Actions live under `src/harrix_swiss_knife/actions/`. The package root holds only `__init__.py` and **subpackages**. Each menu section is a subpackage with **one** public `On*` class per `.py` file. Framework code and shared helpers live in `actions/common/` (not menu items).

| Section         | Package                   | Import example                                              |
| --------------- | ------------------------- | ----------------------------------------------------------- |
| Apps            | `actions/apps/`           | `harrix_swiss_knife.actions.apps.OnFinance`                 |
| Android         | `actions/android/`        | `harrix_swiss_knife.actions.android.OnAndroidBuild`         |
| Dev             | `actions/development/`    | `harrix_swiss_knife.actions.development.OnAboutDialog`      |
| File operations | `actions/files/`          | `harrix_swiss_knife.actions.files.On…`                      |
| Images          | `actions/images/`         | `harrix_swiss_knife.actions.images.On…`                     |
| Markdown        | `actions/markdown/`       | `harrix_swiss_knife.actions.markdown.On…`                   |
| Python          | `actions/python/`         | `harrix_swiss_knife.actions.python.On…`                     |
| Site            | `actions/site/`           | `harrix_swiss_knife.actions.site.OnPullSiteSubmodules`      |
| Text            | `actions/text/`           | `harrix_swiss_knife.actions.text.OnFixTextWithAI`           |
| VS Code         | `actions/vscode/`         | `harrix_swiss_knife.actions.vscode.OnVscodeCheck`           |
| Quick launcher  | `actions/quick_launcher/` | `harrix_swiss_knife.actions.quick_launcher.OnQuickLauncher` |
| Common          | `actions/common/`         | Framework + shared helpers (see below)                      |

**`actions/common/`** (not tray menu actions):

- Framework: `base` (`ActionBase`), `dialog_service`, `dialog_geometry`, `dialog_widgets`, log/usage browsers, `text_result_dialog`, `text_diff_dialog`
- Shared helpers used by more than one action (images, Git/Markdown commit, quick launcher wiring, site links, subprocess, …)

Import the base class from common:

```python
from harrix_swiss_knife.actions.common.base import ActionBase
```

**Structure rules** (subcategory folders only, not `common/`):

- One public `On*` class per file; no module-level helpers or constants.
- Put helpers on the class (`@staticmethod` / methods); constants as class attributes / `ClassVar`.
- Helper classes used only by that action → nested inside the `On*` class.
- Code shared by several actions (and not in harrix-pylib) → `actions/common/`.

**File name:** drop the `On` prefix and use snake_case — `OnCheckFeaturedImageInFolders` → `check_featured_image_in_folders.py`. For a reserved name like `exit`, use `exit_.py`.

**Steps:**

1. Create `src/harrix_swiss_knife/actions/<section>/<action_snake_case>.py` with `class On<Action>(ActionBase)` (import `ActionBase` from `harrix_swiss_knife.actions.common.base`; see existing files in the same section).
2. Export the class from `src/harrix_swiss_knife/actions/<section>/__init__.py` (`from … import On…` and add to `__all__`).
3. Add the class to `get_menu_structure()` in `src/harrix_swiss_knife/menu_structure.py`.
4. Emoji icons: <https://emojidb.org/>.
5. If the action should be available from CLI (`hsk`):
   - Set `cli_available = True` and `cli_hint = "<section> <command-name>"` on the class.
   - Add a Click command in `src/harrix_swiss_knife/cli.py` (import from `harrix_swiss_knife.actions.<section>`).
   - Verify: `hsk <section> <command-name> --help` and a test run.
6. Run or restart `harrix-swiss-knife`.
7. Run `ty check` and `ruff check`.
8. From the tray app: `Python` → `ruff sort, ruff format, sort, make docs PY in …` on `harrix-swiss-knife` (or `hsk py ruff-sort-docs .`). On the project root this also refreshes `## 📋 List of commands` in `README.md`. Then `Harrix PY check in …` on the same folder.

If the new action **inherits** another action or calls `OtherOnAction().execute(...)`, import that class from its module (e.g. `from harrix_swiss_knife.actions.images.optimize import OnOptimize`), not only from the section `__init__.py`.

Example action file:

```python
# src/harrix_swiss_knife/actions/files/check_featured_image_in_folders.py
"""Check for featured image files in all configured folders."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.common.base import ActionBase


class OnCheckFeaturedImageInFolders(ActionBase):
    """Check for featured image files in all configured folders.

    This action automatically checks all directories specified in the
    paths_with_featured_image configuration setting for the presence of
    files named `featured_image` with any extension, providing a status
    report for each directory.

    """

    icon = "✅"
    title = "Check featured_image in all folders"

    @ActionBase.handle_exceptions("checking featured image in folders")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Check for featured image files in all configured folders."""
        for path in self.config["paths_with_featured_image"]:
            result = h.file.check_featured_image(path)[1]
            self.add_line(result)
        self.show_result()
```

Register in the section package:

```python
# src/harrix_swiss_knife/actions/files/__init__.py (add import + __all__ entry)
from harrix_swiss_knife.actions.files.check_featured_image_in_folders import OnCheckFeaturedImageInFolders
```

### Example action with CLI command

- Add CLI command in `src/harrix_swiss_knife/cli.py` (import action + Click group/command).
- In the action, prefer `folder_path` + `noninteractive` so the same logic works in tray UI and CLI.
- Set `cli_available = True` and `cli_hint` (e.g. `"md check"`) so the tray menu and main window show a `ꟲᴸᴵ` suffix and CLI tooltip. The menu action also gets `cli_copy_command` for right-click **Copy CLI command** (tray menu and main window list).
- In `cli.py`, call `_exit_if_action_failed(action)` after the action runs. It exits with code `1` when `_cli_action_failed` finds any `❌` line or a `🔢 Count errors` line in `result_lines` (script-friendly checks):

```python
# src/harrix_swiss_knife/actions/<section>/<action_snake_case>.py
from __future__ import annotations
from pathlib import Path
from typing import Any
from harrix_swiss_knife.actions.common.base import ActionBase
class On<SomeActionName>Folder(ActionBase):
    """Do something with a folder (tray action + CLI command)."""
    icon = "🛠️"
    title = "<Human readable title>"
    cli_available = True
    cli_hint = "<section> <command-name>"
    def do_work_common(self) -> None:
        """Shared logic for tray thread and CLI (no dialogs)."""
        if self.folder_path is None:
            return
        self.add_line(f"🔵 Starting processing for path: {self.folder_path}")
        # ... do work synchronously ...
    @ActionBase.handle_exceptions("<context for errors>")
    def execute(
        self,
        *_args: Any,
        folder_path: Path | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        if noninteractive and folder_path is None:
            self.handle_error(
                ValueError("folder_path is required when noninteractive is True"),
                self.title,
            )
            return
        if folder_path is not None:
            self.folder_path = Path(folder_path).resolve()
        else:
            self.folder_path = self.dialogs.get_folder_with_choice_option(
                self.config["<paths_config_key>"],
                self.config["<default_path_config_key>"],
            )
        if not self.folder_path:
            return
        if noninteractive:
            self.do_work_common()
            return
        self.start_thread(self.in_thread, self.thread_after, self.title)
    @ActionBase.handle_exceptions("<context> thread")
    def in_thread(self) -> str | None:
        self.do_work_common()
        return f"{self.title} completed"
    @ActionBase.handle_exceptions("<context> thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

```python
# src/harrix_swiss_knife/cli.py (add import + command; reuse _exit_if_action_failed at file bottom)
from __future__ import annotations
from pathlib import Path
import click
from harrix_swiss_knife.actions.<section> import On<SomeActionName>Folder
@cli.group("<section>")
def <section>_group() -> None:
    """<Section-related commands>."""
@<section>_group.command("<command-name>")
@click.argument(
    "folder",
    required=False,
    default=".",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
def <command_name>(folder: Path) -> None:
    """<One-line help> (same as tray action)."""
    action = On<SomeActionName>Folder()
    action(folder_path=folder, noninteractive=True)
    _exit_if_action_failed(action)
```

CLI call examples:

- `hsk <section> <command-name> --help`
- `hsk <section> <command-name> "D:/path/to/folder"`
- `hsk <section> <command-name>` (uses current directory when `folder` defaults to `.`)

**Other CLI shapes** (see existing commands in `cli.py`):

- **Dialogs / Qt UI:** call `_ensure_qt_app()` before the action (e.g. `md new-note`, `md add-from-template`).
- **No folder argument:** pass kwargs to `execute(..., noninteractive=True)` (e.g. `dev install-harrix-notes-explorer-hsk` with `editor=` and optional `with_public=True`).
- **Extra Click options:** e.g. `md check --rule H001` (repeatable `--rule`), `md check --include-g-md`; wire options into `execute` kwargs.

Example action with QThread:

```python
class OnNpmManagePackages(ActionBase):
    """Install or update configured NPM packages globally.
    This action manages NPM packages specified in the `config["npm_packages"]` list:
    1. Updates NPM itself to the latest version
    2. Installs/updates all configured packages (npm install will update if already exists)
    3. Runs global update to ensure all packages are at latest versions
    This ensures all configured packages are present and up-to-date in the system.
    """

    icon = "📦"
    title = "Update/Install global NPM packages"

    @ActionBase.handle_exceptions("NPM package management")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Install or update configured NPM packages globally."""
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("NPM operations thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        # Update NPM itself first
        self.add_line("Updating NPM...")
        result = h.dev.run_command("npm update npm -g")
        self.add_line(result)
        # Install/update all configured packages
        self.add_line("Installing/updating configured packages...")
        install_commands = "\n".join([f"npm i -g {package}" for package in self.config["npm_packages"]])
        result = h.dev.run_command(install_commands)
        self.add_line(result)
        # Run global update to ensure everything is up-to-date
        self.add_line("Running global update...")
        result = h.dev.run_command("npm update -g")
        self.add_line(result)
        return "NPM packages management completed"

    @ActionBase.handle_exceptions("NPM thread completion")
    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast("NPM packages management completed")
        self.add_line(result)
        self.show_result()
```

Example action with sequence of QThread (illustrative pattern only — this class is not shipped in the repo):

```python
class OnHarrixActionWithSequenceOfThread(ActionBase):
    """Docstring."""

    icon = "👷‍♂️"
    title = "Sequence of thread"

    @ActionBase.handle_exceptions("action")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.start_thread(self.in_thread_01, self.thread_after_01, self.title)
        return "Started the process chain"

    @ActionBase.handle_exceptions("action thread 01")
    def in_thread_01(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        # First operation
        self.add_line("Starting first operation")
        time.sleep(5)  # Simulating work
        return "First operation completed"

    @ActionBase.handle_exceptions("action thread 02")
    def in_thread_02(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        # Second operation
        self.add_line("Starting second operation")
        time.sleep(self.time_waiting_seconds)  # Simulating work
        return "Second operation completed"

    @ActionBase.handle_exceptions("action thread 03")
    def in_thread_03(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        # Third operation
        self.add_line("Starting third operation")
        time.sleep(5)  # Simulating work
        return "Third operation completed"

    @ActionBase.handle_exceptions("action thread 01 completion")
    def thread_after_01(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread_01(). For handling the results of thread execution."""
        self.add_line(result)  # Log the result from the first thread
        # Start the second operation
        self.time_waiting_seconds = 20
        message = f"Wait {self.time_waiting_seconds} seconds for the package to be published."
        self.start_thread(self.in_thread_02, self.thread_after_02, message)

    @ActionBase.handle_exceptions("action thread 02 completion")
    def thread_after_02(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread_02(). For handling the results of thread execution."""
        self.add_line(result)  # Log the result from the second thread
        # Start the third operation
        self.start_thread(self.in_thread_03, self.thread_after_03, self.title)

    @ActionBase.handle_exceptions("action thread 03 completion")
    def thread_after_03(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread_03(). For handling the results of thread execution."""
        self.add_line(result)  # Log the result from the third thread
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

## 📁 Add file to a resource file

Add files (pictures, etc.) to the `src\harrix_swiss_knife\assets` folder.

In the file `resources.qrc` add line for example `<file>assets/logo.svg</file>`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<RCC>
    <qresource prefix="/">
        <file>assets/logo.svg</file>
    </qresource>
</RCC>
```

Generate `resources_rc.py`:

```shell
pyside6-rcc src/harrix_swiss_knife/resources.qrc -o src/harrix_swiss_knife/resources_rc.py
```

## 📝 Add a new Markdown template (for 📝 Add Markdown from template)

### 🚀 Quick start

Template system allows adding structured Markdown content (movies, books, etc.) through dynamic forms.

Create a new `.md` file in `config/` folder with field placeholders:

```markdown
## {{Title:line}}: {{Score:float:10}}

![Featured Image]({{Featured Image:image}})

- **Date:** {{Date:date}}
- **URL:** <{{URL:url}}>
- **Source:** {{Source:line}}
- **Published:** {{Published:bool:true}}
- **Review:** {{Review:multiline}}

## Gallery

{{Gallery Images:images}}

## Documents

[Download]({{Main Document:file}})

## Attachments

{{Attachments:files}}
```

Add template configuration to `config/config.json`:

```json
"markdown_templates": {
  "your-template-name": {
    "template_file": "config/template-your-name.md",
    "path_target": "D:/path/to/target-folder/",
    "insert_position": "start",
    "dialog_links": [
      {"label": "IMDb", "url": "https://www.imdb.com"},
      {"label": "Metacritic", "url": "https://www.metacritic.com"}
    ]
  },
  "Events (single file + image optimize)": {
    "template_file": "config/template-event.md",
    "path_target": "D:/Notes/Events/Events.md",
    "insert_position": "start",
    "image_optimize": true,
    "image_max_size": 1024,
    "dialog_links": [{"label": "Afisha", "url": "https://afisha.yandex.ru/"}]
  }
}
```

Options:

- `template_file` — Path to template file
- `path_target` — Target path (optional). Two modes:
  - **Folder:** path ends with `/` or has no `.md` → file is `{path_target}{current_year}.md`, e.g. `D:/Notes/Movies/` → `D:/Notes/Movies/2026.md`
  - **Single file:** path is a full path to a `.md` file, e.g. `D:/Notes/Events/Events.md` → all entries go into that file; new block is inserted under the current year section `## {year}` (or after TOC if that year section does not exist yet)
- `insert_position` — `"start"` (after year heading or TOC) or `"end"` (default)
- `edit_existing` — Optional. If `true`, the template dialog shows a left panel with a filterable tree of existing entries; **➕ Add new Entry** is selected by default. Supports `city_note` layout (grouped by city) and file layouts (grouped by `.md` file, including year files)
- `path_layout` — Optional. `"city_note"` stores each entry as a separate note under `{path_target}/{subfolder_field}/{note_name_field}/{note_name_field}.md` with optional `img/`. Subfolder and note name fields are declared in the template via `@subfolders` and `@note_name` (see Supported Field Types). Optional fallbacks: `path_city_field`, `path_note_name_field`. Default: folder → `{year}.md`, or single `.md` file
- `path_city_field` — Optional fallback when the template has no `@subfolders` field (default: `"City"`)
- `path_note_name_field` — Optional fallback when the template has no `@note_name` field (default: `"Title"`)
- `note_with_images` — Optional. If `true` with `city_note`, creates `img/` inside each note folder (default: `false`)
- `dialog_links` — Optional list of helper links shown only in the form dialog
- `image_optimize` — Optional legacy fallback in `config.json`. Prefer `#1024` on `image`/`images` fields in the template (e.g. `{{Images:images@Title#1024}}`). When enabled, images are optimized after insert (same as “Optimize selected images in …”): copy to `img/`, optimize, optionally resize.
- `image_max_size` — Optional legacy fallback max width/height in pixels when `image_optimize` is used from config (e.g. `1024`)

**Fill with AI:** The template dialog shows **Fill with AI** when BotHub config is available. It opens the shared text/image source dialog (paste, screenshot). BotHub receives empty/zero fields (and numeric fields still at their template default, e.g. `Score:float:10`), excluding `Review` and media/`bool` fields. Source images are sent to the model only — they are not attached to the note. Prompt: `prompts.markdown_template_fields_from_source` → `config/prompts/markdown-template-fields-from-source.md`.

**Image field when `path_target` is a file:** images are saved to `{path_target_parent}/img/`; drag & drop, paste from clipboard (Ctrl+V or Paste button) are supported; path in Markdown is relative (`img/filename.ext`). If the template also has a `Date` field, the image widget shows an internal “Filename:” row synced with the event date (default filename = date, user can change); existing files are not overwritten (`_1`, `_2` suffixes).

### 📋 Supported Field Types

Syntax:

```text
{{FieldName:FieldType}}
{{FieldName:FieldType:DefaultValue}}
{{FieldName:FieldType@LinkedField}}
{{FieldName:FieldType@LinkedField#1024}}
{{FieldName:FieldType@LinkedField:DefaultValue}}
{{FieldName:FieldType@LinkedField#1024:DefaultValue}}
```

For `image` and `images` fields, `@LinkedField` optionally links the filename base to another field (e.g. `{{Images:images@Title}}`). Default base is the date when the template has a `Date` field; when the linked field is filled, base is replaced by a slug from its value. Append `#1024` after `@LinkedField` to optimize images with max side 1024 px (e.g. `{{Images:images@Title#1024}}`).

For `date` fields, `@Images` links the date to an `image`/`images` field: when the user adds images, a date is parsed from the **original** filename (e.g. `2026-07-10 14.27.19.jpg` → `2026-07-10`) and fills the field only if it is still empty. Use `@Images!` to always update the date on every new image drop (e.g. `{{DateLast:date@Images!}}` for last-visit date). With multiple files in one drop, fill-if-empty uses the earliest parsed date; overwrite mode uses the latest.

For `line` fields, `@subfolders` turns the input into an editable combobox with existing subfolder names under the template `path_target` (first path segment in `city_note` layout). `@note_name` marks the field whose value becomes the note folder and `.md` filename stem in `city_note` layout.

Available types:

| Type          | Widget                        | Example                         | Default Value Example                             |
| ------------- | ----------------------------- | ------------------------------- | ------------------------------------------------- |
| `line`        | Single-line text input        | `{{Title:line}}`                | `{{Title:line:Untitled}}`                         |
| `url`         | URL input with Open button    | `{{Web:url}}`                   | `{{Web:url:https://example.com}}`                 |
| `int`         | Integer spinner               | `{{Season:int}}`                | `{{Season:int:1}}`                                |
| `float`       | Decimal spinner               | `{{Score:float}}`               | `{{Score:float:10}}`                              |
| `date`        | Date picker                   | `{{Date:date}}`                 | `{{Date:date:2025-01-01}}`                        |
| `bool`        | Checkbox                      | `{{Published:bool}}`            | `{{Published:bool:true}}`                         |
| `multiline`   | Text area                     | `{{Review:multiline}}`          | `{{Review:multiline:No review}}`                  |
| `image`       | Single image picker           | `{{Featured:image}}`            | `{{Featured:image:path/to/img.png}}`              |
| `images`      | Multiple image picker         | `{{Gallery:images@Title#1024}}` | `{{Gallery:images@Title#1024:img1.png,img2.jpg}}` |
| `file`        | Single file picker            | `{{Document:file}}`             | `{{Document:file:path/to/doc.pdf}}`               |
| `files`       | Multiple file picker          | `{{Attachments:files}}`         | `{{Attachments:files:doc1.pdf,doc2.docx}}`        |
| `coordinates` | Coordinates with map actions  | `{{Coordinates:coordinates}}`   | `{{Coordinates:coordinates:55.7558, 37.6173}}`    |

Notes:

- Float values that are whole numbers are formatted without decimals (`11.0` → `11`)
- Date format: `yyyy-MM-dd`
- Default values are optional
- **URL fields:** Prefer `<{{Web:url}}>` so Markdown renders an autolink; the dialog shows an **Open** button that opens the URL in the default browser (`https://` is added when the scheme is missing)
- **Empty lines:** When filling a template, a line that contains placeholders is omitted if every field on that line is empty; the line is kept if at least one field on the line has a value
- **Dialog Links:** `dialog_links` items open in your default browser; they do not affect generated Markdown
- **Image/File Types:** Support drag & drop, file dialogs, and preview functionality
- **Image field:** When target is a single `.md` file, images are saved to that file’s `img/` folder; paste from clipboard (Ctrl+V or Paste button) is supported. If the template has a `Date` field, the image widget shows a “Filename:” row (default = date, editable); filenames are made unique (`_1`, `_2`) to avoid overwriting.
- **Images field (multiple):** Same as image; when target is a single `.md` file, images are saved to `img/` with date-based base name. If the template has a `Date` field, the widget shows a "Filename base:" row (default = date; use `{{Images:images@Title}}` in the template to replace it with a slug from `Title` when filled); files are named `base_01`, `base_02`, etc. The placeholder `{{Images:images}}` is replaced by one Markdown image line per file (alt text from `Title` if present).
- **Multiple Types:** `images` and `files` return comma-separated paths
- **Supported Image Formats:** PNG, JPG, JPEG, GIF, BMP, SVG, WEBP, AVIF
- **File Types:** Accept any file type for `file` and `files` fields
