"""
Smriti Auto-Documenter

Automatically generates Markdown documentation for a project using the Smriti LLM.
"""

import os
import sys
import json
import asyncio
import aiohttp
from pathlib import Path
from typing import List, Dict, Optional

import yaml
from openapi_spec_validator import validate
from openapi_spec_validator.validation.exceptions import OpenAPIValidationError

class LLMClient:
    """Client for Smriti LLM API."""

    def __init__(self, base_url: str = "https://smriti.agsci.com/llm/v1"):
        self.base_url = base_url
        self.model = "qwen/qwen3-next-80b"  # Good balance of reason/code

    async def generate_docs(self, code: str, language: str) -> str:
        """Ask LLM to verify/explain code."""
        prompt = f"""You are a technical writer.
Create a Markdown documentation file for this {language} code.

Structure:
# [Module Name]

## Summary
[Brief description of purpose]

## Classes
[List classes with purpose]

## Functions
[List functions with args/returns]

## API Usage (If applicable)
If the code contains API Views (e.g., Django REST Framework, Flask, FastAPI):
- List the HTTP endpoints (e.g., `GET /users/`).
- Provide sample JSON request bodies for POST/PUT.
- Provide sample JSON response bodies.
- Include a `curl` example for the main operations.

CODE:
```{language}
{code}
```

Output ONLY the Markdown content. Do not include wrapping ```markdown blocks.
"""
        return await self._call_llm(prompt)

    async def generate_openapi_fragment(self, code: str) -> Optional[Dict]:
        """Ask LLM to extract OpenAPI paths/schemas."""
        prompt = f"""You are an API Architect.
Extract the OpenAPI 3.0 paths and schemas for the following code.
Return ONLY valid YAML.

Include:
- Paths (e.g., /users/{{id}})
- Methods (get, post, put, delete)
- Request bodies (application/json)
- Responses (200, 201, 400, etc.)
- Schemas for the data models used.
- Schemas for the data models used.
- 'title': A short, specific title for this API (e.g. "User Management API").
- 'description': A short summary of what this API module does.
- Security Schemes (if authentication is detected, e.g. Bearer, Basic). Add 'components: securitySchemes'.
- IMPORTANT: If a class/view has security (e.g. permission_classes), applying 'security: - SchemeName: []' to **EVERY** method (get, post, put, delete) in that path.

Example Output:
title: User Management API
description: User management API for creating and retrieving users.
paths:
  /users/:
    get:
      security:
        - BearerAuth: []
      summary: List users
    put:
      security:
        - BearerAuth: []
      summary: Update user
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer

CODE:
```python
{code}
```

Output ONLY the YAML content. Do not include markdown blocks or "openapi: 3.0.0". Start with "paths:" or "components:".
"""
        result = await self._call_llm(prompt)
        try:
            # Clean up potential markdown blocks
            if result.startswith("```yaml"):
                result = result[7:]
            if result.startswith("```"):
                result = result[3:]
            if result.endswith("```"):
                result = result[:-3]
            
            return yaml.safe_load(result)
        except Exception as e:
            print(f"⚠️ Failed to parse OpenAPI fragment: {e}")
            return None

    async def _call_llm(self, prompt: str) -> str:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.2
                    },
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    result = await response.json()
                    content = result['choices'][0]['message']['content']
                    
                    # Basic cleanup
                    if content.startswith("```markdown"):
                        content = content[11:]
                    elif content.startswith("```"): # fallback
                           if not "yaml" in content[:10]: # Don't strip if it's the inner yaml block 
                                content = content[3:]

                    if content.endswith("```"):
                        content = content[:-3]
                    return content.strip()
        except Exception as e:
            # print(f"Error calling LLM: {e}") # validation: allow silence or log
            return f"Error: {e}"


import hashlib

# ... imports ...

