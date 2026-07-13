from pathlib import Path
import re
import runpy

runpy.run_path("tools/patch_v111_test16_hot_path_core.py", run_name="__main__")

hook = Path("app/src/main/java/com/rww/wetypeswipe/MainHook.java")
text = hook.read_text(encoding="utf-8")

assignment = "cachedConfig = config;"
count = text.count(assignment)
if count < 2:
    raise RuntimeError(f"config assignments missing: {count}")
text = text.replace(
    assignment,
    assignment + "\n                        nativeSingleKeyLabelCache.clear();"
)

old = '            logInfo("v1.11.0-test15 entered target package");'
new = '            logInfo("v1.11.0-test16 entered target package");'
if text.count(old) != 1:
    raise RuntimeError("version log missing")
text = text.replace(old, new, 1)
hook.write_text(text, encoding="utf-8")

build = Path("app/build.gradle.kts")
build_text = build.read_text(encoding="utf-8")
build_text = re.sub(r'versionCode\s*=\s*\d+', 'versionCode = 37', build_text, count=1)
build_text = re.sub(r'versionName\s*=\s*"[^"]+"', 'versionName = "1.11.0-test16"', build_text, count=1)
build.write_text(build_text, encoding="utf-8")

activity = Path("app/src/main/java/com/rww/wetypeswipe/MainActivity.java")
activity_text = activity.read_text(encoding="utf-8")
activity_text, changed = re.subn(
    r'v1\.11\.0-test15 · 短标签与位置修正',
    'v1.11.0-test16 · 原生绘制热路径优化',
    activity_text,
    count=1)
if changed != 1:
    raise RuntimeError("activity version missing")
activity.write_text(activity_text, encoding="utf-8")

print("v1.11.0-test16 final optimization patch applied")
