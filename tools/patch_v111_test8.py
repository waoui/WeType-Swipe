from pathlib import Path
import runpy

runpy.run_path("tools/patch_v111_test7.py", run_name="__main__")


def replace(path: str, old: str, new: str, count: int = 1) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    actual = text.count(old)
    if actual != count:
        raise RuntimeError(f"{path}: expected {count} matches, found {actual}: {old[:180]!r}")
    file.write_text(text.replace(old, new, count), encoding="utf-8")


hook = "app/src/main/java/com/rww/wetypeswipe/MainHook.java"

replace(hook,
        "import android.graphics.Paint;\nimport android.graphics.Typeface;",
        "import android.graphics.Paint;\nimport android.graphics.Rect;\nimport android.graphics.RectF;\nimport android.graphics.Typeface;")

replace(hook,
        "    private volatile Map<String, List<Float>> keyboardLabelCenters = new HashMap<>();",
        "    private volatile Map<String, List<Float>> keyboardLabelCenters = new HashMap<>();\n"
        "    private volatile Map<String, List<KeyLabelBounds>> keyboardLabelBounds = new HashMap<>();")

replace(hook,
        '            logInfo("v1.11.0-test7 entered target package");',
        '            logInfo("v1.11.0-test8 entered target package");')

old_row = '''    private void drawQwertyRow(View keyboard, Canvas canvas, Config config,
                                 String keys, float baseline) {
        Map<String, List<Float>> centers = keyboardLabelCenters;
        if (centers == null || centers.isEmpty()) return;
        int width = Math.max(1, keyboard.getWidth());
        float leftEdgeCorrection = Math.max(dp(keyboard, 5), Math.min(dp(keyboard, 9), width * 0.012f));
        for (int index = 0; index < keys.length(); index++) {
            String key = String.valueOf(keys.charAt(index));
            int action = config.actionFor(key, false);
            if (action == Config.ACTION_NONE || action == Config.ACTION_DISABLE) continue;
            List<Float> positions = centers.get(key);
            if (positions == null) continue;
            for (Float position : positions) {
                if (position == null) continue;
                float x = position;
                // The hit-test region of the leftmost A key extends into the
                // keyboard edge gutter. Its geometric center is therefore left
                // of the visible keycap center. Correct only that edge instance.
                if ("a".equals(key) && x < width * 0.18f) {
                    x += leftEdgeCorrection;
                }
                drawKeyFunctionText(canvas, shortActionLabel(action), x, baseline);
            }
        }
    }
'''

new_row = '''    private void drawQwertyRow(View keyboard, Canvas canvas, Config config,
                                 String keys, float baseline) {
        Map<String, List<KeyLabelBounds>> boundsMap = keyboardLabelBounds;
        Map<String, List<Float>> centers = keyboardLabelCenters;
        if ((boundsMap == null || boundsMap.isEmpty())
                && (centers == null || centers.isEmpty())) return;
        for (int index = 0; index < keys.length(); index++) {
            String key = String.valueOf(keys.charAt(index));
            int action = config.actionFor(key, false);
            if (action == Config.ACTION_NONE || action == Config.ACTION_DISABLE) continue;
            String label = shortActionLabel(action);
            List<KeyLabelBounds> keyBounds = boundsMap == null ? null : boundsMap.get(key);
            if (keyBounds != null && !keyBounds.isEmpty()) {
                for (KeyLabelBounds bounds : keyBounds) {
                    if (bounds == null) continue;
                    drawKeyFunctionText(canvas, label, bounds.centerX(), bounds.baseline,
                            Math.max(dp(keyboard, 14), bounds.width() - dp(keyboard, 6)));
                }
                continue;
            }
            List<Float> positions = centers == null ? null : centers.get(key);
            if (positions == null) continue;
            for (Float x : positions) {
                if (x != null) drawKeyFunctionText(canvas, label, x, baseline);
            }
        }
    }
'''
replace(hook, old_row, new_row)

