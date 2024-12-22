import sys
import argparse

if sys.version_info < (3, 11):
    raise RuntimeError("This script requires Python 3.11 or higher")

from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import yaml
from datetime import datetime
import pathspec
from typing import Set, List, Optional
from project_config import ProjectConfig, AutumnConfig


def parse_extensions(ext_string: str) -> List[str]:
    """Parse comma-separated extensions into a list, ensuring they start with dots."""
    if not ext_string:
        return []
    return [f".{ext.strip('.')}" for ext in ext_string.split(",") if ext.strip()]


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="🍂 Autumn - Maintain an AI-friendly markdown file of your project's source code",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("-p", "--path", default=".", help="Path to watch for changes")

    parser.add_argument("-o", "--output", help="Output markdown file path")

    parser.add_argument(
        "-e",
        "--extensions",
        help='Comma-separated list of file extensions to watch (e.g., "py,js,ts")',
    )

    parser.add_argument(
        "--project", action="store_true", help="Create a project configuration file"
    )

    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    parser.add_argument(
        "--split",
        action="store_true",
        help="Split output into separate files by extension",
    )

    return parser.parse_args()


# Autumn - AI Context File Generator
# Version: 0.1.0


class Autumn:
    """Autumn maintains an up-to-date markdown file of your project's source code.

    Autumn watches your codebase and automatically updates a markdown file containing
    all source code, making it perfect for providing context to AI coding assistants.
    It respects both .gitignore and .docignore patterns, allowing you to precisely
    control which code is included in the context file.
    """

    def __init__(
        self,
        watch_path: str = ".",
        output_file: str = "CONTEXT.md",
        extensions: Optional[List[str]] = None,
        split_by_extension: bool = False,
    ):
        self.watch_path = Path(watch_path).resolve()
        self.output_file = Path(output_file)
        self.split_by_extension = split_by_extension
        # Create parent directories if they don't exist
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

        self.extensions = extensions or [
            ".py",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".css",
            ".scss",
            ".html",
            ".java",
            ".cs",
            ".go",
            ".rs",
            ".php",
            ".sql",
        ]
        self.ignore_spec = self._load_ignore_patterns()
        self.observer = Observer()

    def _load_ignore_patterns(self) -> pathspec.PathSpec:
        patterns = []

        # Load .gitignore patterns
        gitignore = self.watch_path / ".gitignore"
        if gitignore.exists():
            patterns.extend(gitignore.read_text().splitlines())

        # Load .docignore patterns
        docignore = self.watch_path / ".docignore"
        if docignore.exists():
            patterns.extend(docignore.read_text().splitlines())

        # Add default patterns
        patterns.extend(
            [
                ".git/",
                "__pycache__/",
                "*.pyc",
                self.output_file.name,
                "node_modules/",
                "venv/",
                ".env",
                ".autumn/",
            ]
        )

        return pathspec.PathSpec.from_lines("gitwildmatch", patterns)

    def _should_process_file(self, file_path: Path) -> bool:
        if not file_path.is_file():
            return False

        relative_path = str(file_path.relative_to(self.watch_path))

        # Check if file matches ignore patterns
        if self.ignore_spec.match_file(relative_path):
            return False

        # Check if extension should be processed
        return file_path.suffix in self.extensions

    def _extract_frontmatter(self, content: str) -> tuple[dict, str]:
        """Extract YAML frontmatter from content if it exists."""
        if content.startswith("---\n"):
            try:
                # Find the closing '---'
                parts = content.split("\n---\n", 2)
                if len(parts) >= 2:
                    frontmatter = yaml.safe_load(parts[0].replace("---\n", ""))
                    content = parts[1]
                    return frontmatter, content
            except yaml.YAMLError:
                pass
        return {}, content

    def update_documentation(self):
        # Group files by extension
        files_by_extension = {}

        # Process all files
        for file_path in sorted(self.watch_path.rglob("*")):
            if not self._should_process_file(file_path):
                continue

            ext = file_path.suffix
            if ext not in files_by_extension:
                files_by_extension[ext] = []

            relative_path = file_path.relative_to(self.watch_path)
            content = file_path.read_text(encoding="utf-8")
            frontmatter, content = self._extract_frontmatter(content)

            files_by_extension[ext].append(
                {
                    "path": str(self.watch_path / relative_path),
                    "content": content,
                    "frontmatter": frontmatter,
                }
            )

        # Determine the output directory (for split files)
        output_dir = self.output_file.parent

        # Always create the combined file
        markdown = [
            "# Project Source Code Context\n",
            f"*Last updated: {datetime.now().isoformat()}*\n\n",
            "*This file is automatically maintained by Autumn.*\n\n",
        ]

        for ext in sorted(files_by_extension.keys()):
            for file_info in files_by_extension[ext]:
                markdown.append(f"## {file_info['path']}\n\n")
                if file_info["frontmatter"]:
                    markdown.append("### Metadata\n\n```yaml\n")
                    markdown.append(
                        yaml.dump(file_info["frontmatter"], default_flow_style=False)
                    )
                    markdown.append("```\n\n")

                markdown.append(f"```{ext[1:]}\n")
                markdown.append(file_info["content"])
                markdown.append("\n```\n\n")

        self.output_file.write_text("".join(markdown), encoding="utf-8")
        print(f"Documentation updated: {self.output_file}")

        # If split option is enabled, create additional files by extension
        if self.split_by_extension:
            for ext, files in files_by_extension.items():
                # Use the base name of the main output file for split files
                base_name = self.output_file.stem
                output_path = output_dir / f"{base_name}_{ext[1:]}.md"
                markdown = [
                    f"# {ext[1:].upper()} Files\n",
                    f"*Last updated: {datetime.now().isoformat()}*\n\n",
                    "*This file is automatically maintained by Autumn.*\n\n",
                ]

                for file_info in files:
                    markdown.append(f"## {file_info['path']}\n\n")
                    if file_info["frontmatter"]:
                        markdown.append("### Metadata\n\n```yaml\n")
                        markdown.append(
                            yaml.dump(
                                file_info["frontmatter"], default_flow_style=False
                            )
                        )
                        markdown.append("```\n\n")

                    markdown.append(f"```{ext[1:]}\n")
                    markdown.append(file_info["content"])
                    markdown.append("\n```\n\n")

                output_path.write_text("".join(markdown), encoding="utf-8")
                print(f"Documentation updated: {output_path}")


