from pathlib import Path
import re
import runpy

# Start from the stable row-fit implementation. This patch replaces its geometry
# source with WeType's own getKeysLayoutInfo() drawRect array. The row-fit scan
# remains available as a QWERTY fallback for unknown future layouts.
runpy.run_path("tools/patch_v111_test10.py", run_name="__main__")

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


text = replace_once(
    text,
    "import android.content.ContextWrapper;",
    "import android.content.ContextWrapper;\nimport android.content.res.Configuration;",
    "configuration import")

text = replace_once(
    text,
    "    private final Paint keyboardLabelPaint = new Paint(Paint.ANTI_ALIAS_FLAG);",
    "    private final Paint keyboardLabelPaint = new Paint(Paint.ANTI_ALIAS_FLAG);\n"
    "    private volatile WeakReference<View> nativeLabelGeometryViewRef = new WeakReference<>(null);\n"
    "    private volatile Map<String, float[]> nativeLabelGeometry = new HashMap<>();\n"
    "    private volatile int nativeLabelGeometryWidth;\n"
    "    private volatile int nativeLabelGeometryHeight;\n"
    "    private volatile String nativeLabelGeometryClass = \"\";\n"
    "    private volatile boolean nativeLabelGeometryBuilding;\n"
    "    private volatile boolean nativeLabelGeometryUnavailable;",
    "native geometry fields")

text = replace_once(
    text,
    '            logInfo("v1.11.0-test10 entered target package");',
    '            logInfo("v1.11.0-test11 entered target package");',
    "version log")

paint_replacement = '''    private void prepareKeyboardLabelPaint(View keyboard) {
        float scaledDensity = keyboard.getResources().getDisplayMetrics().scaledDensity;
        float estimatedKeyHeight = keyboard.getHeight() / 4f;
        float keyHeightBased = estimatedKeyHeight * 0.145f;
        float textSize = Math.max(5.8f * scaledDensity, Math.min(8.0f * scaledDensity, keyHeightBased));
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
text = replace_between(
    text,
    "    private void prepareKeyboardLabelPaint(View keyboard) {",
    "    private void drawQwertyFunctionLabels(View keyboard, Canvas canvas, Config config) {",
    paint_replacement,
    "theme-aware paint")

# Prefer native drawRect geometry. Keep row-fit fallback for future versions where
# getKeysLayoutInfo() is missing or changes shape.
text = replace_once(
    text,
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
''',
    '''    private void drawQwertyFunctionLabels(View keyboard, Canvas canvas, Config config) {
        ensureNativeKeyboardLabelGeometry(keyboard);
        Map<String, float[]> nativeGeometry = nativeLabelGeometry;
        if (nativeGeometry != null && !nativeGeometry.isEmpty()) {
            drawNativeFunctionLabels(canvas, config, "qwertyuiopasdfghjklzxcvbnm", false);
            return;
        }
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
''',
    "native qwerty draw")

text = replace_once(
    text,
    '''    private void drawT9FunctionLabels(View keyboard, Canvas canvas, Config config) {
        int width = keyboard.getWidth();
        float rowHeight = keyboard.getHeight() / 4f;
        float bottomGap = Math.max(dp(keyboard, 4), rowHeight * 0.18f);
        for (int digit = 2; digit <= 9; digit++) {
            int action = config.actionFor(String.valueOf(digit), true);
            if (action == Config.ACTION_NONE || action == Config.ACTION_DISABLE) continue;
            int zeroBased = digit - 1;
            int row = zeroBased / 3;
            int column = zeroBased % 3;
            float x = width * ((column + 0.5f) / 3f);
            float baseline = rowHeight * (row + 1f) - bottomGap;
            drawKeyFunctionText(canvas, shortActionLabel(action), x, baseline);
        }
    }
''',
    '''    private void drawT9FunctionLabels(View keyboard, Canvas canvas, Config config) {
        ensureNativeKeyboardLabelGeometry(keyboard);
        Map<String, float[]> nativeGeometry = nativeLabelGeometry;
        if (nativeGeometry == null || nativeGeometry.isEmpty()) return;
        drawNativeFunctionLabels(canvas, config, "123456789", true);
    }
''',
    "native T9 draw")

