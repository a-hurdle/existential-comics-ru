#!/usr/bin/env python3
"A (very) basic website generator for Existential Comics translations."

import os
import html
import shutil

def sort_images(filenames: list[str]):
    "Sorts image file names."
    if len(filenames) <= 1:
        return filenames
    image_prefix = os.path.commonprefix(filenames)
    def sort_key(fn):
        n = fn[len(image_prefix):-4].lower()
        if n.isdigit():
            return int(n)
        number_words = ['one', 'two', 'three', 'four', 'five']
        if n in number_words:
            return number_words.index(n)
    return sorted(filenames, key = sort_key)

# Ensure that website directories exist
for d in ["site", "site/comics"]:
    if not os.path.isdir(d):
        os.mkdir(d)

# Process source files
issues = sorted(map(int, os.listdir("comics")))
prev_issue = None
listing_links = []
for issue_index in range(len(issues)):
    cur_issue = str(issues[issue_index])
    next_issue = None
    if issue_index + 1 < len(issues):
        next_issue = str(issues[issue_index + 1])
    issue_files = os.listdir("comics/" + cur_issue)
    images = sort_images(list(filter(lambda s: s.endswith(".png"),
                                     issue_files)))
    with open(f"comics/{cur_issue}/transcript-ru.txt") as fh:
        transcript_ru = fh.read()
    text_blocks = transcript_ru.split('\n\n\n')
    with open(f"comics/{cur_issue}/transcript.txt") as fh:
        transcript_en = fh.read()
    orig_text_blocks = transcript_en.split('\n\n\n')

    # The source URL is always in the first block.
    source_url = html.escape(text_blocks[0].removeprefix("Источник: "))
    # The title is always the second
    title = html.escape(text_blocks[1].removeprefix("Заголовок: "))
    # Same in the original
    orig_title = html.escape(orig_text_blocks[1].removeprefix("Title: "))
    # Hover text is among the last two, if present
    hover_text = None
    for i in [-1, -2]:
        if text_blocks[i].startswith("Текст при наведении: "):
            hover_text = html.escape(
                text_blocks[i]. \
                removeprefix("Текст при наведении: "). \
                strip().replace("\n", " "))
    # Description is the last, if present at all
    description = None
    if text_blocks[-1].startswith("Описание:\n\n"):
        description = html.escape(
            text_blocks[-1].removeprefix("Описание:\n\n"))

    # Compose an HTML page
    hover_text_attr = f""" title="{hover_text}" """ if hover_text else ""
    images_html = "<br/>\n".join(
        [f"""    <img src="comics/{fn}" {hover_text_attr} />"""
         for fn in images])
    prev_issue_html = \
        f"<a href=\"{prev_issue}.html\">предыдущий</a>" if prev_issue else ""
    next_issue_html = \
        f"<a href=\"{next_issue}.html\">следующий</a>" if next_issue else ""
    description_html = ""
    if description:
        description_html = "\n".join(
            [f"<p>{description_paragraph}</p>"
             for description_paragraph in description.split("\n\n")])
    issue_page = f"""
<!DOCTYPE html>
<html lang="ru">
  <head>
    <meta charset="utf-8">
    <title>{title} - Переводы Existential Comics</title>
  </head>
  <body>
    <h1>{title}</h1>
    <p>{prev_issue_html} | {next_issue_html}</p>
{images_html}
    {description_html}
    <p>Оригинал: <a href="{source_url}">{orig_title}</a>
    (Exisential Comics by Corey Mohler)</p>
  </body>
</html>
    """

    # Check if the files (HTML and images) must be updated, and
    # write/copy them if so.
    if (not os.path.isfile(f"site/{cur_issue}.html") or
        (os.path.getmtime(f"site/{cur_issue}.html") <
         max(os.path.getmtime(f"comics/{cur_issue}/transcript-ru.txt"),
             os.path.getmtime(f"comics/{cur_issue}/transcript.txt")))):
        # Write the HTML and image files
        with open(f"site/{cur_issue}.html", 'w') as fh:
            fh.write(issue_page)
    for image in images:
        if (not os.path.isfile(f"site/comics/{image}") or
            (os.path.getmtime(f"site/comics/{image}") <
             os.path.getmtime(f"comics/{cur_issue}/{image}"))):
            shutil.copyfile(f"comics/{cur_issue}/{image}",
                            f"site/comics/{image}")

    # Remember the link for listing
    listing_links.append(f"""
    #{cur_issue}
    <a href="{cur_issue}.html">{title}</a>\n
    (<a href="{source_url}">{orig_title}</a>)
    """)
    prev_issue = cur_issue

# Prepare the index page
listing_links_html = "<br>\n".join(listing_links)
index_html = f"""
<!DOCTYPE html>
<html lang="ru">
  <head>
    <meta charset="utf-8">
    <title>Переводы Existential Comics</title>
  </head>
  <body>
    <h1>Переводы Existential Comics</h1>
{listing_links_html}
  </body>
</html>
"""

with open(f"site/index.html", 'w') as fh:
        fh.write(index_html)
