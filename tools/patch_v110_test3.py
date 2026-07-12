from pathlib import Path

# Apply the feature patch first.
exec(compile(Path("tools/patch_v110_test.py").read_text(encoding="utf-8"), "tools/patch_v110_test.py", "exec"))


def replace(path: str, old: str, new: str, count: int = 1) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    actual = text.count(old)
    if actual != count:
        raise RuntimeError(f"{path}: expected {count} matches, found {actual}: {old[:140]!r}")
    file.write_text(text.replace(old, new, count), encoding="utf-8")


hook = "app/src/main/java/com/rww/wetypeswipe/MainHook.java"
replace(hook, "import java.lang.reflect.Method;\n", "import java.lang.reflect.Field;\nimport java.lang.reflect.Method;\nimport java.lang.reflect.Modifier;\n")
replace(hook, 'logInfo("v1.10.0-test1 entered target package");', 'logInfo("v1.10.0-test3 entered target package");')
replace(
    hook,
    "    private volatile Class<?> selectionHookedClass;\n    private BroadcastReceiver configReceiver;",
    "    private volatile Class<?> selectionHookedClass;\n    private volatile long nativeProbeDownTime = -1L;\n    private volatile int nativeProbeDispatchCount;\n    private final java.util.Set<String> nativeProbeClasses = ConcurrentHashMap.newKeySet();\n    private BroadcastReceiver configReceiver;",
)
replace(
    hook,
    '''        View view = (View) target;
        MotionEvent event = (MotionEvent) eventObject;
        Class<?> keyboardBase = keyboardBaseClass;

        if (keyboardBase == null) {
            if (event.getActionMasked() != MotionEvent.ACTION_DOWN) return chain.proceed();
            keyboardBase = findKeyboardBase(view.getClass());
            if (keyboardBase == null) return chain.proceed();
            keyboardBaseClass = keyboardBase;
            logInfo("keyboard class cached: " + keyboardBase.getName());
        } else if (!keyboardBase.isInstance(view)) {
            return chain.proceed();
        }
''',
    '''        View view = (View) target;
        MotionEvent event = (MotionEvent) eventObject;
        Class<?> keyboardBase = keyboardBaseClass;
        boolean probeDown = event.getActionMasked() == MotionEvent.ACTION_DOWN
                && isNativeProbeCandidate(view);
        if (probeDown) logNativeDispatchTarget(view, event);

        if (keyboardBase == null) {
            if (event.getActionMasked() != MotionEvent.ACTION_DOWN) return chain.proceed();
            keyboardBase = findKeyboardBase(view.getClass());
            if (keyboardBase == null) {
                Object result = chain.proceed();
                if (probeDown) probeNativeActionObject(view, event);
                return result;
            }
            keyboardBaseClass = keyboardBase;
            logInfo("keyboard class cached: " + keyboardBase.getName());
        } else if (!keyboardBase.isInstance(view)) {
            Object result = chain.proceed();
            if (probeDown) probeNativeActionObject(view, event);
            return result;
        }
''',
)
replace(
    hook,
    '''    private KeyInfo keyAfterDown(Object keyboard, MotionEvent event) {
        Object button = invoke(keyboard, "getActionButton");
        if (button == null) button = invoke(keyboard, "v1", event, false);
        if (button == null) button = invoke(keyboard, "v1", event, true);
        return keyFromButton(keyboard, button);
    }
''',
    '''    private KeyInfo keyAfterDown(Object keyboard, MotionEvent event) {
        Object button = invoke(keyboard, "getActionButton");
        if (button == null) button = invoke(keyboard, "v1", event, false);
        if (button == null) button = invoke(keyboard, "v1", event, true);
        KeyInfo keyInfo = keyFromButton(keyboard, button);
        if (keyInfo == null) logNativeActionObject(keyboard, event, button);
        return keyInfo;
    }
''',
)

