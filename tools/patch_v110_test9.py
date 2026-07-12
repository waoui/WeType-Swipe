from pathlib import Path

# Reuse test8 diagnostics/helpers, then replace target-button callbacks with a generic toolbar command carrier.
exec(compile(Path("tools/patch_v110_test8.py").read_text(encoding="utf-8"), "tools/patch_v110_test8.py", "exec"))


def replace(path: str, old: str, new: str, count: int = 1) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    actual = text.count(old)
    if actual != count:
        raise RuntimeError(f"{path}: expected {count} matches, found {actual}: {old[:180]!r}")
    file.write_text(text.replace(old, new, count), encoding="utf-8")


hook = "app/src/main/java/com/rww/wetypeswipe/MainHook.java"
replace(hook, 'logInfo("v1.10.0-test8 entered target package");', 'logInfo("v1.10.0-test9 entered target package");')
replace(
    hook,
    '''    private boolean openNativePanel(InputMethodService ime, int action) {
        View root = imeRootView(ime);
        if (root != null) cacheNativePanelListeners(root);
        return invokeCachedNativeCallback(ime, action);
    }
''',
    '''    private boolean openNativePanel(InputMethodService ime, int action) {
        View root = imeRootView(ime);
        if (root == null) return false;
        return invokeToolbarCommandCarrier(root, action);
    }
''',
)

helpers = r'''
    private boolean invokeToolbarCommandCarrier(View root, int action) {
        Object[] carrier = findToolbarCommandCarrier(root);
        if (carrier == null) {
            logError(Config.actionName(action) + " failed: toolbar command carrier unavailable", null);
            return false;
        }

        View source = (View) carrier[0];
        Object listener = carrier[1];
        Object callback = carrier[2];
        Object holder = readNamedField(callback, "this$0");
        if (holder == null) {
            logError(Config.actionName(action) + " failed: toolbar holder unavailable", null);
            return false;
        }

        Field functionField = findNamedField(holder.getClass(), "f");
        Field categoryField = findNamedField(holder.getClass(), "g");
        Field groupField = findNamedField(holder.getClass(), "h");
        if (functionField == null) {
            logError(Config.actionName(action) + " failed: toolbar function field unavailable", null);
            return false;
        }

        int targetFunction = action == Config.ACTION_OPEN_CLIPBOARD ? 4 : 8;
        Object oldFunction = null;
        Object oldCategory = null;
        Object oldGroup = null;
        try {
            functionField.setAccessible(true);
            oldFunction = functionField.get(holder);
            functionField.set(holder, targetFunction);

            if (categoryField != null) {
                categoryField.setAccessible(true);
                oldCategory = categoryField.get(holder);
                Object permanent = enumConstant(categoryField.getType(), "Permanent");
                if (permanent != null) categoryField.set(holder, permanent);
            }
            if (groupField != null) {
                groupField.setAccessible(true);
                oldGroup = groupField.get(holder);
                groupField.set(holder, 6);
            }

            Method invokeMethod = findCompatibleInvoke(callback.getClass());
            if (invokeMethod == null) {
                logError(Config.actionName(action) + " failed: toolbar callback invoke unavailable", null);
                return false;
            }
            Object capturedView = readNamedField(callback, "$this_apply");
            View argument = capturedView instanceof View ? (View) capturedView : source;
            Object result = invokeMethod.invoke(callback, argument);
            logInfo("toolbar-command-carrier invoked action=" + Config.actionName(action)
                    + " targetFunction=" + targetFunction
                    + " oldFunction=" + String.valueOf(oldFunction)
                    + " listener=" + listener.getClass().getName()
                    + " callback=" + callback.getClass().getName()
                    + " holder=" + holder.getClass().getName()
                    + " sourceShown=" + source.isShown()
                    + " sourceAttached=" + source.isAttachedToWindow()
                    + " result=" + String.valueOf(result));
            return true;
        } catch (Throwable throwable) {
            logError("toolbar-command-carrier failed action=" + Config.actionName(action), throwable);
            return false;
        } finally {
            try { if (oldFunction != null) functionField.set(holder, oldFunction); } catch (Throwable ignored) {}
            try { if (categoryField != null && oldCategory != null) categoryField.set(holder, oldCategory); } catch (Throwable ignored) {}
            try { if (groupField != null && oldGroup != null) groupField.set(holder, oldGroup); } catch (Throwable ignored) {}
        }
    }

    private Object[] findToolbarCommandCarrier(View view) {
        if (view == null) return null;
        try {
            if (view.hasOnClickListeners() || view.isClickable()) {
                View.OnClickListener listener = readOnClickListener(view);
                if (listener != null && "com.tencent.wetype.plugin.hld.utils.h3".equals(listener.getClass().getName())) {
                    Object callback = readNamedField(listener, "c");
                    if (callback != null
                            && "com.tencent.wetype.plugin.hld.toolbar.a0$b".equals(callback.getClass().getName())
                            && readNamedField(callback, "this$0") != null) {
                        return new Object[]{view, listener, callback};
                    }
                }
            }
        } catch (Throwable ignored) {}
        if (view instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) view;
            for (int index = 0; index < group.getChildCount(); index++) {
                Object[] result = findToolbarCommandCarrier(group.getChildAt(index));
                if (result != null) return result;
            }
        }
        return null;
    }

    private static Field findNamedField(Class<?> type, String name) {
        for (Class<?> current = type; current != null; current = current.getSuperclass()) {
            try {
                Field field = current.getDeclaredField(name);
                field.setAccessible(true);
                return field;
            } catch (NoSuchFieldException ignored) {
            } catch (Throwable ignored) {
                return null;
            }
        }
        return null;
    }

    private static Object enumConstant(Class<?> type, String name) {
        if (type == null || !type.isEnum()) return null;
        try {
            Object[] constants = type.getEnumConstants();
            if (constants == null) return null;
            for (Object constant : constants) {
                if (name.equals(String.valueOf(constant))) return constant;
            }
        } catch (Throwable ignored) {}
        return null;
    }

'''
replace(hook, "    private boolean invokeCachedNativeCallback(InputMethodService ime, int action) {", helpers + "    private boolean invokeCachedNativeCallback(InputMethodService ime, int action) {")

replace(
    "app/build.gradle.kts",
    'versionName = "1.10.0-test8"',
    'versionName = "1.10.0-test9"',
)
replace(
    "app/src/main/java/com/rww/wetypeswipe/MainActivity.java",
    'v1.10.0-test8 · 工具栏回调直调与控制器探测',
    'v1.10.0-test9 · 工具栏功能编号直调',
)

print("v1.10.0-test9 toolbar command carrier patch applied")
