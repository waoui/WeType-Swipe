from pathlib import Path
import runpy

runpy.run_path("tools/patch_v1111_test1_actions_labels.py", run_name="__main__")

path = Path("app/src/main/java/com/rww/wetypeswipe/Config.java")
text = path.read_text(encoding="utf-8")
anchor = "        String clean = value.replace("
start = text.find(anchor)
if start < 0:
    raise RuntimeError("normalizeLabelValue anchor not found")
end = text.find(";", start)
if end < 0:
    raise RuntimeError("normalizeLabelValue statement end not found")
fixed = "        String clean = value.replace('\\n', ' ').replace('\\r', ' ').trim();"
text = text[:start] + fixed + text[end + 1:]
path.write_text(text, encoding="utf-8")
print("Applied newline escape compile fix")