class AutoDoc:
    """Main documentation generator."""

    def __init__(self, source_dir: str):
        self.source_dir = Path(source_dir).resolve()
        self.docs_dir = self.source_dir / "docs"
        self.llm = LLMClient()
        # Clean name: /path/to/demo -> "Demo"
        self.project_name = self.source_dir.name.capitalize() 
        self.cache_file = self.docs_dir / ".autodoc_cache.json"
        self.cache = self._load_cache()

    async def run(self):
        """Run the documentation process."""
        print(f"🚀 Starting Auto-Documenter on {self.source_dir}")
        print(f"📦 Output directory: {self.docs_dir}\n")

        self.docs_dir.mkdir(exist_ok=True)
        
        # ... (scanning logic) ...


        files = self._scan_files()
        if not files:
            print("❌ No files found!")
            return

        print(f"Found {len(files)} files to document.\n")

        for file_path in files:
            await self._process_file(file_path)

        self._generate_index(files)
        self._save_cache()
        print("\n✅ Documentation complete!")

    def _scan_files(self) -> List[Path]:
        """Find source files, ignoring common trash."""
        found = []
        skip_dirs = {'.git', '__pycache__', 'vocab', 'venv', 'env', 'node_modules', 'docs'}
        
        for root, dirs, filenames in os.walk(self.source_dir):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for name in filenames:
                if name.endswith('.py'):
                    found.append(Path(root) / name)
        return found

    async def _process_file(self, file_path: Path):
        """Read code, generate docs, write markdown."""
        rel_path = file_path.relative_to(self.source_dir)
        print(f"📄 Processing {rel_path}...")

        try:
            code = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            print(f"   ⚠️ Read error: {e}")
            return

        # Hash check
        current_hash = self._calculate_md5(code)
        if str(rel_path) in self.cache and self.cache[str(rel_path)] == current_hash:
             print(f"   ⏭️  Skipping (unchanged)")
             return
        
        # ... logic continues below ...
        
        # Generate docs
        doc_content = await self.llm.generate_docs(code, "python")
        
        # Save cache on success
        self.cache[str(rel_path)] = current_hash

        # Determine output path
        # src/utils/foo.py -> docs/src/utils/foo.md
        out_path = self.docs_dir / rel_path.parent / (file_path.stem + ".md")
        out_path.parent.mkdir(parents=True, exist_ok=True)

        out_path.write_text(doc_content, encoding='utf-8')
        print(f"   ✨ Saved to {out_path.relative_to(self.source_dir)}")

        # Check for API-like content for OpenAPI
        if any(k in code for k in ["APIView", "route", "def get(", "def post("]):
             print(f"   🔍 Detecting API endpoints for OpenAPI...")
             fragment = await self.llm.generate_openapi_fragment(code)
             
             if fragment and "paths" in fragment:
                 # Wrap as valid standalone OpenAPI spec
                 spec = {
                     "openapi": "3.0.0",
                     "info": {
                         "title": fragment.get("title", f"{self.project_name} API's Documentation"),
                         "version": "1.0.0",
                         "description": fragment.get("description", f"Auto-generated spec for {file_path.name}")
                     },
                     "paths": fragment.get("paths", {}),
                     "components": fragment.get("components", {"schemas": {}})
                 }

                 # VALIDATION
                 try:
                     validate(spec)
                 except OpenAPIValidationError as e:
                     print(f"   ⚠️  OpenAPI Validation Error: {e}")
                     # Ensure we note it in the file? Or maybe append .invalid?
                     # For now, we print to stderr but still save, so user can debug.
                 except Exception as e:
                     print(f"   ⚠️  Validation Exception: {e}")

                 spec_path = self.docs_dir / rel_path.parent / (file_path.stem + ".yaml")
                 with open(spec_path, 'w') as f:
                     yaml.dump(spec, f, sort_keys=False)
                 print(f"   🌐 Generated spec: {spec_path.relative_to(self.source_dir)}")

                 # SWAGGER UI
                 html_content = self._create_swagger_html(spec)
                 html_path = self.docs_dir / rel_path.parent / (file_path.stem + ".html")
                 html_path.write_text(html_content, encoding='utf-8')
                 print(f"   🎨 Generated Swagger UI: {html_path.relative_to(self.source_dir)}")

    def _calculate_md5(self, content: str) -> str:
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def _load_cache(self) -> Dict:
        if self.cache_file.exists():
            try:
                return json.loads(self.cache_file.read_text())
            except:
                return {}
        return {}

    def _save_cache(self):
        self.cache_file.write_text(json.dumps(self.cache, indent=2))

    def _create_swagger_html(self, spec: Dict) -> str:
        """Generate standalone Swagger UI HTML."""
        spec_json = json.dumps(spec)
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{spec['info']['title']}</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui.css" />
    <style>
        body {{ margin: 0; padding: 0; }}
        #swagger-ui {{ max-width: 1460px; margin: 0 auto; }}
        /* Dark mode tweaks if needed, but default is clean */
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui-bundle.js" crossorigin></script>
    <script>
        window.onload = () => {{
            window.ui = SwaggerUIBundle({{
                spec: {spec_json},
                dom_id: '#swagger-ui',
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.SwaggerUIStandalonePreset
                ],
                layout: "BaseLayout",
                deepLinking: true,
                showExtensions: true,
                showCommonExtensions: true
            }});
        }};
    </script>
</body>
</html>
"""


    def _generate_index(self, files: List[Path]):
        """Create a master README."""
        index_path = self.docs_dir / "README.md"
        
        lines = ["# Project Documentation", "\nGenerated by Smriti Auto-Doc\n", "## Modules\n"]
        
        for f in sorted(files):
            rel_path = f.relative_to(self.source_dir)
            doc_rel = rel_path.parent / (f.stem + ".md")
            
            # Check if yaml/html exists
            yaml_path = self.docs_dir / rel_path.parent / (f.stem + ".yaml")
            html_path = self.docs_dir / rel_path.parent / (f.stem + ".html")
            
            links = []
            if yaml_path.exists():
                links.append(f"[OpenAPI]({f.stem}.yaml)")
            if html_path.exists():
                links.append(f"[Swagger UI]({f.stem}.html)")
            
            if links:
                lines.append(f"- [{rel_path}]({doc_rel}) ({' | '.join(links)})")
            else:
                lines.append(f"- [{rel_path}]({doc_rel})")

        index_path.write_text("\n".join(lines), encoding='utf-8')
        print(f"📚 Index generated at docs/README.md")



async def main():
    if len(sys.argv) < 2:
        target = "." 
    else:
        target = sys.argv[1]
    
    app = AutoDoc(target)
    await app.run()

if __name__ == "__main__":
    asyncio.run(main())
