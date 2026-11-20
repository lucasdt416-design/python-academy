# The learner's own tests for Site Builder: at least eight, including the edges.
from builder import escape, slug, build

assert escape("Tom & Jerry") == "Tom &amp; Jerry"
assert escape("<b>") == "&lt;b&gt;"
assert escape("&lt;") == "&amp;lt;"                  # & first, so nothing is escaped twice
assert slug("Sea Glass") == "sea-glass"
assert slug("  Sea   Glass & Shells! ") == "sea-glass-shells"
assert slug("!!!") == "page"                         # a name with no letters still gets a file
data = {"title": "T", "about": "A", "items": [{"name": "One", "text": "x"}, {"name": "Two", "text": "y"}]}
pages = build(data)
assert sorted(pages) == ["index.html", "one.html", "two.html"]
assert '<a href="two.html">Two</a>' in pages["one.html"]   # every page links to every other
risky = build({"title": "<script>", "about": "", "items": [{"name": "<i>x</i>", "text": "<script>alert(1)</script>"}]})
assert all("<script>" not in html for html in risky.values())
try:
    build({"title": "T", "about": "", "items": [{"name": "A b", "text": ""}, {"name": "a-b", "text": ""}]})
    assert False, "two items with the same page name should be refused"
except ValueError as problem:
    assert "a-b.html" in str(problem)
print("All Site Builder tests passed.")
