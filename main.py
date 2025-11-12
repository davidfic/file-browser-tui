#!/usr/bin/env python3
"""A TUI file browser built with Textual."""

import os
from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Static, Header, Footer, Label, Input, ListView, ListItem, Markdown
from textual.screen import ModalScreen
from textual.message import Message
from rich.syntax import Syntax
from rich.table import Table
from rapidfuzz import fuzz, process


# Color scheme definitions
COLOR_SCHEMES = {
    "Tokyo Night": {
        "background": "#1a1b26",
        "surface": "#1f2335",
        "surface_light": "#24283b",
        "text": "#c0caf5",
        "blue": "#7aa2f7",
        "cyan": "#7dcfff",
        "green": "#9ece6a",
        "purple": "#9d7cd8",
        "purple_light": "#bb9af7",
        "pink": "#f7768e",
        "yellow": "#e0af68",
        "orange": "#ff9e64",
        "border": "#565f89",
    },
    "Dracula": {
        "background": "#282a36",
        "surface": "#21222c",
        "surface_light": "#343746",
        "text": "#f8f8f2",
        "blue": "#6272a4",
        "cyan": "#8be9fd",
        "green": "#50fa7b",
        "purple": "#bd93f9",
        "purple_light": "#bd93f9",
        "pink": "#ff79c6",
        "yellow": "#f1fa8c",
        "orange": "#ffb86c",
        "border": "#44475a",
    },
    "Nord": {
        "background": "#2e3440",
        "surface": "#3b4252",
        "surface_light": "#434c5e",
        "text": "#eceff4",
        "blue": "#5e81ac",
        "cyan": "#88c0d0",
        "green": "#a3be8c",
        "purple": "#b48ead",
        "purple_light": "#b48ead",
        "pink": "#d08770",
        "yellow": "#ebcb8b",
        "orange": "#d08770",
        "border": "#4c566a",
    },
    "Catppuccin Mocha": {
        "background": "#1e1e2e",
        "surface": "#181825",
        "surface_light": "#313244",
        "text": "#cdd6f4",
        "blue": "#89b4fa",
        "cyan": "#89dceb",
        "green": "#a6e3a1",
        "purple": "#cba6f7",
        "purple_light": "#f5c2e7",
        "pink": "#f5c2e7",
        "yellow": "#f9e2af",
        "orange": "#fab387",
        "border": "#45475a",
    },
    "Gruvbox Dark": {
        "background": "#282828",
        "surface": "#1d2021",
        "surface_light": "#3c3836",
        "text": "#ebdbb2",
        "blue": "#458588",
        "cyan": "#689d6a",
        "green": "#98971a",
        "purple": "#b16286",
        "purple_light": "#d3869b",
        "pink": "#d3869b",
        "yellow": "#d79921",
        "orange": "#d65d0e",
        "border": "#504945",
    },
    "Solarized Dark": {
        "background": "#002b36",
        "surface": "#073642",
        "surface_light": "#073642",
        "text": "#839496",
        "blue": "#268bd2",
        "cyan": "#2aa198",
        "green": "#859900",
        "purple": "#6c71c4",
        "purple_light": "#d33682",
        "pink": "#d33682",
        "yellow": "#b58900",
        "orange": "#cb4b16",
        "border": "#586e75",
    },
    "One Dark": {
        "background": "#282c34",
        "surface": "#21252b",
        "surface_light": "#2c313c",
        "text": "#abb2bf",
        "blue": "#61afef",
        "cyan": "#56b6c2",
        "green": "#98c379",
        "purple": "#c678dd",
        "purple_light": "#c678dd",
        "pink": "#e06c75",
        "yellow": "#e5c07b",
        "orange": "#d19a66",
        "border": "#3e4451",
    },
    "Monokai Pro": {
        "background": "#2d2a2e",
        "surface": "#221f22",
        "surface_light": "#403e41",
        "text": "#fcfcfa",
        "blue": "#78dce8",
        "cyan": "#78dce8",
        "green": "#a9dc76",
        "purple": "#ab9df2",
        "purple_light": "#ab9df2",
        "pink": "#ff6188",
        "yellow": "#ffd866",
        "orange": "#fc9867",
        "border": "#5b595c",
    },
}


