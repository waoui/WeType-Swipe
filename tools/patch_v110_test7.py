from pathlib import Path

# Apply the v1.10.0 feature patch first.
exec(compile(Path("tools/patch_v110_test.py").read_text(encoding="utf-8"), "tools/patch_v110_test.py", "exec"))


def replace(path: str, old: str, new: str, count: int = 1) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    actual = text.count(old)
    if actual != count:
        raise RuntimeError(f"{path}: expected {count} matches, found {actual}: {old[:180]!r}")
    file.write_text(text.replace(old, new, count), encoding="utf-8")


hook = "app/src/main/java/com/rww/wetypeswipe/MainHook.java"
replace(hook, "import android.widget.TextView;\n", "import android.widget.ImageView;\nimport android.widget.TextView;\n")
replace(hook, "import java.lang.reflect.Method;\n", "import java.lang.reflect.Field;\nimport java.lang.reflect.Method;\nimport java.lang.reflect.Modifier;\n")
replace(hook, 'logInfo("v1.10.0-test1 entered target package");', 'logInfo("v1.10.0-test7 entered target package");')
replace(
    hook,
    "    private volatile Class<?> selectionHookedClass;\n    private BroadcastReceiver configReceiver;",
    "    private volatile Class<?> selectionHookedClass;\n"
    "    private volatile View.OnClickListener clipboardNativeListener;\n"
    "    private volatile View.OnClickListener quickPhraseNativeListener;\n"
    "    private volatile WeakReference<View> clipboardListenerSourceRef = new WeakReference<>(null);\n"
    "    private volatile WeakReference<View> quickPhraseListenerSourceRef = new WeakReference<>(null);\n"
    "    private BroadcastReceiver configReceiver;",
)
replace(
    hook,
    '''        if (maskedAction == MotionEvent.ACTION_DOWN) {
            tracker.begin(keyboard, event.getX(), event.getY());
            Object result = chain.proceed();
''',
    '''        if (maskedAction == MotionEvent.ACTION_DOWN) {
            cacheNativePanelListeners(findIme(keyboard.getContext()));
            tracker.begin(keyboard, event.getX(), event.getY());
            Object result = chain.proceed();
''',
)

old_open = '''    private boolean openNativePanel(InputMethodService ime, int action) {
        View root = imeRootView(ime);
        if (root == null) return false;

        String[] targets = action == Config.ACTION_OPEN_CLIPBOARD
                ? new String[]{"剪贴板", "clipboard", "clip_board"}
                : new String[]{"快捷发送", "常用语", "快捷语", "quickphrase", "quick_phrase", "commonphrase", "common_phrase"};

        if (clickMatchingView(root, targets)) return true;

        String[] moreTargets = {"更多", "more", "tool_more", "toolbar_more", "expand_tools"};
        if (!clickMatchingView(root, moreTargets)) return false;

        root.postDelayed(() -> {
            View latestRoot = imeRootView(ime);
            if (latestRoot == null || !clickMatchingView(latestRoot, targets)) {
                logError(Config.actionName(action) + " failed after opening more panel", null);
            }
        }, 240L);
        return true;
    }
'''
new_open = '''    private boolean openNativePanel(InputMethodService ime, int action) {
        View root = imeRootView(ime);
        if (root != null) cacheNativePanelListeners(root);
        return invokeCachedNativeListener(action);
    }
'''
replace(hook, old_open, new_open)

