from pathlib import Path
import runpy

runpy.run_path("tools/patch_v111_test4.py", run_name="__main__")


def replace(path: str, old: str, new: str, count: int = 1) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    actual = text.count(old)
    if actual != count:
        raise RuntimeError(f"{path}: expected {count} matches, found {actual}: {old[:180]!r}")
    file.write_text(text.replace(old, new, count), encoding="utf-8")


hook = "app/src/main/java/com/rww/wetypeswipe/MainHook.java"

replace(hook,
        "import android.os.Build;",
        "import android.os.Build;\nimport android.os.SystemClock;")
replace(hook,
        "import java.util.List;\nimport java.util.Locale;",
        "import java.util.ArrayList;\nimport java.util.HashMap;\nimport java.util.List;\nimport java.util.Locale;\nimport java.util.Map;")

replace(hook,
        "    private final Paint keyboardLabelPaint = new Paint(Paint.ANTI_ALIAS_FLAG);",
        "    private final Paint keyboardLabelPaint = new Paint(Paint.ANTI_ALIAS_FLAG);\n"
        "    private volatile WeakReference<View> keyboardLabelGeometryViewRef = new WeakReference<>(null);\n"
        "    private volatile Map<String, List<Float>> keyboardLabelCenters = new HashMap<>();\n"
        "    private volatile int keyboardLabelGeometryWidth;\n"
        "    private volatile int keyboardLabelGeometryHeight;\n"
        "    private volatile String keyboardLabelLayoutSignature = \"\";\n"
        "    private volatile long keyboardLabelSignatureCheckedAt;\n"
        "    private volatile boolean keyboardLabelGeometryBuilding;")

replace(hook,
        '            logInfo("v1.11.0-test4 entered target package");',
        '            logInfo("v1.11.0-test5 entered target package");')

replace(hook,
        '''            String name = keyboard.getClass().getName().toLowerCase(Locale.ROOT);
            prepareKeyboardLabelPaint(keyboard);
            if (name.contains("t9") || name.contains("nine")) {
                drawT9FunctionLabels(keyboard, canvas, config);
            } else if (name.contains("qwerty") || name.contains("wubi") || name.contains("pinyin")) {
                drawQwertyFunctionLabels(keyboard, canvas, config);
            }
''',
        '''            String name = keyboard.getClass().getName().toLowerCase(Locale.ROOT);
            prepareKeyboardLabelPaint(keyboard);
            if (name.contains("t9") || name.contains("nine")) {
                drawT9FunctionLabels(keyboard, canvas, config);
            } else if (name.contains("qwerty") || name.contains("wubi") || name.contains("pinyin")) {
                ensureKeyboardLabelGeometry(keyboard);
                drawQwertyFunctionLabels(keyboard, canvas, config);
            }
''')

replace(hook,
        '''    private void prepareKeyboardLabelPaint(View keyboard) {
        float scaledDensity = keyboard.getResources().getDisplayMetrics().scaledDensity;
        float widthBased = keyboard.getWidth() / 155f;
        float textSize = Math.max(6.2f * scaledDensity, Math.min(8.2f * scaledDensity, widthBased));
''',
        '''    private void prepareKeyboardLabelPaint(View keyboard) {
        float scaledDensity = keyboard.getResources().getDisplayMetrics().scaledDensity;
        float keyHeightBased = keyboard.getHeight() * 0.024f;
        float textSize = Math.max(6.0f * scaledDensity, Math.min(8.4f * scaledDensity, keyHeightBased));
''')

old_qwerty = '''    private void drawQwertyFunctionLabels(View keyboard, Canvas canvas, Config config) {
        int width = keyboard.getWidth();
        int height = keyboard.getHeight();
        float inset = Math.max(dp(keyboard, 2), height * 0.014f);
        drawQwertyRow(canvas, config, "qwertyuiop", width, height * 0.25f - inset, 0);
        drawQwertyRow(canvas, config, "asdfghjkl", width, height * 0.50f - inset, 1);
        drawQwertyRow(canvas, config, "zxcvbnm", width, height * 0.75f - inset, 2);
    }

    private void drawQwertyRow(Canvas canvas, Config config, String keys,
                               int width, float baseline, int row) {
        for (int index = 0; index < keys.length(); index++) {
            String key = String.valueOf(keys.charAt(index));
            int action = config.actionFor(key, false);
            if (action == Config.ACTION_NONE) continue;
            float x;
            if (row == 0) {
                x = width * ((index + 0.5f) / 10f);
            } else if (row == 1) {
                x = width * ((index + 1f) / 10f);
            } else {
                x = width * (0.20f + index * 0.10f);
            }
            drawKeyFunctionText(canvas, shortActionLabel(action), x, baseline);
        }
    }
'''

