
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

API_KEY = os.environ["WAKATIME_API_KEY"]
README = Path("README.md")

START = "<!--START_WAKATIME-->"
END = "<!--END_WAKATIME-->"

# Fetch the last 7 days of WakaTime language statistics.
params = urllib.parse.urlencode({"api_key": API_KEY})
url = (
    "https://wakatime.com/api/v1/users/current/"
    f"stats/last_7_days?{params}"
)

request = urllib.request.Request(
    url,
    headers={"Accept": "application/json"},
)

with urllib.request.urlopen(request, timeout=30) as response:
    data = json.load(response)

languages = data.get("data", {}).get("languages", [])

if not languages:
    raise RuntimeError(
        "No language statistics returned by WakaTime."
    )

# Show the 10 most-used languages.
languages = sorted(
    languages,
    key=lambda item: item.get("percent", 0),
    reverse=True,
)[:10]

name_width = max(
    len(item.get("name", "Other"))
    for item in languages
)

lines = ["```text"]

for language in languages:
    name = language.get("name", "Other")
    percent = float(language.get("percent", 0))

    # Approximately one block for every 4 percentage points.
    bar_length = max(1, round(percent / 4))
    bar = "█" * bar_length

    lines.append(
        f"{name:<{name_width}}  "
        f"{bar:<12} {percent:.0f}%"
    )

lines.append("```")
generated = "\n".join(lines)

readme = README.read_text(encoding="utf-8")

if START not in readme or END not in readme:
    raise RuntimeError(
        "WakaTime markers are missing from README.md."
    )

before, remainder = readme.split(START, 1)
_, after = remainder.split(END, 1)

updated = (
    before
    + START
    + "\n"
    + generated
    + "\n"
    + END
    + after
)

README.write_text(updated, encoding="utf-8")
print("WakaTime language stats updated successfully.")
