from pathlib import Path

# Reuse the functional v1.10.0-test1 patch, then add diagnostic probes.
exec(compile(Path("tools/patch_v110_test.py").read_text(encoding="utf-8"), "tools/patch_v110_test.py", "exec"))


def replace(path: str, old: str, new: str, count: int = 1) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    actual = text.count(old)
    if actual != count:
        raise RuntimeError(f"{path}: expected {count} matches, found {actual}: {old[:120]!r}")
    file.write_text(text.replace(old, new, count), encoding="utf-8")


hook = "app/src/main/java/com/rww/wetypeswipe/MainHook.java"
replace(hook, "import java.lang.reflect.Method;\n", "import java.lang.reflect.Field;\nimport java.lang.reflect.Method;\nimport java.lang.reflect.Modifier;\n")
replace(hook, 'logInfo("v1.10.0-test1 entered target package");', 'logInfo("v1.10.0-test2 entered target package");')
replace(
    hook,
    '''    private KeyInfo keyAfterDown(Object keyboard, MotionEvent event) {
        Object button = invoke(keyboard, "getActionButton");
        if (button == null) button = invoke(keyboard, "v1", event, false);
        if (button == null) button = invoke(keyboard, "v1", event, true);
        return keyFromButton(keyboard, button);
    }
''',
    '''    private KeyInfo keyAfterDown(Object keyboard, MotionEvent event) {
        Object button = invoke(keyboard, "getActionButton");
        if (button == null) button = invoke(keyboard, "v1", event, false);
        if (button == null) button = invoke(keyboard, "v1", event, true);
        KeyInfo keyInfo = keyFromButton(keyboard, button);
        if (keyInfo == null && button != null) logUnknownActionButton(button);
        return keyInfo;
    }
''',
)
replace(
    hook,
    '        if (!clickMatchingView(root, moreTargets)) return false;',
    '        if (!clickMatchingView(root, moreTargets)) {\n            dumpVisibleViewTree(root, Config.actionName(action));\n            return false;\n        }',
)
replace(
    hook,
    '                logError(Config.actionName(action) + " failed after opening more panel", null);',
    '                dumpVisibleViewTree(latestRoot, Config.actionName(action) + " after-more");\n                logError(Config.actionName(action) + " failed after opening more panel", null);',
)

probe_helpers = r'''
    private void logUnknownActionButton(Object button) {
        try {
            StringBuilder value = new StringBuilder(2048);
            appendObjectSummary(value, "button", button);
            Object keyData = invoke(button, "O");
            appendObjectSummary(value, "keyData", keyData);
            appendValue(value, "button.K", invoke(button, "K"));
            appendValue(value, "main", invoke(keyData, "getMainText"));
            appendValue(value, "sub", invoke(keyData, "getSubText"));
            appendValue(value, "secondary", invoke(keyData, "getSecondaryText"));
            appendValue(value, "hint", invoke(keyData, "getHintText"));
            appendValue(value, "assist", invoke(keyData, "getAssistText"));
            appendValue(value, "id", invoke(keyData, "getId"));
            logInfo("native-probe unknown button: " + value);
        } catch (Throwable throwable) {
            logError("native-probe button dump failed", throwable);
        }
    }

    private static void appendObjectSummary(StringBuilder out, String label, Object object) {
        if (object == null || out.length() > 3200) return;
        out.append(label).append('=').append(object.getClass().getName()).append('{');
        int fields = 0;
        for (Class<?> type = object.getClass(); type != null && fields < 36; type = type.getSuperclass()) {
            Field[] declared;
            try { declared = type.getDeclaredFields(); }
            catch (Throwable ignored) { continue; }
            for (Field field : declared) {
                if (fields >= 36 || out.length() > 3200) break;
                if (Modifier.isStatic(field.getModifiers())) continue;
                try {
                    field.setAccessible(true);
                    Object value = field.get(object);
                    out.append(field.getName()).append('=');
                    if (value == null || value instanceof Number || value instanceof Boolean
                            || value instanceof Character || value instanceof CharSequence
                            || value.getClass().isEnum()) {
                        out.append(String.valueOf(value));
                    } else {
                        out.append('<').append(value.getClass().getName()).append('>');
                    }
                    out.append(',');
                    fields++;
                } catch (Throwable ignored) {}
            }
        }
        out.append("};");
    }

    private static void appendValue(StringBuilder out, String label, Object value) {
        if (value == null || out.length() > 3400) return;
        out.append(label).append('=').append(String.valueOf(value)).append(';');
    }

    private void dumpVisibleViewTree(View root, String reason) {
        if (root == null) return;
        try {
            StringBuilder out = new StringBuilder(3600);
            int[] count = {0};
            appendViewTree(out, root, 0, count);
            logInfo("native-probe view-tree[" + reason + "]: " + out);
        } catch (Throwable throwable) {
            logError("native-probe view tree failed", throwable);
        }
    }

    private void appendViewTree(StringBuilder out, View view, int depth, int[] count) {
        if (view == null || depth > 14 || count[0] >= 140 || out.length() > 3400) return;
        count[0]++;
        String descriptor = describeView(view);
        if (view.getVisibility() == View.VISIBLE || !descriptor.isEmpty()) {
            out.append('[').append(depth).append(':')
                    .append(view.getClass().getName())
                    .append(" id=").append(view.getId())
                    .append(" click=").append(view.isClickable())
                    .append(" shown=").append(view.isShown())
                    .append(" desc=").append(descriptor).append(']');
        }
        if (view instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) view;
            for (int index = 0; index < group.getChildCount(); index++) {
                appendViewTree(out, group.getChildAt(index), depth + 1, count);
            }
        }
    }

'''
replace(hook, '    private static boolean isNativePanelAction(int action) {', probe_helpers + '    private static boolean isNativePanelAction(int action) {')

replace(
    "app/build.gradle.kts",
    'versionName = "1.10.0-test1"',
    'versionName = "1.10.0-test2"',
)
replace(
    "app/src/main/java/com/rww/wetypeswipe/MainActivity.java",
    'v1.10.0 测试版 · 原生剪贴板与快捷发送',
    'v1.10.0-test2 · 原生面板诊断版',
)

print("v1.10.0-test2 diagnostic patch applied")
