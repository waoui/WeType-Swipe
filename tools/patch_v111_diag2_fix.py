from pathlib import Path
import re
import runpy

runpy.run_path("tools/patch_v111_diag1.py", run_name="__main__")

hook = Path("app/src/main/java/com/rww/wetypeswipe/MainHook.java")
text = hook.read_text(encoding="utf-8")


def replace_once(source: str, old: str, new: str, name: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"{name}: expected 1 match, found {count}")
    return source.replace(old, new, 1)


def replace_between(source: str, start_marker: str, end_marker: str, replacement: str, name: str) -> str:
    start = source.find(start_marker)
    if start < 0:
        raise RuntimeError(f"{name}: start marker missing")
    end = source.find(end_marker, start + len(start_marker))
    if end < 0:
        raise RuntimeError(f"{name}: end marker missing")
    return source[:start] + replacement + source[end:]


text = replace_once(text, "import android.content.ContextWrapper;",
                    "import android.content.ContextWrapper;\nimport android.content.res.Configuration;",
                    "configuration import")

text = replace_once(
    text,
    "    private final Paint keyboardLabelPaint = new Paint(Paint.ANTI_ALIAS_FLAG);",
    "    private final Paint keyboardLabelPaint = new Paint(Paint.ANTI_ALIAS_FLAG);\n"
    "    private volatile WeakReference<View> t9LabelGeometryViewRef = new WeakReference<>(null);\n"
    "    private volatile Map<String, float[]> t9LabelGeometry = new HashMap<>();\n"
    "    private volatile int t9LabelGeometryWidth;\n"
    "    private volatile int t9LabelGeometryHeight;\n"
    "    private volatile String t9LabelGeometrySignature = \"\";\n"
    "    private volatile boolean t9LabelGeometryBuilding;",
    "T9 geometry fields")

text = replace_once(text,
                    '            logInfo("v1.11.0-diag1 entered target package");',
                    '            logInfo("v1.11.0-diag2 entered target package");',
                    "diag2 version log")

paint_replacement = '''    private void prepareKeyboardLabelPaint(View keyboard) {
        float scaledDensity = keyboard.getResources().getDisplayMetrics().scaledDensity;
        float keyHeightBased = keyboard.getHeight() * 0.024f;
        float textSize = Math.max(6.0f * scaledDensity, Math.min(8.4f * scaledDensity, keyHeightBased));
        boolean night = (keyboard.getResources().getConfiguration().uiMode
                & Configuration.UI_MODE_NIGHT_MASK) == Configuration.UI_MODE_NIGHT_YES;
        keyboardLabelPaint.reset();
        keyboardLabelPaint.setAntiAlias(true);
        keyboardLabelPaint.setTextAlign(Paint.Align.CENTER);
        keyboardLabelPaint.setTypeface(Typeface.create(Typeface.DEFAULT, Typeface.BOLD));
        keyboardLabelPaint.setTextSize(textSize);
        if (night) {
            keyboardLabelPaint.setColor(0xEDFFFFFF);
            keyboardLabelPaint.setShadowLayer(Math.max(1f, dp(keyboard, 1)), 0f, 0f, 0xD9000000);
        } else {
            keyboardLabelPaint.setColor(0xC45C626A);
            keyboardLabelPaint.setShadowLayer(Math.max(1f, dp(keyboard, 1)), 0f, 0f, 0xE6FFFFFF);
        }
    }

'''
text = replace_between(text,
                       "    private void prepareKeyboardLabelPaint(View keyboard) {",
                       "    private void drawQwertyFunctionLabels(View keyboard, Canvas canvas, Config config) {",
                       paint_replacement,
                       "paint method")

