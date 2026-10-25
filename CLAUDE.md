# CLAUDE.md

This file gives context to Claude Code (and anyone else) working on this repo.

## What this is

A Micro.blog theme plug-in that ports the look of the [Blowfish](https://github.com/nunocoracao/blowfish) Hugo theme. Micro.blog wouldn't host full Blowfish, which is over 200 MB with its example site, images and bundled JS. This port is about 450 KB.

It keeps Blowfish's precompiled Tailwind stylesheet, color schemes, a handful of SVG icons and its MIT license, all from Blowfish commit `ebe683e` (2026-10-07). Every template is rewritten for Micro.blog, reusing Blowfish's markup and class names so its CSS applies unchanged. Nothing is built at deploy time: no Hugo Pipes, no npm and no image processing.

The first deployment is https://harrisonripps.com, installed over the Microwave theme. The theme may be offered to Micro.blog as a supported theme, so keep it generic: no site-specific values in `config.json`.

## Micro.blog platform facts

These were learned while building it, from the reference themes listed below, and several caused real bugs.

- **Hugo 0.158.** `.Site.Author` and `.RSSLink` no longer exist.
  - Micro.blog exposes the author as `.Site.Params.author.name`, `.username` and `.avatar`. See the official themes' "Fix compatibility with Hugo 0.158" commits from 2026-09-19/20, e.g. microdotblog/theme-alpine.
  - For feeds, use `.OutputFormats.Get "RSS"`.
  - For the language, use `site.Language.Locale` rather than `.Site.LanguageCode`.
- **Plug-in themes are layered over the design selected underneath.** Any template this theme lacks falls through to the theme below.
  - Example: Microwave's `_default/taxonomy.html` beat our `list.html` for category pages until we added `taxonomy.html`, `term.html` and `terms.html`.
  - When adding a page type, provide every name Hugo's lookup might use.
- **Posts** have `type: post` and live in per-year sections (`/2026/…`). As a result:
  - `.InSection` and `.NextInSection` stop at year boundaries, so `single-post.html` walks the full post list (`post-list.html`) to find older and newer posts.
  - Replies have `type: reply`.
- **Special pages** use custom output formats:
  - `/archive/` uses `archivehtml`, rendered by `list.archivehtml.html`.
  - `/photos/` uses `photoshtml`, rendered by `list.photoshtml.html`.
  - Micro.blog's default `/archive/index.json` (JSON Feed) cuts each post's `content_text` to about 100 characters and has no categories. This theme replaces it with `list.archivejson.json` (full text capped at 3000 characters, categories as `tags`) for search, as mnml and Cobalt do.
- **Hooks every theme must call:** `partial "microblog_head.html"` in `<head>` and `partial "custom_footer.html"`, and loops over `site.Params.plugins_css`, `plugins_js` and `plugins_html`. `custom_head.html` is optional (guard with `templates.Exists`).
- **Platform params:**
  - `theme_seconds`: cache-busting query string for static assets.
  - `include_conversation`: adds `https://micro.blog/conversation.js?url=…`.
  - `paginate_replies`
  - `itunes_description`: the site description, used as a fallback.
- **Menu entries** come from pages added to navigation. A page with `redirect_url` (most themes) or `redirect` (older themes) should link straight to that URL. See `partials/functions/menu-url.html`.
- **Media in post content:**
  - Uploaded videos are `<video poster="…" src="…/playlist.m3u8">`. HLS needs a script outside Safari, so cards show the poster rather than playing inline.
  - SoundCloud and similar embeds are `<iframe>`s.
  - Photos are in `.Params.photos`.
  - See `partials/functions/post-media.html`.
- **`/newsletters/` is reserved by Micro.blog** for its sent-newsletter archive, so a page or redirect at that path never renders.
- **Settings screen** (`plugin.json` fields): types are `string`, `boolean` and `color`. There are no lists, which is why list-like settings would need numbered fields. Values land in `site.Params`. Hugo lowercases param keys, so `index site.Params "homebutton1label"`-style lookups must use lowercase.

## Layout map

| File | Renders |
| --- | --- |
| `layouts/_default/baseof.html` | Page shell: skip link, header, main, footer, scripts |
| `layouts/partials/head.html` | Meta, social cards, feeds, no-flash dark mode script, CSS, Micro.blog hooks, home image preload |
| `layouts/partials/header.html` | Site title (not on home), desktop menu, CSS-only mobile menu (checkbox + `peer-checked`), appearance toggle |
| `layouts/partials/footer.html` | `custom_footer.html`, copyright, credits |
| `layouts/index.html` | Home: profile card (big image or avatar, name, headline, social links), optional recent posts |
| `layouts/post/single.html`, `reply/single.html` → `partials/single-post.html` | Post permalink: title, meta, content, conversation, older/newer |
| `layouts/_default/single.html` | Pages (About etc.) |
| `layouts/_default/list.html`, `term.html`, `taxonomy.html` → `partials/list-body.html` | Category and section lists: cards (`article-card.html`) or list (`article-link.html`), via the `listCards` setting |
| `layouts/_default/terms.html` → `partials/terms-body.html` | `/categories/` index as cards |
| `layouts/list.archivehtml.html` | Archive grouped by year, with category badges |
| `layouts/list.photoshtml.html` | Photo grid |
| `layouts/section/replies.html` | Replies |
| `layouts/list.archivejson.json` | `/archive/index.json`, the search index |
| `partials/search.html` + `static/js/search.js` | Search on category and archive pages, in two parts: `part: "box"` sits in the `.page-header` beside the title (stacked on small screens, see `custom.css`) and `part: "results"` goes in the body. The index loads on first focus. On a category page it can search that category or everything. Elements marked `data-search-hide` are hidden while results show, and `?q=` pre-fills the search. |
| `partials/article-meta.html` | Date, reading time, category badges (the current category's badge is hidden on its own page via `hide`) |
| `partials/functions/post-media.html` | Returns `{image, video, embed}` for a post's card thumbnail |
| `partials/social-links.html` | Icons for the `social_*` settings, which are full URLs |
| `partials/icon.html`, `partials/icons/*.html` | Inline SVGs copied from Blowfish's `assets/icons` |
| `static/css/main.css` | Blowfish's compiled Tailwind CSS. Don't edit; replace wholesale when updating from Blowfish. |
| `static/css/schemes/*.css` | Blowfish color schemes, chosen by the `colorScheme` setting |
| `static/css/custom.css` | Small additions for Micro.blog markup (photo tiles, card hover, play badge, embeds) |
| `static/js/appearance.js` | Light/dark toggle and following system changes |

## Conventions

- **Only use CSS classes that exist in `static/css/main.css`.** Tailwind purged everything Blowfish's own templates don't use, so plausible utilities like `gap-y-1`, `ms-3`, `hover:decoration-primary-500` and `sm:items-center` silently do nothing. Copy class lists from Blowfish's templates where possible, check with `dev/classcheck.py`, and put anything else in `custom.css`.
- **Settings live in three places:** `config.json` (defaults, grouped with the most-set first), `plugin.json` (settings-screen fields) and the README's settings table. Keep them in sync.
- **Bump `plugin.json` `version`** for each user-visible change. Micro.blog uses it to offer updates.
- **Keep `config.json` generic.** Site owners set their values in the plug-in settings.
- **Template style:** two-space indent, `{{- … }}` trimming like the existing files, and short `{{/* */}}` comments explaining *why*, especially for Micro.blog quirks.
- **Commit messages:** imperative subject, then a body explaining the reason.

## Testing

There's no Micro.blog to run locally. Use the fake site generator, which mimics Micro.blog's content layout, output formats, author params and partials:

```sh
python3 dev/make-test-site.py /tmp/mbtest                       # this theme alone
python3 dev/make-test-site.py /tmp/mbtest2 --under ../microwave  # layered over another theme, as on Micro.blog
cd /tmp/mbtest && hugo && python3 -m http.server -d public 8099
python3 dev/classcheck.py static/css/main.css,static/css/custom.css /tmp/mbtest/public
```

To check pages visually, take screenshots with headless Chrome:

```sh
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --hide-scrollbars \
  --window-size=1280,1200 --screenshot=out.png http://localhost:8099/categories/posts/
```

- **Phone width:** headless Chrome can't go narrower than about 500 px. Load the page in a 390 px-wide `<iframe>` in a wrapper HTML file instead.
- **Dark mode:** build with `params.defaultAppearance: dark` and `params.autoSwitchAppearance: false`.

Local Hugo (Homebrew) is newer than Micro.blog's 0.158, so a clean local build is necessary but not sufficient. The real test is installing on Micro.blog. When something breaks there, compare the live HTML with what the templates should produce: fetch the page, and look for which template's markup it contains.

## Reference themes

When unsure how Micro.blog expects something done, look at recently updated themes:
- **[jimmitchell/mnml](https://github.com/jimmitchell/mnml)** has the most complete coverage (archive, photos, replies, newsletter, redirect, search) and is actively maintained.
- **The official microdotblog themes** (theme-alpine, theme-soho, theme-gateway, Sumo-Theme) show the Hugo 0.158 fixes.
- **mikeschepker/Cobalt** shows the `Language.Locale` change.

## Not ported yet / ideas

- **Footer name.** The footer copyright uses the Micro.blog profile name; it could use `homeName` instead.
- **Images and longer posts.** Image zoom or a lightbox, a table of contents for long posts, and related posts.
- **Other platform features.** Translations (English strings are hard-coded) and a `newsletter.html` template for Micro.blog's email newsletters.
- **CSS size.** Purge `main.css` against these templates to shrink it (needs Node and Tailwind's CLI).
