---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# Third-party notices (downloaded binaries)

This repository is licensed under the MIT license (see `LICENSE.md`), but during installation and/or from the app UI it can **download and use third-party executables**. Those executables are **not** covered by this repository’s MIT license and remain under their **own** licenses.

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [Embedded assets (bundled in this repo)](#embedded-assets-bundled-in-this-repo)
- [UI sounds (bundled WAV assets)](#ui-sounds-bundled-wav-assets)
  - [Habits (UI SFX cinematic)](#habits-ui-sfx-cinematic)
  - [Fitness voiceover (Kenney)](#fitness-voiceover-kenney)
  - [Fitness UI cues (UI SFX cinematic)](#fitness-ui-cues-ui-sfx-cinematic)
  - [Fitness record applause (BigSoundBank + UI SFX)](#fitness-record-applause-bigsoundbank--ui-sfx)
- [FFmpeg (`ffmpeg.exe`)](#ffmpeg-ffmpegexe)
- [libavif tools (`avifenc.exe`, `avifdec.exe`)](#libavif-tools-avifencexe-avifdecexe)
- [Online download vs offline bundle (`install/dependencies/`)](#online-download-vs-offline-bundle-installdependencies)
- [Other third-party downloads used by the offline bundle builder](#other-third-party-downloads-used-by-the-offline-bundle-builder)
- [Data sources / external services](#data-sources--external-services)

</details>

The GUI installer that performs these downloads is the PySide6 package under `src/harrix_swiss_knife/installer/`.

## Embedded assets (bundled in this repo)

This repository also contains some third-party assets that are bundled into the application resources (for example `src/harrix_swiss_knife/assets/py.svg`). See `attribution.yaml` for attribution and the relevant upstream usage policy / licensing terms.

## UI sounds (bundled WAV assets)

Short UI effects from **UI SFX**, **Kenney**, and **BigSoundBank**, license **CC0 1.0**. WAV copies live under `src/harrix_swiss_knife/assets/sounds/` (compiled into Qt resources). Attribution is not required by CC0; it is recorded here on purpose. WAV copies are lossless conversions of the original OGG/MP3 files from those packs.

### Habits (UI SFX cinematic)

- Pack: <https://uisfx.com/> (`cinematic`)
- Source: <https://github.com/romainsimon/uisfx>
- License: CC0 1.0 (audio); MIT (runtime, not bundled)
- Files used:
  - `habit_done.wav` — UI SFX `cinematic/check` (habit Done)
  - `habit_not_done.wav` — UI SFX `cinematic/delete` (habit Not done)

### Fitness voiceover (Kenney)

- Pack: <https://kenney.nl/assets/voiceover-pack> (Female)
- Author: Kenney (<http://www.kenney.nl>); voice: Giselle
- License: Creative Commons Zero, CC0 1.0
- Files used:
  - `fitness_ready.wav` — `ready` (Prepare countdown start)
  - `fitness_3.wav` / `fitness_2.wav` / `fitness_1.wav` — last three prepare seconds
  - `fitness_go.wav` — `go` (main stopwatch starts)
  - `fitness_time_over.wav` — `time_over` (timed exercise finished)
  - `fitness_congratulations.wav` — `congratulations` (workout complete)

### Fitness UI cues (UI SFX cinematic)

- Pack: <https://uisfx.com/> (`cinematic`)
- Source: <https://github.com/romainsimon/uisfx>
- License: CC0 1.0 (audio)
- Files used:
  - `fitness_paste.wav` — UI SFX `cinematic/paste` (set added to process / workout)
  - `fitness_success.wav` — UI SFX `cinematic/success`
  - `fitness_pause.wav` — UI SFX `cinematic/pause` (timer paused)
  - `fitness_continue.wav` — UI SFX `cinematic/play` (timer resumed)

### Fitness record applause (BigSoundBank + UI SFX)

- Packs: <https://bigsoundbank.com/applause-1-s2363.html> (Applause #1, sound 2363) and UI SFX `cinematic/achievement`
- Authors: Dorian CLAIR (BigSoundBank); UI SFX (Romain Simon)
- License: CC0 1.0
- Files used:
  - `fitness_applause.wav` — trimmed ~2.9 s mix of BigSoundBank applause and UI SFX `cinematic/achievement` (new record / monthly goal)

## FFmpeg (`ffmpeg.exe`)

- **What:** `ffmpeg.exe` (used as an external command-line tool).
- **Where it comes from:** GitHub releases of **BtbN/FFmpeg-Builds:** `https://github.com/BtbN/FFmpeg-Builds/releases`
- **What the installer fetches:** a Win64 **GPL** build zip (example filename used by the installer: `ffmpeg-master-latest-win64-gpl.zip`) and extracts `ffmpeg.exe`.
- **License:** depends on the exact build and enabled components; the referenced build is labelled **GPL** by the publisher of that release artifact. For the authoritative licensing details, refer to the FFmpeg project and the specific build’s documentation/release notes:
  - FFmpeg project: `https://ffmpeg.org/`
  - Licenses overview: `https://ffmpeg.org/legal.html`

## libavif tools (`avifenc.exe`, `avifdec.exe`)

- **What:** `avifenc.exe` and `avifdec.exe` (used as external command-line tools).
- **Where they come from:** GitHub releases of **AOMediaCodec/libavif:** `https://github.com/AOMediaCodec/libavif/releases`
- **What the installer fetches:** `windows-artifacts.zip` (as published in libavif releases) and extracts `avifenc.exe` / `avifdec.exe`.
- **License:** the licensing for libavif and bundled components can include multiple permissive licenses depending on the artifact. For authoritative details, see the upstream repository and the release artifact documentation:
  - libavif repository: `https://github.com/AOMediaCodec/libavif`

## Online download vs offline bundle (`install/dependencies/`)

This project supports an “offline bundle” workflow that may place installers and binaries into `install/dependencies/` (this folder is ignored by Git).

- **Online download:** the installer downloads binaries from the upstream release pages listed above.
- **Offline bundle / redistribution:** if you copy and redistribute third-party binaries (for example, by distributing a prepared offline EXE), you may take on additional license compliance obligations required by those third-party licenses. Review the upstream license terms for each included binary.

## Other third-party downloads used by the offline bundle builder

The Python installer builder (**Dev** → **Build installer EXEs** / `hsk dev build-install-zips`) may download installers/archives from these upstream sources:

- Git for Windows: `https://github.com/git-for-windows/git/releases`
- Managed CPython (via `uv python install`): archives cached under `install/dependencies/uv-python-cache/` for offline installs; see [uv Python distributions](https://docs.astral.sh/uv/concepts/python-versions/)
- uv: `https://github.com/astral-sh/uv/releases`
- Visual Studio Code installer: `https://code.visualstudio.com/` (downloads via `https://update.code.visualstudio.com/`)

Refer to each project’s website/repository for license terms of their installers.

## Data sources / external services

Some app features rely on third-party services. For example, the finance module can fetch exchange-rate data via the `yfinance` library (which in turn relies on Yahoo Finance endpoints). Availability and terms of use may change; treat these data sources as best-effort.
