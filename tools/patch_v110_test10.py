from pathlib import Path

# Reuse the verified test9 implementation, then optimize its hot paths.
exec(compile(Path("tools/patch_v110_test9.py").read_text(encoding="utf-8"), "tools/patch_v110_test9.py", "exec"))


def replace(path: str, old: str, new: str, count: int = 1) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    actual = text.count(old)
    if actual != count:
        raise RuntimeError(f"{path}: expected {count} matches, found {actual}: {old[:180]!r}")
    file.write_text(text.replace(old, new, count), encoding="utf-8")


hook = "app/src/main/java/com/rww/wetypeswipe/MainHook.java"
replace(hook, 'logInfo("v1.10.0-test9 entered target package");', 'logInfo("v1.10.0-test10 entered target package");')

# test7 left a full View-tree scan on every key ACTION_DOWN. test9 no longer needs it.
replace(
    hook,
    '''        if (maskedAction == MotionEvent.ACTION_DOWN) {
            cacheNativePanelListeners(findIme(keyboard.getContext()));
            tracker.begin(keyboard, event.getX(), event.getY());
''',
    '''        if (maskedAction == MotionEvent.ACTION_DOWN) {
            tracker.begin(keyboard, event.getX(), event.getY());
''',
)

# Cache the generic toolbar command carrier and all reflection members.
replace(
    hook,
    "    private volatile Object quickPhraseNativeCallback;\n",
    "    private volatile Object quickPhraseNativeCallback;\n"
    "    private volatile WeakReference<View> toolbarCarrierSourceRef = new WeakReference<>(null);\n"
    "    private volatile WeakReference<View> toolbarCarrierArgumentRef = new WeakReference<>(null);\n"
    "    private volatile Object toolbarCarrierCallback;\n"
    "    private volatile Object toolbarCarrierHolder;\n"
    "    private volatile Field toolbarCarrierFunctionField;\n"
    "    private volatile Field toolbarCarrierCategoryField;\n"
    "    private volatile Field toolbarCarrierGroupField;\n"
    "    private volatile Method toolbarCarrierInvokeMethod;\n"
    "    private volatile Object toolbarPermanentCategory;\n",
)

# Invalidate the carrier only when the actual IME service instance changes.
replace(
    hook,
    '''        imeRef = new WeakReference<>(ime);
        ensureConfigSync(ime);
''',
    '''        InputMethodService previousIme = imeRef.get();
        if (previousIme != ime) clearToolbarCarrierCache();
        imeRef = new WeakReference<>(ime);
        ensureConfigSync(ime);
''',
)

file = Path(hook)
text = file.read_text(encoding="utf-8")
start = text.index("    private boolean invokeToolbarCommandCarrier(View root, int action) {")
end = text.index("    private Object[] findToolbarCommandCarrier(View view) {", start)
optimized_carrier = r'''    private boolean invokeToolbarCommandCarrier(View root, int action) {
        int targetFunction = action == Config.ACTION_OPEN_CLIPBOARD ? 4 : 8;

        for (int attempt = 0; attempt < 2; attempt++) {
            if (!resolveToolbarCommandCarrier(root)) {
                if (attempt == 0) {
                    clearToolbarCarrierCache();
                    continue;
                }
                logError(Config.actionName(action) + " failed: toolbar command carrier unavailable", null);
                return false;
            }

            View source = toolbarCarrierSourceRef.get();
            Object callback = toolbarCarrierCallback;
            Object holder = toolbarCarrierHolder;
            Field functionField = toolbarCarrierFunctionField;
            Field categoryField = toolbarCarrierCategoryField;
            Field groupField = toolbarCarrierGroupField;
            Method invokeMethod = toolbarCarrierInvokeMethod;

            if (source == null || !source.isAttachedToWindow()
                    || callback == null || holder == null
                    || functionField == null || invokeMethod == null) {
                clearToolbarCarrierCache();
                continue;
            }

            Object oldFunction = null;
            Object oldCategory = null;
            Object oldGroup = null;
            boolean functionChanged = false;
            boolean categoryChanged = false;
            boolean groupChanged = false;
            try {
                oldFunction = functionField.get(holder);
                functionField.set(holder, targetFunction);
                functionChanged = true;

                if (categoryField != null && toolbarPermanentCategory != null) {
                    oldCategory = categoryField.get(holder);
                    categoryField.set(holder, toolbarPermanentCategory);
                    categoryChanged = true;
                }
                if (groupField != null) {
                    oldGroup = groupField.get(holder);
                    groupField.set(holder, 6);
                    groupChanged = true;
                }

                View argument = toolbarCarrierArgumentRef.get();
                if (argument == null) argument = source;
                invokeMethod.invoke(callback, argument);
                return true;
            } catch (Throwable throwable) {
                clearToolbarCarrierCache();
                if (attempt == 1) {
                    logError("toolbar-command-carrier failed action=" + Config.actionName(action), throwable);
                    return false;
                }
            } finally {
                try { if (functionChanged) functionField.set(holder, oldFunction); } catch (Throwable ignored) {}
                try { if (categoryChanged) categoryField.set(holder, oldCategory); } catch (Throwable ignored) {}
                try { if (groupChanged) groupField.set(holder, oldGroup); } catch (Throwable ignored) {}
            }
        }
        return false;
    }

    private boolean resolveToolbarCommandCarrier(View root) {
        View cachedSource = toolbarCarrierSourceRef.get();
        if (cachedSource != null && cachedSource.isAttachedToWindow()
                && toolbarCarrierCallback != null
                && toolbarCarrierHolder != null
                && toolbarCarrierFunctionField != null
                && toolbarCarrierInvokeMethod != null) {
            return true;
        }

        clearToolbarCarrierCache();
        Object[] carrier = findToolbarCommandCarrier(root);
        if (carrier == null) return false;

        View source = (View) carrier[0];
        Object callback = carrier[2];
        Object holder = readNamedField(callback, "this$0");
        if (source == null || callback == null || holder == null) return false;

        Field functionField = findNamedField(holder.getClass(), "f");
        if (functionField == null) return false;
        Field categoryField = findNamedField(holder.getClass(), "g");
        Field groupField = findNamedField(holder.getClass(), "h");
        Method invokeMethod = findCompatibleInvoke(callback.getClass());
        if (invokeMethod == null) return false;

        Object permanent = categoryField == null ? null : enumConstant(categoryField.getType(), "Permanent");
        Object capturedView = readNamedField(callback, "$this_apply");
        View argument = capturedView instanceof View ? (View) capturedView : source;

        toolbarCarrierSourceRef = new WeakReference<>(source);
        toolbarCarrierArgumentRef = new WeakReference<>(argument);
        toolbarCarrierCallback = callback;
        toolbarCarrierHolder = holder;
        toolbarCarrierFunctionField = functionField;
        toolbarCarrierCategoryField = categoryField;
        toolbarCarrierGroupField = groupField;
        toolbarCarrierInvokeMethod = invokeMethod;
        toolbarPermanentCategory = permanent;
        logInfo("toolbar command carrier cached");
        return true;
    }

    private void clearToolbarCarrierCache() {
        toolbarCarrierSourceRef = new WeakReference<>(null);
        toolbarCarrierArgumentRef = new WeakReference<>(null);
        toolbarCarrierCallback = null;
        toolbarCarrierHolder = null;
        toolbarCarrierFunctionField = null;
        toolbarCarrierCategoryField = null;
        toolbarCarrierGroupField = null;
        toolbarCarrierInvokeMethod = null;
        toolbarPermanentCategory = null;
    }

'''
text = text[:start] + optimized_carrier + text[end:]
file.write_text(text, encoding="utf-8")