# Replace only the T9 method; preserve the following draw helpers from diag1.
t9_replacement = '''    private void drawT9FunctionLabels(View keyboard, Canvas canvas, Config config) {
        ensureT9LabelGeometry(keyboard);
        Map<String, float[]> geometry = t9LabelGeometry;
        if (geometry == null || geometry.isEmpty()) return;
        for (int digit = 2; digit <= 9; digit++) {
            int action = config.actionFor(String.valueOf(digit), true);
            if (action == Config.ACTION_NONE || action == Config.ACTION_DISABLE) continue;
            float[] item = geometry.get(String.valueOf(digit));
            if (item == null || item.length < 3) continue;
            drawKeyFunctionText(canvas, shortActionLabel(action), item[0], item[1], item[2]);
        }
    }

    private void ensureT9LabelGeometry(View keyboard) {
        if (keyboard == null || keyboard.getWidth() <= 0 || keyboard.getHeight() <= 0) return;
        String signature = keyboard.getClass().getName() + '@' + keyboard.getWidth() + 'x'
                + keyboard.getHeight();
        boolean sameView = t9LabelGeometryViewRef.get() == keyboard;
        boolean sameSize = t9LabelGeometryWidth == keyboard.getWidth()
                && t9LabelGeometryHeight == keyboard.getHeight();
        if (sameView && sameSize && signature.equals(t9LabelGeometrySignature)
                && t9LabelGeometry != null && !t9LabelGeometry.isEmpty()) return;
        if (t9LabelGeometryBuilding) return;
        t9LabelGeometryBuilding = true;
        keyboard.post(() -> rebuildT9LabelGeometry(keyboard, signature));
    }

    private void rebuildT9LabelGeometry(View keyboard, String signature) {
        try {
            if (keyboard == null || !keyboard.isAttachedToWindow()
                    || keyboard.getWidth() <= 0 || keyboard.getHeight() <= 0) return;
            int width = keyboard.getWidth();
            int height = keyboard.getHeight();
            int stepX = Math.max(dp(keyboard, 5), Math.max(6, width / 54));
            int stepY = Math.max(dp(keyboard, 5), Math.max(6, height / 42));
            Map<String, float[]> bounds = new HashMap<>();
            for (int y = Math.max(1, stepY / 2); y < height; y += stepY) {
                for (int x = Math.max(1, stepX / 2); x < width; x += stepX) {
                    String key = t9KeyAtKeyboardPoint(keyboard, x, y);
                    if (key == null || key.length() != 1 || key.charAt(0) < '1' || key.charAt(0) > '9') continue;
                    float[] item = bounds.get(key);
                    if (item == null) {
                        item = new float[]{x, y, x, y, 1f};
                        bounds.put(key, item);
                    } else {
                        item[0] = Math.min(item[0], x);
                        item[1] = Math.min(item[1], y);
                        item[2] = Math.max(item[2], x);
                        item[3] = Math.max(item[3], y);
                        item[4] += 1f;
                    }
                }
            }
            Map<String, float[]> result = new HashMap<>();
            float[] rowBaseline = new float[]{Float.NaN, Float.NaN, Float.NaN};
            for (int row = 0; row < 3; row++) {
                List<Float> values = new ArrayList<>();
                for (int digit = row * 3 + 1; digit <= row * 3 + 3; digit++) {
                    float[] item = bounds.get(String.valueOf(digit));
                    if (item == null || item[4] < 3f) continue;
                    float keyHeight = Math.max(stepY, item[3] - item[1] + stepY);
                    values.add(item[3] + stepY * 0.5f
                            - Math.max(dp(keyboard, 4), keyHeight * 0.18f));
                }
                if (!values.isEmpty()) {
                    values.sort(Float::compare);
                    rowBaseline[row] = values.get(values.size() / 2);
                }
            }
            for (int digit = 1; digit <= 9; digit++) {
                String key = String.valueOf(digit);
                float[] item = bounds.get(key);
                if (item == null || item[4] < 3f) continue;
                int row = (digit - 1) / 3;
                float centerX = (item[0] + item[2]) * 0.5f;
                float keyWidth = Math.max(stepX, item[2] - item[0] + stepX);
                float baseline = Float.isFinite(rowBaseline[row]) ? rowBaseline[row]
                        : item[3] - Math.max(dp(keyboard, 4), (item[3] - item[1] + stepY) * 0.18f);
                result.put(key, new float[]{centerX, baseline,
                        Math.max(dp(keyboard, 20), keyWidth - dp(keyboard, 8))});
            }
            if (!result.isEmpty()) {
                t9LabelGeometryViewRef = new WeakReference<>(keyboard);
                t9LabelGeometryWidth = width;
                t9LabelGeometryHeight = height;
                t9LabelGeometrySignature = signature;
                t9LabelGeometry = result;
                diagnosticLog("diag-t9-geometry keys=" + result.keySet() + " size=" + width + 'x' + height);
                keyboard.postInvalidate();
            }
        } catch (Throwable throwable) {
            logError("T9 key-label geometry scan failed", throwable);
        } finally {
            t9LabelGeometryBuilding = false;
        }
    }

    private String t9KeyAtKeyboardPoint(View keyboard, float x, float y) {
        long now = SystemClock.uptimeMillis();
        MotionEvent event = MotionEvent.obtain(now, now, MotionEvent.ACTION_DOWN, x, y, 0);
        try {
            Object button = invoke(keyboard, "v1", event, false);
            if (button == null) button = invoke(keyboard, "v1", event, true);
            KeyInfo info = keyFromButton(keyboard, button);
            return info == null || !info.t9 ? null : info.key;
        } catch (Throwable ignored) {
            return null;
        } finally {
            event.recycle();
        }
    }

'''
text = replace_between(text,
                       "    private void drawT9FunctionLabels(View keyboard, Canvas canvas, Config config) {",
                       "    private void drawKeyFunctionText(Canvas canvas, String text, float x, float baseline) {",
                       t9_replacement,
                       "T9 draw method")

