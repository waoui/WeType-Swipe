from pathlib import Path
import re
import runpy

runpy.run_path("tools/patch_v111_test11_native_layout.py", run_name="__main__")

hook = Path("app/src/main/java/com/rww/wetypeswipe/MainHook.java")
text = hook.read_text(encoding="utf-8")


def replace_once(source: str, old: str, new: str, name: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"{name}: expected 1 match, found {count}")
    return source.replace(old, new, 1)


text = replace_once(
    text,
    "    private volatile boolean nativeLabelGeometryUnavailable;",
    "    private volatile boolean nativeLabelGeometryUnavailable;\n"
    "    private volatile String nativeLabelLayoutSignature = \"\";\n"
    "    private volatile long nativeLabelLastSignatureCheckMs;",
    "native layout signature fields")

text = replace_once(
    text,
    '            logInfo("v1.11.0-test11 entered target package");',
    '            logInfo("v1.11.0-test12 entered target package");',
    "version log")

old_ensure = '''    private void ensureNativeKeyboardLabelGeometry(View keyboard) {
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
'''
new_ensure = '''    private void ensureNativeKeyboardLabelGeometry(View keyboard) {
        if (keyboard == null || keyboard.getWidth() <= 0 || keyboard.getHeight() <= 0) return;
        boolean sameView = nativeLabelGeometryViewRef.get() == keyboard;
        boolean sameSize = nativeLabelGeometryWidth == keyboard.getWidth()
                && nativeLabelGeometryHeight == keyboard.getHeight();
        String className = keyboard.getClass().getName();
        boolean sameClass = className.equals(nativeLabelGeometryClass);
        boolean hasCachedState = nativeLabelGeometryUnavailable || !nativeLabelGeometry.isEmpty();
        if (sameView && sameSize && sameClass && hasCachedState) {
            long now = SystemClock.uptimeMillis();
            if (now - nativeLabelLastSignatureCheckMs < 320L) return;
            nativeLabelLastSignatureCheckMs = now;
            String currentSignature = readNativeLayoutSignature(keyboard);
            if (!currentSignature.isEmpty() && currentSignature.equals(nativeLabelLayoutSignature)) return;
            if (currentSignature.isEmpty() && nativeLabelGeometryUnavailable) return;
        }
        if (nativeLabelGeometryBuilding) return;
        nativeLabelGeometryBuilding = true;
        keyboard.post(() -> rebuildNativeKeyboardLabelGeometry(keyboard, className));
    }
'''
text = replace_once(text, old_ensure, new_ensure, "layout-refresh ensure method")

text = replace_once(
    text,
    "            String[] ids = (String[]) idsValue;\n            Object drawItems = readNamedField(pair, \"first\");",
    "            String[] ids = (String[]) idsValue;\n"
    "            Object drawItems = readNamedField(pair, \"first\");",
    "ids marker")

# Publish the exact native-layout signature after reading the drawRect array.
text = replace_once(
    text,
    "            Map<String, float[]> result = buildNativeLabelGeometry(keyboard, raw);\n"
    "            publishNativeKeyboardLabelGeometry(keyboard, expectedClass, result, true);",
    "            Map<String, float[]> result = buildNativeLabelGeometry(keyboard, raw);\n"
    "            nativeLabelLayoutSignature = nativeLayoutSignature(ids, drawItems);\n"
    "            nativeLabelLastSignatureCheckMs = SystemClock.uptimeMillis();\n"
    "            publishNativeKeyboardLabelGeometry(keyboard, expectedClass, result, true);",
    "publish native signature")

# Move labels closer to the keycap bottom.
text = replace_once(
    text,
    "        float baseline = rowBottom - Math.max(dp(keyboard, 4), rowHeight * 0.18f);",
    "        float baseline = rowBottom - Math.max(dp(keyboard, 2), rowHeight * 0.08f);",
    "lower native label baseline")

signature_helpers = r'''    private String readNativeLayoutSignature(View keyboard) {
        if (keyboard == null) return "";
        try {
            Method idsMethod = findMethod(keyboard.getClass(), "getKeyIdsForLayoutInfo", new Class<?>[0]);
            Method layoutMethod = findMethod(keyboard.getClass(), "getKeysLayoutInfo", new Class<?>[0]);
            if (idsMethod == null || layoutMethod == null) return "";
            idsMethod.setAccessible(true);
            layoutMethod.setAccessible(true);
            Object idsValue = idsMethod.invoke(keyboard);
            Object pair = layoutMethod.invoke(keyboard);
            if (!(idsValue instanceof String[]) || pair == null) return "";
            Object drawItems = readNamedField(pair, "first");
            if (drawItems == null || !drawItems.getClass().isArray()) {
                Object first = invokeNoArg(pair, "a");
                if (first != null && first.getClass().isArray()) drawItems = first;
            }
            return nativeLayoutSignature((String[]) idsValue, drawItems);
        } catch (Throwable ignored) {
            return "";
        }
    }

    private static String nativeLayoutSignature(String[] ids, Object drawItems) {
        if (ids == null || drawItems == null || !drawItems.getClass().isArray()) return "";
        int count = Math.min(ids.length, java.lang.reflect.Array.getLength(drawItems));
        long hash = 1125899906842597L;
        hash = hash * 31L + count;
        for (int index = 0; index < count; index++) {
            String id = ids[index];
            hash = hash * 31L + (id == null ? 0 : id.hashCode());
            Object item = java.lang.reflect.Array.get(drawItems, index);
            if (item == null) {
                hash = hash * 31L;
                continue;
            }
            Integer left = integerField(item, "x_left");
            Integer right = integerField(item, "x_right");
            Integer top = integerField(item, "y_top");
            Integer bottom = integerField(item, "y_bottom");
            hash = hash * 31L + (left == null ? 0 : left);
            hash = hash * 31L + (right == null ? 0 : right);
            hash = hash * 31L + (top == null ? 0 : top);
            hash = hash * 31L + (bottom == null ? 0 : bottom);
        }
        return Long.toHexString(hash);
    }

'''
marker = "    private static String keyFromNativeLayoutId(String id) {"
if text.count(marker) != 1:
    raise RuntimeError(f"signature helper marker: expected 1 match, found {text.count(marker)}")
text = text.replace(marker, signature_helpers + marker, 1)

hook.write_text(text, encoding="utf-8")

build = Path("app/build.gradle.kts")
build_text = build.read_text(encoding="utf-8")
build_text, code_count = re.subn(r'versionCode\s*=\s*\d+', 'versionCode = 33', build_text, count=1)
build_text, name_count = re.subn(r'versionName\s*=\s*"[^"]+"', 'versionName = "1.11.0-test12"', build_text, count=1)
if code_count != 1 or name_count != 1:
    raise RuntimeError(f"version update failed: code={code_count}, name={name_count}")
build.write_text(build_text, encoding="utf-8")

activity = Path("app/src/main/java/com/rww/wetypeswipe/MainActivity.java")
activity_text = activity.read_text(encoding="utf-8")
activity_text, activity_count = re.subn(
    r'v1\.11\.0-test11 · 原生键帽坐标标注',
    'v1.11.0-test12 · 原生布局自动刷新',
    activity_text,
    count=1)
if activity_count != 1:
    raise RuntimeError(f"activity version update failed: {activity_count}")
activity.write_text(activity_text, encoding="utf-8")

print("v1.11.0-test12 lower baseline and native-layout refresh patch applied")
