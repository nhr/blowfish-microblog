"""Generate a throwaway Hugo site shaped like a Micro.blog blog, for testing.

Mimics what Micro.blog provides: posts with type "post" under year sections,
/archive/ as extra outputs of the home page,
titled articles and untitled microposts, photo, video and SoundCloud posts,
replies, archive/photos output formats, menu pages (one with redirect_url),
author info under params.author, and stub microblog_head/custom_footer
partials.

Usage:
  python3 dev/make-test-site.py SITE_DIR [--under PATH_TO_OTHER_THEME]

--under layers this theme over another (e.g. a clone of Microwave), the way
Micro.blog layers a plug-in theme over the selected design. Then:

  cd SITE_DIR && hugo && python3 -m http.server -d public 8099

Local Hugo is usually newer than Micro.blog's 0.158, so a clean local build
is a good sign, not proof.
"""
import argparse
import datetime
import json
import os
import random

THEME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = "https://eu.uploads.micro.blog/215277/2025/action-shot.png"
POSTER = "https://eu.uploads.micro.blog/215277/2026/frames/1840458-2-fd4b87.jpg"
LOREM = ("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod "
         "tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam.")


def write(path, front_matter, body=""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("---\n" + json.dumps(front_matter) + "\n---\n" + body + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("site")
    parser.add_argument("--under", help="theme to layer this one over")
    args = parser.parse_args()

    site = os.path.abspath(args.site)
    os.makedirs(os.path.join(site, "themes"), exist_ok=True)
    os.makedirs(os.path.join(site, "layouts", "partials"), exist_ok=True)
    os.makedirs(os.path.join(site, "content"), exist_ok=True)

    themes = ["blowfish-microblog"]
    links = {"blowfish-microblog": THEME}
    if args.under:
        themes.append("underlying")
        links["underlying"] = os.path.abspath(args.under)
    for name, target in links.items():
        link = os.path.join(site, "themes", name)
        if os.path.lexists(link):
            os.remove(link)
        os.symlink(target, link)

    # Partials Micro.blog supplies at build time
    with open(os.path.join(site, "layouts/partials/microblog_head.html"), "w") as f:
        f.write('<link rel="me" href="https://micro.blog/test">\n')
    with open(os.path.join(site, "layouts/partials/custom_footer.html"), "w") as f:
        f.write("")

    params = json.load(open(os.path.join(THEME, "config.json")))["params"]
    params.update({
        "author": {"name": "Test Author", "username": "test",
                   "avatar": "https://avatars.micro.blog/avatars/2025/11/1741495.jpg"},
        "homeName": "Test Author",
        "homeHeadline": "DJ, writer and occasional *newsletter* person",
        "homeImage": IMG,
        "social_bluesky": "https://bsky.app/profile/example.bsky.social",
        "social_instagram": "https://instagram.com/example",
        "include_conversation": True,
        "paginate_replies": True,
        "theme_seconds": "1",
    })
    config = {
        "baseURL": "http://localhost:8099/",
        "title": "Test Site",
        "theme": themes,
        "pagination": {"pagerSize": 10},
        "taxonomies": {"category": "categories"},
        "markup": {"goldmark": {"renderer": {"unsafe": True}}},
        "outputFormats": {
            # Micro.blog renders /archive/ as outputs of the home page, so
            # .IsHome is true there too (see partials/functions/is-home.html)
            "archivehtml": {"mediaType": "text/html", "baseName": "index", "isHTML": True, "path": "archive"},
            "photoshtml": {"mediaType": "text/html", "baseName": "index", "isHTML": True},
            "archivejson": {"mediaType": "application/json", "baseName": "index", "isPlainText": True, "path": "archive"},
        },
        "outputs": {"home": ["html", "rss", "archivehtml", "archivejson"]},
        "menus": {"main": [{"name": "Archive", "url": "/archive/", "weight": 50}]},
        "params": params,
    }
    json.dump(config, open(os.path.join(site, "hugo.json"), "w"), indent=1)

    content = os.path.join(site, "content")
    write(f"{content}/photos/_index.md", {"title": "Photos", "outputs": ["photoshtml"]})
    write(f"{content}/replies/_index.md", {"title": "Replies"})
    write(f"{content}/subscribe.md", {"title": "Mailing List!", "redirect_url": "https://example.com/subscribe",
                                      "menu": {"main": {"name": "Mailing List!", "weight": 10}}}, LOREM)
    write(f"{content}/about.md", {"title": "About", "menu": {"main": {"name": "About", "weight": 40}}}, LOREM)

    random.seed(4)
    date = datetime.datetime(2026, 10, 1, 10, 0)
    for i in range(30):
        date -= datetime.timedelta(days=random.randint(5, 40))
        fm = {"date": date.strftime("%Y-%m-%dT%H:%M:%S-05:00"), "type": "post"}
        kind = i % 4
        if kind == 0:
            fm.update(title=f"Article {i}", categories=["Posts"])
            if i % 8 == 0:
                fm["images"] = [IMG]
            body = "\n\n".join([LOREM] * 6)
        elif kind == 1:
            fm.update(title=f"Newsletter {i}", categories=["Newsletters"])
            body = "\n\n".join([LOREM] * 3)
        elif kind == 2:
            body = f"Short micropost {i}."
        else:
            fm["photos"] = [IMG]
            body = f'Photo post {i}\n\n<img src="{IMG}" width="600" height="338" alt="">'
        write(f"{content}/{date:%Y/%m/%d}/post-{i}.md", fm, body)

    # Media posts, using markup copied from real Micro.blog output
    write(f"{content}/2026/10/22/video.md",
          {"title": "Video post", "date": "2026-10-22T10:00:00-05:00", "type": "post", "categories": ["Posts", "Music"]},
          f'<p>A video.</p>\n<p><video controls="controls" playsinline="playsinline" preload="none" width="720" '
          f'height="1280" poster="{POSTER}" src="https://cdn.uploads.micro.mov/example/playlist.m3u8"></video></p>')
    write(f"{content}/2026/10/21/soundcloud.md",
          {"title": "SoundCloud post", "date": "2026-10-21T10:00:00-05:00", "type": "post", "categories": ["Posts"]},
          'A mix.\n\n<iframe width="100%" height="300" scrolling="no" frameborder="no" allow="autoplay" '
          'src="https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/soundcloud%253Atracks%253A2200124363'
          '&visual=true"></iframe>')
    write(f"{content}/2026/10/20/youtube.md",
          {"title": "YouTube post", "date": "2026-10-20T10:00:00-05:00", "type": "post", "categories": ["Posts"]},
          'A video.\n\n<iframe width="560" height="315" src="https://www.youtube.com/embed/dQw4w9WgXcQ"></iframe>')

    for i in range(3):
        write(f"{content}/replies/r{i}.md",
              {"date": f"2026-0{i + 1}-05T10:00:00-05:00", "type": "reply"}, f"@someone reply {i}.")

    print(f"Test site written to {site}")


if __name__ == "__main__":
    main()