class AutumnEventHandler(FileSystemEventHandler):
    def __init__(self, autumn: Autumn):
        self.autumn = autumn

    def on_any_event(self, event):
        # Get the file path
        file_path = Path(event.src_path)

        # Ignore directory events and the documentation file itself
        if event.is_directory or file_path.name == self.autumn.output_file.name:
            return

        # Print the triggering file and event type
        event_type = event.event_type.capitalize()
        relative_path = file_path.relative_to(self.autumn.watch_path)
        print(f"\n🍂 {event_type} detected: {relative_path}")

        # If .docignore changed, reload ignore patterns and update all
        if file_path.name == ".docignore":
            self.autumn.ignore_spec = self.autumn._load_ignore_patterns()

        # Update documentation for any file event
        self.autumn.update_documentation()


def main():
    args = parse_args()

    print("🍂 Autumn Documentation Generator")
    print("Version 0.1.0\n")

    watch_path = Path(args.path)
    autumn_dir = watch_path / ".autumn"

    if args.project:
        # Create default configuration
        ProjectConfig.create_project(
            path=watch_path,
            extensions=[
                ".py",
                ".js",
                ".jsx",
                ".ts",
                ".tsx",
                ".css",
                ".scss",
                ".html",
                ".java",
                ".cs",
                ".go",
                ".rs",
                ".php",
                ".sql",
            ],
            output_file=autumn_dir / "CODE_DOCUMENTATION.md",
            watch_path=watch_path,
        )
        return

    # Check for project configuration
    config_file = ProjectConfig.find_config(watch_path)
    print(f"Config file: {config_file}")
    if config_file:
        print(f"Loading config from {config_file}")
        config = ProjectConfig.load_config(config_file)
        output_file = config.output_file  # Already resolved in AutumnConfig
        extensions = config.extensions
    else:
        # If no project config, use command line args or defaults
        output_file = AutumnConfig._resolve_output_path(
            args.output or "CODE_DOCUMENTATION.md", watch_path
        )
        extensions = parse_extensions(args.extensions) if args.extensions else None

    # Initialize Autumn with configuration
    autumn = Autumn(
        watch_path=args.path,
        output_file=output_file,
        extensions=extensions,
        split_by_extension=args.split,
    )

    # Create initial documentation
    autumn.update_documentation()

    # Set up file watching
    event_handler = AutumnEventHandler(autumn)
    autumn.observer.schedule(event_handler, str(autumn.watch_path), recursive=True)
    autumn.observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        autumn.observer.stop()

    autumn.observer.join()


if __name__ == "__main__":
    main()
