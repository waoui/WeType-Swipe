from pathlib import Path

# Reuse the verified test10 performance implementation, then make the native
# toolbar command carrier window-aware for landscape floating keyboards.
exec(compile(Path("tools/patch_v110_test10.py").read_text(encoding="utf-8"), "tools/patch_v110_test10.py", "exec"))


def replace(path: str, old: str, new: str, count: int = 1) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    actual = text.count(old)
    if actual != count:
        raise RuntimeError(f"{path}: expected {count} matches, found {actual}: {old[:180]!r}")
    file.write_text(text.replace(old, new, count), encoding="utf-8")


hook = "app/src/main/java/com/rww/wetypeswipe/MainHook.java"
replace(hook, 'logInfo("v1.10.0-test10 entered target package");', 'logInfo("v1.10.0-test11 entered target package");')

# Carry the actual keyboard View into the action layer. In floating mode its
# root belongs to a different Window than InputMethodService#getWindow().
replace(
    hook,
    '                    keyboard.post(() -> performAction(context, requestedAction, key));',
    '                    keyboard.post(() -> performAction(context, keyboard, requestedAction, key));',
)
replace(
    hook,
    '    private void performAction(Context context, int action, String key) {',
    '    private void performAction(Context context, View keyboard, int action, String key) {',
)
replace(
    hook,
    '                if (!openNativePanel(ime, action)) {',
    '                if (!openNativePanel(ime, keyboard, action)) {',
)

replace(
    hook,
    '''    private boolean openNativePanel(InputMethodService ime, int action) {
        View root = imeRootView(ime);
        if (root == null) return false;
        return invokeToolbarCommandCarrier(root, action);
    }
''',
    '''    private boolean openNativePanel(InputMethodService ime, View keyboard, int action) {
        View root = keyboardWindowRoot(keyboard);
        if (root == null) root = imeRootView(ime);
        if (root == null) return false;
        return invokeToolbarCommandCarrier(root, action);
    }

    private static View keyboardWindowRoot(View keyboard) {
        if (keyboard == null) return null;
        try {
            View root = keyboard.getRootView();
            return root == null ? keyboard : root;
        } catch (Throwable ignored) {
            return keyboard;
        }
    }
''',
)

# Associate the cached command carrier with the exact Window root. Switching
# normal/floating layout invalidates and resolves a carrier from the new tree.
replace(
    hook,
    '    private volatile WeakReference<View> toolbarCarrierSourceRef = new WeakReference<>(null);\n',
    '    private volatile WeakReference<View> toolbarCarrierRootRef = new WeakReference<>(null);\n'
    '    private volatile WeakReference<View> toolbarCarrierSourceRef = new WeakReference<>(null);\n',
)
replace(
    hook,
    '''        View cachedSource = toolbarCarrierSourceRef.get();
        if (cachedSource != null && cachedSource.isAttachedToWindow()
                && toolbarCarrierCallback != null
''',
    '''        View cachedRoot = toolbarCarrierRootRef.get();
        View cachedSource = toolbarCarrierSourceRef.get();
        if (cachedRoot == root
                && cachedSource != null && cachedSource.isAttachedToWindow()
                && toolbarCarrierCallback != null
''',
)
replace(
    hook,
    '''        toolbarCarrierSourceRef = new WeakReference<>(source);
        toolbarCarrierArgumentRef = new WeakReference<>(argument);
''',
    '''        toolbarCarrierRootRef = new WeakReference<>(root);
        toolbarCarrierSourceRef = new WeakReference<>(source);
        toolbarCarrierArgumentRef = new WeakReference<>(argument);
''',
)
replace(
    hook,
    '''    private void clearToolbarCarrierCache() {
        toolbarCarrierSourceRef = new WeakReference<>(null);
''',
    '''    private void clearToolbarCarrierCache() {
        toolbarCarrierRootRef = new WeakReference<>(null);
        toolbarCarrierSourceRef = new WeakReference<>(null);
''',
)

replace(
    "app/build.gradle.kts",
    'versionName = "1.10.0-test10"',
    'versionName = "1.10.0-test11"',
)
replace(
    "app/src/main/java/com/rww/wetypeswipe/MainActivity.java",
    'v1.10.0-test10 · 性能优化与缓存失效保护',
    'v1.10.0-test11 · 横屏悬浮键盘窗口适配',
)

print("v1.10.0-test11 floating keyboard window patch applied")