class HelpScreen(ModalScreen[None]):
    """Modal screen showing keybindings help."""

    CSS = """
    HelpScreen {
        align: center middle;
        background: #00000099;
    }

    #help-dialog {
        width: 60;
        height: auto;
        max-height: 80%;
        border: thick #7dcfff;
        background: #1f2335;
        padding: 1 2;
    }

    #help-content {
        width: 100%;
        height: auto;
        color: #c0caf5;
    }

    #help-title {
        color: #7dcfff;
    }

    #help-footer {
        color: #565f89;
    }
    """

    BINDINGS = [
        ("escape", "dismiss", "Close"),
        ("q", "dismiss", "Close"),
        ("/", "dismiss", "Close"),
    ]

    def compose(self) -> ComposeResult:
        """Create the help dialog."""
        with Container(id="help-dialog"):
            yield Static("[bold cyan]File Browser Keybindings[/bold cyan]\n", id="help-title")

            # Create a table with keybindings
            table = Table(show_header=False, box=None, padding=(0, 2))
            table.add_column("Key", style="bold green")
            table.add_column("Action", style="white")

            table.add_row("j / Down", "Move selection down")
            table.add_row("k / Up", "Move selection up")
            table.add_row("l / Enter", "Enter directory or select file")
            table.add_row("h", "Go back to parent directory")
            table.add_row(".", "Toggle hidden files")
            table.add_row("Ctrl+F", "Fuzzy find files")
            table.add_row("s", "Settings (change color scheme)")
            table.add_row("/", "Show this help")
            table.add_row("q", "Quit application")
            table.add_row("Esc", "Close this dialog")

            yield Static(table, id="help-content")
            yield Static("\n[dim]Press Esc, q, or / to close[/dim]", id="help-footer")

    def on_mount(self) -> None:
        """Focus the dialog when mounted."""
        pass


