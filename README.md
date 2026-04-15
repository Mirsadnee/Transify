# Universal Translator ML API

Production-oriented starter API for machine translation with FastAPI.

Integrates easily from PHP, JavaScript, Python, Java, C#, or any client that can call HTTP endpoints.

## Features

- FastAPI backend with OpenAPI docs (`/docs`)
- Lightweight web translator provider by default (`deep-translator`)
- Optional local ML provider (Transformers + NLLB)
- Text and HTML translation endpoints
- SQLite cache for repeated translations
- Optional API key authentication (`X-API-Key`)
- Docker and docker-compose support
- Example clients for PHP, JS, and Python
- Test suite using a lightweight dummy provider

## Architecture

```text
Website / App / CMS / PHP / JS / Python
                |
                v
         Universal Translator API
                |
        +-------+--------+
        |                |
        v                v
  Translation Cache   Translation Provider
    (SQLite)         (Web or Local NLLB)
```

## API Endpoints

### `GET /health`
Health check endpoint.

### `GET /languages`
Returns configured language map.

### `POST /detect-language`
Detects input language.

Request body:

```json
{
  "text": "Mire se vini ne faqen time"
}
```

### `POST /translate`
Translates plain text.

Request body:

```json
{
  "text": "Mire se vini ne faqen time",
  "source_lang": "sq",
  "target_lang": "en"
}
```

Response example:

```json
{
  "provider": "deep_translator",
  "model_name": "google-web",
  "source_lang": "sq",
  "target_lang": "en",
  "translated": "Welcome to my website",
  "detected_source_lang": null,
  "cache_hits": 0,
  "items_translated": 1
}
```

### `POST /translate-html`
Translates rendered HTML while preserving markup.

Request body:

```json
{
  "html": "<h1>Mire se vini</h1><p>Kjo eshte faqja ime.</p>",
  "source_lang": "sq",
  "target_lang": "en"
}
```

## Quick Start

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Linux/macOS

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API URLs:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs

## Docker

```bash
docker compose up --build
```

## Environment Variables

Default runtime values:

```env
TRANSLATION_PROVIDER=local_nllb
TRANSLATION_MODEL_NAME=facebook/nllb-200-distilled-600M
```

Free-memory default:

```env
TRANSLATION_PROVIDER=deep_translator
```

Optional API key protection:

```env
APP_API_KEY=super-secret-key
```

Send API key as request header:

```http
X-API-Key: super-secret-key
```

## Provider Modes

- `deep_translator` (default): lightweight and suitable for low-memory hosting.
- `local_nllb`: higher quality local model, but requires heavier dependencies/resources.

For `local_nllb`, the first startup downloads the NLLB model from Hugging Face, which can take time and disk space.

## Render Free Plan Tips

For 512MB plans, use:

```env
TRANSLATION_PROVIDER=deep_translator
```

If you deploy using Docker (this repo includes a Dockerfile), you do not need a custom start command.

## HTML Translation Rules

By default, these tags are skipped:

- `script`
- `style`
- `code`
- `pre`
- `textarea`
- `noscript`
- `svg`
- `math`

You can also mark content as non-translatable:

```html
<div translate="no">BrandName</div>
<div class="notranslate">SKU-12345</div>
<div data-no-translate>Internal code</div>
```

## Example Clients

- PHP: `examples/php/translate_page.php`
- JavaScript: `examples/js/client.mjs`
- Python: `examples/python/client.py`

## Tests

Tests run with the dummy provider (no heavy model download needed).

```bash
pytest -q
```

## Project Structure

```text
app/
  auth.py
  config.py
  language_map.py
  main.py
  schemas.py
  services/
    cache.py
    engine.py
    providers/
      base.py
      dummy.py
      local_nllb.py
  utils/
    html.py
    language.py
    text.py
examples/
  php/
  js/
  python/
demo/
tests/
```

## Notes

- This is a production-oriented starter, not a complete SaaS product.
- Review the license of any ML model before commercial deployment.
- Use caching aggressively for better performance at scale.
