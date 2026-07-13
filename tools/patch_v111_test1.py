from pathlib import Path


def replace(path: str, old: str, new: str, count: int = 1) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    actual = text.count(old)
    if actual != count:
        raise RuntimeError(f"{path}: expected {count} matches, found {actual}: {old[:160]!r}")
    file.write_text(text.replace(old, new, count), encoding="utf-8")


hook = "app/src/main/java/com/rww/wetypeswipe/MainHook.java"

replace(hook,
        "import android.inputmethodservice.InputMethodService;\nimport android.os.Build;",
        "import android.inputmethodservice.InputMethodService;\nimport android.graphics.Color;\nimport android.graphics.drawable.GradientDrawable;\nimport android.os.Build;")
replace(hook,
        "import android.view.HapticFeedbackConstants;\nimport android.view.MotionEvent;",
        "import android.view.Gravity;\nimport android.view.HapticFeedbackConstants;\nimport android.view.MotionEvent;")
replace(hook,
        "import android.view.inputmethod.SurroundingText;\n",
        "import android.view.inputmethod.SurroundingText;\nimport android.widget.FrameLayout;\nimport android.widget.TextView;\n")

replace(hook,
        "    private volatile Object toolbarPermanentCategory;\n    private BroadcastReceiver configReceiver;",
        "    private volatile Object toolbarPermanentCategory;\n"
        "    private volatile WeakReference<View> keyboardHintRootRef = new WeakReference<>(null);\n"
        "    private volatile WeakReference<TextView> keyboardHintViewRef = new WeakReference<>(null);\n"
        "    private Runnable keyboardHintHideTask;\n"
        "    private BroadcastReceiver configReceiver;")

replace(hook,
        '            logInfo("v1.10.0 entered target package");',
        '            logInfo("v1.11.0-test1 entered target package");')

replace(hook,
        "        if (previousIme != ime) clearToolbarCarrierCache();",
        "        if (previousIme != ime) {\n"
        "            clearToolbarCarrierCache();\n"
        "            clearKeyboardHint();\n"
        "        }")

replace(hook,
        "        if (event.getPointerCount() != 1) {\n"
        "            if (maskedAction == MotionEvent.ACTION_UP || maskedAction == MotionEvent.ACTION_CANCEL) tracker.clear(keyboard);\n"
        "            return chain.proceed();\n"
        "        }",
        "        if (event.getPointerCount() != 1) {\n"
        "            if (maskedAction == MotionEvent.ACTION_UP || maskedAction == MotionEvent.ACTION_CANCEL) {\n"
        "                tracker.clear(keyboard);\n"
        "                keyboard.post(() -> hideKeyboardHint(0L));\n"
        "            }\n"
        "            return chain.proceed();\n"
        "        }")

replace(hook,
        "            tracker.setBinding(keyboard, keyInfo, requestedAction, thresholdPx);\n"
        "            if (requestedAction == Config.ACTION_NONE) tracker.clear(keyboard);\n"
        "            return result;",
        "            tracker.setBinding(keyboard, keyInfo, requestedAction, thresholdPx);\n"
        "            if (requestedAction == Config.ACTION_NONE) {\n"
        "                tracker.clear(keyboard);\n"
        "                keyboard.post(() -> hideKeyboardHint(0L));\n"
        "            } else {\n"
        "                final KeyInfo hintKey = keyInfo;\n"
        "                final int hintAction = requestedAction;\n"
        "                keyboard.post(() -> showKeyboardHint(keyboard, hintKey, hintAction, false));\n"
        "            }\n"
        "            return result;")

replace(hook,
        "                if (requestedAction != Config.ACTION_DISABLE) {\n"
        "                    keyboard.post(() -> performAction(context, keyboard, requestedAction, key));\n"
        "                }",
        "                keyboard.post(() -> showKeyboardHint(keyboard, null, requestedAction, true));\n"
        "                if (requestedAction != Config.ACTION_DISABLE) {\n"
        "                    keyboard.post(() -> performAction(context, keyboard, requestedAction, key));\n"
        "                }")

replace(hook,
        "        Object result = chain.proceed();\n"
        "        if (maskedAction == MotionEvent.ACTION_UP || maskedAction == MotionEvent.ACTION_CANCEL) tracker.clear(keyboard);\n"
        "        return result;",
        "        Object result = chain.proceed();\n"
        "        if (maskedAction == MotionEvent.ACTION_UP || maskedAction == MotionEvent.ACTION_CANCEL) {\n"
        "            tracker.clear(keyboard);\n"
        "            keyboard.post(() -> hideKeyboardHint(120L));\n"
        "        }\n"
        "        return result;")

