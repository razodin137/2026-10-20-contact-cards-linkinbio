#!/usr/bin/env python3
"""Build a one-page contact card from contact.yaml.

The page is a template until you provide input: with no contact.yaml every
section falls back to placeholder content, and with a contact.yaml anything
you leave out is simply omitted. Copy contact.example.yaml to contact.yaml,
fill in what you want, and rebuild.

    uv run build.py        # or: pip install pyyaml && python3 build.py
"""

from __future__ import annotations

import html
import re
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
CONTACT_PATH = ROOT / "contact.yaml"
TEMPLATE_PATH = ROOT / "template.html"
OUTPUT_PATH = ROOT / "index.html"

URL_SCHEMES = re.compile(r"^(?:https?://|mailto:|tel:|#)", re.IGNORECASE)

_HTTP_URL = re.compile(r"^https?://", re.IGNORECASE)
_SITE_PATH = re.compile(r"^[\w\-./]+$")

# The example card image shipped with the template; the newsletter section
# falls back to it when no image link is provided.
DEFAULT_CARD = "assets/card.svg"

PLACEHOLDERS = {
    "name": "Your Name",
    "headline": "Your one-line headline goes here.",
    "about": "A sentence or two about who you are, what you do, and how to reach you.",
    "email": "you@example.com",
    "phone": "+1 (555) 010-0100",
    "location": "Your City",
    "project_name": "Your Project",
    "project_note": "what you\u2019re building",
}

# Inline icons for known platforms; anything else gets the generic mark.
_ICONS = {
    "youtube": (
        '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>'
    ),
    "x": (
        '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.748l7.738-8.835L1.254 2.25H8.08l4.261 5.631 5.903-5.631zm-1.161 17.52h1.833L7.084 4.126H5.117L17.083 19.77z"/></svg>'
    ),
    "instagram": (
        '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/></svg>'
    ),
    "tiktok": (
        '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/></svg>'
    ),
}
_GENERIC_ICON = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">'
    '<circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4.5" ry="9"/><path d="M3 12h18"/></svg>'
)


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def safe_url(value) -> str:
    url = str(value).strip()
    if not URL_SCHEMES.match(url):
        sys.exit(
            f"error: refusing unsafe URL {value!r} "
            "(only http(s)://, mailto:, tel: and # are allowed)"
        )
    return esc(url)


def safe_src(value) -> str:
    src = str(value).strip()
    if not (_HTTP_URL.match(src) or _SITE_PATH.match(src)):
        sys.exit(
            f"error: refusing unsafe image source {value!r} "
            "(use an https:// URL or a site-relative path)"
        )
    return esc(src)