helpers = r'''
    private void cacheNativePanelListeners(InputMethodService ime) {
        cacheNativePanelListeners(imeRootView(ime));
    }

    private void cacheNativePanelListeners(View root) {
        if (root == null) return;
        cacheNativePanelListener(root, 2131231369, Config.ACTION_OPEN_CLIPBOARD);
        cacheNativePanelListener(root, 2131231376, Config.ACTION_OPEN_QUICK_PHRASE);
    }

    private void cacheNativePanelListener(View root, int resourceId, int action) {
        View icon = findImageResourceAny(root, resourceId);
        if (icon == null) return;
        View source = nearestClickHandler(icon);
        if (source == null) return;
        View.OnClickListener listener = readOnClickListener(source);
        if (listener == null) return;

        View.OnClickListener previous = action == Config.ACTION_OPEN_CLIPBOARD
                ? clipboardNativeListener : quickPhraseNativeListener;
        if (previous == listener) return;

        if (action == Config.ACTION_OPEN_CLIPBOARD) {
            clipboardNativeListener = listener;
            clipboardListenerSourceRef = new WeakReference<>(source);
        } else {
            quickPhraseNativeListener = listener;
            quickPhraseListenerSourceRef = new WeakReference<>(source);
        }

        logInfo("native-listener-object cached action=" + Config.actionName(action)
                + " resource=" + resourceId
                + " listener=" + listener.getClass().getName()
                + " source=" + source.getClass().getName()
                + " sourceId=" + source.getId()
                + " attached=" + source.isAttachedToWindow());
        logInfo("native-listener-fields action=" + Config.actionName(action)
                + " " + describeListenerFields(listener));
        logInfo("native-listener-methods action=" + Config.actionName(action)
                + " " + describeListenerMethods(listener.getClass()));
    }

    private boolean invokeCachedNativeListener(int action) {
        View.OnClickListener listener = action == Config.ACTION_OPEN_CLIPBOARD
                ? clipboardNativeListener : quickPhraseNativeListener;
        WeakReference<View> sourceReference = action == Config.ACTION_OPEN_CLIPBOARD
                ? clipboardListenerSourceRef : quickPhraseListenerSourceRef;
        View source = sourceReference.get();

        if (listener == null || source == null) {
            logError(Config.actionName(action) + " failed: native listener object unavailable", null);
            return false;
        }

        try {
            listener.onClick(source);
            logInfo("native-listener-object invoked action=" + Config.actionName(action)
                    + " listener=" + listener.getClass().getName()
                    + " source=" + source.getClass().getName()
                    + " sourceId=" + source.getId()
                    + " shown=" + source.isShown()
                    + " attached=" + source.isAttachedToWindow());
            return true;
        } catch (Throwable throwable) {
            logError("native-listener-object invoke failed action=" + Config.actionName(action), throwable);
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

    private static View.OnClickListener readOnClickListener(View view) {
        if (view == null) return null;
        try {
            Method method = View.class.getDeclaredMethod("getListenerInfo");
            method.setAccessible(true);
            Object listenerInfo = method.invoke(view);
            if (listenerInfo == null) return null;
            Field field = listenerInfo.getClass().getDeclaredField("mOnClickListener");
            field.setAccessible(true);
            Object value = field.get(listenerInfo);
            return value instanceof View.OnClickListener ? (View.OnClickListener) value : null;
        } catch (Throwable ignored) {
            return null;
        }
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

    private static String describeListenerFields(Object listener) {
        if (listener == null) return "null";
        StringBuilder out = new StringBuilder(3000);
        int count = 0;
        for (Class<?> type = listener.getClass(); type != null && count < 60; type = type.getSuperclass()) {
            Field[] fields;
            try { fields = type.getDeclaredFields(); }
            catch (Throwable ignored) { continue; }
            for (Field field : fields) {
                if (count >= 60 || out.length() > 2850) break;
                if (Modifier.isStatic(field.getModifiers())) continue;
                try {
                    field.setAccessible(true);
                    Object value = field.get(listener);
                    out.append(type.getSimpleName()).append('.').append(field.getName())
                            .append(':').append(field.getType().getName()).append('=');
                    if (value == null || value instanceof Number || value instanceof Boolean
                            || value instanceof Character || value instanceof CharSequence
                            || value.getClass().isEnum()) {
                        out.append(String.valueOf(value));
                    } else {
                        out.append('<').append(value.getClass().getName()).append('>');
                    }
                    out.append(',');
                    count++;
                } catch (Throwable ignored) {}
            }
        }
        return out.toString();
    }

    private static String describeListenerMethods(Class<?> listenerClass) {
        if (listenerClass == null) return "null";
        StringBuilder out = new StringBuilder(2200);
        int count = 0;
        for (Class<?> type = listenerClass; type != null && count < 50; type = type.getSuperclass()) {
            Method[] methods;
            try { methods = type.getDeclaredMethods(); }
            catch (Throwable ignored) { continue; }
            for (Method method : methods) {
                if (count >= 50 || out.length() > 2050) break;
                out.append(type.getSimpleName()).append('.').append(method.getName()).append('(');
                Class<?>[] parameters = method.getParameterTypes();
                for (int index = 0; index < parameters.length; index++) {
                    if (index > 0) out.append(',');
                    out.append(parameters[index].getName());
                }
                out.append(")->").append(method.getReturnType().getName()).append(',');
                count++;
            }
        }
        return out.toString();
    }

'''
replace(hook, "    private boolean clickMatchingView(View root, String[] tokens) {", helpers + "    private boolean clickMatchingView(View root, String[] tokens) {")

replace(
    "app/build.gradle.kts",
    'versionName = "1.10.0-test1"',
    'versionName = "1.10.0-test7"',
)
replace(
    "app/src/main/java/com/rww/wetypeswipe/MainActivity.java",
    'v1.10.0 测试版 · 原生剪贴板与快捷发送',
    'v1.10.0-test7 · 原生监听器对象直调',
)

print("v1.10.0-test7 native listener object patch applied")
