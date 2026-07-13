from pathlib import Path
import re
import runpy

# Start from the last stable visual baseline. test8/test9 Rect probing is
# intentionally excluded because it can confuse touch hit boxes with keycaps.
runpy.run_path("tools/patch_v111_test6.py", run_name="__main__")

hook = Path("app/src/main/java/com/rww/wetypeswipe/MainHook.java")
text = hook.read_text(encoding="utf-8")


def replace_once(source: str, old: str, new: str, name: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"{name}: expected 1 match, found {count}")
    return source.replace(old, new, 1)


text = replace_once(
    text,
    '            logInfo("v1.11.0-test6 entered target package");',
    '            logInfo("v1.11.0-test10 entered target package");',
    "version log")

# Keep disabled bindings functional but omit their persistent labels.
text = replace_once(
    text,
    "            if (action == Config.ACTION_NONE) continue;\n            List<Float> positions = centers.get(key);",
    "            if (action == Config.ACTION_NONE || action == Config.ACTION_DISABLE) continue;\n"
    "            List<Float> positions = centers.get(key);",
    "qwerty disabled label")
text = replace_once(
    text,
    "            if (action == Config.ACTION_NONE) continue;\n            int zeroBased = digit - 1;",
    "            if (action == Config.ACTION_NONE || action == Config.ACTION_DISABLE) continue;\n"
    "            int zeroBased = digit - 1;",
    "t9 disabled label")
text = replace_once(
    text,
    '            case Config.ACTION_DISABLE: return "禁用";',
    '            case Config.ACTION_DISABLE: return "";',
    "disabled short label")

# Convert raw hit-test centers into stable row models once per layout rebuild.
text = replace_once(
    text,
    "                keyboardLabelCenters = result;\n                keyboard.postInvalidate();",
    "                keyboardLabelCenters = fitKeyboardLabelRows(result, keyboard.getWidth());\n"
    "                keyboard.postInvalidate();",
    "fitted geometry assignment")