replace(hook,
'''                keyboardLabelLayoutSignature = expectedSignature;
                keyboardLabelCenters = result;
                keyboard.postInvalidate();
''',
'''                keyboardLabelLayoutSignature = expectedSignature;
                keyboardLabelCenters = result;
                keyboardLabelBounds = buildKeyboardLabelBounds(keyboard, result);
                keyboard.postInvalidate();
''')

insert_before = "    private void ensureKeyboardLabelGeometry(View keyboard) {"
helpers = r'''    private Map<String, List<KeyLabelBounds>> buildKeyboardLabelBounds(
            View keyboard, Map<String, List<Float>> centers) {
        Map<String, List<KeyLabelBounds>> output = new HashMap<>();
        if (keyboard == null || centers == null || centers.isEmpty()) return output;
        addKeyboardRowBounds(keyboard, centers, output, "qwertyuiop", 0);
        addKeyboardRowBounds(keyboard, centers, output, "asdfghjkl", 1);
        addKeyboardRowBounds(keyboard, centers, output, "zxcvbnm", 2);
        return output;
    }

    private void addKeyboardRowBounds(View keyboard, Map<String, List<Float>> centers,
                                      Map<String, List<KeyLabelBounds>> output,
                                      String keys, int row) {
        float rowHeight = keyboard.getHeight() / 4f;
        float rowTop = rowHeight * row;
        float rowBottom = rowTop + rowHeight;
        float sampleY = rowTop + rowHeight * 0.50f;
        float spacing = medianKeyboardRowSpacing(centers, keys);
        if (spacing <= 0f) spacing = keyboard.getWidth() / 10f;
        float inferredWidth = Math.max(dp(keyboard, 24), spacing * 0.84f);
        float bottomRatio = row == 0 ? 0.18f : (row == 1 ? 0.19f : 0.20f);
        float fallbackBaseline = rowBottom - Math.max(dp(keyboard, 4), rowHeight * bottomRatio);

        for (int index = 0; index < keys.length(); index++) {
            String key = String.valueOf(keys.charAt(index));
            List<Float> positions = centers.get(key);
            if (positions == null || positions.isEmpty()) continue;
            List<KeyLabelBounds> keyOutput = output.get(key);
            if (keyOutput == null) {
                keyOutput = new ArrayList<>();
                output.put(key, keyOutput);
            }
            for (Float value : positions) {
                if (value == null) continue;
                float center = inferVisualKeyCenter(centers, keys, index, value, spacing);
                RectF nativeRect = nativeKeyRectAt(keyboard, center, sampleY);
                if (nativeRect != null) {
                    float baseline = nativeRect.bottom
                            - Math.max(dp(keyboard, 3), nativeRect.height() * 0.16f);
                    keyOutput.add(new KeyLabelBounds(nativeRect.left, nativeRect.top,
                            nativeRect.right, nativeRect.bottom, baseline, true));
                } else {
                    keyOutput.add(new KeyLabelBounds(center - inferredWidth * 0.5f, rowTop,
                            center + inferredWidth * 0.5f, rowBottom,
                            fallbackBaseline, false));
                }
            }
        }
    }

    private float inferVisualKeyCenter(Map<String, List<Float>> centers, String keys,
                                       int index, float measuredCenter, float spacing) {
        if (index == 0 && keys.length() >= 3) {
            Float next = firstKeyboardPosition(centers.get(String.valueOf(keys.charAt(1))));
            Float nextNext = firstKeyboardPosition(centers.get(String.valueOf(keys.charAt(2))));
            if (next != null && nextNext != null && nextNext > next) {
                float predicted = next - (nextNext - next);
                if (Math.abs(predicted - measuredCenter) > spacing * 0.10f) return predicted;
            }
        } else if (index == keys.length() - 1 && keys.length() >= 3) {
            Float previous = lastKeyboardPosition(
                    centers.get(String.valueOf(keys.charAt(keys.length() - 2))));
            Float previousPrevious = lastKeyboardPosition(
                    centers.get(String.valueOf(keys.charAt(keys.length() - 3))));
            if (previous != null && previousPrevious != null && previous > previousPrevious) {
                float predicted = previous + (previous - previousPrevious);
                if (Math.abs(predicted - measuredCenter) > spacing * 0.10f) return predicted;
            }
        }
        return measuredCenter;
    }

    private float medianKeyboardRowSpacing(Map<String, List<Float>> centers, String keys) {
        List<Float> gaps = new ArrayList<>();
        for (int index = 0; index < keys.length() - 1; index++) {
            List<Float> left = centers.get(String.valueOf(keys.charAt(index)));
            List<Float> right = centers.get(String.valueOf(keys.charAt(index + 1)));
            float gap = nearestPositiveKeyboardGap(left, right);
            if (gap > 0f) gaps.add(gap);
        }
        if (gaps.isEmpty()) return 0f;
        java.util.Collections.sort(gaps);
        return gaps.get(gaps.size() / 2);
    }

    private float nearestPositiveKeyboardGap(List<Float> left, List<Float> right) {
        if (left == null || right == null) return 0f;
        float best = Float.MAX_VALUE;
        for (Float l : left) {
            if (l == null) continue;
            for (Float r : right) {
                if (r == null) continue;
                float gap = r - l;
                if (gap > 0f && gap < best) best = gap;
            }
        }
        return best == Float.MAX_VALUE ? 0f : best;
    }

    private static Float firstKeyboardPosition(List<Float> values) {
        if (values == null || values.isEmpty()) return null;
        Float result = null;
        for (Float value : values) {
            if (value != null && (result == null || value < result)) result = value;
        }
        return result;
    }

    private static Float lastKeyboardPosition(List<Float> values) {
        if (values == null || values.isEmpty()) return null;
        Float result = null;
        for (Float value : values) {
            if (value != null && (result == null || value > result)) result = value;
        }
        return result;
    }

    private RectF nativeKeyRectAt(View keyboard, float x, float y) {
        Object button = keyboardButtonAtPoint(keyboard, x, y);
        if (button == null) return null;
        java.util.IdentityHashMap<Object, Boolean> visited = new java.util.IdentityHashMap<>();
        return findNativeKeyRect(button, keyboard.getWidth(), keyboard.getHeight(), x, y, 0, visited);
    }

    private Object keyboardButtonAtPoint(View keyboard, float x, float y) {
        long now = SystemClock.uptimeMillis();
        MotionEvent event = MotionEvent.obtain(now, now, MotionEvent.ACTION_DOWN, x, y, 0);
        try {
            Object button = invoke(keyboard, "v1", event, false);
            if (button == null) button = invoke(keyboard, "v1", event, true);
            return button;
        } catch (Throwable ignored) {
            return null;
        } finally {
            event.recycle();
        }
    }

    private RectF findNativeKeyRect(Object object, int keyboardWidth, int keyboardHeight,
                                    float sampleX, float sampleY, int depth,
                                    java.util.IdentityHashMap<Object, Boolean> visited) {
        if (object == null || depth > 2 || visited.put(object, Boolean.TRUE) != null) return null;
        RectF direct = validNativeKeyRect(object, keyboardWidth, keyboardHeight, sampleX, sampleY);
        if (direct != null) return direct;
        for (Class<?> current = object.getClass(); current != null && current != Object.class;
             current = current.getSuperclass()) {
            for (Field field : current.getDeclaredFields()) {
                try {
                    field.setAccessible(true);
                    Object value = field.get(object);
                    RectF rect = validNativeKeyRect(value, keyboardWidth, keyboardHeight, sampleX, sampleY);
                    if (rect != null) return rect;
                    if (depth < 2 && value != null) {
                        String typeName = value.getClass().getName();
                        if (typeName.startsWith("com.tencent.wetype")
                                || typeName.startsWith("com.tencent.mm")) {
                            rect = findNativeKeyRect(value, keyboardWidth, keyboardHeight,
                                    sampleX, sampleY, depth + 1, visited);
                            if (rect != null) return rect;
                        }
                    }
                } catch (Throwable ignored) {
                }
            }
        }
        return null;
    }

    private RectF validNativeKeyRect(Object value, int keyboardWidth, int keyboardHeight,
                                     float sampleX, float sampleY) {
        RectF rect;
        if (value instanceof RectF) {
            rect = new RectF((RectF) value);
        } else if (value instanceof Rect) {
            Rect source = (Rect) value;
            rect = new RectF(source.left, source.top, source.right, source.bottom);
        } else {
            return null;
        }
        float width = rect.width();
        float height = rect.height();
        if (width < keyboardWidth * 0.035f || width > keyboardWidth * 0.24f
                || height < keyboardHeight * 0.07f || height > keyboardHeight * 0.36f) return null;
        if (rect.left < -keyboardWidth * 0.05f || rect.right > keyboardWidth * 1.05f
                || rect.top < -keyboardHeight * 0.05f || rect.bottom > keyboardHeight * 1.05f) return null;
        float toleranceX = width * 0.35f;
        float toleranceY = height * 0.35f;
        if (sampleX < rect.left - toleranceX || sampleX > rect.right + toleranceX
                || sampleY < rect.top - toleranceY || sampleY > rect.bottom + toleranceY) return null;
        return rect;
    }

    private static final class KeyLabelBounds {
        final float left;
        final float top;
        final float right;
        final float bottom;
        final float baseline;
        final boolean nativeBounds;

        KeyLabelBounds(float left, float top, float right, float bottom,
                       float baseline, boolean nativeBounds) {
            this.left = left;
            this.top = top;
            this.right = right;
            this.bottom = bottom;
            this.baseline = baseline;
            this.nativeBounds = nativeBounds;
        }

        float centerX() {
            return (left + right) * 0.5f;
        }

        float width() {
            return Math.max(0f, right - left);
        }
    }

'''
replace(hook, insert_before, helpers + insert_before)

