# Blowfish for Micro.blog

A port of the [Blowfish](https://blowfish.page/) Hugo theme to [Micro.blog](https://micro.blog), cut down to what a Micro.blog site needs. Blowfish's full repository is over 200 MB. This theme is under 500 KB, most of which is Blowfish's precompiled stylesheet.

Requires Micro.blog's Hugo 0.158 (Design → Hugo version).

## What's included

- **Home page.** A profile card: a large image or your avatar, your name, a headline and social links. Recent posts can optionally appear below it.
- **Header.** Your Micro.blog menu, a light/dark toggle and a full-screen mobile menu. Pages with a `redirect_url` or `redirect` parameter link to that address.
- **Posts and replies.** Titled posts get Blowfish's article layout with reading time and category badges. Untitled microposts show in full. Each post links to the next older and newer post, and `include_conversation` adds Micro.blog's conversation embed.
- **Category pages.** Paginated posts as a grid of cards, with the post's first photo on top (or a plain list, if you turn cards off).
- **Archive page.** Posts grouped by year, plus links to every category.
- **Photos page.** A square-tile grid.
- **Replies page.** Respects `paginate_replies`.
- **Light and dark mode.** It follows the system setting by default, and visitors can override it with the toggle.
- **Color schemes.** All of Blowfish's color schemes are included.
- **Micro.blog hooks.** `microblog_head.html`, `custom_footer.html`, `custom_head.html` and `plugins_css` / `plugins_js` / `plugins_html` work, so other plug-ins keep working.

## Settings

All settings are on the plug-in's settings screen.

| Setting | Notes |
| --- | --- |
| Color scheme | `blowfish` (default), `avocado`, `autumn`, `bloody`, `burufugu`, `congo`, `fire`, `forest`, `github`, `marvel`, `neon`, `noir`, `ocean`, `one-light`, `princess`, `slate`, `terminal` |
| Default appearance | `light` or `dark`, used when not following the system setting |
| Home page name, headline, image | The name defaults to your Micro.blog name. Without an image, your avatar is shown. |
| Show category pages as cards | On by default |
| Show recent posts on home page | Optionally limited to one category |
| Social profile URLs | Bluesky, Mastodon, Threads, Instagram, Pixelfed, Tumblr, X, LinkedIn, GitHub, Last.fm, Letterboxd, email |

`photosIgnoreCategories`, a list of categories to leave off the Photos page, can only be set in `config.json`.

## How it was cut down

Blowfish builds its pages through Hugo Pipes, image processing, about 30 translations and a large set of bundled JavaScript libraries (search, charts, diagrams, maths, galleries and others). This port keeps Blowfish's precompiled Tailwind stylesheet and color schemes. Its templates are rewritten for Micro.blog, reusing Blowfish's markup and class names so the stylesheet applies as-is.

Micro.blog layers a plug-in theme over the design selected underneath it, and any template the plug-in doesn't provide falls through to the theme below. That's why this theme also provides `taxonomy.html`, `term.html` and `terms.html`, which older themes use for category pages, rather than relying on `list.html` alone.

Tailwind only ships the classes Blowfish's own templates use. When changing templates, use a class that already appears in `static/css/main.css`, or add a rule to `static/css/custom.css`.

Left out for now:
- search
- table of contents
- image zoom
- related posts
- shortcodes
- translations other than English

## Development

See [CLAUDE.md](CLAUDE.md) for how the theme fits Micro.blog, the conventions it follows and how to test it. `dev/make-test-site.py` builds a fake Micro.blog site to test against, and `dev/classcheck.py` finds CSS classes the stylesheet doesn't define.

## Credits

Design and stylesheet by [Nuno Coração](https://github.com/nunocoracao) and the [Blowfish contributors](https://github.com/nunocoracao/blowfish), MIT licensed. Ported from Blowfish commit `ebe683e` (2026-10-07).
