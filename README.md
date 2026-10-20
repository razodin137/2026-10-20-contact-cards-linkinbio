# contact-card

A one-page contact card rendered from a single YAML file. Fill in
`contact.yaml`, run the build, and deploy the generated `index.html` to any
static host. Don't fill it in — or leave fields out — and the page falls
back to placeholder content, so the template works before you've written a
word.

## Quick start

```sh
cp contact.example.yaml contact.yaml   # then edit it
uv run build.py                        # or: pip install pyyaml && python3 build.py
```

The build writes `index.html`: one self-contained page — inline CSS, no
JavaScript, no external assets.

## YAML reference

| Field | Type | When absent |
|---|---|---|
| `name` | string | falls back to the "Your Name" placeholder |
| `headline` | string | omitted (placeholder without `contact.yaml`) |
| `about` | string | omitted (placeholder without `contact.yaml`) |
| `title` | string | defaults to `name` |
| `description` | string | defaults to `headline` |
| `url` | string | canonical / `og:url` tags omitted |
| `email`, `phone`, `location` | string | row omitted (placeholders without `contact.yaml`) |
| `socials` | list of mappings | section omitted (placeholder pills without `contact.yaml`) |
| `projects` | list of mappings | section omitted (placeholder entry without `contact.yaml`) |
| `newsletter` | mapping | section omitted (example card + example form without `contact.yaml`) |

`socials` entries: `url` (required), `platform` (optional — `youtube`, `x`,
`instagram` and `tiktok` have icons, anything else gets a generic globe),
`label` (optional). `projects` entries: `name` (required), `url` and `note`
(optional).

`newsletter` entries: `invitation`, `title`, `caption`, `note` (optional
copy), `image` — the card image link, an `https://` URL or a site-relative
path, defaulting to the bundled example `assets/card.svg` — plus `action`
(the form's POST endpoint; the form stays inert without it), `button`
(default "Subscribe") and `email_field` (the posted field name, default
`email`).

Behavior rules:

- **No `contact.yaml`** (or an empty file) → the entire page is placeholder
  content; this is what "not using YAML" looks like.
- **With `contact.yaml`** → only what you specify renders; blank fields are
  omitted rather than faked, so a half-filled page never shows fake data.
- Explicitly empty lists (`socials: []`) omit the section.
- URLs are restricted to `http(s)://`, `mailto:`, `tel:` and `#`.

## Files

- `build.py` — the generator (Python ≥ 3.10, PyYAML)
- `template.html` — page skeleton with `{{TOKENS}}`
- `contact.example.yaml` — documented example input
- `assets/card.svg` — the example card image shown above the signup form
- `contact.yaml` — your input (gitignored, so real contact data stays local)
- `index.html` — generated output (gitignored; don't edit by hand)