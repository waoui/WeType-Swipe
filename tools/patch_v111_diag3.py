from pathlib import Path
import re
import runpy

runpy.run_path("tools/patch_v111_diag2_buildfix.py", run_name="__main__")

hook = Path("app/src/main/java/com/rww/wetypeswipe/MainHook.java")
text = hook.read_text(encoding="utf-8")


def replace_once(source: str, old: str, new: str, name: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"{name}: expected 1 match, found {count}")
    return source.replace(old, new, 1)


def replace_between(source: str, start_marker: str, end_marker: str,
                    replacement: str, name: str) -> str:
    start = source.find(start_marker)
    if start < 0:
        raise RuntimeError(f"{name}: start marker missing")
    end = source.find(end_marker, start + len(start_marker))
    if end < 0:
        raise RuntimeError(f"{name}: end marker missing")
    return source[:start] + replacement + source[end:]


text = replace_once(
    text,
    "import android.graphics.Paint;\nimport android.graphics.Rect;",
    "import android.graphics.Matrix;\nimport android.graphics.Paint;\nimport android.graphics.Rect;",
    "matrix import")

text = replace_once(
    text,
    "    private final ConcurrentHashMap<Method, Boolean> nativeDiagnosticInvokedMethods = new ConcurrentHashMap<>();",
    "    private final ConcurrentHashMap<Method, Boolean> nativeDiagnosticInvokedMethods = new ConcurrentHashMap<>();\n"
    "    private final ConcurrentHashMap<Method, java.util.concurrent.atomic.AtomicInteger> preciseDiagnosticCounts = new ConcurrentHashMap<>();\n"
    "    private final ConcurrentHashMap<Integer, String> preciseModelLabels = new ConcurrentHashMap<>();",
    "precise diagnostic fields")

text = replace_once(
    text,
    '            logInfo("v1.11.0-diag2 entered target package");',
    '            logInfo("v1.11.0-diag3 entered target package");',
    "diag3 version log")

# Run targeted diagnostics for both QWERTY and T9 layouts.
text = replace_once(
    text,
    '''            if (name.contains("t9") || name.contains("nine")) {
                drawT9FunctionLabels(keyboard, canvas, config);
            } else if (name.contains("qwerty") || name.contains("wubi") || name.contains("pinyin")) {''',
    '''            if (name.contains("t9") || name.contains("nine")) {
                ensureNativeKeyDiagnostics(keyboard);
                drawT9FunctionLabels(keyboard, canvas, config);
            } else if (name.contains("qwerty") || name.contains("wubi") || name.contains("pinyin")) {''',
    "T9 diagnostic entry")

run_method = r'''    private void runNativeKeyDiagnostics(View keyboard, String signature) {
        if (keyboard == null || !keyboard.isAttachedToWindow()) return;
        diagnosticLog("diag3-start signature=" + signature);
        diagnosticLog("diag3-keyboard class=" + keyboard.getClass().getName());

        java.util.LinkedHashSet<Class<?>> classes = new java.util.LinkedHashSet<>();
        collectDiagnosticClasses(keyboard, 4, classes,
                new java.util.IdentityHashMap<Object, Boolean>());

        String[] sampleKeys = {"q", "a", "s", "z", "v"};
        for (String key : sampleKeys) {
            Object button = diagnosticButtonForKey(keyboard, key);
            if (button == null) continue;
            collectDiagnosticClasses(button, 3, classes,
                    new java.util.IdentityHashMap<Object, Boolean>());
            diagnosticLog("diag3-button key=" + key + " class=" + button.getClass().getName()
                    + " id=" + Integer.toHexString(System.identityHashCode(button)));
        }

        int installed = 0;
        for (Class<?> type : classes) {
            if (!preciseDiagnosticClass(type)) continue;
            installed += installNativeDiagnosticHooks(type, 48 - installed);
            if (installed >= 48) break;
        }
        diagnosticLog("diag3-hooks installed=" + installed + " candidateClasses=" + classes.size());
        keyboard.postInvalidate();
        diagnosticLog("diag3-end redraw-requested");
    }

'''
text = replace_between(
    text,
    "    private void runNativeKeyDiagnostics(View keyboard, String signature) {",
    "    private Object diagnosticButtonForKey(View keyboard, String key) {",
    run_method,
    "run diagnostics")

