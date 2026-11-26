# Site Builder: turn site.json into a small website, one page per item.
# The site is built on the three functions below. Each page your program
# writes with open(name, "w") appears in this project when "Keep files my
# program writes" is on.
import json


def escape(text):
    """Text made safe to put inside HTML: <b> shows as <b>, and is never read as a tag."""
    return text


def slug(name):
    """A file name for a page: slug("Sea Glass & Shells!") is "sea-glass-shells"."""
    return name


def build(data):
    """Every page of the site, as {file name: HTML}."""
    return {}


with open("site.json") as f:
    data = json.load(f)
print(data["title"])
