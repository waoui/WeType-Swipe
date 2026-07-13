from pathlib import Path
import runpy

runpy.run_path("tools/patch_v111_test2.py", run_name="__main__")


def replace(path: str, old: str, new: str, count: int = 1) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    actual = text.count(old)
    if actual != count:
        raise RuntimeError(f"{path}: expected {count} matches, found {actual}: {old[:180]!r}")
    file.write_text(text.replace(old, new, count), encoding="utf-8")


hook = "app/src/main/java/com/rww/wetypeswipe/MainHook.java"

replace(hook,
        '            logInfo("v1.11.0-test2 entered target package");',
        '            logInfo("v1.11.0-test3 entered target package");')

# Do not show anything on a normal key press. The preview appears only after a
# deliberate downward movement has started.
replace(hook,
'''            if (requestedAction == Config.ACTION_NONE) {
                tracker.clear(keyboard);
                keyboard.post(() -> hideKeyboardHint(0L));
            } else {
                final KeyInfo hintKey = keyInfo;
                final int hintAction = requestedAction;
                keyboard.post(() -> showKeyboardHint(keyboard, hintKey, hintAction, false));
            }
''',
'''            if (requestedAction == Config.ACTION_NONE) {
                tracker.clear(keyboard);
            }
            keyboard.post(() -> hideKeyboardHint(0L));
''')

# Show the candidate-bar preview after 30% of the configured trigger distance.
replace(hook,
'''            float horizontalLimit = tracker.t9
                    ? Math.max(tracker.thresholdPx * 0.9f, deltaY * 0.75f)
                    : Math.max(tracker.thresholdPx * 2.5f, deltaY * 1.2f);
            if (deltaY >= tracker.thresholdPx && Math.abs(deltaX) <= horizontalLimit) {
''',
'''            float horizontalLimit = tracker.t9
                    ? Math.max(tracker.thresholdPx * 0.9f, deltaY * 0.75f)
                    : Math.max(tracker.thresholdPx * 2.5f, deltaY * 1.2f);
            if (maskedAction == MotionEvent.ACTION_MOVE) {
                if (deltaY >= tracker.thresholdPx * 0.30f
                        && deltaY < tracker.thresholdPx
                        && Math.abs(deltaX) <= horizontalLimit) {
                    final String hintLabel = tracker.displayKey;
                    final int hintAction = tracker.action;
                    keyboard.post(() -> showKeyboardHint(keyboard, hintLabel, hintAction, false));
                } else if (deltaY < tracker.thresholdPx) {
                    keyboard.post(() -> hideKeyboardHint(0L));
                }
            }
            if (deltaY >= tracker.thresholdPx && Math.abs(deltaX) <= horizontalLimit) {
''')

replace(hook,
        "    private void showKeyboardHint(View keyboard, KeyInfo keyInfo, int action, boolean executed) {",
        "    private void showKeyboardHint(View keyboard, String keyLabel, int action, boolean executed) {")
replace(hook,
'''                text = action == Config.ACTION_DISABLE
                        ? "已禁用该键下滑"
                        : "已执行：" + Config.actionName(action);
            } else {
                String keyLabel = keyInfo == null ? "当前键" : keyInfo.display;
                text = keyLabel + " 下滑：" + Config.actionName(action);
''',
'''                text = action == Config.ACTION_DISABLE
                        ? "✓ 已禁用下滑"
                        : "✓ " + Config.actionName(action);
            } else {
                String display = keyLabel == null || keyLabel.isEmpty() ? "当前键" : keyLabel;
                text = display + " 下滑：" + Config.actionName(action);
''')
replace(hook, "            if (executed) hideKeyboardHint(650L);",
              "            if (executed) hideKeyboardHint(400L);")

# Lightweight candidate-bar text: no opaque pill and no large touch-area cover.
replace(hook, "        hint.setTextColor(Color.WHITE);",
              "        hint.setTextColor(0xF2FFFFFF);")
replace(hook, "        hint.setTextSize(10f);",
              "        hint.setTextSize(11f);")
replace(hook,
        "        hint.setPadding(dp(keyboard, 9), dp(keyboard, 3), dp(keyboard, 9), dp(keyboard, 3));",
        "        hint.setPadding(dp(keyboard, 4), dp(keyboard, 1), dp(keyboard, 4), dp(keyboard, 1));")
replace(hook,
'''        GradientDrawable background = new GradientDrawable();
        background.setColor(0xD9202124);
        background.setCornerRadius(dp(keyboard, 13));
        hint.setBackground(background);
''',
'''        hint.setBackground(null);
        hint.setTypeface(android.graphics.Typeface.DEFAULT_BOLD);
        hint.setShadowLayer(dp(keyboard, 2), 0f, dp(keyboard, 1), 0xD0000000);
''')

old_position = '''    private void positionKeyboardHint(View keyboard, TextView hint) {
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

new_position = '''    private void positionKeyboardHint(View keyboard, TextView hint) {
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
            if (rootWidth <= 0 || rootHeight <= 0) {
                hint.setVisibility(View.GONE);
                return;
            }

            int[] rootLocation = new int[2];
            int[] keyboardLocation = new int[2];
            root.getLocationInWindow(rootLocation);
            keyboard.getLocationInWindow(keyboardLocation);

            int keyboardLeft = keyboardLocation[0] - rootLocation[0];
            int keyboardTop = keyboardLocation[1] - rootLocation[1];
            int keyboardWidth = Math.max(1, keyboard.getWidth());
            int edge = dp(keyboard, 3);
            int maxWidth = Math.max(dp(keyboard, 92),
                    Math.min(Math.round(rootWidth * 0.52f), Math.round(keyboardWidth * 0.56f)));
            hint.setMaxWidth(maxWidth);
            hint.measure(
                    View.MeasureSpec.makeMeasureSpec(maxWidth, View.MeasureSpec.AT_MOST),
                    View.MeasureSpec.makeMeasureSpec(rootHeight, View.MeasureSpec.AT_MOST));
            int hintWidth = Math.max(dp(keyboard, 64), hint.getMeasuredWidth());
            int hintHeight = Math.max(dp(keyboard, 17), hint.getMeasuredHeight());

            // The candidate strip is the narrow band immediately above the
            // self-drawn key area. If that band does not exist, do not cover
            // any key as a fallback.
            if (keyboardTop < hintHeight + edge * 2) {
                hint.setVisibility(View.GONE);
                return;
            }

            int targetLeft = keyboardLeft + (keyboardWidth - hintWidth) / 2;
            targetLeft = Math.max(edge, Math.min(targetLeft, rootWidth - hintWidth - edge));
            int targetTop = keyboardTop - hintHeight - edge;

            params.leftMargin = targetLeft;
            params.topMargin = Math.max(edge, Math.min(targetTop, rootHeight - hintHeight - edge));
            hint.setLayoutParams(params);
            hint.bringToFront();
        } catch (Throwable throwable) {
            hint.setVisibility(View.GONE);
            logError("candidate hint positioning failed", throwable);
        }
    }
'''
replace(hook, old_position, new_position)

replace("app/build.gradle.kts", 'versionName = "1.11.0-test2"', 'versionName = "1.11.0-test3"')
replace("app/src/main/java/com/rww/wetypeswipe/MainActivity.java",
        'v1.11.0-test2 · 键盘提示动态定位',
        'v1.11.0-test3 · 候选栏轻量提示')

print("v1.11.0-test3 candidate-bar lightweight hint patch applied")
