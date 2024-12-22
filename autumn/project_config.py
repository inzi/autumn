from pathlib import Path
import yaml
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class AutumnConfig:
    extensions: list[str]
    output_file: Path
    watch_path: Path

    @classmethod
    def from_dict(cls, data: Dict[str, Any], base_path: Path) -> "AutumnConfig":
        """Create config from dictionary, resolving paths relative to base_path."""
        watch_path = base_path / data.get("watch_path", ".")
        output_file = cls._resolve_output_path(
            output_arg=data.get("output_file", "CODE_DOCUMENTATION.md"),
            watch_path=watch_path,
        )
        return cls(
            extensions=data.get("extensions", []),
            output_file=output_file,
            watch_path=watch_path,
        )

    @staticmethod
    def _resolve_output_path(output_arg: str, watch_path: Path) -> Path:
        """Resolve the output path according to .autumn directory rules."""
        # If output includes a path separator, use it as-is
        if "/" in output_arg or "\\" in output_arg:
            print(f"Using provided path: {output_arg}")
            return Path(output_arg)

        # Get just the filename part
        output_name = Path(output_arg).name

        # If .autumn exists in watch_path, always use it unless path was specified
        autumn_dir = watch_path / ".autumn"
        if autumn_dir.exists():
            print(f"Using .autumn directory: {autumn_dir}")
            return autumn_dir / output_name

        # Fallback to watch_path if no .autumn directory
        print(f"Using watch_path: {watch_path}")
        return watch_path / output_name

    def to_dict(self, base_path: Path) -> Dict[str, Any]:
        """Convert config to dictionary with paths relative to base_path."""
        return {
            "extensions": self.extensions,
            "output_file": str(self.output_file.relative_to(base_path)),
            "watch_path": str(self.watch_path.relative_to(base_path)),
        }


class ProjectConfig:
    """Handles Autumn project configuration files."""

    CONFIG_DIR = ".autumn"
    CONFIG_FILE = "project.autumn"

    @classmethod
    def find_config(cls, start_path: Path) -> Optional[Path]:
        """Search for .autumn/project.autumn file in start_path and its parents."""
        current = start_path.absolute()
        while True:
            config_path = current / cls.CONFIG_DIR / cls.CONFIG_FILE
            if config_path.exists():
                return config_path
            if current.parent == current:  # Reached root
                return None
            current = current.parent

    @classmethod
    def save_config(
        cls, path: Path, extensions: list[str], output_file: Path, watch_path: Path
    ) -> None:
        """Save project configuration."""
        config_dir = path / cls.CONFIG_DIR
        config_dir.mkdir(exist_ok=True)

        config = AutumnConfig(
            extensions=extensions, output_file=output_file, watch_path=watch_path
        )

        with open(config_dir / cls.CONFIG_FILE, "w") as f:
            yaml.dump(config.to_dict(path), f, default_flow_style=False)

    @classmethod
    def load_config(cls, config_path: Path) -> AutumnConfig:
        """Load project configuration."""
        with open(config_path, "r") as f:
            data = yaml.safe_load(f)

        return AutumnConfig.from_dict(data, config_path.parent.parent)

    @classmethod
    def create_project(
        cls, path: Path, extensions: list[str], output_file: Path, watch_path: Path
    ) -> None:
        """Create a new Autumn project configuration."""
        # Ensure all paths are absolute before saving
        abs_path = path.absolute()
        abs_output = output_file.absolute()
        abs_watch = watch_path.absolute()

        # Save the configuration
        cls.save_config(abs_path, extensions, abs_output, abs_watch)

        print(f"Created Autumn project configuration in {abs_path / cls.CONFIG_DIR}")
