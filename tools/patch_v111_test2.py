from pathlib import Path
import runpy

runpy.run_path("tools/patch_v111_test1.py", run_name="__main__")


def replace(path: str, old: str, new: str, count: int = 1) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    actual = text.count(old)
    if actual != count:
        raise RuntimeError(f"{path}: expected {count} matches, found {actual}: {old[:180]!r}")
    file.write_text(text.replace(old, new, count), encoding="utf-8")


hook = "app/src/main/java/com/rww/wetypeswipe/MainHook.java"

replace(hook,
        '            logInfo("v1.11.0-test1 entered target package");',
        '            logInfo("v1.11.0-test2 entered target package");')

replace(hook,
'''    private TextView resolveKeyboardHint(View keyboard) {
        View root = keyboardWindowRoot(keyboard);
        if (!(root instanceof FrameLayout)) return null;
''',
'''    private TextView resolveKeyboardHint(View keyboard) {
        InputMethodService ime = imeRef.get();
        View keyboardRoot = keyboardWindowRoot(keyboard);
        View imeRoot = imeRootView(ime);
        View root = keyboardRoot;
        try {
            if (imeRoot instanceof FrameLayout
                    && keyboard.getWindowToken() != null
                    && keyboard.getWindowToken() == imeRoot.getWindowToken()) {
                root = imeRoot;
            }
        } catch (Throwable ignored) {}
        if (!(root instanceof FrameLayout)) return null;
''')

replace(hook,
'''        hint.setTextSize(12f);
''',
'''        hint.setTextSize(10f);
''')
replace(hook,
'''        hint.setPadding(dp(keyboard, 12), dp(keyboard, 5), dp(keyboard, 12), dp(keyboard, 5));
''',
'''        hint.setPadding(dp(keyboard, 9), dp(keyboard, 3), dp(keyboard, 9), dp(keyboard, 3));
''')
replace(hook,
'''        background.setCornerRadius(dp(keyboard, 16));
''',
'''        background.setCornerRadius(dp(keyboard, 13));
''')
replace(hook,
'''        FrameLayout.LayoutParams params = new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT,
                Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL);
        params.bottomMargin = dp(keyboard, 6);
        host.addView(hint, params);
''',
'''        FrameLayout.LayoutParams params = new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT,
                Gravity.TOP | Gravity.START);
        host.addView(hint, params);
''')

start = '''    private void positionKeyboardHint(View keyboard, TextView hint) {
        View root = keyboardHintRootRef.get();
        if (!(root instanceof FrameLayout) || hint == null) return;
        FrameLayout.LayoutParams params = hint.getLayoutParams() instanceof FrameLayout.LayoutParams
                ? (FrameLayout.LayoutParams) hint.getLayoutParams()
                : new FrameLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT,
                ViewGroup.LayoutParams.WRAP_CONTENT, Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL);
        params.gravity = Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL;
        params.bottomMargin = dp(keyboard, 6);
        try {
            int[] rootLocation = new int[2];
            int[] keyboardLocation = new int[2];
            root.getLocationInWindow(rootLocation);
            keyboard.getLocationInWindow(keyboardLocation);
            int keyboardBottom = keyboardLocation[1] - rootLocation[1] + keyboard.getHeight();
            if (root.getHeight() > 0 && keyboardBottom > 0) {
                params.bottomMargin = Math.max(dp(keyboard, 4),
                        root.getHeight() - keyboardBottom + dp(keyboard, 4));
            }
        } catch (Throwable ignored) {}
        int rootWidth = root.getWidth();
        if (rootWidth > 0) hint.setMaxWidth(Math.max(dp(keyboard, 140), Math.round(rootWidth * 0.72f)));
        hint.setLayoutParams(params);
    }
'''

new = '''    private void positionKeyboardHint(View keyboard, TextView hint) {
        View root = keyboardHintRootRef.get();
        if (!(root instanceof FrameLayout) || hint == null || keyboard == null) return;

        FrameLayout.LayoutParams params = hint.getLayoutParams() instanceof FrameLayout.LayoutParams
                ? (FrameLayout.LayoutParams) hint.getLayoutParams()
                : new FrameLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT,
                ViewGroup.LayoutParams.WRAP_CONTENT, Gravity.TOP | Gravity.START);
        params.gravity = Gravity.TOP | Gravity.START;
        params.bottomMargin = 0;

        try {
            int rootWidth = root.getWidth();
            int rootHeight = root.getHeight();
            if (rootWidth <= 0 || rootHeight <= 0) return;

            int[] rootLocation = new int[2];
            int[] keyboardLocation = new int[2];
            root.getLocationInWindow(rootLocation);
            keyboard.getLocationInWindow(keyboardLocation);

            int keyboardLeft = keyboardLocation[0] - rootLocation[0];
            int keyboardTop = keyboardLocation[1] - rootLocation[1];
            int keyboardWidth = Math.max(1, keyboard.getWidth());
            int keyboardBottom = keyboardTop + Math.max(1, keyboard.getHeight());

            int edge = dp(keyboard, 4);
            int maxWidth = Math.max(dp(keyboard, 120),
                    Math.min(Math.round(rootWidth * 0.68f), Math.round(keyboardWidth * 0.66f)));
            hint.setMaxWidth(maxWidth);
            hint.measure(
                    View.MeasureSpec.makeMeasureSpec(maxWidth, View.MeasureSpec.AT_MOST),
                    View.MeasureSpec.makeMeasureSpec(rootHeight, View.MeasureSpec.AT_MOST));
            int hintWidth = Math.max(dp(keyboard, 80), hint.getMeasuredWidth());
            int hintHeight = Math.max(dp(keyboard, 22), hint.getMeasuredHeight());

            int targetLeft = keyboardLeft + (keyboardWidth - hintWidth) / 2;
            targetLeft = Math.max(edge, Math.min(targetLeft, rootWidth - hintWidth - edge));

            int spaceBelow = rootHeight - keyboardBottom;
            int targetTop;
            if (spaceBelow >= hintHeight + edge * 2) {
                targetTop = keyboardBottom + edge;
            } else if (keyboardTop >= hintHeight + edge * 2) {
                targetTop = keyboardTop - hintHeight - edge;
            } else {
                targetTop = Math.max(edge, keyboardBottom - hintHeight - edge);
            }

            params.leftMargin = targetLeft;
            params.topMargin = Math.max(edge, Math.min(targetTop, rootHeight - hintHeight - edge));
            hint.setLayoutParams(params);
            hint.bringToFront();
        } catch (Throwable throwable) {
            logError("keyboard hint positioning failed", throwable);
        }
    }
'''
replace(hook, start, new)

replace("app/build.gradle.kts", 'versionName = "1.11.0-test1"', 'versionName = "1.11.0-test2"')
replace("app/src/main/java/com/rww/wetypeswipe/MainActivity.java",
        'v1.11.0-test1 · 键盘底部功能提示',
        'v1.11.0-test2 · 键盘提示动态定位')

print("v1.11.0-test2 dynamic keyboard hint positioning patch applied")
