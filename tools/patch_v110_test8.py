from pathlib import Path

# Reuse test7 listener-object capture, then call the underlying toolbar callback directly.
exec(compile(Path("tools/patch_v110_test7.py").read_text(encoding="utf-8"), "tools/patch_v110_test7.py", "exec"))


def replace(path: str, old: str, new: str, count: int = 1) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    actual = text.count(old)
    if actual != count:
        raise RuntimeError(f"{path}: expected {count} matches, found {actual}: {old[:180]!r}")
    file.write_text(text.replace(old, new, count), encoding="utf-8")


hook = "app/src/main/java/com/rww/wetypeswipe/MainHook.java"
replace(hook, 'logInfo("v1.10.0-test7 entered target package");', 'logInfo("v1.10.0-test8 entered target package");')
replace(
    hook,
    "    private volatile View.OnClickListener clipboardNativeListener;\n"
    "    private volatile View.OnClickListener quickPhraseNativeListener;\n",
    "    private volatile View.OnClickListener clipboardNativeListener;\n"
    "    private volatile View.OnClickListener quickPhraseNativeListener;\n"
    "    private volatile Object clipboardNativeCallback;\n"
    "    private volatile Object quickPhraseNativeCallback;\n",
)
replace(
    hook,
    '''    private boolean openNativePanel(InputMethodService ime, int action) {
        View root = imeRootView(ime);
        if (root != null) cacheNativePanelListeners(root);
        return invokeCachedNativeListener(action);
    }
''',
    '''    private boolean openNativePanel(InputMethodService ime, int action) {
        View root = imeRootView(ime);
        if (root != null) cacheNativePanelListeners(root);
        return invokeCachedNativeCallback(ime, action);
    }
''',
)
replace(
    hook,
    '''        if (action == Config.ACTION_OPEN_CLIPBOARD) {
            clipboardNativeListener = listener;
            clipboardListenerSourceRef = new WeakReference<>(source);
        } else {
            quickPhraseNativeListener = listener;
            quickPhraseListenerSourceRef = new WeakReference<>(source);
        }

        logInfo("native-listener-object cached action=" + Config.actionName(action)
''',
    '''        Object callback = readNamedField(listener, "c");
        if (action == Config.ACTION_OPEN_CLIPBOARD) {
            clipboardNativeListener = listener;
            clipboardNativeCallback = callback;
            clipboardListenerSourceRef = new WeakReference<>(source);
        } else {
            quickPhraseNativeListener = listener;
            quickPhraseNativeCallback = callback;
            quickPhraseListenerSourceRef = new WeakReference<>(source);
        }

        logInfo("native-listener-object cached action=" + Config.actionName(action)
''',
)
replace(
    hook,
    '''        logInfo("native-listener-methods action=" + Config.actionName(action)
                + " " + describeListenerMethods(listener.getClass()));
    }

    private boolean invokeCachedNativeListener(int action) {
''',
    '''        logInfo("native-listener-methods action=" + Config.actionName(action)
                + " " + describeListenerMethods(listener.getClass()));
        logInfo("native-callback-object action=" + Config.actionName(action)
                + " class=" + (callback == null ? "null" : callback.getClass().getName())
                + " graph=" + describeObjectGraph(callback));
        if (callback != null) {
            logInfo("native-callback-methods action=" + Config.actionName(action)
                    + " " + describeListenerMethods(callback.getClass()));
        }
    }

    private boolean invokeCachedNativeCallback(InputMethodService ime, int action) {
        Object callback = action == Config.ACTION_OPEN_CLIPBOARD
                ? clipboardNativeCallback : quickPhraseNativeCallback;
        if (callback != null && ime != null) {
            try {
                Method invokeMethod = findCompatibleInvoke(callback.getClass());
                if (invokeMethod != null) {
                    View detachedArgument = new View(ime);
                    Object result = invokeMethod.invoke(callback, detachedArgument);
                    logInfo("native-callback-direct invoked action=" + Config.actionName(action)
                            + " callback=" + callback.getClass().getName()
                            + " argument=" + detachedArgument.getClass().getName()
                            + " result=" + String.valueOf(result));
                    return true;
                }
            } catch (Throwable throwable) {
                logError("native-callback-direct failed action=" + Config.actionName(action), throwable);
            }
        }
        return invokeCachedNativeListener(action);
    }

    private boolean invokeCachedNativeListener(int action) {
''',
)

