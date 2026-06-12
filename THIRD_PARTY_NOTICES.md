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
- [FFmpeg (`ffmpeg.exe`)](#ffmpeg-ffmpegexe)
- [libavif tools (`avifenc.exe`, `avifdec.exe`)](#libavif-tools-avifencexe-avifdecexe)
- [Online download vs offline bundle (`install/dependencies/`)](#online-download-vs-offline-bundle-installdependencies)
- [Other third-party downloads used by the offline bundle script](#other-third-party-downloads-used-by-the-offline-bundle-script)
- [Data sources / external services](#data-sources--external-services)

</details>

The installer script that performs these downloads is `install/harrix-swiss-knife.ps1`.

## Embedded assets (bundled in this repo)

This repository also contains some third-party assets that are bundled into the application resources (for example `src/harrix_swiss_knife/assets/py.svg`). See `attribution.yaml` for attribution and the relevant upstream usage policy / licensing terms.

## FFmpeg (`ffmpeg.exe`)

- **What**: `ffmpeg.exe` (used as an external command-line tool).
- **Where it comes from**: GitHub releases of **BtbN/FFmpeg-Builds**: `https://github.com/BtbN/FFmpeg-Builds/releases`
- **What the installer fetches**: a Win64 **GPL** build zip (example filename used by the installer: `ffmpeg-master-latest-win64-gpl.zip`) and extracts `ffmpeg.exe`.
- **License**: depends on the exact build and enabled components; the referenced build is labelled **GPL** by the publisher of that release artifact. For the authoritative licensing details, refer to the FFmpeg project and the specific build’s documentation/release notes:
  - FFmpeg project: `https://ffmpeg.org/`
  - Licenses overview: `https://ffmpeg.org/legal.html`

## libavif tools (`avifenc.exe`, `avifdec.exe`)

- **What**: `avifenc.exe` and `avifdec.exe` (used as external command-line tools).
- **Where they come from**: GitHub releases of **AOMediaCodec/libavif**: `https://github.com/AOMediaCodec/libavif/releases`
- **What the installer fetches**: `windows-artifacts.zip` (as published in libavif releases) and extracts `avifenc.exe` / `avifdec.exe`.
- **License**: the licensing for libavif and bundled components can include multiple permissive licenses depending on the artifact. For authoritative details, see the upstream repository and the release artifact documentation:
  - libavif repository: `https://github.com/AOMediaCodec/libavif`

## Online download vs offline bundle (`install/dependencies/`)

This project supports an “offline bundle” workflow that may place installers and binaries into `install/dependencies/` (this folder is ignored by git).

- **Online download**: the scripts download binaries from the upstream release pages listed above.
- **Offline bundle / redistribution**: if you copy and redistribute third-party binaries (for example, by distributing a prepared bundle), you may take on additional license compliance obligations required by those third-party licenses. Review the upstream license terms for each included binary.

## Other third-party downloads used by the offline bundle script

The offline bundle helper script `install/download-bundle.ps1` may download installers/archives from these upstream sources:

- Git for Windows: `https://github.com/git-for-windows/git/releases`
- Python installer: `https://www.python.org/downloads/windows/` (direct file downloads from `https://www.python.org/ftp/python/`)
- Node.js distributions: `https://nodejs.org/dist/`
- uv: `https://github.com/astral-sh/uv/releases`
- Visual Studio Code installer: `https://code.visualstudio.com/` (downloads via `https://update.code.visualstudio.com/`)

Refer to each project’s website/repository for license terms of their installers.

## Data sources / external services

Some app features rely on third-party services. For example, the finance module can fetch exchange-rate data via the `yfinance` library (which in turn relies on Yahoo Finance endpoints). Availability and terms of use may change; treat these data sources as best-effort.
