from pathlib import Path

# Apply the working test5 implementation first.
exec(compile(Path("tools/patch_v110_test5.py").read_text(encoding="utf-8"), "tools/patch_v110_test5.py", "exec"))


def replace(path: str, old: str, new: str, count: int = 1) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    actual = text.count(old)
    if actual != count:
        raise RuntimeError(f"{path}: expected {count} matches, found {actual}: {old[:180]!r}")
    file.write_text(text.replace(old, new, count), encoding="utf-8")


hook = "app/src/main/java/com/rww/wetypeswipe/MainHook.java"
replace(hook, 'logInfo("v1.10.0-test5 entered target package");', 'logInfo("v1.10.0-test6 entered target package");')

# Native panel actions must never fall through to text/more-panel clicking.
replace(
    hook,
    '''        int iconResource = action == Config.ACTION_OPEN_CLIPBOARD
                ? 2131231369
                : 2131231376;
        if (invokeNativePanelListener(root, iconResource, action)) return true;

        String[] targets = action == Config.ACTION_OPEN_CLIPBOARD
                ? new String[]{"剪贴板", "clipboard", "clip_board"}
                : new String[]{"快捷发送", "常用语", "快捷语", "quickphrase", "quick_phrase", "commonphrase", "common_phrase"};

        if (clickMatchingView(root, targets)) return true;
''',
    '''        int iconResource = action == Config.ACTION_OPEN_CLIPBOARD
                ? 2131231369
                : 2131231376;
        return invokeValidatedNativePanelListener(root, iconResource, action);
''',
)

replace(
    hook,
    '''    private boolean invokeNativePanelListener(View root, int resourceId, int action) {
        cacheNativePanelButton(root, resourceId, action);
        WeakReference<View> reference = action == Config.ACTION_OPEN_CLIPBOARD
                ? clipboardNativeButtonRef : quickPhraseNativeButtonRef;
        View handler = reference.get();
        if (handler == null) {
            logError(Config.actionName(action) + " failed: native listener cache empty", null);
            return false;
        }
        try {
            boolean direct = handler.callOnClick();
            logInfo("native listener direct action=" + Config.actionName(action)
                    + " resource=" + resourceId
                    + " view=" + handler.getClass().getName()
                    + " shown=" + handler.isShown()
                    + " attached=" + handler.isAttachedToWindow()
                    + " result=" + direct);
            if (direct) return true;
        } catch (Throwable throwable) {
            logError("native listener direct failed action=" + Config.actionName(action), throwable);
        }
        try {
            boolean fallback = handler.performClick();
            logInfo("native listener performClick fallback action=" + Config.actionName(action)
                    + " result=" + fallback);
            return fallback;
        } catch (Throwable throwable) {
            logError("native listener fallback failed action=" + Config.actionName(action), throwable);
            return false;
        }
    }
''',
    '''    private boolean invokeValidatedNativePanelListener(View root, int resourceId, int action) {
        // The current hierarchy is authoritative. A stale cached listener may be
        // rebound by WeType to another toolbar action (notably hide-keyboard).
        View icon = findImageResourceAny(root, resourceId);
        if (icon == null) {
            clearNativePanelButton(action);
            logInfo("native action ignored: toolbar item disabled action="
                    + Config.actionName(action) + " resource=" + resourceId);
            return true;
        }

        View currentHandler = nearestClickHandler(icon);
        if (currentHandler == null || !currentHandler.isAttachedToWindow()) {
            clearNativePanelButton(action);
            logInfo("native action ignored: current handler unavailable action="
                    + Config.actionName(action) + " resource=" + resourceId);
            return true;
        }

        // Refresh the cache only from the currently matching icon.
        if (action == Config.ACTION_OPEN_CLIPBOARD) {
            clipboardNativeButtonRef = new WeakReference<>(currentHandler);
        } else {
            quickPhraseNativeButtonRef = new WeakReference<>(currentHandler);
        }

        try {
            boolean direct = currentHandler.callOnClick();
            logInfo("native listener validated action=" + Config.actionName(action)
                    + " resource=" + resourceId
                    + " view=" + currentHandler.getClass().getName()
                    + " shown=" + currentHandler.isShown()
                    + " attached=" + currentHandler.isAttachedToWindow()
                    + " result=" + direct);
            return direct;
        } catch (Throwable throwable) {
            clearNativePanelButton(action);
            logError("validated native listener failed action=" + Config.actionName(action), throwable);
            return true;
        }
    }

    private void clearNativePanelButton(int action) {
        if (action == Config.ACTION_OPEN_CLIPBOARD) {
            clipboardNativeButtonRef = new WeakReference<>(null);
        } else {
            quickPhraseNativeButtonRef = new WeakReference<>(null);
        }
    }
''',
)

replace(
    "app/build.gradle.kts",
    'versionName = "1.10.0-test5"',
    'versionName = "1.10.0-test6"',
)
replace(
    "app/src/main/java/com/rww/wetypeswipe/MainActivity.java",
    'v1.10.0-test5 · 原生监听器直调测试',
    'v1.10.0-test6 · 原生按钮存在性校验',
)

print("v1.10.0-test6 strict native button validation applied")
