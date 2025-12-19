import os
import yaml

for filename in os.listdir("."):
    if not filename.endswith(".yaml"):
        continue
    with open(filename) as infile:
        item = yaml.safe_load(infile)
    try:
        item["issue"] = item.pop("number")
    except KeyError:
        pass
    else:
        print(filename)
        with open(filename, "w") as outfile:
            outfile.write(yaml.dump(item, allow_unicode=True))