install_method = r'''    private int installNativeDiagnosticHooks(Class<?> type, int remaining) {
        if (type == null || remaining <= 0 || !preciseDiagnosticClass(type)) return 0;
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
                            .intercept(chain -> preciseDiagnosticIntercept(method, chain));
                    installed++;
                    diagnosticLog("diag3-hook " + diagnosticMethodSignature(method));
                } catch (Throwable throwable) {
                    nativeDiagnosticHookedMethods.remove(method);
                    diagnosticLog("diag3-hook-failed signature=" + diagnosticMethodSignature(method)
                            + " error=" + throwable.getClass().getSimpleName());
                }
            }
        }
        return installed;
    }

    private Object preciseDiagnosticIntercept(Method method, XposedInterface.Chain chain) throws Throwable {
        String name = method.getName();
        boolean mapping = "x1".equals(name) || "E2".equals(name);
        if (mapping) {
            Object result = chain.proceed();
            try { recordPreciseModelMapping(method, chain, result); }
            catch (Throwable throwable) {
                diagnosticLog("diag3-map-error " + throwable.getClass().getSimpleName());
            }
            return result;
        }

        java.util.concurrent.atomic.AtomicInteger counter = preciseDiagnosticCounts.computeIfAbsent(
                method, ignored -> new java.util.concurrent.atomic.AtomicInteger());
        int occurrence = counter.incrementAndGet();
        if (occurrence <= 8) {
            try { recordPreciseDrawInvocation(method, chain, occurrence); }
            catch (Throwable throwable) {
                diagnosticLog("diag3-draw-error signature=" + diagnosticMethodSignature(method)
                        + " error=" + throwable.getClass().getSimpleName());
            }
        }
        return chain.proceed();
    }

    private void recordPreciseModelMapping(Method method, XposedInterface.Chain chain, Object result) {
        StringBuilder label = new StringBuilder();
        Object model = null;
        Class<?>[] parameters = method.getParameterTypes();
        for (int index = 0; index < parameters.length; index++) {
            Object arg;
            try { arg = chain.getArg(index); }
            catch (Throwable ignored) { arg = null; }
            if (arg instanceof CharSequence) {
                String value = safeDiagnosticText((CharSequence) arg);
                if (!value.isEmpty()) {
                    if (label.length() > 0) label.append('/');
                    label.append(value);
                }
            }
            if (preciseKeyModelObject(arg)) model = arg;
        }
        if (preciseKeyModelObject(result)) model = result;
        if (model == null) return;
        String resolved = label.length() == 0 ? "unknown" : label.toString();
        preciseModelLabels.put(System.identityHashCode(model), resolved);
        diagnosticLog("diag3-map method=" + method.getName() + " label=" + resolved
                + " model=" + model.getClass().getName() + '@'
                + Integer.toHexString(System.identityHashCode(model)));
        diagnosticLog("diag3-model " + preciseModelSummary(model));
    }

    private void recordPreciseDrawInvocation(Method method, XposedInterface.Chain chain,
                                             int occurrence) {
        Canvas canvas = null;
        Object model = null;
        StringBuilder args = new StringBuilder();
        Class<?>[] parameters = method.getParameterTypes();
        for (int index = 0; index < parameters.length; index++) {
            Object arg;
            try { arg = chain.getArg(index); }
            catch (Throwable ignored) { arg = null; }
            if (arg instanceof Canvas) canvas = (Canvas) arg;
            if (preciseKeyModelObject(arg)) model = arg;
            if (index > 0) args.append(';');
            args.append(index).append(':').append(diagnosticValueSummary(arg));
        }
        String label = model == null ? "none"
                : preciseModelLabels.getOrDefault(System.identityHashCode(model), "unknown");
        diagnosticLog("diag3-draw occurrence=" + occurrence + " method="
                + diagnosticMethodSignature(method) + " label=" + label + " args=" + args);
        if (canvas != null) diagnosticLog("diag3-canvas " + preciseCanvasSummary(canvas));
        if (model != null) diagnosticLog("diag3-model " + preciseModelSummary(model));
        if (occurrence <= 2) diagnosticLog("diag3-stack " + diagnosticTencentStack());
    }

'''
text = replace_between(
    text,
    "    private int installNativeDiagnosticHooks(Class<?> type, int remaining) {",
    "    private static boolean diagnosticMethodCandidate(Method method) {",
    install_method,
    "precise hook installer")

candidate_method = r'''    private static boolean diagnosticMethodCandidate(Method method) {
        if (method == null || method.isSynthetic() || method.isBridge()) return false;
        String owner = method.getDeclaringClass().getName();
        String name = method.getName();
        Class<?>[] parameters = method.getParameterTypes();

        if ((owner.endsWith(".drawmethod.d") && ("a".equals(name) || "b".equals(name)))
                || (owner.endsWith(".drawmethod.c")
                && ("a".equals(name) || "e".equals(name)
                || "f".equals(name) || "g".equals(name)))) {
            return parameters.length == 2 && parameters[0] == Canvas.class;
        }
        if (owner.endsWith(".drawmethod.d") && "i".equals(name)) {
            return parameters.length == 1 && parameters[0] == Canvas.class;
        }
        if ("x1".equals(name) || "E2".equals(name)
                || "getButtonDrawer".equals(name)
                || "getKeysLayoutInfo".equals(name)
                || "getKeyIdsForLayoutInfo".equals(name)) return true;
        return false;
    }

'''
text = replace_between(
    text,
    "    private static boolean diagnosticMethodCandidate(Method method) {",
    "    private static boolean diagnosticTencentType(Class<?> type) {",
    candidate_method,
    "precise method candidate")