class SettingsScreen(ModalScreen[str | None]):
    """Modal screen for settings and color scheme selection."""

    CSS = """
    SettingsScreen {
        align: center middle;
        background: #00000099;
    }

    #settings-dialog {
        width: 70;
        height: auto;
        max-height: 80%;
        border: thick #7dcfff;
        background: #1f2335;
        padding: 1 2;
    }

    #settings-title {
        color: #7dcfff;
        text-align: center;
        margin-bottom: 1;
    }

    #settings-list {
        height: auto;
        max-height: 30;
        background: #24283b;
        border: round #565f89;
        padding: 1;
    }

    #settings-footer {
        color: #565f89;
        text-align: center;
        margin-top: 1;
    }
    """

    BINDINGS = [
        ("escape", "dismiss_settings", "Close"),
        ("q", "dismiss_settings", "Close"),
    ]

    def __init__(self, current_scheme: str):
        super().__init__()
        self.current_scheme = current_scheme
        self.selected_index = 0
        self.schemes = list(COLOR_SCHEMES.keys())
        # Find current scheme index
        try:
            self.selected_index = self.schemes.index(current_scheme)
        except ValueError:
            self.selected_index = 0

    def compose(self) -> ComposeResult:
        """Create the settings dialog."""
        with Container(id="settings-dialog"):
            yield Static("[bold cyan]Settings - Color Schemes[/bold cyan]", id="settings-title")
            yield ListView(id="settings-list")
            yield Static("\n[dim]Use ↑/↓ to navigate, Enter to select, Esc/q to close[/dim]", id="settings-footer")

    def on_mount(self) -> None:
        """Populate the list when mounted."""
        list_view = self.query_one("#settings-list", ListView)

        for i, scheme_name in enumerate(self.schemes):
            if i == self.selected_index:
                label = Label(f"▸ [bold cyan]{scheme_name}[/bold cyan]  [dim](current)[/dim]")
            else:
                label = Label(f"  {scheme_name}")
            list_view.append(ListItem(label))

        list_view.index = self.selected_index

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle scheme selection."""
        if event.list_view.index is not None:
            selected_scheme = self.schemes[event.list_view.index]
            self.dismiss(selected_scheme)

    def action_dismiss_settings(self) -> None:
        """Dismiss the settings without selection."""
        self.dismiss(None)


class FuzzyFinderScreen(ModalScreen[Path | None]):
    """Modal screen for fuzzy finding files."""

    CSS = """
    FuzzyFinderScreen {
        align: center middle;
        background: #00000099;
    }

    #fuzzy-dialog {
        width: 80;
        height: 30;
        border: thick #f7768e;
        background: #1f2335;
    }

    #fuzzy-input {
        dock: top;
        width: 100%;
        margin: 1;
        background: #24283b;
        border: round #565f89;
        color: #c0caf5;
    }

    #fuzzy-input:focus {
        border: round #7aa2f7;
    }

    #fuzzy-results {
        height: 1fr;
        width: 100%;
        margin: 0 1 1 1;
        background: #1f2335;
        scrollbar-color: #565f89;
        scrollbar-color-hover: #7aa2f7;
    }

    #fuzzy-results > ListItem {
        background: #1f2335;
        color: #c0caf5;
    }

    #fuzzy-results > ListItem:hover {
        background: #292e42;
    }
    """

    BINDINGS = [
        ("escape", "dismiss_finder", "Close"),
        ("ctrl+c", "dismiss_finder", "Close"),
    ]

    def __init__(self, current_path: Path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_path = current_path
        self.all_files: list[Path] = []
        self.filtered_files: list[Path] = []

    def compose(self) -> ComposeResult:
        """Create the fuzzy finder dialog."""
        with Container(id="fuzzy-dialog"):
            yield Input(placeholder="Type to search files...", id="fuzzy-input")
            yield ListView(id="fuzzy-results")

    def on_mount(self) -> None:
        """Collect all files and focus input when mounted."""
        self.collect_files()
        self.query_one(Input).focus()
        self.update_results("")

    def collect_files(self) -> None:
        """Recursively collect all files from current directory."""
        try:
            # Use rglob to recursively find all files
            self.all_files = []
            for path in self.current_path.rglob("*"):
                # Skip hidden files and directories
                if any(part.startswith('.') for part in path.parts):
                    continue
                self.all_files.append(path)

            # Sort by name
            self.all_files.sort(key=lambda x: x.name.lower())
        except PermissionError:
            self.all_files = []

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes and update filtered results."""
        self.update_results(event.value)

    def update_results(self, query: str) -> None:
        """Update the results list based on fuzzy matching."""
        results_list = self.query_one(ListView)
        results_list.clear()

        if not query:
            # Show all files if no query
            self.filtered_files = self.all_files[:100]  # Limit to first 100
        else:
            # Create a mapping of string paths to Path objects for fuzzy matching
            path_strings = {}
            for path in self.all_files:
                try:
                    rel_path_str = str(path.relative_to(self.current_path))
                except ValueError:
                    rel_path_str = str(path)
                path_strings[rel_path_str] = path

            # Use rapidfuzz to find matches
            matches = process.extract(
                query,
                path_strings.keys(),
                scorer=fuzz.WRatio,
                limit=100
            )
            self.filtered_files = [path_strings[match[0]] for match in matches]

        # Add results to ListView
        for file_path in self.filtered_files:
            try:
                rel_path = file_path.relative_to(self.current_path)
                path_str = str(rel_path)
            except ValueError:
                path_str = str(file_path)

            # Add prefix based on type
            if file_path.is_dir():
                prefix = "▸"
                label = f" {prefix} [bold #7dcfff]{path_str}/[/bold #7dcfff]"
            else:
                suffix = file_path.suffix.lower()
                if suffix in ['.py']:
                    prefix = "[#7dcfff]●[/#7dcfff]"
                elif suffix in ['.js', '.ts', '.jsx', '.tsx']:
                    prefix = "[#e0af68]●[/#e0af68]"
                elif suffix in ['.md', '.txt', '.rst']:
                    prefix = "[#9ece6a]●[/#9ece6a]"
                elif suffix in ['.json', '.yaml', '.yml', '.toml']:
                    prefix = "[#bb9af7]●[/#bb9af7]"
                elif suffix in ['.jpg', '.jpeg', '.png', '.gif', '.svg']:
                    prefix = "[#f7768e]●[/#f7768e]"
                elif suffix in ['.zip', '.tar', '.gz', '.bz2']:
                    prefix = "[#ff9e64]●[/#ff9e64]"
                else:
                    prefix = "·"
                label = f" {prefix} [#c0caf5]{path_str}[/#c0caf5]"

            results_list.append(ListItem(Label(label)))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle file selection."""
        if event.list_view.index is not None and event.list_view.index < len(self.filtered_files):
            selected_path = self.filtered_files[event.list_view.index]
            self.dismiss(selected_path)

    def action_dismiss_finder(self) -> None:
        """Dismiss the finder without selection."""
        self.dismiss(None)


class InfoBox(Static):
    """A styled box for displaying information."""

    def __init__(self, title: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title
        self.border_title = title

    def update_content(self, content: str):
        """Update the content of the info box."""
        self.update(content)


class FileList(Static):
    """Widget to display the list of files and directories."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_path = Path.cwd()
        self.selected_index = 0
        self.show_hidden = False
        self.entries = []

    def on_mount(self):
        """Initialize the file list when mounted."""
        self.border_title = "Files"
        self.refresh_list()

    def refresh_list(self):
        """Refresh the file list based on current directory."""
        try:
            entries = list(self.current_path.iterdir())

            # Filter hidden files if needed
            if not self.show_hidden:
                entries = [e for e in entries if not e.name.startswith('.')]

            # Sort: directories first, then files, alphabetically
            entries.sort(key=lambda x: (not x.is_dir(), x.name.lower()))

            # Always add parent directory at the top if not at root
            if self.current_path != self.current_path.parent:
                self.entries = [self.current_path.parent] + entries
            else:
                self.entries = entries

            self.selected_index = 0
            self.render_list()
        except PermissionError:
            self.update("[red]Permission denied[/red]")

    def render_list(self):
        """Render the file list with selection highlight."""
        lines = []
        for i, entry in enumerate(self.entries):
            # Determine the display name
            if i == 0 and entry == self.current_path.parent:
                name = ".."
                prefix = "[dim]◄[/dim]"
            else:
                name = entry.name
                # Add prefix based on type
                if entry.is_dir():
                    prefix = "▸"
                else:
                    # Add file type prefixes
                    suffix = entry.suffix.lower()
                    if suffix in ['.py']:
                        prefix = "[#7dcfff]●[/#7dcfff]"
                    elif suffix in ['.js', '.ts', '.jsx', '.tsx']:
                        prefix = "[#e0af68]●[/#e0af68]"
                    elif suffix in ['.md', '.txt', '.rst']:
                        prefix = "[#9ece6a]●[/#9ece6a]"
                    elif suffix in ['.json', '.yaml', '.yml', '.toml']:
                        prefix = "[#bb9af7]●[/#bb9af7]"
                    elif suffix in ['.jpg', '.jpeg', '.png', '.gif', '.svg']:
                        prefix = "[#f7768e]●[/#f7768e]"
                    elif suffix in ['.zip', '.tar', '.gz', '.bz2']:
                        prefix = "[#ff9e64]●[/#ff9e64]"
                    else:
                        prefix = "·"

            # Color based on type
            if entry.is_dir():
                colored_name = f"[bold #7dcfff]{name}/[/bold #7dcfff]"
            else:
                colored_name = f"[#c0caf5]{name}[/#c0caf5]"

            # Highlight selected item
            if i == self.selected_index:
                lines.append(f"[reverse] {prefix} {colored_name} [/reverse]")
            else:
                lines.append(f" {prefix} {colored_name}")

        self.update("\n".join(lines))

    def get_selected_entry(self):
        """Get the currently selected path."""
        if 0 <= self.selected_index < len(self.entries):
            return self.entries[self.selected_index]
        return None

    def move_selection_up(self):
        """Move selection up one item."""
        if self.selected_index > 0:
            self.selected_index -= 1
            self.render_list()
            return True
        return False

    def move_selection_down(self):
        """Move selection down one item."""
        if self.selected_index < len(self.entries) - 1:
            self.selected_index += 1
            self.render_list()
            return True
        return False

    def enter_selected(self):
        """Enter the selected directory or preview file."""
        selected = self.get_selected_entry()
        if selected and selected.is_dir():
            self.current_path = selected
            self.refresh_list()
            return True
        return False

    def toggle_hidden_files(self):
        """Toggle showing hidden files."""
        self.show_hidden = not self.show_hidden
        self.refresh_list()