helpers = r'''    private void ensureNativeKeyboardLabelGeometry(View keyboard) {
        if (keyboard == null || keyboard.getWidth() <= 0 || keyboard.getHeight() <= 0) return;
        boolean sameView = nativeLabelGeometryViewRef.get() == keyboard;
        boolean sameSize = nativeLabelGeometryWidth == keyboard.getWidth()
                && nativeLabelGeometryHeight == keyboard.getHeight();
        String className = keyboard.getClass().getName();
        boolean sameClass = className.equals(nativeLabelGeometryClass);
        if (sameView && sameSize && sameClass
                && (nativeLabelGeometryUnavailable || !nativeLabelGeometry.isEmpty())) return;
        if (nativeLabelGeometryBuilding) return;
        nativeLabelGeometryBuilding = true;
        keyboard.post(() -> rebuildNativeKeyboardLabelGeometry(keyboard, className));
    }

    private void rebuildNativeKeyboardLabelGeometry(View keyboard, String expectedClass) {
        try {
            if (keyboard == null || !keyboard.isAttachedToWindow()
                    || keyboard.getWidth() <= 0 || keyboard.getHeight() <= 0) return;
            Method idsMethod = findMethod(keyboard.getClass(), "getKeyIdsForLayoutInfo", new Class<?>[0]);
            Method layoutMethod = findMethod(keyboard.getClass(), "getKeysLayoutInfo", new Class<?>[0]);
            if (idsMethod == null || layoutMethod == null) {
                publishNativeKeyboardLabelGeometry(keyboard, expectedClass, new HashMap<>(), false);
                return;
            }
            idsMethod.setAccessible(true);
            layoutMethod.setAccessible(true);
            Object idsValue = idsMethod.invoke(keyboard);
            Object pair = layoutMethod.invoke(keyboard);
            if (!(idsValue instanceof String[]) || pair == null) {
                publishNativeKeyboardLabelGeometry(keyboard, expectedClass, new HashMap<>(), false);
                return;
            }
            String[] ids = (String[]) idsValue;
            Object drawItems = readNamedField(pair, "first");
            if (drawItems == null || !drawItems.getClass().isArray()) {
                Object first = invokeNoArg(pair, "a");
                if (first != null && first.getClass().isArray()) drawItems = first;
            }
            if (drawItems == null || !drawItems.getClass().isArray()) {
                publishNativeKeyboardLabelGeometry(keyboard, expectedClass, new HashMap<>(), false);
                return;
            }
            int count = Math.min(ids.length, java.lang.reflect.Array.getLength(drawItems));
            Map<String, float[]> raw = new HashMap<>();
            for (int index = 0; index < count; index++) {
                String key = keyFromNativeLayoutId(ids[index]);
                if (key == null) continue;
                Object item = java.lang.reflect.Array.get(drawItems, index);
                if (item == null) continue;
                Integer left = integerField(item, "x_left");
                Integer right = integerField(item, "x_right");
                Integer top = integerField(item, "y_top");
                Integer bottom = integerField(item, "y_bottom");
                if (left == null || right == null || top == null || bottom == null
                        || right <= left || bottom <= top) continue;
                raw.put(key, new float[]{left, top, right, bottom});
            }
            Map<String, float[]> result = buildNativeLabelGeometry(keyboard, raw);
            publishNativeKeyboardLabelGeometry(keyboard, expectedClass, result, true);
        } catch (Throwable throwable) {
            logError("native key draw-rect geometry failed", throwable);
            publishNativeKeyboardLabelGeometry(keyboard, expectedClass, new HashMap<>(), false);
        } finally {
            nativeLabelGeometryBuilding = false;
        }
    }

    private void publishNativeKeyboardLabelGeometry(View keyboard, String className,
                                                     Map<String, float[]> result,
                                                     boolean nativeAvailable) {
        nativeLabelGeometryViewRef = new WeakReference<>(keyboard);
        nativeLabelGeometryWidth = keyboard.getWidth();
        nativeLabelGeometryHeight = keyboard.getHeight();
        nativeLabelGeometryClass = className == null ? "" : className;
        nativeLabelGeometry = result == null ? new HashMap<>() : result;
        nativeLabelGeometryUnavailable = !nativeAvailable || nativeLabelGeometry.isEmpty();
        if (!nativeLabelGeometry.isEmpty()) {
            logInfo("native key draw-rect geometry ready keys=" + nativeLabelGeometry.size()
                    + " size=" + keyboard.getWidth() + 'x' + keyboard.getHeight());
            keyboard.postInvalidate();
        }
    }

    private Map<String, float[]> buildNativeLabelGeometry(View keyboard,
                                                           Map<String, float[]> raw) {
        Map<String, float[]> output = new HashMap<>();
        if (raw == null || raw.isEmpty()) return output;
        addNativeLabelRow(keyboard, raw, output, "qwertyuiop");
        addNativeLabelRow(keyboard, raw, output, "asdfghjkl");
        addNativeLabelRow(keyboard, raw, output, "zxcvbnm");
        addNativeLabelRow(keyboard, raw, output, "123");
        addNativeLabelRow(keyboard, raw, output, "456");
        addNativeLabelRow(keyboard, raw, output, "789");
        return output;
    }

    private void addNativeLabelRow(View keyboard, Map<String, float[]> raw,
                                   Map<String, float[]> output, String keys) {
        List<Float> bottoms = new ArrayList<>();
        List<Float> heights = new ArrayList<>();
        for (int index = 0; index < keys.length(); index++) {
            float[] rect = raw.get(String.valueOf(keys.charAt(index)));
            if (rect == null || rect.length < 4) continue;
            bottoms.add(rect[3]);
            heights.add(rect[3] - rect[1]);
        }
        if (bottoms.isEmpty()) return;
        bottoms.sort(Float::compare);
        heights.sort(Float::compare);
        float rowBottom = bottoms.get(bottoms.size() / 2);
        float rowHeight = heights.get(heights.size() / 2);
        float baseline = rowBottom - Math.max(dp(keyboard, 4), rowHeight * 0.18f);
        for (int index = 0; index < keys.length(); index++) {
            String key = String.valueOf(keys.charAt(index));
            float[] rect = raw.get(key);
            if (rect == null || rect.length < 4) continue;
            float centerX = (rect[0] + rect[2]) * 0.5f;
            float width = rect[2] - rect[0];
            output.put(key, new float[]{centerX, baseline, width});
        }
    }

    private void drawNativeFunctionLabels(Canvas canvas, Config config,
                                          String keys, boolean t9) {
        Map<String, float[]> geometry = nativeLabelGeometry;
        if (geometry == null || geometry.isEmpty()) return;
        for (int index = 0; index < keys.length(); index++) {
            String key = String.valueOf(keys.charAt(index));
            int action = config.actionFor(key, t9);
            if (action == Config.ACTION_NONE || action == Config.ACTION_DISABLE) continue;
            float[] item = geometry.get(key);
            if (item == null || item.length < 2) continue;
            drawKeyFunctionText(canvas, shortActionLabel(action), item[0], item[1]);
        }
    }

    private static String keyFromNativeLayoutId(String id) {
        if (id == null) return null;
        int marker = id.lastIndexOf("_key_");
        String key = marker >= 0 ? id.substring(marker + 5) : id;
        if (key.length() != 1) return null;
        char value = Character.toLowerCase(key.charAt(0));
        if ((value >= 'a' && value <= 'z') || (value >= '1' && value <= '9')) {
            return String.valueOf(value);
        }
        return null;
    }

    private static Integer integerField(Object object, String name) {
        Object value = readNamedField(object, name);
        return value instanceof Number ? ((Number) value).intValue() : null;
    }

    private static Object invokeNoArg(Object object, String name) {
        if (object == null || name == null) return null;
        for (Class<?> current = object.getClass(); current != null; current = current.getSuperclass()) {
            try {
                Method method = current.getDeclaredMethod(name);
                method.setAccessible(true);
                return method.invoke(object);
            } catch (NoSuchMethodException ignored) {
            } catch (Throwable ignored) {
                return null;
            }
        }
        return null;
    }

'''
marker = "    private Map<String, List<Float>> fitKeyboardLabelRows("
if text.count(marker) != 1:
    raise RuntimeError(f"native helper insertion marker: expected 1 match, found {text.count(marker)}")
text = text.replace(marker, helpers + marker, 1)

hook.write_text(text, encoding="utf-8")

build = Path("app/build.gradle.kts")
build_text = build.read_text(encoding="utf-8")
build_text, code_count = re.subn(r'versionCode\s*=\s*\d+', 'versionCode = 32', build_text, count=1)
build_text, name_count = re.subn(r'versionName\s*=\s*"[^"]+"', 'versionName = "1.11.0-test11"', build_text, count=1)
if code_count != 1 or name_count != 1:
    raise RuntimeError(f"version update failed: code={code_count}, name={name_count}")
build.write_text(build_text, encoding="utf-8")

activity = Path("app/src/main/java/com/rww/wetypeswipe/MainActivity.java")
activity_text = activity.read_text(encoding="utf-8")
activity_text, activity_count = re.subn(
    r'v1\.11\.0-test10 · 行列拟合按键标注',
    'v1.11.0-test11 · 原生键帽坐标标注',
    activity_text,
    count=1)
if activity_count != 1:
    raise RuntimeError(f"activity version update failed: {activity_count}")
activity.write_text(activity_text, encoding="utf-8")

print("v1.11.0-test11 native draw-rect label geometry patch applied")
