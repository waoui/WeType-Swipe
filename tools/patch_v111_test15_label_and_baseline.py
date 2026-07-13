from pathlib import Path
import re
import runpy

runpy.run_path("tools/patch_v111_test14_landscape_baseline.py", run_name="__main__")

hook = Path("app/src/main/java/com/rww/wetypeswipe/MainHook.java")
text = hook.read_text(encoding="utf-8")


def replace_once(source: str, old: str, new: str, name: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"{name}: expected 1 match, found {count}")
    return source.replace(old, new, 1)


text = replace_once(
    text,
    '            case Config.ACTION_SELECT_TO_PARAGRAPH_START: return "选段首";',
    '            case Config.ACTION_SELECT_TO_PARAGRAPH_START: return "选前";',
    "short select-to-start label")

text = replace_once(
    text,
    '            case Config.ACTION_SELECT_TO_PARAGRAPH_END: return "选段尾";',
    '            case Config.ACTION_SELECT_TO_PARAGRAPH_END: return "选后";',
    "short select-to-end label")

text = replace_once(
    text,
    '''        Paint.FontMetrics metrics = keyboardLabelPaint.getFontMetrics();
        float visibleBottomPadding = Math.max(dp(keyboard, 3), keyHeight * 0.09f);
        float baseline = drawRect.bottom - visibleBottomPadding - metrics.descent;
        float topPadding = Math.max(dp(keyboard, 1), keyHeight * 0.03f);
        float minimumBaseline = drawRect.top + topPadding - metrics.ascent;
        if (baseline < minimumBaseline) baseline = minimumBaseline;''',
    '''        Paint.FontMetrics metrics = keyboardLabelPaint.getFontMetrics();
        float visibleBottomPadding = Math.max(dp(keyboard, 1), keyHeight * 0.045f);
        float baseline = drawRect.bottom - visibleBottomPadding - metrics.descent;''',
    "lower native label baseline")

text = replace_once(
    text,
    '''        Paint.FontMetrics metrics = keyboardLabelPaint.getFontMetrics();
        float visibleBottomPadding = Math.max(dp(keyboard, 3), rowHeight * 0.09f);
        float baseline = rowBottom - visibleBottomPadding - metrics.descent;''',
    '''        Paint.FontMetrics metrics = keyboardLabelPaint.getFontMetrics();
        float visibleBottomPadding = Math.max(dp(keyboard, 1), rowHeight * 0.045f);
        float baseline = rowBottom - visibleBottomPadding - metrics.descent;''',
    "lower fallback label baseline")

text = replace_once(
    text,
    '            logInfo("v1.11.0-test14 entered target package");',
    '            logInfo("v1.11.0-test15 entered target package");',
    "version log")

hook.write_text(text, encoding="utf-8")

build = Path("app/build.gradle.kts")
build_text = build.read_text(encoding="utf-8")
build_text, code_count = re.subn(r'versionCode\s*=\s*\d+', 'versionCode = 36', build_text, count=1)
build_text, name_count = re.subn(r'versionName\s*=\s*"[^"]+"',
                                  'versionName = "1.11.0-test15"',
                                  build_text, count=1)
if code_count != 1 or name_count != 1:
    raise RuntimeError(f"version update failed: code={code_count}, name={name_count}")
build.write_text(build_text, encoding="utf-8")

activity = Path("app/src/main/java/com/rww/wetypeswipe/MainActivity.java")
activity_text = activity.read_text(encoding="utf-8")
activity_text, activity_count = re.subn(
    r'v1\.11\.0-test14 · 横屏字体基线修正',
    'v1.11.0-test15 · 短标签与位置修正',
    activity_text,
    count=1)
if activity_count != 1:
    raise RuntimeError(f"activity version update failed: {activity_count}")
activity.write_text(activity_text, encoding="utf-8")

print("v1.11.0-test15 short labels and lower adaptive baseline patch applied")