old_draw = '''    private void drawKeyFunctionText(Canvas canvas, String text, float x, float baseline) {
        if (text == null || text.isEmpty()) return;
        float originalSize = keyboardLabelPaint.getTextSize();
        float scale = text.length() >= 4 ? 0.78f : (text.length() == 3 ? 0.88f : 1f);
        keyboardLabelPaint.setTextSize(originalSize * scale);
        Paint.FontMetrics metrics = keyboardLabelPaint.getFontMetrics();
        float safeBaseline = Math.max(-metrics.ascent + 1f, baseline);
        canvas.drawText(text, x, safeBaseline, keyboardLabelPaint);
        keyboardLabelPaint.setTextSize(originalSize);
    }
'''
new_draw = '''    private void drawKeyFunctionText(Canvas canvas, String text, float x, float baseline) {
        drawKeyFunctionText(canvas, text, x, baseline, Float.MAX_VALUE);
    }

    private void drawKeyFunctionText(Canvas canvas, String text, float x, float baseline,
                                     float maximumWidth) {
        if (text == null || text.isEmpty()) return;
        float originalSize = keyboardLabelPaint.getTextSize();
        float scale = text.length() >= 4 ? 0.78f : (text.length() == 3 ? 0.88f : 1f);
        keyboardLabelPaint.setTextSize(originalSize * scale);
        if (maximumWidth < Float.MAX_VALUE) {
            float measured = keyboardLabelPaint.measureText(text);
            if (measured > maximumWidth && measured > 0f) {
                keyboardLabelPaint.setTextSize(keyboardLabelPaint.getTextSize()
                        * Math.max(0.68f, maximumWidth / measured));
            }
        }
        Paint.FontMetrics metrics = keyboardLabelPaint.getFontMetrics();
        float safeBaseline = Math.max(-metrics.ascent + 1f, baseline);
        canvas.drawText(text, x, safeBaseline, keyboardLabelPaint);
        keyboardLabelPaint.setTextSize(originalSize);
    }
'''
replace(hook, old_draw, new_draw)

replace("app/build.gradle.kts", "versionCode = 25", "versionCode = 26")
replace("app/build.gradle.kts", 'versionName = "1.11.0-test7"', 'versionName = "1.11.0-test8"')
replace("app/src/main/java/com/rww/wetypeswipe/MainActivity.java",
        'v1.11.0-test7 · 边缘按键位置修正',
        'v1.11.0-test8 · 原生键帽边界优先')

print("v1.11.0-test8 native key-bounds cache patch applied")
