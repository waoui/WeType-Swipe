from pathlib import Path
import runpy

runpy.run_path("tools/patch_v111_test3.py", run_name="__main__")


def replace(path: str, old: str, new: str, count: int = 1) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    actual = text.count(old)
    if actual != count:
        raise RuntimeError(f"{path}: expected {count} matches, found {actual}: {old[:180]!r}")
    file.write_text(text.replace(old, new, count), encoding="utf-8")


hook = "app/src/main/java/com/rww/wetypeswipe/MainHook.java"

replace(hook,
        "import android.graphics.Color;\nimport android.graphics.drawable.GradientDrawable;",
        "import android.graphics.Canvas;\nimport android.graphics.Color;\nimport android.graphics.Paint;\nimport android.graphics.Typeface;\nimport android.graphics.drawable.GradientDrawable;")

replace(hook,
        "    private final ConcurrentHashMap<String, Method> methodCache = new ConcurrentHashMap<>();",
        "    private final ConcurrentHashMap<String, Method> methodCache = new ConcurrentHashMap<>();\n"
        "    private final ConcurrentHashMap<Method, Boolean> keyboardLabelHookedMethods = new ConcurrentHashMap<>();\n"
        "    private final Paint keyboardLabelPaint = new Paint(Paint.ANTI_ALIAS_FLAG);")

replace(hook,
        '            logInfo("v1.11.0-test3 entered target package");',
        '            logInfo("v1.11.0-test4 entered target package");')

replace(hook,
        '''        if (event.getActionMasked() == MotionEvent.ACTION_DOWN && !targetCacheLoaded) {
            ensureConfigSync(view.getContext());
        }
        return interceptKeyboardTouch(chain, view, event);
''',
        '''        ensureKeyboardLabelDrawHook(view.getClass(), view);
        if (event.getActionMasked() == MotionEvent.ACTION_DOWN && !targetCacheLoaded) {
            ensureConfigSync(view.getContext());
        }
        return interceptKeyboardTouch(chain, view, event);
''')

