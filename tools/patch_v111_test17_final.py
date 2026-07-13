from pathlib import Path
import re
import runpy

runpy.run_path("tools/patch_v111_test17_display_logic.py", run_name="__main__")

build = Path("app/build.gradle.kts")
text = build.read_text(encoding="utf-8")
text, code_count = re.subn(r'versionCode\s*=\s*\d+', 'versionCode = 38', text, count=1)
text, name_count = re.subn(r'versionName\s*=\s*"[^"]+"', 'versionName = "1.11.0-test17"', text, count=1)
if code_count != 1 or name_count != 1:
    raise RuntimeError(f"version update failed: {code_count}/{name_count}")
build.write_text(text, encoding="utf-8")

activity = Path("app/src/main/java/com/rww/wetypeswipe/MainActivity.java")
text = activity.read_text(encoding="utf-8")
text, changed = re.subn(
    r'v1\.11\.0-test16 · 原生绘制热路径优化',
    'v1.11.0-test17 · 显示选项开关',
    text,
    count=1)
if changed != 1:
    raise RuntimeError(f"activity version update failed: {changed}")
activity.write_text(text, encoding="utf-8")

print("v1.11.0-test17 display toggles finalized")