insert_before = "    private void proceedWithCancel(XposedInterface.Chain chain, MotionEvent source) throws Throwable {"
hint_methods = r'''    private void showKeyboardHint(View keyboard, KeyInfo keyInfo, int action, boolean executed) {
        if (keyboard == null || action == Config.ACTION_NONE) {
            hideKeyboardHint(0L);
            return;
        }
        try {
            InputMethodService ime = imeRef.get();
            EditorInfo editorInfo = ime == null ? null : ime.getCurrentInputEditorInfo();
            if (editorInfo != null && isPassword(editorInfo.inputType)) {
                hideKeyboardHint(0L);
                return;
            }

            TextView hint = resolveKeyboardHint(keyboard);
            if (hint == null) return;
            if (keyboardHintHideTask != null) hint.removeCallbacks(keyboardHintHideTask);

            String text;
            if (executed) {
                text = action == Config.ACTION_DISABLE
                        ? "已禁用该键下滑"
                        : "已执行：" + Config.actionName(action);
            } else {
                String keyLabel = keyInfo == null ? "当前键" : keyInfo.display;
                text = keyLabel + " 下滑：" + Config.actionName(action);
            }
            hint.setText(text);
            positionKeyboardHint(keyboard, hint);
            hint.setAlpha(1f);
            hint.setVisibility(View.VISIBLE);
            if (executed) hideKeyboardHint(650L);
        } catch (Throwable throwable) {
            logError("keyboard hint display failed", throwable);
        }
    }

    private TextView resolveKeyboardHint(View keyboard) {
        View root = keyboardWindowRoot(keyboard);
        if (!(root instanceof FrameLayout)) return null;

        TextView cached = keyboardHintViewRef.get();
        if (keyboardHintRootRef.get() == root && cached != null && cached.getParent() == root) {
            return cached;
        }
        clearKeyboardHint();

        TextView hint = new TextView(keyboard.getContext());
        hint.setTextColor(Color.WHITE);
        hint.setTextSize(12f);
        hint.setGravity(Gravity.CENTER);
        hint.setSingleLine(true);
        hint.setMaxLines(1);
        hint.setEllipsize(android.text.TextUtils.TruncateAt.END);
        hint.setPadding(dp(keyboard, 12), dp(keyboard, 5), dp(keyboard, 12), dp(keyboard, 5));
        hint.setClickable(false);
        hint.setFocusable(false);
        hint.setFocusableInTouchMode(false);
        hint.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO);
        hint.setElevation(dp(keyboard, 10));
        hint.setVisibility(View.GONE);

        GradientDrawable background = new GradientDrawable();
        background.setColor(0xD9202124);
        background.setCornerRadius(dp(keyboard, 16));
        hint.setBackground(background);

        FrameLayout host = (FrameLayout) root;
        FrameLayout.LayoutParams params = new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT,
                Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL);
        params.bottomMargin = dp(keyboard, 6);
        host.addView(hint, params);

        keyboardHintRootRef = new WeakReference<>(root);
        keyboardHintViewRef = new WeakReference<>(hint);
        return hint;
    }

    private void positionKeyboardHint(View keyboard, TextView hint) {
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

    private void hideKeyboardHint(long delayMillis) {
        TextView hint = keyboardHintViewRef.get();
        if (hint == null) return;
        if (keyboardHintHideTask != null) hint.removeCallbacks(keyboardHintHideTask);
        final TextView target = hint;
        keyboardHintHideTask = () -> {
            if (keyboardHintViewRef.get() == target) target.setVisibility(View.GONE);
        };
        if (delayMillis <= 0L) keyboardHintHideTask.run();
        else hint.postDelayed(keyboardHintHideTask, delayMillis);
    }

    private void clearKeyboardHint() {
        TextView hint = keyboardHintViewRef.get();
        if (hint != null) {
            try {
                if (keyboardHintHideTask != null) hint.removeCallbacks(keyboardHintHideTask);
                if (hint.getParent() instanceof ViewGroup) {
                    ((ViewGroup) hint.getParent()).removeView(hint);
                }
            } catch (Throwable ignored) {}
        }
        keyboardHintHideTask = null;
        keyboardHintRootRef = new WeakReference<>(null);
        keyboardHintViewRef = new WeakReference<>(null);
    }

'''
replace(hook, insert_before, hint_methods + insert_before)

replace(hook,
        "            if (isNativePanelAction(action)) {\n"
        "                if (!openNativePanel(ime, keyboard, action)) {",
        "            if (isNativePanelAction(action)) {\n"
        "                hideKeyboardHint(0L);\n"
        "                if (!openNativePanel(ime, keyboard, action)) {")

replace("app/build.gradle.kts", 'versionCode = 22', 'versionCode = 23')
replace("app/build.gradle.kts", 'versionName = "1.10.0"', 'versionName = "1.11.0-test1"')
replace("app/src/main/java/com/rww/wetypeswipe/MainActivity.java",
        'v1.10.0 · 原生剪贴板与快捷发送',
        'v1.11.0-test1 · 键盘底部功能提示')

print("v1.11.0-test1 keyboard hint overlay patch applied")