insert_before = "    private static Class<?> findKeyboardBase(Class<?> type) {"
methods = r'''    private synchronized void ensureKeyboardLabelDrawHook(Class<?> keyboardClass, View keyboard) {
        if (keyboardClass == null || keyboard == null) return;
        Method drawMethod = findKeyboardDrawMethod(keyboardClass, "onDraw");
        if (drawMethod == null) drawMethod = findKeyboardDrawMethod(keyboardClass, "dispatchDraw");
        if (drawMethod == null || keyboardLabelHookedMethods.putIfAbsent(drawMethod, Boolean.TRUE) != null) return;
        try {
            hookAfter(drawMethod, chain -> {
                Object target = chain.getThisObject();
                Object canvas = chain.getArg(0);
                if (target instanceof View && canvas instanceof Canvas) {
                    drawKeyboardFunctionLabels((View) target, (Canvas) canvas);
                }
            });
            keyboard.postInvalidate();
            logInfo("keyboard function-label draw hook installed for "
                    + drawMethod.getDeclaringClass().getName() + '#' + drawMethod.getName());
        } catch (Throwable throwable) {
            keyboardLabelHookedMethods.remove(drawMethod);
            logError("keyboard function-label draw hook failed", throwable);
        }
    }

    private static Method findKeyboardDrawMethod(Class<?> type, String name) {
        for (Class<?> current = type; current != null && current != View.class;
             current = current.getSuperclass()) {
            try {
                Method method = current.getDeclaredMethod(name, Canvas.class);
                method.setAccessible(true);
                return method;
            } catch (NoSuchMethodException ignored) {
            } catch (Throwable ignored) {
                return null;
            }
        }
        return null;
    }

    private void drawKeyboardFunctionLabels(View keyboard, Canvas canvas) {
        if (keyboard == null || canvas == null || keyboard.getWidth() <= 0 || keyboard.getHeight() <= 0) return;
        Config config = cachedConfig;
        if (config == null || !config.hasAnyBinding()) return;
        try {
            InputMethodService ime = imeRef.get();
            EditorInfo editorInfo = ime == null ? null : ime.getCurrentInputEditorInfo();
            if (editorInfo != null && isPassword(editorInfo.inputType)) return;

            String name = keyboard.getClass().getName().toLowerCase(Locale.ROOT);
            prepareKeyboardLabelPaint(keyboard);
            if (name.contains("t9") || name.contains("nine")) {
                drawT9FunctionLabels(keyboard, canvas, config);
            } else if (name.contains("qwerty") || name.contains("wubi") || name.contains("pinyin")) {
                drawQwertyFunctionLabels(keyboard, canvas, config);
            }
        } catch (Throwable throwable) {
            logError("keyboard function-label drawing failed", throwable);
        }
    }

    private void prepareKeyboardLabelPaint(View keyboard) {
        float scaledDensity = keyboard.getResources().getDisplayMetrics().scaledDensity;
        float widthBased = keyboard.getWidth() / 155f;
        float textSize = Math.max(6.2f * scaledDensity, Math.min(8.2f * scaledDensity, widthBased));
        keyboardLabelPaint.reset();
        keyboardLabelPaint.setAntiAlias(true);
        keyboardLabelPaint.setTextAlign(Paint.Align.CENTER);
        keyboardLabelPaint.setTypeface(Typeface.create(Typeface.DEFAULT, Typeface.BOLD));
        keyboardLabelPaint.setTextSize(textSize);
        keyboardLabelPaint.setColor(0xB35C626A);
        keyboardLabelPaint.setShadowLayer(Math.max(1f, dp(keyboard, 1)), 0f, 0f, 0xBFFFFFFF);
    }

    private void drawQwertyFunctionLabels(View keyboard, Canvas canvas, Config config) {
        int width = keyboard.getWidth();
        int height = keyboard.getHeight();
        float inset = Math.max(dp(keyboard, 2), height * 0.014f);
        drawQwertyRow(canvas, config, "qwertyuiop", width, height * 0.25f - inset, 0);
        drawQwertyRow(canvas, config, "asdfghjkl", width, height * 0.50f - inset, 1);
        drawQwertyRow(canvas, config, "zxcvbnm", width, height * 0.75f - inset, 2);
    }

    private void drawQwertyRow(Canvas canvas, Config config, String keys,
                               int width, float baseline, int row) {
        for (int index = 0; index < keys.length(); index++) {
            String key = String.valueOf(keys.charAt(index));
            int action = config.actionFor(key, false);
            if (action == Config.ACTION_NONE) continue;
            float x;
            if (row == 0) {
                x = width * ((index + 0.5f) / 10f);
            } else if (row == 1) {
                x = width * ((index + 1f) / 10f);
            } else {
                x = width * (0.20f + index * 0.10f);
            }
            drawKeyFunctionText(canvas, shortActionLabel(action), x, baseline);
        }
    }

    private void drawT9FunctionLabels(View keyboard, Canvas canvas, Config config) {
        int width = keyboard.getWidth();
        int height = keyboard.getHeight();
        float inset = Math.max(dp(keyboard, 2), height * 0.014f);
        for (int digit = 2; digit <= 9; digit++) {
            int action = config.actionFor(String.valueOf(digit), true);
            if (action == Config.ACTION_NONE) continue;
            int zeroBased = digit - 1;
            int row = zeroBased / 3;
            int column = zeroBased % 3;
            float x = width * ((column + 0.5f) / 3f);
            float baseline = height * ((row + 1f) / 4f) - inset;
            drawKeyFunctionText(canvas, shortActionLabel(action), x, baseline);
        }
    }

    private void drawKeyFunctionText(Canvas canvas, String text, float x, float baseline) {
        if (text == null || text.isEmpty()) return;
        canvas.drawText(text, x, baseline, keyboardLabelPaint);
    }

    private static String shortActionLabel(int action) {
        switch (Config.validAction(action)) {
            case Config.ACTION_SELECT_ALL: return "全选";
            case Config.ACTION_CUT: return "剪切";
            case Config.ACTION_COPY: return "复制";
            case Config.ACTION_PASTE: return "粘贴";
            case Config.ACTION_DISABLE: return "禁用";
            case Config.ACTION_PARAGRAPH_START: return "段首";
            case Config.ACTION_PARAGRAPH_END: return "段尾";
            case Config.ACTION_SELECT_TO_PARAGRAPH_START: return "选段首";
            case Config.ACTION_SELECT_TO_PARAGRAPH_END: return "选段尾";
            case Config.ACTION_OPEN_CLIPBOARD: return "剪贴板";
            case Config.ACTION_OPEN_QUICK_PHRASE: return "快捷发送";
            default: return "";
        }
    }

'''
replace(hook, insert_before, methods + insert_before)

replace("app/build.gradle.kts", "versionCode = 23", "versionCode = 24")
replace("app/build.gradle.kts", 'versionName = "1.11.0-test3"', 'versionName = "1.11.0-test4"')
replace("app/src/main/java/com/rww/wetypeswipe/MainActivity.java",
        'v1.11.0-test3 · 候选栏轻量提示',
        'v1.11.0-test4 · 按键内功能文字')

print("v1.11.0-test4 key function labels patch applied")
