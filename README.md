# Smriti AutoDoc

An intelligent, AI-powered documentation generator for Python projects.

Smriti AutoDoc goes beyond simple docstrings. It analyzes your source code using an LLM to generate:
- 📝 **Comprehensive Markdown** documentation.
- 🌐 **OpenAPI 3.0 Specifications** (`.yaml`) for API modules.
- 🎨 **Interactive Swagger UI** (`.html`) for instant API testing.
- 🧠 **Dynamic Metadata**, including meaningful titles and summaries.
- 🛡️ **Security Detection**, automatically identifying protected endpoints.

## Features

- **Smart Caching**: Uses MD5 hashing to skip unchanged files, saving time and API costs.
- **Production Ready**: Generated OpenAPI specs are validated against the standard schema.
- **Visual**: Standalone Swagger UI files let you view APIs in any browser without a server.
- **Secure**: Automatically detects authentication (e.g., Bearer tokens) and applies security schemes.

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd smriti_autodoc
   ```

2. **Set up a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the auto-documenter on any directory:

```bash
python src/autodoc.py <path_to_source_code>
```

### Example

To run the included demo:

```bash
python src/autodoc.py demo
```

This will generate a `docs/` folder inside `demo/` containing:
- `README.md`: Index of all documented modules.
- `user_view.md`: Markdown documentation.
- `user_view.yaml`: OpenAPI Specification.
- `user_view.html`: Interactive Swagger UI.

## Testing

Run the test suite to verify functionality:

```bash
PYTHONPATH=. pytest tests/test_autodoc.py
```