extra_helpers = r'''
    private static Object readNamedField(Object object, String name) {
        if (object == null || name == null) return null;
        for (Class<?> type = object.getClass(); type != null; type = type.getSuperclass()) {
            try {
                Field field = type.getDeclaredField(name);
                field.setAccessible(true);
                return field.get(object);
            } catch (NoSuchFieldException ignored) {
            } catch (Throwable ignored) {
                return null;
            }
        }
        return null;
    }

    private static Method findCompatibleInvoke(Class<?> type) {
        if (type == null) return null;
        for (Class<?> current = type; current != null; current = current.getSuperclass()) {
            Method[] methods;
            try { methods = current.getDeclaredMethods(); }
            catch (Throwable ignored) { continue; }
            for (Method method : methods) {
                if (!"invoke".equals(method.getName()) || method.getParameterTypes().length != 1) continue;
                try { method.setAccessible(true); } catch (Throwable ignored) {}
                return method;
            }
        }
        return null;
    }

    private static String describeObjectGraph(Object root) {
        if (root == null) return "null";
        StringBuilder out = new StringBuilder(5200);
        java.util.IdentityHashMap<Object, Boolean> seen = new java.util.IdentityHashMap<>();
        appendObjectGraph(out, "root", root, 0, seen);
        return out.toString();
    }

    private static void appendObjectGraph(StringBuilder out, String label, Object object, int depth,
                                          java.util.IdentityHashMap<Object, Boolean> seen) {
        if (object == null || depth > 4 || out.length() > 5000) return;
        if (seen.put(object, Boolean.TRUE) != null) {
            out.append(label).append("=<cycle:").append(object.getClass().getName()).append(">;");
            return;
        }
        Class<?> objectClass = object.getClass();
        out.append(label).append('=').append(objectClass.getName()).append('{');
        int count = 0;
        for (Class<?> type = objectClass; type != null && count < 36; type = type.getSuperclass()) {
            Field[] fields;
            try { fields = type.getDeclaredFields(); }
            catch (Throwable ignored) { continue; }
            for (Field field : fields) {
                if (Modifier.isStatic(field.getModifiers()) || count >= 36 || out.length() > 5000) continue;
                try {
                    field.setAccessible(true);
                    Object value = field.get(object);
                    String fieldLabel = type.getSimpleName() + "." + field.getName();
                    if (value == null || value instanceof Number || value instanceof Boolean
                            || value instanceof Character || value instanceof CharSequence
                            || value.getClass().isEnum()) {
                        out.append(fieldLabel).append('=').append(String.valueOf(value)).append(';');
                    } else {
                        String name = value.getClass().getName();
                        if (depth < 4 && (name.startsWith("com.tencent.wetype")
                                || name.startsWith("fo.") || name.startsWith("go."))) {
                            appendObjectGraph(out, fieldLabel, value, depth + 1, seen);
                        } else {
                            out.append(fieldLabel).append("=<").append(name).append(">;");
                        }
                    }
                    count++;
                } catch (Throwable ignored) {}
            }
        }
        out.append("};");
    }

'''
replace(hook, "    private static String describeListenerFields(Object listener) {", extra_helpers + "    private static String describeListenerFields(Object listener) {")

replace(
    "app/build.gradle.kts",
    'versionName = "1.10.0-test7"',
    'versionName = "1.10.0-test8"',
)
replace(
    "app/src/main/java/com/rww/wetypeswipe/MainActivity.java",
    'v1.10.0-test7 · 原生监听器对象直调',
    'v1.10.0-test8 · 工具栏回调直调与控制器探测',
)

print("v1.10.0-test8 direct callback probe applied")
