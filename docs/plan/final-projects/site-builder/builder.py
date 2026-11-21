# Site Builder: turn a data file into a small website, one page per item.
# Reference version of final project 2. Uses units 1 to 10 plus three new lessons:
# multi-line string templates, HTML as text, and escaping.
import json
import re

STYLE = "body{font-family:sans-serif;max-width:40rem;margin:2rem auto;padding:0 1rem;line-height:1.5}nav a{margin-right:1rem}"

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>{style}</style>
</head>
<body>
<nav>{nav}</nav>
<main>
<h1>{title}</h1>
{body}
</main>
</body>
</html>
"""


def escape(text):
    """Text made safe to put inside HTML: <b> shows as <b>, and is never read as a tag.
    & goes first, or the other replacements would be escaped twice."""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    return text


def slug(name):
    """A file name for a page: slug("Sea Glass & Shells!") is "sea-glass-shells"."""
    words = re.findall(r"[a-z0-9]+", name.lower())
    return "-".join(words) or "page"


def page(title, body, nav):
    """A whole HTML page. title is plain text; body and nav are HTML already."""
    return PAGE.format(title=escape(title), style=STYLE, nav=nav, body=body)


def nav_links(items):
    links = ['<a href="index.html">Home</a>']
    for item in items:
        links.append(f'<a href="{slug(item["name"])}.html">{escape(item["name"])}</a>')
    return " ".join(links)


def card(item):
    """One item on the home page: a link to its page, and its tags."""
    tags = ", ".join(escape(tag) for tag in item.get("tags", []))
    return f'<li><a href="{slug(item["name"])}.html">{escape(item["name"])}</a> <small>{tags}</small></li>'


def build(data):
    """Every page of the site, as {file name: HTML}."""
    items = data["items"]
    nav = nav_links(items)
    cards = "\n".join(card(item) for item in items)
    pages = {"index.html": page(data["title"], f"<p>{escape(data['about'])}</p>\n<ul>\n{cards}\n</ul>", nav)}
    for item in items:
        name = slug(item["name"]) + ".html"
        if name in pages:
            raise ValueError(f'Two pages would both be called {name}. Rename "{item["name"]}".')
        paragraphs = "\n".join(f"<p>{escape(p)}</p>" for p in item["text"].split("\n\n"))
        pages[name] = page(item["name"], paragraphs, nav)
    return pages


def main():
    with open("site.json") as f:
        data = json.load(f)
    pages = build(data)
    for name, html in pages.items():
        with open(name, "w") as f:
            f.write(html)
        print(f"Wrote {name} ({len(html)} characters)")


if __name__ == "__main__":
    main()