new_qwerty = '''    private void drawQwertyFunctionLabels(View keyboard, Canvas canvas, Config config) {
        int height = keyboard.getHeight();
        float inset = Math.max(dp(keyboard, 4), height * 0.026f);
        drawQwertyRow(canvas, config, "qwertyuiop", height * 0.25f - inset);
        drawQwertyRow(canvas, config, "asdfghjkl", height * 0.50f - inset);
        drawQwertyRow(canvas, config, "zxcvbnm", height * 0.75f - inset);
    }

    private void drawQwertyRow(Canvas canvas, Config config, String keys, float baseline) {
        Map<String, List<Float>> centers = keyboardLabelCenters;
        if (centers == null || centers.isEmpty()) return;
        for (int index = 0; index < keys.length(); index++) {
            String key = String.valueOf(keys.charAt(index));
            int action = config.actionFor(key, false);
            if (action == Config.ACTION_NONE) continue;
            List<Float> positions = centers.get(key);
            if (positions == null) continue;
            for (Float x : positions) {
                if (x != null) drawKeyFunctionText(canvas, shortActionLabel(action), x, baseline);
            }
        }
    }

    private void ensureKeyboardLabelGeometry(View keyboard) {
        if (keyboard == null || keyboard.getWidth() <= 0 || keyboard.getHeight() <= 0) return;
        long now = SystemClock.uptimeMillis();
        boolean sameView = keyboardLabelGeometryViewRef.get() == keyboard;
        boolean sameSize = keyboardLabelGeometryWidth == keyboard.getWidth()
                && keyboardLabelGeometryHeight == keyboard.getHeight();
        String signature = keyboardLabelLayoutSignature;
        if (now - keyboardLabelSignatureCheckedAt >= 700L) {
            keyboardLabelSignatureCheckedAt = now;
            signature = keyboardLayoutSignature(keyboard);
        }
        boolean signatureChanged = !signature.equals(keyboardLabelLayoutSignature);
        if (sameView && sameSize && !signatureChanged && !keyboardLabelCenters.isEmpty()) return;
        keyboardLabelLayoutSignature = signature;
        if (keyboardLabelGeometryBuilding) return;
        keyboardLabelGeometryBuilding = true;
        keyboard.post(() -> rebuildKeyboardLabelGeometry(keyboard, signature));
    }

    private void rebuildKeyboardLabelGeometry(View keyboard, String expectedSignature) {
        try {
            if (keyboard == null || !keyboard.isAttachedToWindow()
                    || keyboard.getWidth() <= 0 || keyboard.getHeight() <= 0) return;
            Map<String, List<Float>> result = new HashMap<>();
            scanKeyboardRow(keyboard, "qwertyuiop", keyboard.getHeight() * 0.125f, result);
            scanKeyboardRow(keyboard, "asdfghjkl", keyboard.getHeight() * 0.375f, result);
            scanKeyboardRow(keyboard, "zxcvbnm", keyboard.getHeight() * 0.625f, result);
            if (!result.isEmpty()) {
                keyboardLabelGeometryViewRef = new WeakReference<>(keyboard);
                keyboardLabelGeometryWidth = keyboard.getWidth();
                keyboardLabelGeometryHeight = keyboard.getHeight();
                keyboardLabelLayoutSignature = expectedSignature;
                keyboardLabelCenters = result;
                keyboard.postInvalidate();
            }
        } catch (Throwable throwable) {
            logError("keyboard key-geometry scan failed", throwable);
        } finally {
            keyboardLabelGeometryBuilding = false;
        }
    }

    private void scanKeyboardRow(View keyboard, String expectedKeys, float y,
                                 Map<String, List<Float>> output) {
        int width = keyboard.getWidth();
        int step = Math.max(dp(keyboard, 2), Math.max(2, width / 260));
        String activeKey = null;
        float segmentStart = 0f;
        float previousX = 0f;
        for (int x = Math.max(1, step / 2); x < width; x += step) {
            String key = keyAtKeyboardPoint(keyboard, x, y);
            if (key == null || expectedKeys.indexOf(key) < 0) key = null;
            if (activeKey == null ? key != null : !activeKey.equals(key)) {
                if (activeKey != null) addKeyboardKeyCenter(output, activeKey,
                        (segmentStart + previousX) * 0.5f);
                activeKey = key;
                segmentStart = x;
            }
            previousX = x;
        }
        if (activeKey != null) addKeyboardKeyCenter(output, activeKey,
                (segmentStart + previousX) * 0.5f);
    }

    private void addKeyboardKeyCenter(Map<String, List<Float>> output, String key, float center) {
        List<Float> values = output.get(key);
        if (values == null) {
            values = new ArrayList<>();
            output.put(key, values);
        }
        if (values.isEmpty() || Math.abs(values.get(values.size() - 1) - center) > 2f) {
            values.add(center);
        }
    }

    private String keyAtKeyboardPoint(View keyboard, float x, float y) {
        long now = SystemClock.uptimeMillis();
        MotionEvent event = MotionEvent.obtain(now, now, MotionEvent.ACTION_DOWN, x, y, 0);
        try {
            Object button = invoke(keyboard, "v1", event, false);
            if (button == null) button = invoke(keyboard, "v1", event, true);
            KeyInfo info = keyFromButton(keyboard, button);
            return info == null || info.t9 ? null : info.key;
        } catch (Throwable ignored) {
            return null;
        } finally {
            event.recycle();
        }
    }

    private String keyboardLayoutSignature(View keyboard) {
        StringBuilder value = new StringBuilder();
        float[] xs = {0.25f, 0.45f, 0.50f, 0.55f, 0.75f};
        float[] ys = {0.125f, 0.375f, 0.625f};
        for (float y : ys) {
            for (float x : xs) {
                String key = keyAtKeyboardPoint(keyboard,
                        keyboard.getWidth() * x, keyboard.getHeight() * y);
                value.append(key == null ? '_' : key).append('|');
            }
        }
        return value.toString();
    }
'''
replace(hook, old_qwerty, new_qwerty)

replace("app/build.gradle.kts", 'versionName = "1.11.0-test4"', 'versionName = "1.11.0-test5"')
replace("app/src/main/java/com/rww/wetypeswipe/MainActivity.java",
        'v1.11.0-test4 · 按键内功能文字',
        'v1.11.0-test5 · 真实按键边界标注')

print("v1.11.0-test5 real key-bound label patch applied")
