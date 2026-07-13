from pathlib import Path
import re
import runpy

runpy.run_path("tools/patch_v111_test10.py", run_name="__main__")

hook = Path("app/src/main/java/com/rww/wetypeswipe/MainHook.java")
text = hook.read_text(encoding="utf-8")


def replace_once(source: str, old: str, new: str, name: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"{name}: expected 1 match, found {count}")
    return source.replace(old, new, 1)


text = replace_once(
    text,
    "import android.graphics.Paint;\nimport android.graphics.Typeface;",
    "import android.graphics.Paint;\nimport android.graphics.Rect;\nimport android.graphics.RectF;\nimport android.graphics.Typeface;",
    "diagnostic graphics imports")

text = replace_once(
    text,
    "    private final Paint keyboardLabelPaint = new Paint(Paint.ANTI_ALIAS_FLAG);",
    "    private final Paint keyboardLabelPaint = new Paint(Paint.ANTI_ALIAS_FLAG);\n"
    "    private final ConcurrentHashMap<Method, Boolean> nativeDiagnosticHookedMethods = new ConcurrentHashMap<>();\n"
    "    private final ConcurrentHashMap<Method, Boolean> nativeDiagnosticInvokedMethods = new ConcurrentHashMap<>();\n"
    "    private volatile WeakReference<View> nativeDiagnosticViewRef = new WeakReference<>(null);\n"
    "    private volatile String nativeDiagnosticSignature = \"\";\n"
    "    private volatile boolean nativeDiagnosticRunning;\n"
    "    private volatile int nativeDiagnosticLogBudget = 260;",
    "diagnostic fields")

text = replace_once(
    text,
    '            logInfo("v1.11.0-test10 entered target package");',
    '            logInfo("v1.11.0-diag1 entered target package");',
    "diagnostic version log")

text = replace_once(
    text,
    "                ensureKeyboardLabelGeometry(keyboard);\n                drawQwertyFunctionLabels(keyboard, canvas, config);",
    "                ensureKeyboardLabelGeometry(keyboard);\n"
    "                ensureNativeKeyDiagnostics(keyboard);\n"
    "                drawQwertyFunctionLabels(keyboard, canvas, config);",
    "diagnostic draw entry")

