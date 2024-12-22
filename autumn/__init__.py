"""
🍂 Autumn - AI Context File Generator
Maintains an up-to-date markdown file of your project's source code.
"""

from pathlib import Path
from typing import List, Optional

from .autumn import Autumn, main, parse_extensions, AutumnEventHandler
from .project_config import ProjectConfig, AutumnConfig

__version__ = "0.1.0"

__all__ = [
    "Autumn",
    "ProjectConfig",
    "AutumnConfig",
    "parse_extensions",
    "main",
    "__version__",
]

def run(
    path: str = ".",
    output: Optional[str] = None,
    extensions: Optional[List[str]] = None,
    split: bool = False,
) -> None:
    """
    Convenience function to run Autumn with the specified configuration.
    
    Args:
        path: Directory to watch for changes
        output: Output markdown file path
        extensions: List of file extensions to watch
        split: Whether to split output into separate files by extension
    """
    autumn = Autumn(
        watch_path=path,
        output_file=output or "CODE_DOCUMENTATION.md",
        extensions=extensions,
        split_by_extension=split
    )
    
    # Create initial documentation
    autumn.update_documentation()
    
    # Set up file watching
    from watchdog.observers import Observer
    
    event_handler = AutumnEventHandler(autumn)
    observer = Observer()
    observer.schedule(event_handler, str(autumn.watch_path), recursive=True)
    observer.start()
    
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        
    observer.join()