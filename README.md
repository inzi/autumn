# 🍂 Autumn

Autumn watches your codebase and maintains an up-to-date markdown file containing all your project's source code. This file can be used to provide context to AI coding assistants, making them more effective at understanding and working with your codebase.

## Features

- 📝 Automatically maintains a markdown file with your project's source code
- 🔍 Respects `.gitignore` patterns
- ⚙️ Supports custom `.docignore` for additional filtering
- 🔄 Real-time updates as files change
- 🎯 Configurable file extensions and paths
- 📂 Optional file splitting by extension
- 🚀 Written in Python 3.11+ for modern performance

## Installation

Requires Python 3.11 or higher.

```bash
pip install autumn-ai
```

## Usage

### As a Command Line Tool

The simplest way to use Autumn is from the command line:

```bash
# Basic usage - watches current directory
autumn

# Watch a specific directory
autumn --path ./src

# Specify file extensions to watch
autumn --extensions "py,js,tsx"

# Custom output file
autumn --output docs/CONTEXT.md

# Split output into separate files by extension
autumn --split
```

Available options:
```
-p, --path PATH       Path to watch for changes (default: .)
-o, --output FILE     Output markdown file path (default: CODE_DOCUMENTATION.md)
-e, --extensions EXT  Comma-separated list of file extensions to watch (e.g., "py,js,ts")
--split              Split output into separate files by extension
--project            Create a project configuration file
--version           Show version number and exit
```

### As a Python Package

You can also use Autumn programmatically in your Python code:

```python
from autumn import run

# Basic usage
run()

# With custom configuration
run(
    path="./src",
    output="docs/CONTEXT.md",
    extensions=[".py", ".js", ".tsx"],
    split=True
)
```

For more control, you can use the `Autumn` class directly:

```python
from autumn import Autumn

# Initialize with custom settings
autumn = Autumn(
    watch_path="./src",
    output_file="docs/CONTEXT.md",
    extensions=[".py", ".js", ".tsx"],
    split_by_extension=True
)

# Generate documentation once without watching
autumn.update_documentation()
```

### Project Configuration

Autumn supports project-specific configurations using a `.autumn/project.autumn` file. Create one with:

```bash
autumn --project
```

This creates a `.autumn/project.autumn` file in YAML format:

```yaml
extensions:
  - .py
  - .js
  - .jsx
  - .ts
  - .tsx
  - .css
  - .scss
  - .html
  - .java
  - .cs
  - .go
  - .rs
  - .php
  - .sql
output_file: .autumn/CODE_DOCUMENTATION.md
watch_path: .
```

Once configured, Autumn will automatically use these settings. You can still override them with command-line arguments.

### Output Organization

By default, Autumn creates a single markdown file with all your source code. The file is structured like this:

```markdown
# Project Source Code Context

*Last updated: 2024-02-21T15:30:45.123456*

*This file is automatically maintained by Autumn.*

## Example: src/app.py

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"
```

## Example: src/components/Button.tsx

```typescript
export function Button({ label }: { label: string }) {
    return <button>{label}</button>;
}
```


When using the `--split` option, Autumn creates separate files for each extension (e.g., `CODE_DOCUMENTATION_py.md`, `CODE_DOCUMENTATION_ts.md`).

### Ignoring Files

Autumn respects two types of ignore files:

1. `.gitignore` - Standard Git ignore patterns
2. `.docignore` - Additional patterns specific to Autumn

Example `.docignore`:
```
# Ignore generated files
*.generated.ts
*.g.cs
build/
dist/

# Ignore test files
test/
**/*.test.ts
**/*.spec.py

# Ignore a documentation folder
docs/
```

### Note:
By default, Autumn also ignores:
- `.git/`
- `__pycache__/`
- `*.pyc`
- `node_modules/`
- `venv/`
- `.env`
- `.autumn/`

## Use with AI Assistants

The generated markdown files can be used to provide context to AI coding assistants:

1. **Claude**: Upload the generated markdown file when starting a conversation
2. **GitHub Copilot**: Reference the file in your workspace
3. **Other AI Assistants**: Copy relevant sections as needed

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Why the name?

Like autumn leaves falling and creating a colorful landscape, Autumn gently collects your source code into a beautiful markdown file. 🍂