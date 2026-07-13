from pathlib import Path
import re
import runpy

runpy.run_path("tools/patch_v111_test12_native_refresh.py", run_name="__main__")

hook = Path("app/src/main/java/com/rww/wetypeswipe/MainHook.java")
text = hook.read_text(encoding="utf-8")


def replace_once(source: str, old: str, new: str, name: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"{name}: expected 1 match, found {count}")
    return source.replace(old, new, 1)


text = replace_once(
    text,
    "import android.graphics.Paint;",
    "import android.graphics.Paint;\nimport android.graphics.Rect;",
    "Rect import")

text = replace_once(
    text,
    "    private volatile long nativeLabelLastSignatureCheckMs;",
    "    private volatile long nativeLabelLastSignatureCheckMs;\n"
    "    private final ConcurrentHashMap<Method, Boolean> nativeSingleKeyHookedMethods = new ConcurrentHashMap<>();\n"
    "    private volatile boolean nativeSingleKeyHooksResolved;\n"
    "    private volatile WeakReference<View> nativeSingleKeyActiveKeyboardRef = new WeakReference<>(null);\n"
    "    private volatile long nativeSingleKeyLastDrawUptimeMs;\n"
    "    private volatile long nativeSingleKeyPaintSignature = Long.MIN_VALUE;\n"
    "    private volatile Class<?> nativeSingleKeyModelClass;\n"
    "    private volatile Field nativeSingleKeyDrawRectField;\n"
    "    private volatile Field nativeSingleKeyParentField;\n"
    "    private volatile boolean nativeSingleKeyActivationLogged;\n"
    "    private volatile boolean currentEditorPassword;",
    "native single-key fields")

text = replace_once(
    text,
    '            logInfo("v1.11.0-test12 entered target package");',
    '            logInfo("v1.11.0-test13 entered target package");',
    "version log")

text = replace_once(
    text,
    '''        hookBefore(InputMethodService.class.getDeclaredMethod("onStartInput", EditorInfo.class, boolean.class),
                chain -> captureStartInput(chain.getThisObject()));''',
    '''        hookBefore(InputMethodService.class.getDeclaredMethod("onStartInput", EditorInfo.class, boolean.class),
                chain -> captureStartInput(chain.getThisObject(), (EditorInfo) chain.getArg(0)));''',
    "start-input password tracking hook")

text = replace_once(
    text,
    '''    private void captureStartInput(Object object) {
        currentSelectionStart = -1;
        currentSelectionEnd = -1;
        captureIme(object);
    }
''',
    '''    private void captureStartInput(Object object, EditorInfo editorInfo) {
        currentSelectionStart = -1;
        currentSelectionEnd = -1;
        currentEditorPassword = editorInfo != null && isPassword(editorInfo.inputType);
        captureIme(object);
    }
''',
    "start-input password state")

text = replace_once(
    text,
    '''    private synchronized void ensureKeyboardLabelDrawHook(Class<?> keyboardClass, View keyboard) {
        if (keyboardClass == null || keyboard == null) return;
        Method drawMethod = findKeyboardDrawMethod(keyboardClass, "onDraw");''',
    '''    private synchronized void ensureKeyboardLabelDrawHook(Class<?> keyboardClass, View keyboard) {
        if (keyboardClass == null || keyboard == null) return;
        ensureNativeSingleKeyDrawHooks(keyboard);
        Method drawMethod = findKeyboardDrawMethod(keyboardClass, "onDraw");''',
    "single-key hook installation entry")

text = replace_once(
    text,
    '''            InputMethodService ime = imeRef.get();
            EditorInfo editorInfo = ime == null ? null : ime.getCurrentInputEditorInfo();
            if (editorInfo != null && isPassword(editorInfo.inputType)) return;

            String name = keyboard.getClass().getName().toLowerCase(Locale.ROOT);''',
    '''            InputMethodService ime = imeRef.get();
            EditorInfo editorInfo = ime == null ? null : ime.getCurrentInputEditorInfo();
            if (editorInfo != null && isPassword(editorInfo.inputType)) return;

            ensureNativeSingleKeyDrawHooks(keyboard);
            View activeKeyboard = nativeSingleKeyActiveKeyboardRef.get();
            if (activeKeyboard == keyboard
                    && SystemClock.uptimeMillis() - nativeSingleKeyLastDrawUptimeMs < 250L) {
                return;
            }

            String name = keyboard.getClass().getName().toLowerCase(Locale.ROOT);''',
    "outer renderer fallback gate")