helpers = r'''
    private boolean isNativeProbeCandidate(View view) {
        if (view == null) return false;
        try {
            Context context = view.getContext();
            if (context == null || !TARGET.equals(context.getPackageName())) return false;
        } catch (Throwable ignored) {
            return false;
        }
        String name = view.getClass().getName();
        return name.startsWith("com.tencent.wetype")
                || name.contains("hld")
                || view.isClickable()
                || view.getId() != View.NO_ID;
    }

    private void logNativeDispatchTarget(View view, MotionEvent event) {
        try {
            long downTime = event.getDownTime();
            synchronized (this) {
                if (nativeProbeDownTime != downTime) {
                    nativeProbeDownTime = downTime;
                    nativeProbeDispatchCount = 0;
                    logInfo("native-touch begin downTime=" + downTime
                            + " raw=" + event.getRawX() + "," + event.getRawY());
                }
                if (nativeProbeDispatchCount >= 48) return;
                nativeProbeDispatchCount++;
            }

            StringBuilder value = new StringBuilder(900);
            value.append("native-touch target#").append(nativeProbeDispatchCount)
                    .append(" class=").append(view.getClass().getName())
                    .append(" id=").append(view.getId())
                    .append(" res=").append(resourceEntryName(view))
                    .append(" clickable=").append(view.isClickable())
                    .append(" enabled=").append(view.isEnabled())
                    .append(" shown=").append(view.isShown())
                    .append(" local=").append(event.getX()).append(',').append(event.getY())
                    .append(" size=").append(view.getWidth()).append('x').append(view.getHeight())
                    .append(" desc=").append(String.valueOf(view.getContentDescription()));
            logInfo(value.toString());

            String className = view.getClass().getName();
            if ((className.startsWith("com.tencent.wetype") || className.contains("hld"))
                    && nativeProbeClasses.add(className)) {
                logInfo("native-class " + describeClass(view.getClass()));
                logInfo("native-fields " + describeCandidateFields(view));
            }
        } catch (Throwable throwable) {
            logError("native-touch target probe failed", throwable);
        }
    }

    private void probeNativeActionObject(Object owner, MotionEvent event) {
        probeNativeActionObject(owner, event, null);
    }

    private void probeNativeActionObject(Object owner, MotionEvent event, Object initialButton) {
        try {
            Object button = initialButton;
            if (button == null) button = invoke(owner, "getActionButton");
            if (button == null) button = invoke(owner, "getCurrentButton");
            if (button == null) button = invoke(owner, "getPressedButton");
            if (button == null) button = invoke(owner, "v1", event, false);
            if (button == null) button = invoke(owner, "v1", event, true);

            StringBuilder out = new StringBuilder(3400);
            out.append("owner=").append(owner == null ? "null" : owner.getClass().getName()).append(';');
            appendObjectSummary(out, "button", button);
            Object keyData = invoke(button, "O");
            appendObjectSummary(out, "keyData", keyData);
            appendSimpleValue(out, "button.K", invoke(button, "K"));
            appendSimpleValue(out, "main", invoke(keyData, "getMainText"));
            appendSimpleValue(out, "sub", invoke(keyData, "getSubText"));
            appendSimpleValue(out, "secondary", invoke(keyData, "getSecondaryText"));
            appendSimpleValue(out, "hint", invoke(keyData, "getHintText"));
            appendSimpleValue(out, "assist", invoke(keyData, "getAssistText"));
            appendSimpleValue(out, "id", invoke(keyData, "getId"));
            if (button == null) out.append("ownerFields=").append(describeCandidateFields(owner));
            logInfo("native-action " + out);
        } catch (Throwable throwable) {
            logError("native-action probe failed", throwable);
        }
    }

    private static String resourceEntryName(View view) {
        if (view == null || view.getId() == View.NO_ID) return "-";
        try {
            return view.getResources().getResourceEntryName(view.getId());
        } catch (Throwable ignored) {
            return String.valueOf(view.getId());
        }
    }

    private static String describeClass(Class<?> type) {
        StringBuilder out = new StringBuilder(3000);
        out.append(type.getName()).append(" methods=");
        int count = 0;
        for (Class<?> current = type; current != null && count < 70; current = current.getSuperclass()) {
            Method[] methods;
            try {
                methods = current.getDeclaredMethods();
            } catch (Throwable ignored) {
                continue;
            }
            for (Method method : methods) {
                if (count >= 70 || out.length() > 2900) break;
                out.append(method.getName()).append('(');
                Class<?>[] params = method.getParameterTypes();
                for (int index = 0; index < params.length; index++) {
                    if (index > 0) out.append(',');
                    out.append(params[index].getSimpleName());
                }
                out.append(")->").append(method.getReturnType().getSimpleName()).append(',');
                count++;
            }
        }
        return out.toString();
    }

    private static String describeCandidateFields(Object object) {
        if (object == null) return "null";
        StringBuilder out = new StringBuilder(2600);
        int count = 0;
        for (Class<?> type = object.getClass(); type != null && count < 48; type = type.getSuperclass()) {
            Field[] fields;
            try {
                fields = type.getDeclaredFields();
            } catch (Throwable ignored) {
                continue;
            }
            for (Field field : fields) {
                if (count >= 48 || out.length() > 2500) break;
                if (Modifier.isStatic(field.getModifiers())) continue;
                try {
                    field.setAccessible(true);
                    Object value = field.get(object);
                    out.append(field.getName()).append(':').append(field.getType().getSimpleName()).append('=');
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

    private static void appendObjectSummary(StringBuilder out, String label, Object object) {
        if (object == null || out.length() > 3100) return;
        out.append(label).append('=').append(object.getClass().getName()).append('{');
        int count = 0;
        for (Class<?> type = object.getClass(); type != null && count < 40; type = type.getSuperclass()) {
            Field[] fields;
            try {
                fields = type.getDeclaredFields();
            } catch (Throwable ignored) {
                continue;
            }
            for (Field field : fields) {
                if (count >= 40 || out.length() > 3100) break;
                if (Modifier.isStatic(field.getModifiers())) continue;
                try {
                    field.setAccessible(true);
                    Object value = field.get(object);
                    out.append(field.getName()).append('=');
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
        out.append("};");
    }

    private static void appendSimpleValue(StringBuilder out, String label, Object value) {
        if (value == null || out.length() > 3250) return;
        out.append(label).append('=').append(String.valueOf(value)).append(';');
    }

'''
replace(hook, '    private static boolean isNativePanelAction(int action) {', helpers + '    private static boolean isNativePanelAction(int action) {')

replace(
    "app/build.gradle.kts",
    'versionName = "1.10.0-test1"',
    'versionName = "1.10.0-test3"',
)
replace(
    "app/src/main/java/com/rww/wetypeswipe/MainActivity.java",
    'v1.10.0 测试版 · 原生剪贴板与快捷发送',
    'v1.10.0-test3 · 原生工具栏触摸诊断',
)

print("v1.10.0-test3 touch diagnostic patch applied")