# Avoid regex allocations in the typing hot path.
replace(
    hook,
    '''    private static String normalizeText(Object value) {
        if (value == null) return "";
        return String.valueOf(value).trim().toLowerCase(Locale.ROOT)
                .replaceAll("[^a-z0-9]", "");
    }
''',
    '''    private static String normalizeText(Object value) {
        if (value == null) return "";
        String text = String.valueOf(value).trim().toLowerCase(Locale.ROOT);
        StringBuilder clean = null;
        for (int index = 0; index < text.length(); index++) {
            char c = text.charAt(index);
            boolean allowed = (c >= 'a' && c <= 'z') || (c >= '0' && c <= '9');
            if (allowed) {
                if (clean != null) clean.append(c);
            } else if (clean == null) {
                clean = new StringBuilder(text.length());
                clean.append(text, 0, index);
            }
        }
        return clean == null ? text : clean.toString();
    }
''',
)
replace(
    hook,
    '''    private static String t9DigitFromLetters(String value) {
        if (value == null || value.isEmpty()) return null;
        String letters = value.replaceAll("[^a-z]", "");
        if (letters.equals("abc")) return "2";
        if (letters.equals("def")) return "3";
        if (letters.equals("ghi")) return "4";
        if (letters.equals("jkl")) return "5";
        if (letters.equals("mno")) return "6";
        if (letters.equals("pqrs")) return "7";
        if (letters.equals("tuv")) return "8";
        if (letters.equals("wxyz")) return "9";
        return null;
    }
''',
    '''    private static String t9DigitFromLetters(String value) {
        if (value == null || value.isEmpty()) return null;
        if (lettersMatch(value, "abc")) return "2";
        if (lettersMatch(value, "def")) return "3";
        if (lettersMatch(value, "ghi")) return "4";
        if (lettersMatch(value, "jkl")) return "5";
        if (lettersMatch(value, "mno")) return "6";
        if (lettersMatch(value, "pqrs")) return "7";
        if (lettersMatch(value, "tuv")) return "8";
        if (lettersMatch(value, "wxyz")) return "9";
        return null;
    }

    private static boolean lettersMatch(String value, String expected) {
        int matched = 0;
        for (int index = 0; index < value.length(); index++) {
            char c = value.charAt(index);
            if (c < 'a' || c > 'z') continue;
            if (matched >= expected.length() || c != expected.charAt(matched)) return false;
            matched++;
        }
        return matched == expected.length();
    }
''',
)

replace(
    "app/build.gradle.kts",
    'versionName = "1.10.0-test9"',
    'versionName = "1.10.0-test10"',
)
replace(
    "app/src/main/java/com/rww/wetypeswipe/MainActivity.java",
    'v1.10.0-test9 · 工具栏功能编号直调',
    'v1.10.0-test10 · 性能优化与缓存失效保护',
)

print("v1.10.0-test10 performance optimization patch applied")