# Split-key copies keep their original key identity.
text = replace_once(
    text,
    '''        String key = marker >= 0 ? id.substring(marker + 5) : id;
        if (key.length() != 1) return null;''',
    '''        String key = marker >= 0 ? id.substring(marker + 5) : id;
        if (key.endsWith("_copy")) key = key.substring(0, key.length() - 5);
        if (key.length() != 1) return null;''',
    "split-copy key id parsing")

single_key_helpers = r'''    private synchronized void ensureNativeSingleKeyDrawHooks(View keyboard) {
        if (keyboard == null || nativeSingleKeyHooksResolved) return;
        ClassLoader loader = keyboard.getClass().getClassLoader();
        if (loader == null) return;
        try {
            Class<?> modelClass = Class.forName(
                    "com.tencent.wetype.plugin.hld.keyboard.selfdraw.j", false, loader);
            String[] drawerClasses = {
                    "com.tencent.wetype.plugin.hld.keyboard.selfdraw.drawmethod.c",
                    "com.tencent.wetype.plugin.hld.keyboard.selfdraw.drawmethod.d"
            };
            int installed = 0;
            for (String className : drawerClasses) {
                try {
                    Class<?> drawerClass = Class.forName(className, false, loader);
                    Method method = findMethod(drawerClass, "a",
                            new Class<?>[]{Canvas.class, modelClass});
                    if (method == null
                            || nativeSingleKeyHookedMethods.putIfAbsent(method, Boolean.TRUE) != null) {
                        continue;
                    }
                    method.setAccessible(true);
                    hook(method).setExceptionMode(XposedInterface.ExceptionMode.PROTECTIVE)
                            .intercept(chain -> {
                                Object result = chain.proceed();
                                try {
                                    drawNativeSingleKeyFunctionLabel(
                                            chain.getArg(0), chain.getArg(1));
                                } catch (Throwable throwable) {
                                    logError("native single-key label draw failed", throwable);
                                }
                                return result;
                            });
                    installed++;
                } catch (Throwable ignored) {
                }
            }
            if (installed > 0 || !nativeSingleKeyHookedMethods.isEmpty()) {
                nativeSingleKeyHooksResolved = true;
                logInfo("native single-key renderer hooks ready methods="
                        + nativeSingleKeyHookedMethods.size());
                keyboard.postInvalidate();
            }
        } catch (Throwable throwable) {
            logError("native single-key renderer hook setup failed", throwable);
        }
    }

    private void drawNativeSingleKeyFunctionLabel(Object canvasValue, Object model) {
        if (!(canvasValue instanceof Canvas) || model == null) return;
        View keyboard = nativeSingleKeyParent(model);
        Rect drawRect = nativeSingleKeyDrawRect(model);
        if (keyboard == null || drawRect == null || drawRect.isEmpty()) return;

        View previous = nativeSingleKeyActiveKeyboardRef.get();
        if (previous != keyboard) nativeSingleKeyActiveKeyboardRef = new WeakReference<>(keyboard);
        nativeSingleKeyLastDrawUptimeMs = SystemClock.uptimeMillis();
        if (!nativeSingleKeyActivationLogged) {
            nativeSingleKeyActivationLogged = true;
            logInfo("native single-key renderer active class=" + model.getClass().getName());
        }

        if (currentEditorPassword) return;
        Config config = cachedConfig;
        if (config == null || !config.hasAnyBinding()) return;

        String id;
        try { id = String.valueOf(model); }
        catch (Throwable ignored) { id = null; }
        String key = keyFromNativeLayoutId(id);
        if (key == null) {
            Object value = invoke(model, "K");
            key = keyFromNativeLayoutId(value == null ? null : String.valueOf(value));
        }
        if (key == null) return;

        char value = key.charAt(0);
        boolean t9 = value >= '1' && value <= '9';
        int action = config.actionFor(key, t9);
        if (action == Config.ACTION_NONE || action == Config.ACTION_DISABLE) return;

        ensureNativeSingleKeyPaint(keyboard);
        float keyHeight = Math.max(1f, drawRect.height());
        float baseline = drawRect.bottom
                - Math.max(dp(keyboard, 2), keyHeight * 0.08f);
        drawKeyFunctionText((Canvas) canvasValue, shortActionLabel(action),
                drawRect.exactCenterX(), baseline);
    }

    private View nativeSingleKeyParent(Object model) {
        ensureNativeSingleKeyModelFields(model);
        Field field = nativeSingleKeyParentField;
        if (field != null) {
            try {
                Object value = field.get(model);
                if (value instanceof View) return (View) value;
            } catch (Throwable ignored) {
            }
        }
        Object value = invoke(model, "W");
        return value instanceof View ? (View) value : null;
    }

    private Rect nativeSingleKeyDrawRect(Object model) {
        ensureNativeSingleKeyModelFields(model);
        Field field = nativeSingleKeyDrawRectField;
        if (field != null) {
            try {
                Object value = field.get(model);
                if (value instanceof Rect) return (Rect) value;
            } catch (Throwable ignored) {
            }
        }
        Object value = invoke(model, "t");
        return value instanceof Rect ? (Rect) value : null;
    }

    private void ensureNativeSingleKeyModelFields(Object model) {
        if (model == null) return;
        Class<?> type = model.getClass();
        if (nativeSingleKeyModelClass == type
                && nativeSingleKeyDrawRectField != null
                && nativeSingleKeyParentField != null) return;
        synchronized (this) {
            if (nativeSingleKeyModelClass == type
                    && nativeSingleKeyDrawRectField != null
                    && nativeSingleKeyParentField != null) return;
            Field rect = findNamedField(type, "l");
            Field parent = findNamedField(type, "a");
            nativeSingleKeyModelClass = type;
            nativeSingleKeyDrawRectField = rect;
            nativeSingleKeyParentField = parent;
        }
    }

    private void ensureNativeSingleKeyPaint(View keyboard) {
        if (keyboard == null) return;
        int night = keyboard.getResources().getConfiguration().uiMode
                & Configuration.UI_MODE_NIGHT_MASK;
        int density = Float.floatToIntBits(
                keyboard.getResources().getDisplayMetrics().scaledDensity);
        long signature = (((long) keyboard.getWidth()) << 40)
                ^ (((long) keyboard.getHeight()) << 16)
                ^ (((long) night) << 8)
                ^ (density & 0xffffffffL);
        if (signature == nativeSingleKeyPaintSignature) return;
        prepareKeyboardLabelPaint(keyboard);
        nativeSingleKeyPaintSignature = signature;
    }

'''
marker = "    private static Method findKeyboardDrawMethod(Class<?> type, String name) {"
if text.count(marker) != 1:
    raise RuntimeError(f"single-key helper marker: expected 1 match, found {text.count(marker)}")
text = text.replace(marker, single_key_helpers + marker, 1)

hook.write_text(text, encoding="utf-8")

build = Path("app/build.gradle.kts")
build_text = build.read_text(encoding="utf-8")
build_text, code_count = re.subn(r'versionCode\s*=\s*\d+', 'versionCode = 34', build_text, count=1)
build_text, name_count = re.subn(r'versionName\s*=\s*"[^"]+"',
                                 'versionName = "1.11.0-test13"',
                                 build_text, count=1)
if code_count != 1 or name_count != 1:
    raise RuntimeError(f"version update failed: code={code_count}, name={name_count}")
build.write_text(build_text, encoding="utf-8")

activity = Path("app/src/main/java/com/rww/wetypeswipe/MainActivity.java")
activity_text = activity.read_text(encoding="utf-8")
activity_text, activity_count = re.subn(
    r'v1\.11\.0-test12 · 原生布局自动刷新',
    'v1.11.0-test13 · 原生单键同步渲染',
    activity_text,
    count=1)
if activity_count != 1:
    raise RuntimeError(f"activity version update failed: {activity_count}")
activity.write_text(activity_text, encoding="utf-8")

print("v1.11.0-test13 native per-key renderer patch applied")
