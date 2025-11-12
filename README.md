# File Browser TUI

A modern, feature-rich terminal user interface (TUI) file browser built with Python and Textual. Navigate your filesystem with vim-like keybindings, preview files with syntax highlighting, and quickly find files with fuzzy search.

## Features

### Core Navigation
- **Vim-like keybindings** - Navigate with `j/k` or arrow keys
- **Two-pane layout** - File list and preview side-by-side
- **Quick parent navigation** - Press `h` to go up one directory
- **Hidden files toggle** - Show/hide dotfiles with `.`

### File Preview
- **Syntax highlighting** - Automatic language detection using Pygments
- **Smart preview** - Handles text files, binary files, and directories
- **Large file handling** - Automatic truncation for files >1MB or >1000 lines
- **Directory statistics** - Shows file and directory counts

### Information Display
- **File size** - Human-readable format (B, KB, MB, GB, TB)
- **Directory contents** - Real-time count of files and subdirectories
- **Unix permissions** - Display in rwxrwxrwx format

### Fuzzy Finding
- **Recursive search** - Find files anywhere in the current directory tree
- **Real-time filtering** - Results update as you type
- **Fuzzy matching** - Powered by rapidfuzz for intelligent string matching
- **Fast navigation** - Jump directly to any file or directory

### Theming
- **8 built-in themes** - Tokyo Night, Dracula, Nord, Catppuccin Mocha, Gruvbox Dark, Solarized Dark, One Dark, Monokai Pro
- **Live theme preview** - See themes change instantly as you navigate the settings
- **Custom theme support** - Import your own color schemes via `themes.json`

## Installation

### Prerequisites
- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended)

### Install with uv

```bash
# Clone the repository
git clone https://github.com/davidfic/file-browser-tui.git
cd file-browser-tui

# Install dependencies
uv sync

# Run the application
uv run python main.py
```

### Install with pip

```bash
# Clone the repository
git clone https://github.com/davidfic/file-browser-tui.git
cd file-browser-tui

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Usage

### Keybindings

| Key | Action |
|-----|--------|
| `j` / `Down` | Move selection down |
| `k` / `Up` | Move selection up |
| `l` / `Enter` | Enter directory or preview file |
| `h` | Go to parent directory |
| `.` | Toggle hidden files visibility |
| `Ctrl+F` | Open fuzzy finder |
| `/` | Show help dialog |
| `q` | Quit application |
| `Esc` | Close dialog |

### Fuzzy Finder

Press `Ctrl+F` to open the fuzzy finder:
1. Start typing to search recursively through all files
2. Use arrow keys to navigate results
3. Press `Enter` to select a file or directory
4. Press `Esc` to cancel

The fuzzy finder:
- Searches all files recursively from the current directory
- Skips hidden files and directories (starting with `.`)
- Shows up to 100 best matches
- Uses intelligent fuzzy matching (e.g., "mpy" matches "main.py")

## Custom Themes

You can create your own color schemes by editing the `themes.json` file in the project directory.

### Theme File Format

```json
{
  "custom_themes": [
    {
      "name": "my-theme",
      "display_name": "My Custom Theme",
      "primary": "#7aa2f7",
      "secondary": "#7dcfff",
      "warning": "#e0af68",
      "error": "#f7768e",
      "success": "#9ece6a",
      "accent": "#bb9af7",
      "background": "#1a1b26",
      "surface": "#24283b",
      "panel": "#1f2335",
      "dark": true
    }
  ]
}
```

### Theme Properties

- **name** (required) - Internal theme identifier (use kebab-case, e.g., "my-theme")
- **display_name** (optional) - Human-readable name shown in settings
- **primary** (required) - Primary accent color
- **secondary** (optional) - Secondary accent color
- **warning** (optional) - Warning state color
- **error** (optional) - Error state color
- **success** (optional) - Success state color
- **accent** (optional) - Accent color for highlights
- **background** (optional) - Main background color
- **surface** (optional) - Surface/card background color
- **panel** (optional) - Panel background color
- **dark** (optional) - Whether this is a dark theme (true/false)

All colors should be in hex format (e.g., "#1a1b26").

### Using Custom Themes

1. Edit `themes.json` and add your custom theme(s)
2. Run the application
3. Press `s` to open settings
4. Your custom themes will appear in the list alongside built-in themes
5. Navigate with arrow keys to preview, press Enter to apply

The application includes three example custom themes:
- **Forest Green** - Nature-inspired green palette
- **Ocean Blue** - Deep ocean blue palette
- **Sunset Orange** - Warm sunset orange palette

## Dependencies

- **[Textual](https://github.com/Textualize/textual)** (>=6.6.0) - TUI framework
- **[Pygments](https://pygments.org/)** (>=2.17.0) - Syntax highlighting
- **[rapidfuzz](https://github.com/maxbachmann/RapidFuzz)** (>=3.0.0) - Fuzzy string matching

## Development

### Project Structure

```
file-browser-tui/
  main.py              # Main application code
  themes.json          # Custom color scheme definitions
  test_themes.py       # Theme system tests
  pyproject.toml       # Project metadata and dependencies
  README.md            # This file
  TODO.md              # Future enhancements
  .gitignore           # Git ignore rules
  .claude/             # Claude Code configuration
    rules.yaml         # Coding standards and guidelines
    plans/             # Development plans (git-ignored)
  .python-version      # Python version specification
```

### Code Organization

The application is organized into several key components:

- **`HelpScreen`** - Modal dialog showing keybindings
- **`FuzzyFinderScreen`** - Fuzzy file finder with real-time search
- **`InfoBox`** - Reusable information display widget
- **`FileList`** - Directory listing with selection handling
- **`FilePreview`** - File content preview with syntax highlighting
- **`FileBrowserApp`** - Main application orchestrating all components

## Roadmap

See [TODO.md](TODO.md) for planned features and enhancements.

## License

MIT License - feel free to use and modify as needed.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Acknowledgments

- Built with [Textual](https://textual.textualize.io/) by Textualize
- Syntax highlighting by [Pygments](https://pygments.org/)
- Fuzzy matching by [RapidFuzz](https://github.com/maxbachmann/RapidFuzz)
