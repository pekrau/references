"Convert from BibTex to YAML."

from pathlib import Path
import string
import sys

import bibtexparser
import pyperclip
import yaml

import latex_utf8


SUFFIXES = [""] + list(string.ascii_lowercase)

MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}
def cleanup_latex(value):
    "Convert LaTeX characters to UTF-8, remove newlines and normalize blanks."
    return latex_utf8.from_latex_to_utf8(" ".join(value.split()))


def cleanup_whitespaces(value):
    "Replace all whitespaces with blanks."
    return " ".join(value.split())


db = bibtexparser.loads(pyperclip.paste())

for entry in db.entries:
    data = dict(authors = cleanup_latex(entry.get("author", "")).split(" and "))
    if editors := cleanup_latex(entry.get("editor", "")):
        data["editors"] = editors.split(" and ")
    data["year"] = entry["year"]
    data["type"] = entry.get("ENTRYTYPE") or constants.ARTICLE
    for key, value in entry.items():
        if key in ("author", "editor", "ID", "ENTRYTYPE"):
            continue
        data[key] = cleanup_latex(value).strip()
    # Do some post-processing.
    # Change month into date; sometimes has day number.
    month = cleanup_latex(data.pop("month", ""))
    parts = month.split("~")
    if len(parts) == 2 and parts[1]:
        month = MONTHS[parts[1].strip().casefold()]
        day = int("".join([c for c in parts[0] if c in string.digits]))
        data["date"] = f'{entry["year"]}-{month:02d}-{day:02d}'
    elif len(parts) == 1 and parts[0]:
        month = MONTHS[parts[0].strip().casefold()]
        data["date"] = f'{entry["year"]}-{month:02d}-00'
    # Split up keywords
    if keywords := data.pop("keywords", None):
        data["keywords"] = [cleanup_latex(k).strip() for k in keywords.split(";")]
    # Change page numbers double dash to single dash.
    if pages := data.pop("pages", None):
        data["pages"] = pages.replace("--", "-")
    if abstract:= data.pop("abstract", None):
        data["abstract"] = cleanup_latex(cleanup_whitespaces(abstract))

    name = f'{data["authors"][0].split(",")[0]} {data["year"]}'
    lowname = name.casefold().replace(" ", "-")

    # Is there a set of references for the same year?
    if (filename := Path(f"{lowname}a.yaml")).exists():
        for suffix in string.ascii_lowercase:
            if not (filename := Path(f"{lowname}{suffix}.yaml")).exists():
                name = name + suffix
                break

    # Is there a previous reference?
    elif (filename := Path(f"{lowname}.yaml")).exists():
        print(" ", filename, "already exists")
        if input("overwrite it? > ") in "yYjJ":
            pass
        elif input("rename it? > ") in "yYjJ":
            with open(filename) as infile:
                data2 = yaml.safe_load(infile)
            data2["name"] = data2["name"] + "a"
            lowname2 = data2["name"].casefold().replace(" ", "-")
            filename2 = Path(f"{lowname2}.yaml")
            with open(filename2, "w") as outfile:
                outfile.write(yaml.dump(data2, allow_unicode=True))
            filename.unlink()
            print(f"renamed {filename} to {filename2}")
            name = name + "b"
            lowname = name.casefold().replace(" ", "-")
            filename = Path(f"{lowname}.yaml")
        else:
            print("no action; reference not saved")
            sys.exit()

    data["name"] = name
    with open(filename, "w") as outfile:
        outfile.write(yaml.dump(data, allow_unicode=True))
    print("wrote", filename)
