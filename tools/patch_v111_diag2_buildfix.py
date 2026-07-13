from pathlib import Path
import runpy

runpy.run_path("tools/patch_v111_diag2_final.py", run_name="__main__")

hook = Path("app/src/main/java/com/rww/wetypeswipe/MainHook.java")
text = hook.read_text(encoding="utf-8")
old = "            drawKeyFunctionText(canvas, shortActionLabel(action), item[0], item[1], item[2]);"
new = "            drawKeyFunctionText(canvas, shortActionLabel(action), item[0], item[1]);"
if text.count(old) != 1:
    raise RuntimeError(f"diag2 draw overload marker: expected 1 match, found {text.count(old)}")
hook.write_text(text.replace(old, new, 1), encoding="utf-8")
print("v1.11.0-diag2 stable draw-method compatibility fix applied")