class FilePreview(Static):
    """Widget to display file preview."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_mount(self):
        """Initialize the preview pane when mounted."""
        self.border_title = "Preview"
        self.update("[dim]No file selected[/dim]")

    def preview_file(self, path: Path):
        """Preview the contents of a file."""
        if not path.exists():
            self.update("[red]File not found[/red]")
            return

        if path.is_dir():
            # Show directory contents count
            try:
                entries = list(path.iterdir())
                dir_count = sum(1 for e in entries if e.is_dir())
                file_count = len(entries) - dir_count
                self.update(f"[dim]Directory[/dim]\n\n{dir_count} directories\n{file_count} files")
            except PermissionError:
                self.update("[dim]Directory[/dim]\n\n[red]Permission denied[/red]")
            return

        try:
            # Get file size
            file_size = path.stat().st_size

            # If file is too large, show warning
            if file_size > 1_000_000:  # 1MB
                self.update(f"[yellow]File too large to preview[/yellow]\n\nSize: {self._format_size(file_size)}")
                return

            # Try to read as text
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                # Limit to first 1000 lines
                lines = []
                for i, line in enumerate(f):
                    if i >= 1000:
                        lines.append("\n[dim]... (preview truncated)[/dim]")
                        break
                    lines.append(line.rstrip('\n'))
                content = '\n'.join(lines)

                if not content:
                    self.update("[dim]Empty file[/dim]")
                    return

                # Get file extension for syntax detection
                suffix = path.suffix.lstrip('.').lower()

                # Render markdown files with Textual's Markdown widget
                if suffix in ['md', 'markdown']:
                    try:
                        # Create a Markdown widget inline
                        from rich.markdown import Markdown as RichMarkdown
                        md = RichMarkdown(content)
                        self.update(md)
                    except Exception:
                        # Fallback to plain text if markdown rendering fails
                        self.update(content)
                else:
                    # Try to apply syntax highlighting using Rich
                    try:
                        if suffix:
                            syntax = Syntax(content, suffix, theme="monokai", line_numbers=False)
                            self.update(syntax)
                        else:
                            # No extension, display as plain text
                            self.update(content)
                    except Exception:
                        # If syntax highlighting fails, display as plain text
                        self.update(content)
        except UnicodeDecodeError:
            self.update(f"[yellow]Binary file[/yellow]\n\nSize: {self._format_size(file_size)}")
        except PermissionError:
            self.update("[red]Permission denied[/red]")
        except Exception as e:
            self.update(f"[red]Error: {str(e)}[/red]")

    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


class FileBrowserApp(App):
    """A Textual file browser application."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("/", "show_help", "Help"),
        ("s", "show_settings", "Settings"),
        ("ctrl+f", "fuzzy_find", "Fuzzy Find"),
        ("j", "move_down", "Down"),
        ("k", "move_up", "Up"),
        ("down", "move_down", "Down"),
        ("up", "move_up", "Up"),
        ("enter", "select", "Select/Enter"),
        ("l", "select", "Select/Enter"),
        ("h", "go_back", "Back"),
        (".", "toggle_hidden", "Toggle Hidden"),
    ]

    def __init__(self):
        super().__init__()
        self.current_scheme = "Tokyo Night"

    def get_css(self, scheme_name: str) -> str:
        """Generate CSS based on the selected color scheme."""
        colors = COLOR_SCHEMES[scheme_name]
        return f"""
    Screen {{
        background: {colors['background']};
    }}

    /* Shared scrollbar styling */
    Static {{
        scrollbar-color: {colors['border']};
        scrollbar-color-hover: {colors['blue']};
    }}

    /* Horizontal container spacing */
    Horizontal {{
        width: 100%;
        height: 100%;
    }}

    #info-container {{
        height: 5;
        dock: top;
        background: {colors['background']};
    }}

    #info-container Horizontal {{
        padding: 0 1;
    }}

    InfoBox {{
        border: round {colors['border']};
        background: {colors['surface_light']};
        height: 100%;
        width: 1fr;
        padding: 0 1;
        margin: 0 0 0 1;
        color: {colors['text']};
        content-align: center middle;
    }}

    InfoBox:first-child {{
        margin-left: 0;
    }}

    #dir-size {{
        border: round {colors['blue']};
    }}

    #file-size {{
        border: round {colors['green']};
    }}

    #permissions {{
        border: round {colors['pink']};
    }}

    #main-container {{
        height: 1fr;
        background: {colors['background']};
    }}

    #main-container Horizontal {{
        padding: 0 1;
    }}

    FileList {{
        border: round {colors['cyan']};
        background: {colors['surface']};
        width: 1fr;
        padding: 0 1;
        margin: 0 1 0 0;
    }}

    FilePreview {{
        border: round {colors['purple_light']};
        background: {colors['surface']};
        width: 2fr;
        padding: 0 1;
        margin: 0;
    }}
    """

    @property
    def CSS(self) -> str:
        """Return the CSS for the current color scheme."""
        return self.get_css(self.current_scheme)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()

        # Info boxes at the top
        with Container(id="info-container"):
            with Horizontal():
                yield InfoBox("Directory Size", id="dir-size")
                yield InfoBox("File Size", id="file-size")
                yield InfoBox("Permissions", id="permissions")

        # Main content area
        with Container(id="main-container"):
            with Horizontal():
                yield FileList(id="file-list")
                yield FilePreview(id="file-preview")

        yield Footer()

    def on_mount(self):
        """Initialize the app when mounted."""
        self.update_preview()
        self.update_info_boxes()

    def update_info_boxes(self):
        """Update the information in the top boxes."""
        file_list = self.query_one(FileList)
        selected = file_list.get_selected_entry()

        if not selected:
            self.query_one("#dir-size", InfoBox).update_content("N/A")
            self.query_one("#file-size", InfoBox).update_content("N/A")
            self.query_one("#permissions", InfoBox).update_content("N/A")
            return

        try:
            # Get file/directory info
            stat_info = selected.stat()

            # Directory size (count of items)
            if selected.is_dir():
                try:
                    entries = list(selected.iterdir())
                    dir_count = sum(1 for e in entries if e.is_dir())
                    file_count = len(entries) - dir_count
                    self.query_one("#dir-size", InfoBox).update_content(
                        f"{dir_count} dirs, {file_count} files"
                    )
                    self.query_one("#file-size", InfoBox).update_content("Directory")
                except PermissionError:
                    self.query_one("#dir-size", InfoBox).update_content("Permission denied")
                    self.query_one("#file-size", InfoBox).update_content("N/A")
            else:
                # Show current directory info
                try:
                    parent_entries = list(file_list.current_path.iterdir())
                    dir_count = sum(1 for e in parent_entries if e.is_dir())
                    file_count = len(parent_entries) - dir_count
                    self.query_one("#dir-size", InfoBox).update_content(
                        f"{dir_count} dirs, {file_count} files"
                    )
                except PermissionError:
                    self.query_one("#dir-size", InfoBox).update_content("Permission denied")

                # File size
                size = stat_info.st_size
                self.query_one("#file-size", InfoBox).update_content(
                    self._format_size(size)
                )

            # Permissions
            mode = stat_info.st_mode
            perms = []
            perms.append('r' if mode & 0o400 else '-')
            perms.append('w' if mode & 0o200 else '-')
            perms.append('x' if mode & 0o100 else '-')
            perms.append('r' if mode & 0o040 else '-')
            perms.append('w' if mode & 0o020 else '-')
            perms.append('x' if mode & 0o010 else '-')
            perms.append('r' if mode & 0o004 else '-')
            perms.append('w' if mode & 0o002 else '-')
            perms.append('x' if mode & 0o001 else '-')
            self.query_one("#permissions", InfoBox).update_content(''.join(perms))

        except Exception as e:
            self.query_one("#dir-size", InfoBox).update_content("Error")
            self.query_one("#file-size", InfoBox).update_content("Error")
            self.query_one("#permissions", InfoBox).update_content("Error")

    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def action_show_help(self):
        """Show help dialog."""
        self.push_screen(HelpScreen())

    def action_show_settings(self):
        """Show settings dialog."""
        self.push_screen(SettingsScreen(self.current_scheme), self.handle_scheme_change)

    def handle_scheme_change(self, selected_scheme: str | None):
        """Handle color scheme selection."""
        if selected_scheme is None or selected_scheme == self.current_scheme:
            return

        self.current_scheme = selected_scheme
        # Refresh by updating the CSS property and reparsing
        self.stylesheet.parse(self.get_css(selected_scheme))
        self.refresh(layout=True)

    def action_fuzzy_find(self):
        """Show fuzzy finder dialog."""
        file_list = self.query_one(FileList)
        self.push_screen(FuzzyFinderScreen(file_list.current_path), self.handle_fuzzy_selection)

    def handle_fuzzy_selection(self, selected_path: Path | None):
        """Handle the result from fuzzy finder."""
        if selected_path is None:
            return

        file_list = self.query_one(FileList)

        if selected_path.is_dir():
            # Navigate to the directory
            file_list.current_path = selected_path
            file_list.refresh_list()
        else:
            # Navigate to the parent directory and select the file
            file_list.current_path = selected_path.parent
            file_list.refresh_list()
            # Find and select the file in the list
            try:
                file_index = file_list.entries.index(selected_path)
                file_list.selected_index = file_index
                file_list.render_list()
            except (ValueError, IndexError):
                pass

        self.update_preview()
        self.update_info_boxes()

    def action_move_down(self):
        """Move selection down in file list."""
        file_list = self.query_one(FileList)
        if file_list.move_selection_down():
            self.update_preview()
            self.update_info_boxes()

    def action_move_up(self):
        """Move selection up in file list."""
        file_list = self.query_one(FileList)
        if file_list.move_selection_up():
            self.update_preview()
            self.update_info_boxes()

    def action_select(self):
        """Select/enter the current item."""
        file_list = self.query_one(FileList)
        if file_list.enter_selected():
            # Entered a directory
            self.update_preview()
            self.update_info_boxes()
        else:
            # It's a file, just update preview
            self.update_preview()
            self.update_info_boxes()

    def action_go_back(self):
        """Go back to parent directory."""
        file_list = self.query_one(FileList)
        if file_list.current_path != file_list.current_path.parent:
            file_list.current_path = file_list.current_path.parent
            file_list.refresh_list()
            self.update_preview()
            self.update_info_boxes()

    def action_toggle_hidden(self):
        """Toggle showing hidden files."""
        file_list = self.query_one(FileList)
        file_list.toggle_hidden_files()
        self.update_preview()
        self.update_info_boxes()

    def update_preview(self):
        """Update the preview pane with the selected file."""
        file_list = self.query_one(FileList)
        file_preview = self.query_one(FilePreview)
        selected = file_list.get_selected_entry()

        if selected:
            file_preview.preview_file(selected)
        else:
            file_preview.update("[dim]No file selected[/dim]")


def main():
    """Run the file browser application."""
    app = FileBrowserApp()
    app.run()


if __name__ == "__main__":
    main()