helpers = r'''    private Map<String, List<Float>> fitKeyboardLabelRows(
            Map<String, List<Float>> measured, int keyboardWidth) {
        Map<String, List<Float>> fitted = new HashMap<>();
        if (measured == null || measured.isEmpty()) return fitted;
        fitKeyboardLabelRow(measured, fitted, "qwertyuiop", keyboardWidth);
        fitKeyboardLabelRow(measured, fitted, "asdfghjkl", keyboardWidth);
        fitKeyboardLabelRow(measured, fitted, "zxcvbnm", keyboardWidth);
        return fitted.isEmpty() ? measured : fitted;
    }

    private void fitKeyboardLabelRow(Map<String, List<Float>> measured,
                                     Map<String, List<Float>> output,
                                     String keys, int keyboardWidth) {
        List<KeyRowPoint> points = new ArrayList<>();
        for (int index = 0; index < keys.length(); index++) {
            String key = String.valueOf(keys.charAt(index));
            List<Float> values = measured.get(key);
            if (values == null) continue;
            for (Float value : values) {
                if (value != null && Float.isFinite(value)) {
                    points.add(new KeyRowPoint(index, key, value));
                }
            }
        }
        if (points.size() < 2) {
            copyMeasuredKeyboardRow(measured, output, keys);
            return;
        }
        points.sort((left, right) -> Float.compare(left.x, right.x));

        List<Float> gaps = new ArrayList<>();
        float largestGap = 0f;
        int largestGapIndex = -1;
        for (int index = 0; index < points.size() - 1; index++) {
            float gap = points.get(index + 1).x - points.get(index).x;
            if (gap > 1f) gaps.add(gap);
            if (gap > largestGap) {
                largestGap = gap;
                largestGapIndex = index;
            }
        }
        float medianGap = medianPositiveValues(gaps);
        boolean split = largestGapIndex >= 1
                && largestGapIndex < points.size() - 2
                && medianGap > 0f
                && largestGap > medianGap * 1.80f
                && largestGap > keyboardWidth * 0.085f;

        if (split) {
            fitKeyboardPointCluster(points.subList(0, largestGapIndex + 1), output, keys);
            fitKeyboardPointCluster(points.subList(largestGapIndex + 1, points.size()), output, keys);
        } else {
            fitKeyboardPointCluster(points, output, keys);
        }
    }

    private void fitKeyboardPointCluster(List<KeyRowPoint> cluster,
                                         Map<String, List<Float>> output,
                                         String keys) {
        if (cluster == null || cluster.size() < 2) return;
        List<KeyRowPoint> sorted = new ArrayList<>(cluster);
        sorted.sort((left, right) -> Float.compare(left.x, right.x));

        // Edge hit regions are frequently wider than the visible keycaps. Fit
        // from the interior points whenever possible, then extrapolate edges.
        int from = sorted.size() >= 4 ? 1 : 0;
        int to = sorted.size() >= 4 ? sorted.size() - 1 : sorted.size();
        if (to - from < 2) {
            from = 0;
            to = sorted.size();
        }

        float count = 0f;
        float sumIndex = 0f;
        float sumX = 0f;
        float sumIndexSquared = 0f;
        float sumIndexX = 0f;
        for (int position = from; position < to; position++) {
            KeyRowPoint point = sorted.get(position);
            count += 1f;
            sumIndex += point.index;
            sumX += point.x;
            sumIndexSquared += point.index * point.index;
            sumIndexX += point.index * point.x;
        }
        float denominator = count * sumIndexSquared - sumIndex * sumIndex;
        float slope = denominator == 0f ? 0f
                : (count * sumIndexX - sumIndex * sumX) / denominator;
        float intercept = count == 0f ? 0f : (sumX - slope * sumIndex) / count;

        if (!Float.isFinite(slope) || slope <= 0f) {
            slope = medianClusterSlope(sorted);
            KeyRowPoint anchor = sorted.get(sorted.size() / 2);
            intercept = anchor.x - slope * anchor.index;
        }
        if (!Float.isFinite(slope) || slope <= 0f || !Float.isFinite(intercept)) {
            for (KeyRowPoint point : sorted) addFittedKeyboardCenter(output, point.key, point.x);
            return;
        }

        int minimumIndex = keys.length() - 1;
        int maximumIndex = 0;
        for (KeyRowPoint point : sorted) {
            minimumIndex = Math.min(minimumIndex, point.index);
            maximumIndex = Math.max(maximumIndex, point.index);
        }
        for (int index = minimumIndex; index <= maximumIndex; index++) {
            String key = String.valueOf(keys.charAt(index));
            addFittedKeyboardCenter(output, key, intercept + slope * index);
        }
    }

    private float medianClusterSlope(List<KeyRowPoint> points) {
        List<Float> slopes = new ArrayList<>();
        for (int left = 0; left < points.size(); left++) {
            for (int right = left + 1; right < points.size(); right++) {
                int deltaIndex = points.get(right).index - points.get(left).index;
                if (deltaIndex == 0) continue;
                float slope = (points.get(right).x - points.get(left).x) / deltaIndex;
                if (slope > 0f && Float.isFinite(slope)) slopes.add(slope);
            }
        }
        return medianPositiveValues(slopes);
    }

    private float medianPositiveValues(List<Float> values) {
        if (values == null || values.isEmpty()) return 0f;
        List<Float> valid = new ArrayList<>();
        for (Float value : values) {
            if (value != null && value > 0f && Float.isFinite(value)) valid.add(value);
        }
        if (valid.isEmpty()) return 0f;
        valid.sort(Float::compare);
        int middle = valid.size() / 2;
        if ((valid.size() & 1) == 1) return valid.get(middle);
        return (valid.get(middle - 1) + valid.get(middle)) * 0.5f;
    }

    private void copyMeasuredKeyboardRow(Map<String, List<Float>> measured,
                                         Map<String, List<Float>> output,
                                         String keys) {
        for (int index = 0; index < keys.length(); index++) {
            String key = String.valueOf(keys.charAt(index));
            List<Float> values = measured.get(key);
            if (values == null) continue;
            for (Float value : values) {
                if (value != null) addFittedKeyboardCenter(output, key, value);
            }
        }
    }

    private void addFittedKeyboardCenter(Map<String, List<Float>> output,
                                         String key, float center) {
        if (!Float.isFinite(center)) return;
        List<Float> values = output.get(key);
        if (values == null) {
            values = new ArrayList<>();
            output.put(key, values);
        }
        for (Float existing : values) {
            if (existing != null && Math.abs(existing - center) < 2f) return;
        }
        values.add(center);
        values.sort(Float::compare);
    }

    private static final class KeyRowPoint {
        final int index;
        final String key;
        final float x;

        KeyRowPoint(int index, String key, float x) {
            this.index = index;
            this.key = key;
            this.x = x;
        }
    }

'''
marker = "    private void scanKeyboardRow(View keyboard, String expectedKeys, float y,"
if text.count(marker) != 1:
    raise RuntimeError(f"row-fit insertion marker: expected 1 match, found {text.count(marker)}")
text = text.replace(marker, helpers + marker, 1)

hook.write_text(text, encoding="utf-8")

build = Path("app/build.gradle.kts")
build_text = build.read_text(encoding="utf-8")
build_text, code_count = re.subn(r'versionCode\s*=\s*\d+', 'versionCode = 28', build_text, count=1)
build_text, name_count = re.subn(r'versionName\s*=\s*"[^"]+"', 'versionName = "1.11.0-test10"', build_text, count=1)
if code_count != 1 or name_count != 1:
    raise RuntimeError(f"version update failed: code={code_count}, name={name_count}")
build.write_text(build_text, encoding="utf-8")

activity = Path("app/src/main/java/com/rww/wetypeswipe/MainActivity.java")
activity_text = activity.read_text(encoding="utf-8")
activity_text, activity_count = re.subn(
    r'v1\.11\.0-test6 · 按键文字位置优化',
    'v1.11.0-test10 · 行列拟合按键标注',
    activity_text,
    count=1)
if activity_count != 1:
    raise RuntimeError(f"activity version update failed: {activity_count}")
activity.write_text(activity_text, encoding="utf-8")

print("v1.11.0-test10 row-fitted key-label geometry patch applied")