helpers = r'''    private static boolean preciseDiagnosticClass(Class<?> type) {
        if (type == null) return false;
        String name = type.getName();
        return name.startsWith("com.tencent.wetype.plugin.hld.keyboard.selfdraw")
                || name.endsWith(".drawmethod.c") || name.endsWith(".drawmethod.d");
    }

    private static boolean preciseKeyModelObject(Object value) {
        if (value == null) return false;
        String name = value.getClass().getName();
        return name.equals("com.tencent.wetype.plugin.hld.keyboard.selfdraw.j")
                || name.endsWith(".keyboard.selfdraw.j");
    }

    private static String safeDiagnosticText(CharSequence value) {
        if (value == null) return "";
        String text = value.toString();
        if (text.length() > 12) return "len" + text.length();
        for (int index = 0; index < text.length(); index++) {
            char ch = text.charAt(index);
            if (Character.isWhitespace(ch) || Character.isISOControl(ch)) return "len" + text.length();
        }
        return text;
    }

    private static String preciseCanvasSummary(Canvas canvas) {
        if (canvas == null) return "canvas=null";
        try {
            Matrix matrix = canvas.getMatrix();
            float[] values = new float[9];
            matrix.getValues(values);
            Rect clip = new Rect();
            boolean hasClip = canvas.getClipBounds(clip);
            return "size=" + canvas.getWidth() + 'x' + canvas.getHeight()
                    + " clip=" + (hasClip ? clip.toShortString() : "none")
                    + " matrix=[" + roundDiagnostic(values[0]) + ',' + roundDiagnostic(values[1])
                    + ',' + roundDiagnostic(values[2]) + ';' + roundDiagnostic(values[3])
                    + ',' + roundDiagnostic(values[4]) + ',' + roundDiagnostic(values[5])
                    + ';' + roundDiagnostic(values[6]) + ',' + roundDiagnostic(values[7])
                    + ',' + roundDiagnostic(values[8]) + ']';
        } catch (Throwable throwable) {
            return "canvas-error=" + throwable.getClass().getSimpleName();
        }
    }

    private static float roundDiagnostic(float value) {
        return Math.round(value * 100f) / 100f;
    }

    private static String preciseModelSummary(Object model) {
        if (model == null) return "model=null";
        StringBuilder value = new StringBuilder(model.getClass().getName())
                .append('@').append(Integer.toHexString(System.identityHashCode(model))).append('{');
        int count = 0;
        for (Class<?> current = model.getClass(); current != null && current != Object.class;
             current = current.getSuperclass()) {
            Field[] fields;
            try { fields = current.getDeclaredFields(); }
            catch (Throwable ignored) { continue; }
            for (Field field : fields) {
                if (count >= 28) break;
                try {
                    field.setAccessible(true);
                    Object item = field.get(model);
                    if (!preciseFieldValue(item)) continue;
                    if (count++ > 0) value.append(',');
                    value.append(field.getName()).append('=').append(diagnosticValueSummary(item));
                } catch (Throwable ignored) {
                }
            }
            if (count >= 28) break;
        }
        return value.append('}').toString();
    }

    private static boolean preciseFieldValue(Object value) {
        if (value == null) return true;
        return value instanceof Number || value instanceof Boolean || value instanceof Character
                || value instanceof CharSequence || value instanceof Rect || value instanceof RectF
                || value.getClass().isEnum();
    }

'''
marker = "    private static String diagnosticTencentStack() {"
if text.count(marker) != 1:
    raise RuntimeError(f"diag3 helper insertion marker: expected 1 match, found {text.count(marker)}")
text = text.replace(marker, helpers + marker, 1)

# Targeted logging can use a larger budget without flooding unrelated View fields.
text = text.replace("nativeDiagnosticLogBudget = 160", "nativeDiagnosticLogBudget = 420")

hook.write_text(text, encoding="utf-8")

build = Path("app/build.gradle.kts")
build_text = build.read_text(encoding="utf-8")
build_text, code_count = re.subn(r'versionCode\s*=\s*\d+', 'versionCode = 31', build_text, count=1)
build_text, name_count = re.subn(r'versionName\s*=\s*"[^"]+"',
                                 'versionName = "1.11.0-diag3"', build_text, count=1)
if code_count != 1 or name_count != 1:
    raise RuntimeError(f"diag3 version update failed: code={code_count}, name={name_count}")
build.write_text(build_text, encoding="utf-8")

activity = Path("app/src/main/java/com/rww/wetypeswipe/MainActivity.java")
activity_text = activity.read_text(encoding="utf-8")
activity_text, activity_count = re.subn(
    r'v1\.11\.0-diag2 · 深色与九宫格诊断',
    'v1.11.0-diag3 · 精准单键绘制诊断',
    activity_text,
    count=1)
if activity_count != 1:
    raise RuntimeError(f"diag3 activity version update failed: {activity_count}")
activity.write_text(activity_text, encoding="utf-8")

print("v1.11.0-diag3 precise native single-key draw diagnostics applied")
