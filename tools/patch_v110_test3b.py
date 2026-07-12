from pathlib import Path

exec(compile(Path("tools/patch_v110_test3.py").read_text(encoding="utf-8"), "tools/patch_v110_test3.py", "exec"))

hook = Path("app/src/main/java/com/rww/wetypeswipe/MainHook.java")
text = hook.read_text(encoding="utf-8")
old = "if (keyInfo == null) logNativeActionObject(keyboard, event, button);"
new = "if (keyInfo == null) probeNativeActionObject(keyboard, event, button);"
if text.count(old) != 1:
    raise RuntimeError(f"expected one diagnostic method call, found {text.count(old)}")
hook.write_text(text.replace(old, new, 1), encoding="utf-8")

gradle = Path("app/build.gradle.kts")
text = gradle.read_text(encoding="utf-8")
text = text.replace('versionName = "1.10.0-test3"', 'versionName = "1.10.0-test3b"', 1)
gradle.write_text(text, encoding="utf-8")

activity = Path("app/src/main/java/com/rww/wetypeswipe/MainActivity.java")
text = activity.read_text(encoding="utf-8")
text = text.replace('v1.10.0-test3 · 原生工具栏触摸诊断', 'v1.10.0-test3b · 原生工具栏触摸诊断', 1)
activity.write_text(text, encoding="utf-8")

print("v1.10.0-test3b diagnostic patch applied")
