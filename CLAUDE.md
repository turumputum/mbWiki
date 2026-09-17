# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This is the **moduleBox Wiki** (`mbwiki.ru`) — a documentation site for the moduleBox
modular hardware/software platform. It is built on **Quartz 4** (a static site generator),
which is vendored unmodified in `quartz/`. Day-to-day work here is **writing and editing
Markdown content**, not changing the framework.

- `content/` — the actual wiki, authored in Russian. This is where nearly all edits happen.
- `quartz/` — vendored Quartz framework (TypeScript). Generally do not touch.
- `quartz.config.ts` / `quartz.layout.ts` — site config (theme, plugins, page layout).
- `docs/` — upstream Quartz's own documentation, unrelated to moduleBox content.
- `hlam/` — scratch folder ("хлам" = junk); drafts and C source pasted in for reference.
- The repo's working branch is `v4`; `master` is the PR target.

## Commands

```sh
npx quartz build --serve     # build content/ and serve with live reload (main dev loop)
npx quartz build             # one-off build to public/
npm run check                # tsc --noEmit + prettier --check (run before committing)
npm run format               # prettier --write
npm test                     # runs path.test.ts and depgraph.test.ts (framework tests)
```

`npm run docs` serves the upstream Quartz docs (`docs/`), not the moduleBox content — do
not confuse it with the dev loop above.

## Content architecture

`content/` is organized into four sections, each rendered as a folder page:

- `Аппаратные модули/` — hardware modules, files named `{name}_hw.md`
- `Программные модули/` — software modules, files named `{name}_sw.md`
  - `Программные модули/Виртуальные модули/` — virtual (logic-only) modules
  - `Программные модули/Звуковые модули/` — audio modules
  - `Программные модули/Дальномеры/` — distance sensors (the `distanceSens` family)
  - `Программные модули/Кнопки с подсветкой/` — button + backlight modules (`button_*`)
  - `Программные модули/Входы и выходы/` — the firmware `in_out` component: in_2ch/in_3ch/in_out/out_2ch/out_3ch/relay/tachometer
- `Архив/` — pre-constitution versions of module pages, linked from the current page's «Архив» section
- `Устройства/` — complete reference devices assembled from modules
- `Платформа moduleBox/` — platform-level pages (Hardware, Software, firmware, mbApp)

`content/index.md` is the site landing page and a hand-maintained index of every module —
**when adding a new module page, add its wikilink to `index.md`** in the matching section.

Markdown is **Obsidian-flavored**: wikilinks `[[path/to/file|display text]]`, embeds
`![[...]]`, callouts. Links use full paths from `content/` (e.g.
`[[Аппаратные модули/relay_hw|relay]]`). The `.obsidian/` folder makes the repo openable
as an Obsidian vault.

A module's filename, its `mode` value, and its MQTT topic prefix are all coupled — a
hardware module and its software counterpart cross-link each other.

## Writing module documentation

`DOCUMENTATION_SKILL.md` is the **authoritative standard** for module page structure
(frontmatter, the `mode` block, required sections, option/topic/command formatting, the
HW and SW page templates, and a review checklist). Read it before creating or revising any
module page. `template/hw_module_template.md` and `template/sw_module_template.md` are the
starting skeletons.

The critical rule from that standard: documented option names, default values, ranges,
topics, events, and commands **must match the device firmware code exactly**. Firmware
C source is the source of truth — verify against it rather than copying old docs. The
standard lists known stale names (`radar_` → `distanceSens_`, `pwmRGB_` → `pwmLeds_`,
`fadeIncrement` → `fadeTime`) and "ghost" options that exist in code but are never read
from config and so must not be documented.

There is also an `mbwiki` skill available for content tasks in this repo.

## Connection schemes (схемы подключения)

Wiring diagrams embedded in module pages are **generated**, not drawn by hand. A
YAML description (`content/.../_assets/<module>.scheme.yaml`) is turned into an SVG
by `tools/scheme_gen/generate.py`; the SVG is embedded via `![[...]]`. The layout
(controller right, devices left, numbered harnesses) is fixed in the generator —
only the YAML changes per scheme. The `connection-scheme` skill drives this
workflow; `tools/scheme_gen/README.md` is the YAML format spec.