def load_contact() -> dict:
    if not CONTACT_PATH.exists():
        return {}
    try:
        data = yaml.safe_load(CONTACT_PATH.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        sys.exit(f"error: contact.yaml is not valid YAML:\n{exc}")
    if data is None:
        return {}
    if not isinstance(data, dict):
        sys.exit("error: contact.yaml must be a mapping of field names to values")
    return data


def text(data: dict, key: str, using_yaml: bool) -> str:
    """Scalar field: present value; placeholder without YAML; omitted otherwise."""
    value = data.get(key)
    if value is None or not str(value).strip():
        return "" if using_yaml else PLACEHOLDERS[key]
    return str(value).strip()


def _mapping(item, where: str) -> dict:
    if not isinstance(item, dict):
        sys.exit(f"error: each entry in `{where}` must be a mapping")
    return item


def _placeholder_pill(label: str) -> str:
    return (
        f'<span class="social-link placeholder">{_GENERIC_ICON}'
        f"<span>{esc(label)}</span></span>"
    )


def render_socials(data: dict, using_yaml: bool) -> str:
    socials = data.get("socials")
    if socials is None:
        if using_yaml:
            return ""
        pills = "".join(_placeholder_pill(l) for l in ("Website", "Email", "@yourhandle"))
        return f'<nav class="socials" aria-label="Social links">{pills}</nav>'
    if not isinstance(socials, list):
        sys.exit("error: `socials` must be a list")
    if not socials:
        return ""
    pills = []
    for item in socials:
        item = _mapping(item, "socials")
        url = item.get("url")
        if url is None or not str(url).strip():
            sys.exit("error: each entry in `socials` needs a `url`")
        platform = str(item.get("platform") or "website").strip().lower()
        label = str(item.get("label") or item.get("handle") or platform.capitalize()).strip()
        icon = _ICONS.get(platform, _GENERIC_ICON)
        pills.append(
            f'<a class="social-link" href="{safe_url(url)}" target="_blank" '
            f'rel="noopener noreferrer" aria-label="{esc(platform)}: {esc(label)}">'
            f"{icon}<span>{esc(label)}</span></a>"
        )
    return f'<nav class="socials" aria-label="Social links">{"".join(pills)}</nav>'


def _section(title: str, inner: str) -> str:
    return f'<section><h2>{title}</h2>{inner}</section>'


def render_projects(data: dict, using_yaml: bool) -> str:
    projects = data.get("projects")
    if projects is None:
        if using_yaml:
            return ""
        li = (
            f'<li><span class="project-name placeholder">{esc(PLACEHOLDERS["project_name"])}</span>'
            f'<span class="project-note"> \u2014 {esc(PLACEHOLDERS["project_note"])}</span></li>'
        )
        return _section("Projects", f'<ul class="projects">{li}</ul>')
    if not isinstance(projects, list):
        sys.exit("error: `projects` must be a list")
    if not projects:
        return ""
    items = []
    for item in projects:
        item = _mapping(item, "projects")
        name = str(item.get("name") or "").strip()
        if not name:
            sys.exit("error: each entry in `projects` needs a `name`")
        if item.get("url"):
            name_html = f'<a class="project-link" href="{safe_url(item["url"])}">{esc(name)}</a>'
        else:
            name_html = f'<span class="project-name">{esc(name)}</span>'
        note = str(item.get("note") or "").strip()
        note_html = f'<span class="project-note"> \u2014 {esc(note)}</span>' if note else ""
        items.append(f"<li>{name_html}{note_html}</li>")
    return _section("Projects", f'<ul class="projects">{"".join(items)}</ul>')


def render_contact(data: dict, using_yaml: bool) -> str:
    rows = []
    for key, label, scheme in (
        ("email", "Email", "mailto:"),
        ("phone", "Phone", "tel:"),
        ("location", "Location", None),
    ):
        value = str(data.get(key) or "").strip()
        if value:
            if scheme == "tel:":
                href = esc(scheme + "".join(value.split()))
            elif scheme:
                href = esc(scheme + value)
            rows.append(
                f'<li><span class="contact-k">{label}</span>'
                f'<a class="contact-v" href="{href}">{esc(value)}</a></li>'
            )
        elif not using_yaml:
            rows.append(
                f'<li><span class="contact-k">{label}</span>'
                f'<span class="contact-v placeholder">{esc(PLACEHOLDERS[key])}</span></li>'
            )
    if not rows:
        return ""
    return _section("Contact", f'<ul class="contact">{"".join(rows)}</ul>')


def render_newsletter(data: dict, using_yaml: bool) -> str:
    newsletter = data.get("newsletter")
    if newsletter is None:
        if using_yaml:
            return ""
        newsletter = {}
    if not isinstance(newsletter, dict):
        sys.exit("error: `newsletter` must be a mapping")
    if not newsletter and using_yaml:
        return ""
    invitation = str(newsletter.get("invitation") or "").strip()
    if not invitation and not using_yaml:
        invitation = "Occasional notes on what I\u2019m building, straight to your inbox."
    title = str(newsletter.get("title") or "").strip()
    if not title and not using_yaml:
        title = "Newsletter"
    caption = str(newsletter.get("caption") or "").strip()
    note = str(newsletter.get("note") or "").strip()
    if not note and not using_yaml:
        note = "No spam. Unsubscribe whenever."
    button = str(newsletter.get("button") or "Subscribe").strip() or "Subscribe"
    email_field = str(newsletter.get("email_field") or "email").strip() or "email"
    image = safe_src(newsletter.get("image") or DEFAULT_CARD)
    action = newsletter.get("action")
    title_html = f"<h2>{esc(title)}</h2>" if title else ""
    invitation_html = f'<p class="signup-invitation">{esc(invitation)}</p>' if invitation else ""
    caption_html = f"<figcaption>{esc(caption)}</figcaption>" if caption else ""
    note_html = f'<p class="signup-note">{esc(note)}</p>' if note else ""
    return (
        '<section class="newsletter" aria-label="Newsletter">'
        f'<figure class="journal"><img src="{image}" alt="" loading="lazy" />{caption_html}</figure>'
        f'<form class="signup" action="{safe_url(action) if action else "#"}" method="post" target="_blank">'
        f"{title_html}"
        f"{invitation_html}"
        '<div class="signup-row">'
        f'<input id="newsletter-email" type="email" name="{esc(email_field)}" aria-label="Email address" placeholder="you@example.com" required autocomplete="email" />'
        f'<button type="submit">{esc(button)}</button>'
        "</div>"
        f"{note_html}"
        "</form>"
        "</section>"
    )


def render_meta(data: dict, title: str, description: str) -> str:
    tags = []
    if description:
        tags.append(f'<meta name="description" content="{esc(description)}" />')
    url = str(data.get("url") or "").strip()
    if url:
        tags.append(f'<link rel="canonical" href="{safe_url(url)}" />')
    tags.extend(
        [
            '<meta property="og:type" content="website" />',
            f'<meta property="og:title" content="{esc(title)}" />',
            f'<meta name="twitter:card" content="summary" />',
            f'<meta name="twitter:title" content="{esc(title)}" />',
        ]
    )
    if url:
        tags.append(f'<meta property="og:url" content="{safe_url(url)}" />')
    if description:
        tags.extend(
            [
                f'<meta property="og:description" content="{esc(description)}" />',
                f'<meta name="twitter:description" content="{esc(description)}" />',
            ]
        )
    return "\n  ".join(tags)


def main() -> None:
    if not TEMPLATE_PATH.exists():
        sys.exit(f"error: {TEMPLATE_PATH.name} not found next to build.py")
    data = load_contact()
    using_yaml = bool(data)

    name = str(data.get("name") or PLACEHOLDERS["name"]).strip()
    headline = text(data, "headline", using_yaml)
    about = text(data, "about", using_yaml)
    title = str(data.get("title") or name).strip()
    description = str(data.get("description") or headline).strip()

    out = (
        TEMPLATE_PATH.read_text(encoding="utf-8")
        .replace("{{TITLE}}", esc(title))
        .replace("{{META}}", render_meta(data, title, description))
        .replace("{{NAME}}", esc(name))
        .replace("{{HEADLINE}}", f'<p class="headline">{esc(headline)}</p>' if headline else "")
        .replace("{{SOCIALS}}", render_socials(data, using_yaml))
        .replace("{{ABOUT}}", f'<p class="about">{esc(about)}</p>' if about else "")
        .replace("{{PROJECTS}}", render_projects(data, using_yaml))
        .replace("{{CONTACT}}", render_contact(data, using_yaml))
        .replace("{{NEWSLETTER}}", render_newsletter(data, using_yaml))
        .replace("{{YEAR}}", str(date.today().year))
    )
    if leftover := re.search(r"\{\{[A-Z_]+\}\}", out):
        sys.exit(f"error: unresolved template token {leftover.group(0)}")
    OUTPUT_PATH.write_text(out, encoding="utf-8")
    print(f"wrote {OUTPUT_PATH} ({'contact.yaml' if using_yaml else 'placeholder content'})")


if __name__ == "__main__":
    main()