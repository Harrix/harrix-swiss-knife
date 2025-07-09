# harrix-swiss-knife

![Featured image](https://raw.githubusercontent.com/Harrix/harrix-swiss-knife/refs/heads/main/img/featured-image.svg)

A multifunctional tool for developers with a rich set of utilities for working with files, images, Python code, and more.

<details>
<summary>📖 Contents</summary>

## Contents

- [List of commands](#list-of-commands)
- [List of functions](#list-of-functions)
  - [File `main.py`](#file-mainpy)
  - [File `main_menu_base.py`](#file-main_menu_basepy)
  - [File `main_window.py`](#file-main_windowpy)
  - [File `markdown_checker.py`](#file-markdown_checkerpy)
  - [File `python_checker.py`](#file-python_checkerpy)
  - [File `resources_rc.py`](#file-resources_rcpy)
  - [File `toast_countdown_notification.py`](#file-toast_countdown_notificationpy)
  - [File `toast_notification.py`](#file-toast_notificationpy)
  - [File `toast_notification_base.py`](#file-toast_notification_basepy)
  - [File `tray_icon.py`](#file-tray_iconpy)
  - [File `apps.py`](#file-appspy)
  - [File `base.py`](#file-basepy)
  - [File `development.py`](#file-developmentpy)
  - [File `files.py`](#file-filespy)
  - [File `images.py`](#file-imagespy)
  - [File `markdown.py`](#file-markdownpy)
  - [File `markdown_utils.py`](#file-markdown_utilspy)
  - [File `python.py`](#file-pythonpy)
  - [File `database_manager.py`](#file-database_managerpy)
  - [File `main.py`](#file-mainpy-1)
  - [File `mixins.py`](#file-mixinspy)
  - [File `window.py`](#file-windowpy)
- [Deploy on an empty machine (Windows)](#deploy-on-an-empty-machine-windows)
  - [Prerequisites](#prerequisites)
  - [Installation steps](#installation-steps)
  - [Running from command line](#running-from-command-line)
- [Development](#development)
  - [CLI commands](#cli-commands)
  - [Add a new action](#add-a-new-action)
  - [Add file to a resource file](#add-file-to-a-resource-file)
- [Create a shortcut](#create-a-shortcut)
- [License](#license)

</details>

This is a **personal** project tailored to **specific personal** tasks.

![GitHub](https://img.shields.io/badge/GitHub-harrix--swiss--knife-blue?logo=github) ![GitHub](https://img.shields.io/github/license/Harrix/harrix-swiss-knife)

GitHub: <https://github.com/Harrix/harrix-swiss-knife>

This project provides a Windows application with a system tray context menu, featuring mini-programs designed to automate specific personal tasks.

![Screenshot](https://raw.githubusercontent.com/Harrix/harrix-swiss-knife/refs/heads/main/img/screenshot.png)

_Figure 1: Screenshot_

## List of commands

- **Dev**
  - ℹ️ About
  - 📦 Install/Update global NPM packages
  - ⚙️ Open config.json
  - 📥 Update uv
- **Images**
  - 📸 Open Camera Uploads
  - 🚀 Optimize images
  - 🔝 Optimize images (high quality)
  - ⬆️ Optimize images in … and replace
  - 🖼️ Optimize one image
  - ↔️ Resize and optimize images (with PNG to AVIF)
  - 🧹 Clear folders images
  - 📂 Open the folder images
  - 📂 Open the folder optimized_images
- **File operations**
  - 🔒 Block disks
  - ✅ Check featured_image
  - ✅ Check featured_image in …
  - 🗂️ Moves and flattens files from nested folders
  - 🖲️ Rename largest images to featured_image in …
  - ├ Tree view of a folder
  - ├ Tree view of a folder (ignore hidden folders)
- **Markdown**
  - 🎬 Get a list of movies, books for web
  - 👉 Increase heading level
  - ❞ Quotes. Format quotes as Markdown content
  - 😎 Beautify MD and regenerate .g.md in …
  - 😎 Beautify MD in …
  - 🚧 Check in …
  - 📥 Download images in one MD
  - 📥 Download images in …
  - 🧏 Generate a short version with only TOC
  - ⚖️ Optimize images in MD in …
  - ❞ Quotes. Add author and title
  - 📶 Sort sections in one MD
- **New Markdown**
  - ✍️ New article
  - 📖 New diary note
  - 💤 New dream note
  - 📓 New note
  - 📓 New note with images
- **Python**
  - 🚧 Check PY in …
  - 🐍 New uv project
  - 👷‍♂️ Publish Python library to PyPI
  - 🌟 isort, ruff format, sort in PY files
  - ⭐ isort, ruff format, sort, make docs in PY files
- 🏃🏻 Fitness tracker
- 🚀 Optimize image from clipboard
- 🚀 Optimize image from clipboard as …
- × Exit

## List of functions

### File `main.py`

Doc: [main.g.md](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/main.g.md)

| Function/Class                                                                                                                             | Description                                                    |
| ------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------- |
| Class [`MainMenu (hsk.main_menu_base.MainMenuBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/main.g.md#class-mainmenu) | Main menu class that defines the application's menu structure. |

### File `main_menu_base.py`

Doc: [main_menu_base.g.md](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/main_menu_base.g.md)

| Function/Class                                                                                                             | Description                                                        |
| -------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| Class [`MainMenuBase`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/main_menu_base.g.md#class-mainmenubase) | A base class for handling menu operations in a PySide application. |

### File `main_window.py`

Doc: [main_window.g.md](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/main_window.g.md)

| Function/Class                                                                                                                    | Description                                                                            |
| --------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Class [`MainWindow (QMainWindow)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/main_window.g.md#class-mainwindow) | The main window of the application that displays a menu and handles user interactions. |

### File `markdown_checker.py`

Doc: [markdown_checker.g.md](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/markdown_checker.g.md)

| Function/Class                                                                                                                     | Description                                                            |
| ---------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Class [`MarkdownChecker`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/markdown_checker.g.md#class-markdownchecker) | Class for checking Markdown files for compliance with specified rules. |

### File `python_checker.py`

Doc: [python_checker.g.md](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/python_checker.g.md)

| Function/Class                                                                                                               | Description                                                          |
| ---------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| Class [`PythonChecker`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/python_checker.g.md#class-pythonchecker) | Class for checking Python files for compliance with specified rules. |

### File `resources_rc.py`

Doc: [resources_rc.g.md](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/resources_rc.g.md)

| Function/Class                                                                                                                  | Description |
| ------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| [`qCleanupResources`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/resources_rc.g.md#function-qcleanupresources) |             |
| [`qInitResources`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/resources_rc.g.md#function-qinitresources)       |             |

### File `toast_countdown_notification.py`

Doc: [toast_countdown_notification.g.md](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/toast_countdown_notification.g.md)

| Function/Class                                                                                                                                                                                                       | Description                                                 |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Class [`ToastCountdownNotification (toast_notification_base.ToastNotificationBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/toast_countdown_notification.g.md#class-toastcountdownnotification) | A toast notification that displays an elapsed time counter. |

### File `toast_notification.py`

Doc: [toast_notification.g.md](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/toast_notification.g.md)

| Function/Class                                                                                                                                                                           | Description                                                                          |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| Class [`ToastNotification (toast_notification_base.ToastNotificationBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/toast_notification.g.md#class-toastnotification) | A temporary toast notification that automatically closes after a specified duration. |

### File `toast_notification_base.py`

Doc: [toast_notification_base.g.md](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/toast_notification_base.g.md)

| Function/Class                                                                                                                                                  | Description                         |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| Class [`ToastNotificationBase (QDialog)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/toast_notification_base.g.md#class-toastnotificationbase) | Base class for toast notifications. |

### File `tray_icon.py`

Doc: [tray_icon.g.md](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/tray_icon.g.md)

| Function/Class                                                                                                                  | Description                                                                   |
| ------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| Class [`TrayIcon (QSystemTrayIcon)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/tray_icon.g.md#class-trayicon) | Represent a system tray icon with an associated context menu and main window. |

### File `apps.py`

Doc: [apps.g.md](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/apps.g.md)

| Function/Class                                                                                                          | Description                              |
| ----------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| Class [`OnFitness (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/apps.g.md#class-onfitness) | Launch the fitness tracking application. |

### File `base.py`

Doc: [base.g.md](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/base.g.md)

| Function/Class                                                                                               | Description                                                     |
| ------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------- |
| Class [`ActionBase`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/base.g.md#class-actionbase) | Base class for actions that can be executed and produce output. |

### File `development.py`

Doc: [development.g.md](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/development.g.md)

| Function/Class                                                                                                                                     | Description                                         |
| -------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| Class [`AboutDialog (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/development.g.md#class-aboutdialog)                 | Show the about dialog with program information.     |
| Class [`OnExit (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/development.g.md#class-onexit)                           | Exit the application.                               |
| Class [`OnNpmManagePackages (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/development.g.md#class-onnpmmanagepackages) | Install or update configured NPM packages globally. |
| Class [`OnOpenConfigJson (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/development.g.md#class-onopenconfigjson)       | Open the application's configuration file.          |
| Class [`OnUvUpdate (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/development.g.md#class-onuvupdate)                   | Update uv package manager to its latest version.    |

### File `files.py`

Doc: [files.g.md](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/files.g.md)

| Function/Class                                                                                                                                                               | Description                                                |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| Class [`OnAllFilesToParentFolder (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/files.g.md#class-onallfilestoparentfolder)                       | Move and flatten files from nested directories.            |
| Class [`OnBlockDisks (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/files.g.md#class-onblockdisks)                                               | Lock BitLocker-encrypted drives.                           |
| Class [`OnCheckFeaturedImage (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/files.g.md#class-oncheckfeaturedimage)                               | Check for featured image files in a selected folder.       |
| Class [`OnCheckFeaturedImageInFolders (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/files.g.md#class-oncheckfeaturedimageinfolders)             | Check for featured image files in all configured folders.  |
| Class [`OnTreeViewFolder (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/files.g.md#class-ontreeviewfolder)                                       | Generate a text-based tree view of a folder structure.     |
| Class [`OnTreeViewFolderIgnoreHiddenFolders (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/files.g.md#class-ontreeviewfolderignorehiddenfolders) | Generate a tree view excluding hidden folders.             |
| Class [`RenameLargestImagesToFeaturedImage (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/files.g.md#class-renamelargestimagestofeaturedimage)   | Rename the largest image in each folder to featured_image. |

### File `images.py`

Doc: [images.g.md](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/images.g.md)

| Function/Class                                                                                                                                            | Description                                                          |
| --------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| Class [`OnClearImages (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/images.g.md#class-onclearimages)                         | Clear temporary image directories.                                   |
| Class [`OnOpenCameraUploads (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/images.g.md#class-onopencamerauploads)             | Open all Camera Uploads folders.                                     |
| Class [`OnOpenImages (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/images.g.md#class-onopenimages)                           | Open the source images temporary folder.                             |
| Class [`OnOpenOptimizedImages (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/images.g.md#class-onopenoptimizedimages)         | Open the optimized images temporary folder.                          |
| Class [`OnOptimize (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/images.g.md#class-onoptimize)                               | Run standard image optimization on all images in the temp folder.    |
| Class [`OnOptimizeClipboard (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/images.g.md#class-onoptimizeclipboard)             | Optimize an image from the clipboard with default naming.            |
| Class [`OnOptimizeClipboardDialog (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/images.g.md#class-onoptimizeclipboarddialog) | Optimize an image from the clipboard with custom naming.             |
| Class [`OnOptimizeDialogReplace (OnOptimize)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/images.g.md#class-onoptimizedialogreplace)     | Optimize images in a selected folder and replace the originals.      |
| Class [`OnOptimizeQuality (OnOptimize)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/images.g.md#class-onoptimizequality)                 | Optimize images with higher quality settings.                        |
| Class [`OnOptimizeResizePngToAvif (OnOptimize)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/images.g.md#class-onoptimizeresizepngtoavif) | Resize and optimize images and convert PNG files to AVIF format too. |
| Class [`OnOptimizeSingleImage (OnOptimize)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/images.g.md#class-onoptimizesingleimage)         | Optimize a single image file.                                        |

### File `markdown.py`

Doc: [markdown.g.md](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/markdown.g.md)

| Function/Class                                                                                                                                                                | Description                                                                                    |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Class [`OnBeautifyMdFolder (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/markdown.g.md#class-onbeautifymdfolder)                                 | Apply comprehensive beautification to all Markdown notes.                                      |
| Class [`OnBeautifyMdFolderAndRegenerateGMd (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/markdown.g.md#class-onbeautifymdfolderandregenerategmd) | Apply comprehensive beautification to all Markdown notes.                                      |
| Class [`OnCheckMdFolder (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/markdown.g.md#class-oncheckmdfolder)                                       | Action to check all Markdown files in a folder for errors with Harrix rules.                   |
| Class [`OnDownloadAndReplaceImagesFolder (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/markdown.g.md#class-ondownloadandreplaceimagesfolder)     | Download remote images and replace URLs with local references in multiple Markdown files.      |
| Class [`OnGenerateShortNoteTocWithLinks (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/markdown.g.md#class-ongenerateshortnotetocwithlinks)       | Generate a condensed version of a document with only its table of contents.                    |
| Class [`OnGetListMoviesBooks (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/markdown.g.md#class-ongetlistmoviesbooks)                             | Extract and format a list of movies or books from Markdown content.                            |
| Class [`OnIncreaseHeadingLevelContent (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/markdown.g.md#class-onincreaseheadinglevelcontent)           | Increase the heading level of all headings in Markdown content.                                |
| Class [`OnNewArticle (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/markdown.g.md#class-onnewarticle)                                             | Create a new article with predefined template.                                                 |
| Class [`OnNewDiary (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/markdown.g.md#class-onnewdiary)                                                 | Create a new diary entry for the current date.                                                 |
| Class [`OnNewDiaryDream (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/markdown.g.md#class-onnewdiarydream)                                       | Create a new dream journal entry for the current date.                                         |
| Class [`OnNewNoteDialog (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/markdown.g.md#class-onnewnotedialog)                                       | Create a new general note with a user-specified filename.                                      |
| Class [`OnNewNoteDialogWithImages (OnNewNoteDialog)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/markdown.g.md#class-onnewnotedialogwithimages)              | Create a new general note with image support.                                                  |
| Class [`OnOptimizeImagesFolder (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/markdown.g.md#class-onoptimizeimagesfolder)                         | Optimize images in Markdown files with PNG/AVIF size comparison.                               |
| Class [`OnQuotesFormatAsMarkdownContent (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/markdown.g.md#class-onquotesformatasmarkdowncontent)       | Format plain text quotes into properly structured Markdown.                                    |
| Class [`OnQuotesGenerateAuthorAndBook (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/markdown.g.md#class-onquotesgenerateauthorandbook)           | Process quote files to add author and book information.                                        |
| Class [`OnSortSections (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/markdown.g.md#class-onsortsections)                                         | Organize and enhance a single Markdown file by sorting sections and generating image captions. |

### File `markdown_utils.py`

Doc: [markdown_utils.g.md](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/markdown_utils.g.md)

| Function/Class                                                                                                                                  | Description                                                             |
| ----------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| [`beautify_markdown_common`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/markdown_utils.g.md#function-beautify_markdown_common) | Perform common beautification operations on Markdown files in a folder. |

### File `python.py`

Doc: [python.g.md](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/python.g.md)

| Function/Class                                                                                                                                                                              | Description                                                                      |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Class [`OnCheckPythonFolder (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/python.g.md#class-oncheckpythonfolder)                                               | Action to check all Python files in a folder for errors with Harrix rules.       |
| Class [`OnNewUvProject (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/python.g.md#class-onnewuvproject)                                                         | Create a new Python project with uv package manager.                             |
| Class [`OnPublishPythonLibrary (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/python.g.md#class-onpublishpythonlibrary)                                         | Publish a new version of a Python library to PyPI and update dependent projects. |
| Class [`OnSortIsortFmtDocsPythonCodeFolder (ActionBase)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/python.g.md#class-onsortisortfmtdocspythoncodefolder)                 | Format, sort Python code and generate documentation in a selected folder.        |
| Class [`OnSortIsortFmtPythonCodeFolder (OnSortIsortFmtDocsPythonCodeFolder)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/python.g.md#class-onsortisortfmtpythoncodefolder) | Format and sort Python code in a selected folder using multiple tools.           |

### File `database_manager.py`

Doc: [database_manager.g.md](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/database_manager.g.md)

| Function/Class                                                                                                                     | Description                                                           |
| ---------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| Class [`DatabaseManager`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/database_manager.g.md#class-databasemanager) | Manage the connection and operations for a fitness tracking database. |
| [`_safe_identifier`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/database_manager.g.md#function-_safe_identifier)  | Return `identifier` unchanged if it is a valid SQL identifier.        |

### File `main.py`

Doc: [main.g.md](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/main.g.md)

| Function/Class                                                                                                                                                                                                                               | Description                                                   |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| Class [`MainWindow (QMainWindow, window.Ui_MainWindow, TableOperations, ChartOperations, DateOperations, AutoSaveOperations, ValidationOperations)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/main.g.md#class-mainwindow) | Main application window for the fitness tracking application. |

### File `mixins.py`

Doc: [mixins.g.md](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/mixins.g.md)

| Function/Class                                                                                                                     | Description                                                      |
| ---------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| Class [`AutoSaveOperations`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/mixins.g.md#class-autosaveoperations)     | Mixin class for auto-save operations.                            |
| Class [`ChartOperations`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/mixins.g.md#class-chartoperations)           | Mixin class for chart operations.                                |
| Class [`DateOperations`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/mixins.g.md#class-dateoperations)             | Mixin class for date operations.                                 |
| Class [`TableOperations`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/mixins.g.md#class-tableoperations)           | Mixin class for common table operations.                         |
| Class [`ValidationOperations`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/mixins.g.md#class-validationoperations) | Mixin class for validation operations.                           |
| [`requires_database`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/mixins.g.md#function-requires_database)          | Ensure database connection is available before executing method. |

### File `window.py`

Doc: [window.g.md](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/window.g.md)

| Function/Class                                                                                                                | Description |
| ----------------------------------------------------------------------------------------------------------------------------- | ----------- |
| Class [`Ui_MainWindow (object)`](https://github.com/Harrix/harrix-swiss-knife/tree/main/docs/window.g.md#class-ui_mainwindow) |             |

## Deploy on an empty machine (Windows)

### Prerequisites

Install the following software:

- Git
- Cursor or VSCode (with Python extensions)
- Node.js
- [uv](https://docs.astral.sh/uv/) ([Installing and Working with uv (Python) in VSCode](https://github.com/Harrix/harrix.dev-articles-2025-en/blob/main/uv-vscode-python/uv-vscode-python.md))

### Installation steps

1. Clone project:

   ```shell
   mkdir C:/GitHub
   cd C:/GitHub
   git clone https://github.com/Harrix/harrix-swiss-knife.git
   ```

2. Open the folder `C:/GitHub/harrix-swiss-knife` in Cursor (or VSCode).

3. Open a terminal `Ctrl` + `` ` ``.

4. Install dependencies (`uv sync --upgrade` is optional):

   ```shell
   uv sync
   uv sync --upgrade
   npm i
   npm i -g npm-check-updates prettier
   ```

   Alternatively, instead of the two previous commands, run `Dev` → `Install/Update global NPM packages`.

5. Download required executables:
   - **ffmpeg.exe**: Download from [FFmpeg Builds](https://github.com/BtbN/FFmpeg-Builds/releases) (e.g., `ffmpeg-master-latest-win64-gpl.zip`)
   - **libavif executables** (`avifdec.exe`, `avifenc.exe`): Download from [libavif releases](https://github.com/AOMediaCodec/libavif/releases) (e.g., `libavif-v1.3.0-windows-x64-dynamic.zip`)

   Copy all executables to the project folder `C:/GitHub/harrix-swiss-knife`.

6. Run the application:
   Open `src\harrix_swiss_knife\main.py` and run (or run `C:/GitHub/harrix-swiss-knife/.venv/Scripts/pythonw.exe C:/GitHub/harrix-swiss-knife/src/harrix_swiss_knife/main.py` in a terminal).

### Running from command line

After installation, you can run the script from terminal:

```shell
c:/GitHub/harrix-swiss-knife/.venv/Scripts/pythonw.exe c:/GitHub/harrix-swiss-knife/src/harrix_swiss_knife/main.py
```

## Development

<details>
<summary>Development ⬇️</summary>

### CLI commands

CLI commands after installation:

- `uv self update` — update uv itself.
- `uv sync --upgrade` — update all project libraries (sometimes you need to call twice).
- `ruff check` — lint the project's Python files.
- `ruff check --fix` — lint and fix the project's Python files.
- `pyside6-rcc src/harrix_swiss_knife/resources.qrc -o src/harrix_swiss_knife/resources_rc.py` — convert UI file to PY class.
- `isort .` — sort imports.
- `ruff format` — format the project's Python files.
- `uv python install 3.13` + `uv python pin 3.13` + `uv sync` — switch to a different Python version.
- `vermin src` — determine the minimum Python version using [vermin](https://github.com/netromdk/vermin). However, if the version is below 3.10, we stick with 3.10 because Python 3.10 annotations are used.

### Add a new action

- Add a new action `class On<action>(action_base.ActionBase)` in `src/harrix_swiss_knife/action_<section>.py`.
- Site for searching emojis: <https://emojidb.org/>.
- In `main.py` add action `self.add_items(...)`.
- From `harrix-swiss-knife`, call the command `Python` → `isort, ruff format, sort, make docs in PY files` and select the folder `harrix_swiss_knife`.

Example action:

```python
class OnCheckFeaturedImageInFolders(ActionBase):
    """Check for featured image files in all configured folders.

    This action automatically checks all directories specified in the
    paths_with_featured_image configuration setting for the presence of
    files named `featured_image` with any extension, providing a status
    report for each directory.
    """

    icon = "✅"
    title = "Check featured_image"

    @ActionBase.handle_exceptions("checking featured image in folders")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        for path in self.config["paths_with_featured_image"]:
            result = h.file.check_featured_image(path)[1]
            self.add_line(result)
        self.show_result()
```

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
    title = "Install/Update global NPM packages"

    @ActionBase.handle_exceptions("NPM package management")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
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

Example action with sequence of QThread:

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

### Add file to a resource file

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

</details>

## Create a shortcut

To create a desktop shortcut, use the following path:

```shell
C:/GitHub/harrix-swiss-knife/.venv/Scripts/pythonw.exe C:/GitHub/harrix-swiss-knife/src/harrix_swiss_knife/main.py
```

## License

License: [MIT](https://github.com/Harrix/harrix-swiss-knife/blob/main/LICENSE.md).
