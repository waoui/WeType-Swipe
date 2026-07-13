from pathlib import Path
import re
import runpy

runpy.run_path("tools/patch_v111_test13_native_key_draw.py", run_name="__main__")

hook = Path("app/src/main/java/com/rww/wetypeswipe/MainHook.java")
text = hook.read_text(encoding="utf-8")


def replace_once(source: str, old: str, new: str, name: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"{name}: expected 1 match, found {count}")
    return source.replace(old, new, 1)


text = replace_once(
    text,
    '''        ensureNativeSingleKeyPaint(keyboard);
        float keyHeight = Math.max(1f, drawRect.height());
        float baseline = drawRect.bottom
                - Math.max(dp(keyboard, 2), keyHeight * 0.08f);
        drawKeyFunctionText((Canvas) canvasValue, shortActionLabel(action),
                drawRect.exactCenterX(), baseline);''',
    '''        ensureNativeSingleKeyPaint(keyboard, drawRect);
        float keyHeight = Math.max(1f, drawRect.height());
        Paint.FontMetrics metrics = keyboardLabelPaint.getFontMetrics();
        float visibleBottomPadding = Math.max(dp(keyboard, 3), keyHeight * 0.09f);
        float baseline = drawRect.bottom - visibleBottomPadding - metrics.descent;
        float topPadding = Math.max(dp(keyboard, 1), keyHeight * 0.03f);
        float minimumBaseline = drawRect.top + topPadding - metrics.ascent;
        if (baseline < minimumBaseline) baseline = minimumBaseline;
        drawKeyFunctionText((Canvas) canvasValue, shortActionLabel(action),
                drawRect.exactCenterX(), baseline);''',
    "native single-key font-metrics baseline")

text = replace_once(
    text,
    '''    private void ensureNativeSingleKeyPaint(View keyboard) {
        if (keyboard == null) return;
        int night = keyboard.getResources().getConfiguration().uiMode
                & Configuration.UI_MODE_NIGHT_MASK;
        int density = Float.floatToIntBits(
                keyboard.getResources().getDisplayMetrics().scaledDensity);
        long signature = (((long) keyboard.getWidth()) << 40)
                ^ (((long) keyboard.getHeight()) << 16)
                ^ (((long) night) << 8)
                ^ (density & 0xffffffffL);
        if (signature == nativeSingleKeyPaintSignature) return;
        prepareKeyboardLabelPaint(keyboard);
        nativeSingleKeyPaintSignature = signature;
    }
''',
    '''    private void ensureNativeSingleKeyPaint(View keyboard, Rect drawRect) {
        if (keyboard == null || drawRect == null) return;
        int night = keyboard.getResources().getConfiguration().uiMode
                & Configuration.UI_MODE_NIGHT_MASK;
        int density = Float.floatToIntBits(
                keyboard.getResources().getDisplayMetrics().scaledDensity);
        int keyHeight = Math.max(1, drawRect.height());
        long signature = (((long) keyboard.getWidth()) << 40)
                ^ (((long) keyboard.getHeight()) << 16)
                ^ (((long) keyHeight) << 4)
                ^ (((long) night) << 2)
                ^ (density & 0xffffffffL);
        if (signature == nativeSingleKeyPaintSignature) return;
        prepareKeyboardLabelPaint(keyboard);
        float scaledDensity = keyboard.getResources().getDisplayMetrics().scaledDensity;
        float keyBasedSize = keyHeight * 0.145f;
        float textSize = Math.max(5.4f * scaledDensity,
                Math.min(7.8f * scaledDensity, keyBasedSize));
        keyboardLabelPaint.setTextSize(textSize);
        nativeSingleKeyPaintSignature = signature;
    }
''',
    "native single-key adaptive paint")

# Align the outer fallback path to the same visible-bottom rule.
text = replace_once(
    text,
    "        float baseline = rowBottom - Math.max(dp(keyboard, 2), rowHeight * 0.08f);",
    "        Paint.FontMetrics metrics = keyboardLabelPaint.getFontMetrics();\n"
    "        float visibleBottomPadding = Math.max(dp(keyboard, 3), rowHeight * 0.09f);\n"
    "        float baseline = rowBottom - visibleBottomPadding - metrics.descent;",
    "fallback font-metrics baseline")

text = replace_once(
    text,
    '            logInfo("v1.11.0-test13 entered target package");',
    '            logInfo("v1.11.0-test14 entered target package");',
    "version log")

hook.write_text(text, encoding="utf-8")

build = Path("app/build.gradle.kts")
build_text = build.read_text(encoding="utf-8")
build_text, code_count = re.subn(r'versionCode\s*=\s*\d+', 'versionCode = 35', build_text, count=1)
build_text, name_count = re.subn(r'versionName\s*=\s*"[^"]+"',
                                  'versionName = "1.11.0-test14"',
                                  build_text, count=1)
if code_count != 1 or name_count != 1:
    raise RuntimeError(f"version update failed: code={code_count}, name={name_count}")
build.write_text(build_text, encoding="utf-8")

activity = Path("app/src/main/java/com/rww/wetypeswipe/MainActivity.java")
activity_text = activity.read_text(encoding="utf-8")
activity_text, activity_count = re.subn(
    r'v1\.11\.0-test13 · 原生单键同步渲染',
    'v1.11.0-test14 · 横屏字体基线修正',
    activity_text,
    count=1)
if activity_count != 1:
    raise RuntimeError(f"activity version update failed: {activity_count}")
activity.write_text(activity_text, encoding="utf-8")

print("v1.11.0-test14 font-metrics baseline patch applied")
