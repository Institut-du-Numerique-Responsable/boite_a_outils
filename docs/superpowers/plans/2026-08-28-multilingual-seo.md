# Multilingual SEO Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the static toolbox language architecture extensible to FR/EN/NL/ES/DE, add an accessible language selector, and generate correct multilingual SEO signals without publishing untranslated pages.

**Architecture:** Replace the generator’s two-language assumptions with a locale registry and stable resource IDs. Published locales own their data, generated pages, navigation labels, alternates, JSON-LD and sitemap entries; unpublished locales remain available to the build as validated configuration but are absent from public navigation and SEO output.

**Tech Stack:** Python 3 standard library generator and validators, static HTML, vanilla JavaScript, CSS, Node-based site tests, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-08-28-multilingual-seo-design.md`

## Global Constraints

- Use locale-specific directories: `/`, `/en/`, `/nl/`, `/es/`, `/de/`.
- Never use IP, cookie, or browser-language redirects.
- Emit `hreflang` only for pages with a real translated counterpart, plus `x-default` to the language selector.
- A locale is `published` only when its interface strings and translated content pass validation.
- Preserve existing French and English URLs and generated output.
- Keep the implementation dependency-free and keyboard/mobile accessible.

### Task 1: Introduce a locale registry and translation interfaces

**Files:**
- Modify: `tools/generer_pages.py` (`LANGUES`, text lookup helpers, URL helpers)
- Create: `tools/translations.py`
- Test: `tools/test_multilingual.py`

**Interfaces:**
- `translations.py` exports `SUPPORTED_LOCALES`, `published_locales()`, and `ui(locale, key)`.
- `generer_pages.py` consumes locale records with `code`, `published`, `dossier`, `dossier_theme`, `dossier_outil`, `data_file`, and `strings`.

- [ ] **Step 1: Write failing tests** for registry shape, French/English compatibility, and rejection of missing UI keys.
- [ ] **Step 2: Run `python3 -m unittest tools/test_multilingual.py -v` and confirm the new tests fail.**
- [ ] **Step 3: Implement the registry and string lookup without changing generated HTML yet.**
- [ ] **Step 4: Run the focused tests and the existing data validator.**
- [ ] **Step 5: Commit `refactor: make locale configuration extensible`.**

### Task 2: Add the reusable accessible language selector

**Files:**
- Modify: `tools/generer_pages.py` (`entete`, `liens_alternes`)
- Modify: `www/index.html`
- Modify: `www/en/index.html`
- Modify: `www/assets/style.css` (language selector states and responsive layout)
- Test: `tools/test_multilingual.py`

**Interfaces:**
- `entete()` renders a `<nav>` language group from published locale links.
- Each link includes `lang`, `hreflang`, visible native language name, and `aria-current` on the active locale.

- [ ] **Step 1: Add failing assertions for three-link selector semantics on generated FR/EN pages.**
- [ ] **Step 2: Run the focused test and confirm failure.**
- [ ] **Step 3: Implement the selector using existing header markup and add focus-visible/mobile styles.**
- [ ] **Step 4: Regenerate pages and verify keyboard focus and relative links with the Node site test.**
- [ ] **Step 5: Commit `feat: add accessible language selector`.**

### Task 3: Make localized alternates, canonical metadata, and sitemaps data-driven

**Files:**
- Modify: `tools/generer_pages.py` (`liens_alternes`, `jsonld_*`, sitemap and llms generation)
- Modify: `tools/verifier_seo.py`
- Create: `tools/verifier_multilingual.py`
- Test: `tools/test_multilingual.py`

**Interfaces:**
- `liens_alternes(canonique, equivalents)` emits self + all available variants and one `x-default` selector URL.
- `verifier_multilingual.py` exits non-zero for missing reciprocal alternates, stale sitemap URLs, invalid locale codes, or an unpublished locale in navigation.

- [ ] **Step 1: Write failing tests for reciprocal alternates, self-canonical URLs, locale-specific JSON-LD, and sitemap membership.**
- [ ] **Step 2: Run the focused tests and confirm failure.**
- [ ] **Step 3: Implement the data-driven alternate map keyed by stable resource ID and locale.**
- [ ] **Step 4: Add the validator and run it against the regenerated French and English site.**
- [ ] **Step 5: Commit `feat: generate multilingual SEO metadata`.**

### Task 4: Add locale data contracts and the Dutch publication pipeline

**Files:**
- Create: `www/data/tools-nl.json`
- Create: `www/nl/index.html`
- Modify: `tools/generer_pages.py` (Dutch labels, folders and publication flag)
- Modify: `tools/verifier_donnees.py`
- Modify: `README.md` and `CONTRIBUTING.md` (translation workflow)
- Test: `tools/test_multilingual.py`

**Interfaces:**
- Dutch entries use the existing resource schema and stable `id`; missing translated entries remain unpublished rather than falling back silently.
- The generator creates `/nl/`, `/nl/topics/`, and `/nl/tools/` only when Dutch data is marked `published`.

- [ ] **Step 1: Add failing contract tests for Dutch required fields, duplicate IDs, and no implicit French/English fallback.**
- [ ] **Step 2: Run the tests and confirm failure.**
- [ ] **Step 3: Add the Dutch interface strings and a reviewed seed catalogue supplied by the project owner; keep the locale unpublished until its required translation coverage is met.**
- [ ] **Step 4: Regenerate and run data, SEO, multilingual, and site tests.**
- [ ] **Step 5: Commit `feat: add Dutch locale data contract`.**

### Task 5: Prepare Spanish and German without exposing incomplete pages

**Files:**
- Create: `www/data/tools-es.json`
- Create: `www/data/tools-de.json`
- Modify: `tools/generer_pages.py` (Spanish/German interface strings and publication flags)
- Modify: `README.md` (translation status table)
- Test: `tools/test_multilingual.py`

- [ ] **Step 1: Add failing tests ensuring unpublished ES/DE locales never appear in menus, `hreflang`, sitemaps, or robots-visible HTML.**
- [ ] **Step 2: Run tests and confirm failure.**
- [ ] **Step 3: Add complete interface dictionaries and empty, schema-valid locale catalogues with `published: false`.**
- [ ] **Step 4: Run all validators and inspect generated output for accidental fallback text.**
- [ ] **Step 5: Commit `feat: scaffold Spanish and German locales`.**

### Task 6: CI, documentation, and release verification

**Files:**
- Modify: `.github/workflows/validate-data.yml`
- Modify: `tools/README.md`
- Modify: `README.md`
- Test: `tools/verifier_multilingual.py`, `tools/test-site.mjs`

- [ ] **Step 1: Add the multilingual validator and focused tests to the required CI job.**
- [ ] **Step 2: Document how translators add entries, mark a locale published, review SEO output, and roll back a locale.**
- [ ] **Step 3: Run the complete local verification loop: data validator, SEO validator, multilingual validator, Python tests, and Node site tests.**
- [ ] **Step 4: Inspect `git diff --stat`, generated page counts, sitemap URLs, and the language selector manually.**
- [ ] **Step 5: Commit `ci: validate multilingual output` and prepare a PR/release note.**

