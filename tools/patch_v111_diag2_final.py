from pathlib import Path
import runpy

try:
    runpy.run_path("tools/patch_v111_diag2_fix.py", run_name="__main__")
except RuntimeError as error:
    if "activity version update failed: 0" not in str(error):
        raise
    activity = Path("app/src/main/java/com/rww/wetypeswipe/MainActivity.java")
    text = activity.read_text(encoding="utf-8")
    old = "v1.11.0-diag1 · 原生按键模型与绘制链诊断"
    new = "v1.11.0-diag2 · 深色与九宫格诊断"
    if text.count(old) != 1:
        raise RuntimeError(f"diag2 final activity marker: expected 1 match, found {text.count(old)}")
    activity.write_text(text.replace(old, new, 1), encoding="utf-8")
    print("v1.11.0-diag2 final activity version fix applied")