diag_replacement = '''    private static boolean diagnosticMethodCandidate(Method method) {
        if (method == null || method.isSynthetic() || method.isBridge()) return false;
        String owner = method.getDeclaringClass().getName();
        if (!owner.startsWith("com.tencent.wetype.plugin.hld.keyboard.selfdraw")) return false;
        String name = method.getName();
        if (name.equals("getButtonDrawer") || name.equals("getKeysLayoutInfo")
                || name.equals("getKeyIdsForLayoutInfo") || name.equals("x1")
                || name.equals("E2") || name.equals("m1") || name.equals("n1")
                || name.equals("o1") || name.equals("draw") || name.equals("i")) return true;
        for (Class<?> parameter : method.getParameterTypes()) {
            if (parameter == Canvas.class || parameter == Paint.class
                    || parameter == Rect.class || parameter == RectF.class) return true;
        }
        return false;
    }

'''
text = replace_between(text,
                       "    private static boolean diagnosticMethodCandidate(Method method) {",
                       "    private static boolean diagnosticTencentType(Class<?> type) {",
                       diag_replacement,
                       "diagnostic candidate method")

text = text.replace("nativeDiagnosticLogBudget = 260", "nativeDiagnosticLogBudget = 160")
hook.write_text(text, encoding="utf-8")

build = Path("app/build.gradle.kts")
build_text = build.read_text(encoding="utf-8")
build_text, code_count = re.subn(r'versionCode\s*=\s*\d+', 'versionCode = 30', build_text, count=1)
build_text, name_count = re.subn(r'versionName\s*=\s*"[^"]+"', 'versionName = "1.11.0-diag2"', build_text, count=1)
if code_count != 1 or name_count != 1:
    raise RuntimeError(f"version update failed: code={code_count}, name={name_count}")
build.write_text(build_text, encoding="utf-8")

activity = Path("app/src/main/java/com/rww/wetypeswipe/MainActivity.java")
activity_text = activity.read_text(encoding="utf-8")
activity_text, activity_count = re.subn(r'v1\.11\.0-diag1 · 原生按键模型诊断',
                                        'v1.11.0-diag2 · 深色与九宫格诊断',
                                        activity_text, count=1)
if activity_count != 1:
    raise RuntimeError(f"activity version update failed: {activity_count}")
activity.write_text(activity_text, encoding="utf-8")

print("v1.11.0-diag2 robust theme-aware and T9 geometry patch applied")
