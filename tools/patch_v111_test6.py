from pathlib import Path
import runpy

runpy.run_path("tools/patch_v111_test5_fix.py", run_name="__main__")


def replace(path: str, old: str, new: str, count: int = 1) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    actual = text.count(old)
    if actual != count:
        raise RuntimeError(f"{path}: expected {count} matches, found {actual}: {old[:180]!r}")
    file.write_text(text.replace(old, new, count), encoding="utf-8")


hook = "app/src/main/java/com/rww/wetypeswipe/MainHook.java"

replace(hook,
        '            logInfo("v1.11.0-test5 entered target package");',
        '            logInfo("v1.11.0-test6 entered target package");')

replace(hook,
'''    private void prepareKeyboardLabelPaint(View keyboard) {
        float scaledDensity = keyboard.getResources().getDisplayMetrics().scaledDensity;
        float keyHeightBased = keyboard.getHeight() * 0.024f;
        float textSize = Math.max(6.0f * scaledDensity, Math.min(8.4f * scaledDensity, keyHeightBased));
''',
'''    private void prepareKeyboardLabelPaint(View keyboard) {
        float scaledDensity = keyboard.getResources().getDisplayMetrics().scaledDensity;
        float estimatedKeyHeight = keyboard.getHeight() / 4f;
        float keyHeightBased = estimatedKeyHeight * 0.145f;
        float textSize = Math.max(5.8f * scaledDensity, Math.min(8.0f * scaledDensity, keyHeightBased));
''')

replace(hook,
'''    private void drawQwertyFunctionLabels(View keyboard, Canvas canvas, Config config) {
        int height = keyboard.getHeight();
        float inset = Math.max(dp(keyboard, 4), height * 0.026f);
        drawQwertyRow(canvas, config, "qwertyuiop", height * 0.25f - inset);
        drawQwertyRow(canvas, config, "asdfghjkl", height * 0.50f - inset);
        drawQwertyRow(canvas, config, "zxcvbnm", height * 0.75f - inset);
    }
''',
'''    private void drawQwertyFunctionLabels(View keyboard, Canvas canvas, Config config) {
        float rowHeight = keyboard.getHeight() / 4f;
        float minBottomGap = dp(keyboard, 4);
        float firstBaseline = rowHeight
                - Math.max(minBottomGap, rowHeight * 0.18f);
        float secondBaseline = rowHeight * 2f
                - Math.max(minBottomGap, rowHeight * 0.19f);
        float thirdBaseline = rowHeight * 3f
                - Math.max(minBottomGap, rowHeight * 0.20f);
        drawQwertyRow(canvas, config, "qwertyuiop", firstBaseline);
        drawQwertyRow(canvas, config, "asdfghjkl", secondBaseline);
        drawQwertyRow(canvas, config, "zxcvbnm", thirdBaseline);
    }
''')

replace(hook,
'''    private void drawT9FunctionLabels(View keyboard, Canvas canvas, Config config) {
        int width = keyboard.getWidth();
        int height = keyboard.getHeight();
        float inset = Math.max(dp(keyboard, 2), height * 0.014f);
        for (int digit = 2; digit <= 9; digit++) {
            int action = config.actionFor(String.valueOf(digit), true);
            if (action == Config.ACTION_NONE) continue;
            int zeroBased = digit - 1;
            int row = zeroBased / 3;
            int column = zeroBased % 3;
            float x = width * ((column + 0.5f) / 3f);
            float baseline = height * ((row + 1f) / 4f) - inset;
            drawKeyFunctionText(canvas, shortActionLabel(action), x, baseline);
        }
    }
''',
'''    private void drawT9FunctionLabels(View keyboard, Canvas canvas, Config config) {
        int width = keyboard.getWidth();
        float rowHeight = keyboard.getHeight() / 4f;
        float bottomGap = Math.max(dp(keyboard, 4), rowHeight * 0.18f);
        for (int digit = 2; digit <= 9; digit++) {
            int action = config.actionFor(String.valueOf(digit), true);
            if (action == Config.ACTION_NONE) continue;
            int zeroBased = digit - 1;
            int row = zeroBased / 3;
            int column = zeroBased % 3;
            float x = width * ((column + 0.5f) / 3f);
            float baseline = rowHeight * (row + 1f) - bottomGap;
            drawKeyFunctionText(canvas, shortActionLabel(action), x, baseline);
        }
    }
''')

replace(hook,
'''    private void drawKeyFunctionText(Canvas canvas, String text, float x, float baseline) {
        if (text == null || text.isEmpty()) return;
        canvas.drawText(text, x, baseline, keyboardLabelPaint);
    }
''',
'''    private void drawKeyFunctionText(Canvas canvas, String text, float x, float baseline) {
        if (text == null || text.isEmpty()) return;
        float originalSize = keyboardLabelPaint.getTextSize();
        float scale = text.length() >= 4 ? 0.78f : (text.length() == 3 ? 0.88f : 1f);
        keyboardLabelPaint.setTextSize(originalSize * scale);
        Paint.FontMetrics metrics = keyboardLabelPaint.getFontMetrics();
        float safeBaseline = Math.max(-metrics.ascent + 1f, baseline);
        canvas.drawText(text, x, safeBaseline, keyboardLabelPaint);
        keyboardLabelPaint.setTextSize(originalSize);
    }
''')

replace(hook,
        '            case Config.ACTION_OPEN_CLIPBOARD: return "剪贴板";\n'
        '            case Config.ACTION_OPEN_QUICK_PHRASE: return "快捷发送";',
        '            case Config.ACTION_OPEN_CLIPBOARD: return "剪贴";\n'
        '            case Config.ACTION_OPEN_QUICK_PHRASE: return "快捷";')

replace("app/build.gradle.kts", 'versionName = "1.11.0-test5"', 'versionName = "1.11.0-test6"')
replace("app/src/main/java/com/rww/wetypeswipe/MainActivity.java",
        'v1.11.0-test5 · 真实按键边界标注',
        'v1.11.0-test6 · 按键文字位置优化')

print("v1.11.0-test6 key-label position tuning patch applied")