helpers = r'''    private void ensureNativeKeyDiagnostics(View keyboard) {
        if (keyboard == null || keyboard.getWidth() <= 0 || keyboard.getHeight() <= 0) return;
        Map<String, List<Float>> centers = keyboardLabelCenters;
        if (centers == null || centers.isEmpty()) return;
        String signature = keyboard.getClass().getName() + '@' + keyboard.getWidth() + 'x'
                + keyboard.getHeight() + '#' + keyboardLabelLayoutSignature;
        if (nativeDiagnosticViewRef.get() == keyboard && signature.equals(nativeDiagnosticSignature)) return;
        if (nativeDiagnosticRunning) return;
        nativeDiagnosticRunning = true;
        nativeDiagnosticViewRef = new WeakReference<>(keyboard);
        nativeDiagnosticSignature = signature;
        nativeDiagnosticLogBudget = 260;
        keyboard.postDelayed(() -> {
            try {
                runNativeKeyDiagnostics(keyboard, signature);
            } catch (Throwable throwable) {
                logError("native-key diagnostic failed", throwable);
            } finally {
                nativeDiagnosticRunning = false;
            }
        }, 240L);
    }

    private void runNativeKeyDiagnostics(View keyboard, String signature) {
        if (keyboard == null || !keyboard.isAttachedToWindow()) return;
        diagnosticLog("diag-start signature=" + signature);
        diagnosticLog("diag-keyboard class=" + keyboard.getClass().getName());

        java.util.LinkedHashSet<Class<?>> classes = new java.util.LinkedHashSet<>();
        collectDiagnosticClasses(keyboard, 1, classes,
                new java.util.IdentityHashMap<Object, Boolean>());
        dumpDiagnosticObject("keyboard", keyboard, 1,
                new java.util.IdentityHashMap<Object, Boolean>());

        String[] sampleKeys = {"q", "a", "s", "z", "v"};
        for (String key : sampleKeys) {
            Object button = diagnosticButtonForKey(keyboard, key);
            if (button == null) {
                diagnosticLog("diag-button key=" + key + " unavailable");
                continue;
            }
            diagnosticLog("diag-button key=" + key + " class=" + button.getClass().getName()
                    + " id=" + Integer.toHexString(System.identityHashCode(button)));
            dumpDiagnosticObject("key=" + key, button, 2,
                    new java.util.IdentityHashMap<Object, Boolean>());
            collectDiagnosticClasses(button, 2, classes,
                    new java.util.IdentityHashMap<Object, Boolean>());
        }

        int installed = 0;
        for (Class<?> type : classes) {
            installed += installNativeDiagnosticHooks(type, 80 - installed);
            if (installed >= 80) break;
        }
        diagnosticLog("diag-hooks installed=" + installed + " classes=" + classes.size());
        keyboard.postInvalidate();
        diagnosticLog("diag-end; redraw requested");
    }

    private Object diagnosticButtonForKey(View keyboard, String key) {
        Map<String, List<Float>> centers = keyboardLabelCenters;
        List<Float> values = centers == null ? null : centers.get(key);
        if (values == null || values.isEmpty()) return null;
        Float x = values.get(0);
        if (x == null) return null;
        float y;
        if ("qwertyuiop".contains(key)) y = keyboard.getHeight() * 0.125f;
        else if ("asdfghjkl".contains(key)) y = keyboard.getHeight() * 0.375f;
        else y = keyboard.getHeight() * 0.625f;
        long now = SystemClock.uptimeMillis();
        MotionEvent event = MotionEvent.obtain(now, now, MotionEvent.ACTION_DOWN, x, y, 0);
        try {
            Object button = invoke(keyboard, "v1", event, false);
            if (button == null) button = invoke(keyboard, "v1", event, true);
            return button;
        } catch (Throwable ignored) {
            return null;
        } finally {
            event.recycle();
        }
    }

    private void dumpDiagnosticObject(String path, Object object, int depth,
                                      java.util.IdentityHashMap<Object, Boolean> visited) {
        if (object == null || depth < 0 || visited.put(object, Boolean.TRUE) != null) return;
        Class<?> type = object.getClass();
        diagnosticLog("diag-object path=" + path + " class=" + type.getName());
        dumpDiagnosticMethods(type, path);
        for (Class<?> current = type; current != null && current != Object.class;
             current = current.getSuperclass()) {
            Field[] fields;
            try { fields = current.getDeclaredFields(); }
            catch (Throwable ignored) { continue; }
            for (Field field : fields) {
                try {
                    field.setAccessible(true);
                    Object value = field.get(object);
                    String summary = diagnosticValueSummary(value);
                    diagnosticLog("diag-field path=" + path + " owner=" + current.getName()
                            + " name=" + field.getName() + " type=" + field.getType().getName()
                            + " value=" + summary);
                    if (depth > 0 && value != null && diagnosticTencentType(value.getClass())) {
                        dumpDiagnosticObject(path + '.' + field.getName(), value, depth - 1, visited);
                    }
                } catch (Throwable throwable) {
                    diagnosticLog("diag-field-unreadable path=" + path + " name=" + field.getName()
                            + " error=" + throwable.getClass().getSimpleName());
                }
            }
        }
    }

    private void dumpDiagnosticMethods(Class<?> type, String path) {
        if (type == null) return;
        for (Class<?> current = type; current != null && current != Object.class;
             current = current.getSuperclass()) {
            Method[] methods;
            try { methods = current.getDeclaredMethods(); }
            catch (Throwable ignored) { continue; }
            for (Method method : methods) {
                if (!diagnosticMethodCandidate(method)) continue;
                diagnosticLog("diag-method path=" + path + " signature="
                        + diagnosticMethodSignature(method));
            }
        }
    }

    private void collectDiagnosticClasses(Object object, int depth,
                                          java.util.Set<Class<?>> output,
                                          java.util.IdentityHashMap<Object, Boolean> visited) {
        if (object == null || depth < 0 || visited.put(object, Boolean.TRUE) != null) return;
        Class<?> type = object.getClass();
        if (diagnosticTencentType(type)) output.add(type);
        if (depth == 0) return;
        for (Class<?> current = type; current != null && current != Object.class;
             current = current.getSuperclass()) {
            Field[] fields;
            try { fields = current.getDeclaredFields(); }
            catch (Throwable ignored) { continue; }
            for (Field field : fields) {
                try {
                    field.setAccessible(true);
                    Object value = field.get(object);
                    if (value != null && diagnosticTencentType(value.getClass())) {
                        collectDiagnosticClasses(value, depth - 1, output, visited);
                    }
                } catch (Throwable ignored) {
                }
            }
        }
    }

    private int installNativeDiagnosticHooks(Class<?> type, int remaining) {
        if (type == null || remaining <= 0 || !diagnosticTencentType(type)) return 0;
        int installed = 0;
        for (Class<?> current = type; current != null && current != Object.class;
             current = current.getSuperclass()) {
            Method[] methods;
            try { methods = current.getDeclaredMethods(); }
            catch (Throwable ignored) { continue; }
            for (Method method : methods) {
                if (installed >= remaining || !diagnosticMethodCandidate(method)) continue;
                int modifiers = method.getModifiers();
                if (java.lang.reflect.Modifier.isAbstract(modifiers)
                        || java.lang.reflect.Modifier.isNative(modifiers)) continue;
                if (nativeDiagnosticHookedMethods.putIfAbsent(method, Boolean.TRUE) != null) continue;
                try {
                    method.setAccessible(true);
                    hook(method).setExceptionMode(XposedInterface.ExceptionMode.PROTECTIVE)
                            .intercept(chain -> {
                                Object result = chain.proceed();
                                if (nativeDiagnosticInvokedMethods.putIfAbsent(method, Boolean.TRUE) == null) {
                                    StringBuilder line = new StringBuilder("diag-invoke signature=")
                                            .append(diagnosticMethodSignature(method)).append(" args=");
                                    Class<?>[] parameters = method.getParameterTypes();
                                    for (int index = 0; index < parameters.length; index++) {
                                        if (index > 0) line.append(';');
                                        Object arg;
                                        try { arg = chain.getArg(index); }
                                        catch (Throwable ignored) { arg = null; }
                                        line.append(index).append(':').append(diagnosticValueSummary(arg));
                                    }
                                    line.append(" result=").append(diagnosticValueSummary(result));
                                    diagnosticLog(line.toString());
                                    diagnosticLog("diag-stack " + diagnosticTencentStack());
                                }
                                return result;
                            });
                    installed++;
                } catch (Throwable throwable) {
                    nativeDiagnosticHookedMethods.remove(method);
                    diagnosticLog("diag-hook-failed signature=" + diagnosticMethodSignature(method)
                            + " error=" + throwable.getClass().getSimpleName());
                }
            }
        }
        return installed;
    }

    private static boolean diagnosticMethodCandidate(Method method) {
        if (method == null || method.isSynthetic() || method.isBridge()) return false;
        Class<?>[] parameters = method.getParameterTypes();
        if (parameters.length > 8) return false;
        boolean graphics = false;
        boolean text = false;
        for (Class<?> parameter : parameters) {
            if (parameter == Canvas.class || parameter == Paint.class
                    || parameter == Rect.class || parameter == RectF.class
                    || android.graphics.drawable.Drawable.class.isAssignableFrom(parameter)) graphics = true;
            if (parameter == String.class || CharSequence.class.isAssignableFrom(parameter)) text = true;
        }
        Class<?> result = method.getReturnType();
        if (result == String.class || CharSequence.class.isAssignableFrom(result)) text = true;
        String name = method.getName().toLowerCase(Locale.ROOT);
        boolean named = name.contains("draw") || name.contains("render") || name.contains("text")
                || name.contains("label") || name.contains("hint") || name.contains("key");
        return graphics || text || named;
    }

    private static boolean diagnosticTencentType(Class<?> type) {
        if (type == null) return false;
        String name = type.getName();
        return name.startsWith("com.tencent.wetype") || name.startsWith("com.tencent.mm");
    }

    private static String diagnosticMethodSignature(Method method) {
        if (method == null) return "null";
        StringBuilder value = new StringBuilder(method.getDeclaringClass().getName())
                .append('#').append(method.getName()).append('(');
        Class<?>[] parameters = method.getParameterTypes();
        for (int index = 0; index < parameters.length; index++) {
            if (index > 0) value.append(',');
            value.append(parameters[index].getName());
        }
        return value.append(")->").append(method.getReturnType().getName()).toString();
    }

    private static String diagnosticValueSummary(Object value) {
        if (value == null) return "null";
        if (value instanceof Rect) return "Rect" + value;
        if (value instanceof RectF) return "RectF" + value;
        if (value instanceof Number || value instanceof Boolean || value instanceof Character
                || value.getClass().isEnum()) return String.valueOf(value);
        if (value instanceof CharSequence) {
            String text = value.toString();
            boolean safe = text.length() <= 16;
            for (int index = 0; safe && index < text.length(); index++) {
                char ch = text.charAt(index);
                if (Character.isWhitespace(ch) || Character.isISOControl(ch)) safe = false;
            }
            return safe ? "text[" + text + "]" : "text-length=" + text.length();
        }
        if (value instanceof Canvas) return "Canvas";
        if (value instanceof Paint) return "Paint(size=" + ((Paint) value).getTextSize() + ')';
        Class<?> type = value.getClass();
        if (type.isArray()) return type.getComponentType().getName() + "[] length="
                + java.lang.reflect.Array.getLength(value);
        if (value instanceof java.util.Collection) return type.getName() + " size="
                + ((java.util.Collection<?>) value).size();
        if (value instanceof java.util.Map) return type.getName() + " size="
                + ((java.util.Map<?, ?>) value).size();
        return type.getName() + '@' + Integer.toHexString(System.identityHashCode(value));
    }

    private static String diagnosticTencentStack() {
        StringBuilder value = new StringBuilder();
        StackTraceElement[] stack = Thread.currentThread().getStackTrace();
        int count = 0;
        for (StackTraceElement element : stack) {
            String name = element.getClassName();
            if (!name.startsWith("com.tencent.wetype") && !name.startsWith("com.tencent.mm")) continue;
            if (count++ > 0) value.append(" <- ");
            value.append(name).append('#').append(element.getMethodName())
                    .append(':').append(element.getLineNumber());
            if (count >= 10) break;
        }
        return value.length() == 0 ? "no-tencent-frame" : value.toString();
    }

    private void diagnosticLog(String message) {
        if (nativeDiagnosticLogBudget <= 0) return;
        nativeDiagnosticLogBudget--;
        logInfo(message);
    }

'''
marker = "    private static Class<?> findKeyboardBase(Class<?> type) {"
if text.count(marker) != 1:
    raise RuntimeError(f"diagnostic insertion marker: expected 1 match, found {text.count(marker)}")
text = text.replace(marker, helpers + marker, 1)

hook.write_text(text, encoding="utf-8")

build = Path("app/build.gradle.kts")
build_text = build.read_text(encoding="utf-8")
build_text, code_count = re.subn(r'versionCode\s*=\s*\d+', 'versionCode = 29', build_text, count=1)
build_text, name_count = re.subn(r'versionName\s*=\s*"[^"]+"', 'versionName = "1.11.0-diag1"', build_text, count=1)
if code_count != 1 or name_count != 1:
    raise RuntimeError(f"diagnostic version update failed: code={code_count}, name={name_count}")
build.write_text(build_text, encoding="utf-8")

activity = Path("app/src/main/java/com/rww/wetypeswipe/MainActivity.java")
activity_text = activity.read_text(encoding="utf-8")
activity_text, activity_count = re.subn(
    r'v1\.11\.0-test10 · 行列拟合按键标注',
    'v1.11.0-diag1 · 原生按键模型与绘制链诊断',
    activity_text,
    count=1)
if activity_count != 1:
    raise RuntimeError(f"diagnostic activity version update failed: {activity_count}")
activity.write_text(activity_text, encoding="utf-8")

print("v1.11.0-diag1 native key-model and draw-chain diagnostic patch applied")
