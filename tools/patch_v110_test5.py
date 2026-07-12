from pathlib import Path

# Apply the existing v1.10.0-test1 feature patch first.
exec(compile(Path("tools/patch_v110_test.py").read_text(encoding="utf-8"), "tools/patch_v110_test.py", "exec"))


def replace(path: str, old: str, new: str, count: int = 1) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    actual = text.count(old)
    if actual != count:
        raise RuntimeError(f"{path}: expected {count} matches, found {actual}: {old[:160]!r}")
    file.write_text(text.replace(old, new, count), encoding="utf-8")


hook = "app/src/main/java/com/rww/wetypeswipe/MainHook.java"
replace(hook, "import android.widget.TextView;\n", "import android.widget.ImageView;\nimport android.widget.TextView;\n")
replace(hook, "import java.lang.reflect.Method;\n", "import java.lang.reflect.Field;\nimport java.lang.reflect.Method;\n")
replace(hook, 'logInfo("v1.10.0-test1 entered target package");', 'logInfo("v1.10.0-test5 entered target package");')
replace(
    hook,
    "    private volatile Class<?> selectionHookedClass;\n    private BroadcastReceiver configReceiver;",
    "    private volatile Class<?> selectionHookedClass;\n"
    "    private volatile WeakReference<View> clipboardNativeButtonRef = new WeakReference<>(null);\n"
    "    private volatile WeakReference<View> quickPhraseNativeButtonRef = new WeakReference<>(null);\n"
    "    private BroadcastReceiver configReceiver;",
)
replace(
    hook,
    '''        if (maskedAction == MotionEvent.ACTION_DOWN) {
            tracker.begin(keyboard, event.getX(), event.getY());
            Object result = chain.proceed();
''',
    '''        if (maskedAction == MotionEvent.ACTION_DOWN) {
            cacheNativePanelButtons(findIme(keyboard.getContext()));
            tracker.begin(keyboard, event.getX(), event.getY());
            Object result = chain.proceed();
''',
)
replace(
    hook,
    '''        String[] targets = action == Config.ACTION_OPEN_CLIPBOARD
                ? new String[]{"剪贴板", "clipboard", "clip_board"}
                : new String[]{"快捷发送", "常用语", "快捷语", "quickphrase", "quick_phrase", "commonphrase", "common_phrase"};

        if (clickMatchingView(root, targets)) return true;
''',
    '''        int iconResource = action == Config.ACTION_OPEN_CLIPBOARD
                ? 2131231369
                : 2131231376;
        if (invokeNativePanelListener(root, iconResource, action)) return true;

        String[] targets = action == Config.ACTION_OPEN_CLIPBOARD
                ? new String[]{"剪贴板", "clipboard", "clip_board"}
                : new String[]{"快捷发送", "常用语", "快捷语", "quickphrase", "quick_phrase", "commonphrase", "common_phrase"};

        if (clickMatchingView(root, targets)) return true;
''',
)

helpers = r'''
    private void cacheNativePanelButtons(InputMethodService ime) {
        View root = imeRootView(ime);
        if (root == null) return;
        cacheNativePanelButton(root, 2131231369, Config.ACTION_OPEN_CLIPBOARD);
        cacheNativePanelButton(root, 2131231376, Config.ACTION_OPEN_QUICK_PHRASE);
    }

    private void cacheNativePanelButton(View root, int resourceId, int action) {
        View icon = findImageResourceAny(root, resourceId);
        View handler = nearestClickHandler(icon);
        if (handler == null) return;
        WeakReference<View> existing = action == Config.ACTION_OPEN_CLIPBOARD
                ? clipboardNativeButtonRef : quickPhraseNativeButtonRef;
        if (existing.get() == handler) return;
        if (action == Config.ACTION_OPEN_CLIPBOARD) {
            clipboardNativeButtonRef = new WeakReference<>(handler);
        } else {
            quickPhraseNativeButtonRef = new WeakReference<>(handler);
        }
        logInfo("native listener cached action=" + Config.actionName(action)
                + " resource=" + resourceId
                + " view=" + handler.getClass().getName()
                + " shown=" + handler.isShown()
                + " attached=" + handler.isAttachedToWindow()
                + " hasListener=" + handler.hasOnClickListeners());
    }

    private boolean invokeNativePanelListener(View root, int resourceId, int action) {
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

    private View findImageResourceAny(View view, int resourceId) {
        if (view == null) return null;
        if (view instanceof ImageView && imageResourceId((ImageView) view) == resourceId) return view;
        if (view instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) view;
            for (int index = 0; index < group.getChildCount(); index++) {
                View result = findImageResourceAny(group.getChildAt(index), resourceId);
                if (result != null) return result;
            }
        }
        return null;
    }

    private static View nearestClickHandler(View view) {
        View current = view;
        for (int depth = 0; current != null && depth < 10; depth++) {
            if (current.hasOnClickListeners() || current.isClickable()) return current;
            Object parent = current.getParent();
            current = parent instanceof View ? (View) parent : null;
        }
        return null;
    }

    private static int imageResourceId(ImageView image) {
        if (image == null) return 0;
        try {
            Field field = ImageView.class.getDeclaredField("mResource");
            field.setAccessible(true);
            return field.getInt(image);
        } catch (Throwable ignored) {
            return 0;
        }
    }

'''
replace(hook, "    private boolean clickMatchingView(View root, String[] tokens) {", helpers + "    private boolean clickMatchingView(View root, String[] tokens) {")

replace(
    "app/build.gradle.kts",
    'versionName = "1.10.0-test1"',
    'versionName = "1.10.0-test5"',
)
replace(
    "app/src/main/java/com/rww/wetypeswipe/MainActivity.java",
    'v1.10.0 测试版 · 原生剪贴板与快捷发送',
    'v1.10.0-test5 · 原生监听器直调测试',
)

print("v1.10.0-test5 native listener patch applied")
