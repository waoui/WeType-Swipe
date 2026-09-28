from pathlib import Path

MAIN = Path('app/src/main/java/com/rww/wetypeswipe/MainHook.java')


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{label}: expected 1 match, got {count}')
    return text.replace(old, new, 1)


text = MAIN.read_text(encoding='utf-8')

text = replace_once(
    text,
    'import java.util.Map;\nimport java.util.concurrent.ConcurrentHashMap;\n',
    'import java.util.Map;\nimport java.util.WeakHashMap;\nimport java.util.concurrent.ConcurrentHashMap;\n',
    'WeakHashMap import')

text = replace_once(
    text,
    '    private static final int NATIVE_SINGLE_KEY_LABEL_CACHE_LIMIT = 128;\n',
    '',
    'remove native label cache limit')

text = replace_once(
    text,
    '        @Override public void onConfigChanged(Config config) { nativeSingleKeyLabelCache.clear(); }\n',
    '        @Override public void onConfigChanged(Config config) {\n'
    '            keyboardLabelSnapshot = KeyboardLabelSnapshot.from(config);\n'
    '        }\n',
    'config listener snapshot')

text = replace_once(
    text,
    '    private final ConcurrentHashMap<Method, Boolean> keyboardLabelHookedMethods = new ConcurrentHashMap<>();\n'
    '    private final Paint keyboardLabelPaint = new Paint(Paint.ANTI_ALIAS_FLAG);\n',
    '    private final ConcurrentHashMap<Method, Boolean> keyboardLabelHookedMethods = new ConcurrentHashMap<>();\n'
    '    private final ConcurrentHashMap<Class<?>, Boolean> keyboardLabelResolvedClasses = new ConcurrentHashMap<>();\n'
    '    private final Paint keyboardLabelPaint = new Paint(Paint.ANTI_ALIAS_FLAG);\n'
    '    private final Paint.FontMetrics keyboardLabelMetrics = new Paint.FontMetrics();\n'
    '    private volatile KeyboardLabelSnapshot keyboardLabelSnapshot = initialKeyboardLabelSnapshot();\n'
    '    private final Map<View, KeyboardRuntimeState> keyboardRuntimeStates = new WeakHashMap<>();\n'
    '    private volatile WeakReference<View> activeKeyboardRuntimeViewRef = new WeakReference<>(null);\n'
    '    private volatile KeyboardRuntimeState activeKeyboardRuntimeState;\n',
    'hot path fields')

text = replace_once(
    text,
    '    private volatile WeakReference<View> nativeSingleKeyActiveKeyboardRef = new WeakReference<>(null);\n'
    '    private final ConcurrentHashMap<Object, String> nativeSingleKeyLabelCache = new ConcurrentHashMap<>();\n'
    '    private volatile long nativeSingleKeyPaintSignature = Long.MIN_VALUE;\n'
    '    private volatile int lastResolvedNightMode = Configuration.UI_MODE_NIGHT_UNDEFINED;\n',
    '    private volatile WeakReference<View> nativeSingleKeyActiveKeyboardRef = new WeakReference<>(null);\n'
    '    private volatile long nativeSingleKeyPaintSignature = Long.MIN_VALUE;\n'
    '    private volatile float nativeSingleKeyDescent;\n'
    '    private volatile float nativeSingleKeyBottomPadding;\n'
    '    private volatile int lastResolvedNightMode = Configuration.UI_MODE_NIGHT_UNDEFINED;\n',
    'remove model label cache and add paint metrics')

text = replace_once(
    text,
    '            logInfo("v1.11.9-test2 entered target package; phase-1 refactor + live dark-mode refresh enabled");\n',
    '            logInfo("v1.11.9-test3 entered target package; hot-path performance optimizations enabled");\n',
    'version log')

text = replace_once(
    text,
    '        hookAfter(Application.class.getDeclaredMethod("onCreate"),\n'
    '                chain -> captureApplication(chain.getThisObject()));\n\n'
    '        hookAfter(InputMethodService.class.getDeclaredMethod("onCreate"),\n',
    '        hookAfter(Application.class.getDeclaredMethod("onCreate"),\n'
    '                chain -> captureApplication(chain.getThisObject()));\n'
    '        try {\n'
    '            Method configurationChanged = Application.class.getMethod(\n'
    '                    "onConfigurationChanged", Configuration.class);\n'
    '            hookAfter(configurationChanged, chain -> captureApplicationConfiguration(\n'
    '                    chain.getThisObject(), (Configuration) chain.getArg(0)));\n'
    '        } catch (Throwable throwable) {\n'
    '            logError("application configuration hook unavailable", throwable);\n'
    '        }\n\n'
    '        hookAfter(InputMethodService.class.getDeclaredMethod("onCreate"),\n',
    'application configuration hook')

text = replace_once(
    text,
    '        ensureConfigSync(app);\n    }\n\n    private static Activity findActivity(Context context) {\n',
    '        try {\n'
    '            captureApplicationConfiguration(app, app.getResources().getConfiguration());\n'
    '        } catch (Throwable ignored) {}\n'
    '        ensureConfigSync(app);\n'
    '    }\n\n'
    '    private void captureApplicationConfiguration(Object object, Configuration configuration) {\n'
    '        if (!(object instanceof Application) || configuration == null) return;\n'
    '        Application app = (Application) object;\n'
    '        try {\n'
    '            if (!TARGET.equals(app.getPackageName())) return;\n'
    '        } catch (Throwable ignored) {\n'
    '            return;\n'
    '        }\n'
    '        int resolved = KeyboardThemeState.resolveNightMode(\n'
    '                Configuration.UI_MODE_NIGHT_UNDEFINED, configuration.uiMode,\n'
    '                Configuration.UI_MODE_NIGHT_UNDEFINED);\n'
    '        publishResolvedNightMode(resolved, null);\n'
    '    }\n\n'
    '    private static Activity findActivity(Context context) {\n',
    'capture application theme')

old_touch = '''        if (KeyboardCompat.isHandwritingContext(view)) {
            tracker.clear(view);
            view.post(() -> hideKeyboardHint(0L));
            return chain.proceed();
        }

        ensureKeyboardLabelDrawHook(view.getClass(), view);
        if (event.getActionMasked() == MotionEvent.ACTION_DOWN && !configBridge.isLoaded()) {
            ensureConfigSync(view.getContext());
        }
        return interceptKeyboardTouch(chain, view, event);
'''
new_touch = '''        boolean actionDown = event.getActionMasked() == MotionEvent.ACTION_DOWN;
        KeyboardRuntimeState runtimeState = runtimeState(view);
        if (refreshHandwritingState(view, runtimeState, actionDown)) {
            tracker.clear(view);
            view.post(() -> hideKeyboardHint(0L));
            return chain.proceed();
        }

        ensureKeyboardLabelDrawHook(view.getClass(), view);
        if (actionDown) {
            resolveLiveNightMode(view);
            if (!configBridge.isLoaded()) ensureConfigSync(view.getContext());
        }
        return interceptKeyboardTouch(chain, view, event);
'''
text = replace_once(text, old_touch, new_touch, 'touch hot path')

old_hook = '''    private synchronized void ensureKeyboardLabelDrawHook(Class<?> keyboardClass, View keyboard) {
        if (keyboardClass == null || keyboard == null) return;
        ensureNativeSingleKeyDrawHooks(keyboard);
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
'''
new_hook = '''    private void ensureKeyboardLabelDrawHook(Class<?> keyboardClass, View keyboard) {
        if (keyboardClass == null || keyboard == null
                || keyboardLabelResolvedClasses.containsKey(keyboardClass)) return;
        synchronized (this) {
            if (keyboardLabelResolvedClasses.containsKey(keyboardClass)) return;
            ensureNativeSingleKeyDrawHooks(keyboard);
            Method drawMethod = findKeyboardDrawMethod(keyboardClass, "onDraw");
            if (drawMethod == null) drawMethod = findKeyboardDrawMethod(keyboardClass, "dispatchDraw");
            if (drawMethod == null) {
                keyboardLabelResolvedClasses.put(keyboardClass, Boolean.TRUE);
                return;
            }
            if (keyboardLabelHookedMethods.putIfAbsent(drawMethod, Boolean.TRUE) != null) {
                keyboardLabelResolvedClasses.put(keyboardClass, Boolean.TRUE);
                return;
            }
            try {
                hookAfter(drawMethod, chain -> {
                    Object target = chain.getThisObject();
                    Object canvas = chain.getArg(0);
                    if (target instanceof View && canvas instanceof Canvas) {
                        drawKeyboardFunctionLabels((View) target, (Canvas) canvas);
                    }
                });
                keyboardLabelResolvedClasses.put(keyboardClass, Boolean.TRUE);
                keyboard.postInvalidate();
                logInfo("keyboard function-label draw hook installed for "
                        + drawMethod.getDeclaringClass().getName() + '#' + drawMethod.getName());
            } catch (Throwable throwable) {
                keyboardLabelHookedMethods.remove(drawMethod);
                keyboardLabelResolvedClasses.remove(keyboardClass);
                logError("keyboard function-label draw hook failed", throwable);
            }
        }
    }
'''
text = replace_once(text, old_hook, new_hook, 'draw hook class cache')

old_native = '''        if (KeyboardCompat.isHandwritingContext(keyboard)) {
            nativeSingleKeyLabelCache.remove(model);
            return;
        }

        View previous = nativeSingleKeyActiveKeyboardRef.get();
        if (previous != keyboard) {
            nativeSingleKeyActiveKeyboardRef = new WeakReference<>(keyboard);
            nativeSingleKeyLabelCache.clear();
        }
        if (!nativeSingleKeyActivationLogged) {
            nativeSingleKeyActivationLogged = true;
            logInfo("native single-key renderer active class=" + model.getClass().getName());
        }

        if (currentEditorPassword) return;
        Config displayConfig = configBridge.current();
        if (displayConfig == null || !displayConfig.showKeyLabels) return;
        Config config = configBridge.current();
        if (config == null || !config.hasAnyBinding() || !config.showKeyLabels) return;

        // Native key models are reused when switching to number/symbol pages. Their layout id
        // still points at the original QWERTY position, so using that id alone leaks labels onto
        // symbol keys. Resolve the currently visible key text and include it in the cache value.
        KeyInfo visibleKey = keyResolver.visibleKeyFromButton(model);
        if (visibleKey == null) {
            nativeSingleKeyLabelCache.remove(model);
            return;
        }
        String identity = (visibleKey.t9 ? "t9:" : "qwerty:") + visibleKey.key + '\\u0000';
        String cached = nativeSingleKeyLabelCache.get(model);
        String label;
        if (cached == null || !cached.startsWith(identity)) {
            int action = config.actionFor(visibleKey.key, visibleKey.t9);
            label = action == Config.ACTION_NONE || action == Config.ACTION_DISABLE
                    ? "" : config.labelFor(visibleKey.key, visibleKey.t9, action);
            if (nativeSingleKeyLabelCache.size() >= NATIVE_SINGLE_KEY_LABEL_CACHE_LIMIT) {
                nativeSingleKeyLabelCache.clear();
            }
            nativeSingleKeyLabelCache.put(model, identity + label);
        } else {
            label = cached.substring(identity.length());
        }
        if (label.isEmpty()) return;
'''
new_native = '''        KeyboardRuntimeState runtimeState = runtimeState(keyboard);
        View previous = nativeSingleKeyActiveKeyboardRef.get();
        if (previous != keyboard) {
            nativeSingleKeyActiveKeyboardRef = new WeakReference<>(keyboard);
            refreshHandwritingState(keyboard, runtimeState, true);
        }
        if (runtimeState.handwriting()) return;
        if (!nativeSingleKeyActivationLogged) {
            nativeSingleKeyActivationLogged = true;
            logInfo("native single-key renderer active class=" + model.getClass().getName());
        }

        if (currentEditorPassword) return;
        KeyboardLabelSnapshot labels = keyboardLabelSnapshot;
        if (labels == null || !labels.hasAnyLabels()) return;

        // Native key models are reused on number/symbol pages, so visible text still has to be
        // resolved. The resulting action label itself is precomputed and allocation-free here.
        KeyInfo visibleKey = keyResolver.visibleKeyFromButton(model);
        if (visibleKey == null) return;
        String label = labels.labelFor(visibleKey.key, visibleKey.t9);
        if (label.isEmpty()) return;
'''
text = replace_once(text, old_native, new_native, 'native label snapshot')

old_baseline = '''        ensureNativeSingleKeyPaint(keyboard, drawRect);
        float keyHeight = Math.max(1f, drawRect.height());
        Paint.FontMetrics metrics = keyboardLabelPaint.getFontMetrics();
        float visibleBottomPadding = Math.max(dp(keyboard, 1), keyHeight * 0.045f);
        float baseline = drawRect.bottom - visibleBottomPadding - metrics.descent;
        drawKeyFunctionText((Canvas) canvasValue, label,
                drawRect.exactCenterX(), baseline);
'''
new_baseline = '''        ensureNativeSingleKeyPaint(keyboard, drawRect);
        float baseline = drawRect.bottom - nativeSingleKeyBottomPadding - nativeSingleKeyDescent;
        drawKeyFunctionText((Canvas) canvasValue, label,
                drawRect.exactCenterX(), baseline);
'''
text = replace_once(text, old_baseline, new_baseline, 'native baseline cache')

old_paint = '''    private void ensureNativeSingleKeyPaint(View keyboard, Rect drawRect) {
        if (keyboard == null || drawRect == null) return;
        int night = resolveLiveNightMode(keyboard);
        int density = Float.floatToIntBits(
                keyboard.getResources().getDisplayMetrics().scaledDensity);
        int keyHeight = Math.max(1, drawRect.height());
        long signature = KeyboardThemeState.paintSignature(
                keyboard.getWidth(), keyboard.getHeight(), keyHeight, density, night);
        if (signature == nativeSingleKeyPaintSignature) return;
        prepareKeyboardLabelPaint(keyboard);
        float scaledDensity = keyboard.getResources().getDisplayMetrics().scaledDensity;
        float keyBasedSize = keyHeight * 0.145f;
        float textSize = Math.max(5.4f * scaledDensity,
                Math.min(7.8f * scaledDensity, keyBasedSize));
        keyboardLabelPaint.setTextSize(textSize);
        nativeSingleKeyPaintSignature = signature;
    }
'''
new_paint = '''    private void ensureNativeSingleKeyPaint(View keyboard, Rect drawRect) {
        if (keyboard == null || drawRect == null) return;
        int night = lastResolvedNightMode;
        if (!KeyboardThemeState.isDefined(night)) night = resolveLiveNightMode(keyboard);
        float scaledDensity = keyboard.getResources().getDisplayMetrics().scaledDensity;
        int density = Float.floatToIntBits(scaledDensity);
        int keyHeight = Math.max(1, drawRect.height());
        long signature = KeyboardThemeState.paintSignature(
                keyboard.getWidth(), keyboard.getHeight(), keyHeight, density, night);
        if (signature == nativeSingleKeyPaintSignature) return;
        prepareKeyboardLabelPaint(keyboard, night);
        float keyBasedSize = keyHeight * 0.145f;
        float textSize = Math.max(5.4f * scaledDensity,
                Math.min(7.8f * scaledDensity, keyBasedSize));
        keyboardLabelPaint.setTextSize(textSize);
        keyboardLabelPaint.getFontMetrics(keyboardLabelMetrics);
        nativeSingleKeyDescent = keyboardLabelMetrics.descent;
        nativeSingleKeyBottomPadding = Math.max(dp(keyboard, 1), keyHeight * 0.045f);
        nativeSingleKeyPaintSignature = signature;
    }
'''
text = replace_once(text, old_paint, new_paint, 'native paint cache')

old_draw = '''    private void drawKeyboardFunctionLabels(View keyboard, Canvas canvas) {
        if (keyboard == null || canvas == null || keyboard.getWidth() <= 0 || keyboard.getHeight() <= 0) return;
        if (KeyboardCompat.isHandwritingContext(keyboard)) return;
        Config config = configBridge.current();
        if (config == null || !config.hasAnyBinding()) return;
        try {
            InputMethodService ime = imeRef.get();
            EditorInfo editorInfo = ime == null ? null : ime.getCurrentInputEditorInfo();
            if (editorInfo != null && isPassword(editorInfo.inputType)) return;

            ensureNativeSingleKeyDrawHooks(keyboard);
            if (nativeSingleKeyActiveKeyboardRef.get() == keyboard) return;

            String name = keyboard.getClass().getName().toLowerCase(Locale.ROOT);
            prepareKeyboardLabelPaint(keyboard);
            if (name.contains("t9") || name.contains("nine")) {
                drawT9FunctionLabels(keyboard, canvas, config);
            } else if (name.contains("qwerty") || name.contains("wubi") || name.contains("pinyin")) {
                ensureKeyboardLabelGeometry(keyboard);
                drawQwertyFunctionLabels(keyboard, canvas, config);
            }
        } catch (Throwable throwable) {
            logError("keyboard function-label drawing failed", throwable);
        }
    }
'''
new_draw = '''    private void drawKeyboardFunctionLabels(View keyboard, Canvas canvas) {
        if (keyboard == null || canvas == null || keyboard.getWidth() <= 0 || keyboard.getHeight() <= 0) return;
        KeyboardRuntimeState runtimeState = runtimeState(keyboard);
        if (refreshHandwritingState(keyboard, runtimeState, false)) return;
        KeyboardLabelSnapshot labels = keyboardLabelSnapshot;
        if (labels == null || !labels.hasAnyLabels() || currentEditorPassword) return;
        try {
            int night = resolveLiveNightMode(keyboard);
            ensureNativeSingleKeyDrawHooks(keyboard);
            if (nativeSingleKeyActiveKeyboardRef.get() == keyboard) return;

            Config config = configBridge.current();
            if (config == null) return;
            prepareKeyboardLabelPaint(keyboard, night);
            if (runtimeState.t9Class) {
                drawT9FunctionLabels(keyboard, canvas, config);
            } else if (runtimeState.qwertyClass) {
                ensureKeyboardLabelGeometry(keyboard);
                drawQwertyFunctionLabels(keyboard, canvas, config);
            }
        } catch (Throwable throwable) {
            logError("keyboard function-label drawing failed", throwable);
        }
    }
'''
text = replace_once(text, old_draw, new_draw, 'fallback draw hot path')

old_theme = '''    private int resolveLiveNightMode(View keyboard) {
        if (keyboard == null) return Configuration.UI_MODE_NIGHT_UNDEFINED;

        int keyboardUiMode = Configuration.UI_MODE_NIGHT_UNDEFINED;
        int applicationUiMode = Configuration.UI_MODE_NIGHT_UNDEFINED;
        int imeUiMode = Configuration.UI_MODE_NIGHT_UNDEFINED;

        try {
            keyboardUiMode = keyboard.getResources().getConfiguration().uiMode;
        } catch (Throwable ignored) {}

        try {
            Context application = keyboard.getContext().getApplicationContext();
            if (application != null) {
                applicationUiMode = application.getResources().getConfiguration().uiMode;
            }
        } catch (Throwable ignored) {}

        InputMethodService ime = imeRef.get();
        if (ime != null) {
            try {
                Context application = ime.getApplicationContext();
                if (application != null) {
                    applicationUiMode = application.getResources().getConfiguration().uiMode;
                }
            } catch (Throwable ignored) {}
            try {
                imeUiMode = ime.getResources().getConfiguration().uiMode;
            } catch (Throwable ignored) {}
        }

        int resolved = KeyboardThemeState.resolveNightMode(
                keyboardUiMode, applicationUiMode, imeUiMode);
        int previous = lastResolvedNightMode;
        if (resolved != previous) {
            lastResolvedNightMode = resolved;
            nativeSingleKeyPaintSignature = Long.MIN_VALUE;
            View activeKeyboard = nativeSingleKeyActiveKeyboardRef.get();
            if (activeKeyboard != null && activeKeyboard != keyboard) activeKeyboard.postInvalidate();
            keyboard.postInvalidate();
            if (previous != Configuration.UI_MODE_NIGHT_UNDEFINED) {
                logInfo("keyboard label theme refreshed: " + previous + " -> " + resolved);
            }
        }
        return resolved;
    }

    private void prepareKeyboardLabelPaint(View keyboard) {
        float scaledDensity = keyboard.getResources().getDisplayMetrics().scaledDensity;
        float estimatedKeyHeight = keyboard.getHeight() / 4f;
        float keyHeightBased = estimatedKeyHeight * 0.145f;
        float textSize = Math.max(5.8f * scaledDensity, Math.min(8.0f * scaledDensity, keyHeightBased));
        boolean night = KeyboardThemeState.isNight(resolveLiveNightMode(keyboard));
'''
new_theme = '''    private int resolveLiveNightMode(View keyboard) {
        if (keyboard == null) return Configuration.UI_MODE_NIGHT_UNDEFINED;

        int keyboardUiMode = Configuration.UI_MODE_NIGHT_UNDEFINED;
        int applicationUiMode = Configuration.UI_MODE_NIGHT_UNDEFINED;
        int imeUiMode = Configuration.UI_MODE_NIGHT_UNDEFINED;

        try {
            keyboardUiMode = keyboard.getResources().getConfiguration().uiMode;
        } catch (Throwable ignored) {}

        try {
            Context application = keyboard.getContext().getApplicationContext();
            if (application != null) {
                applicationUiMode = application.getResources().getConfiguration().uiMode;
            }
        } catch (Throwable ignored) {}

        InputMethodService ime = imeRef.get();
        if (ime != null) {
            try {
                Context application = ime.getApplicationContext();
                if (application != null) {
                    applicationUiMode = application.getResources().getConfiguration().uiMode;
                }
            } catch (Throwable ignored) {}
            try {
                imeUiMode = ime.getResources().getConfiguration().uiMode;
            } catch (Throwable ignored) {}
        }

        int resolved = KeyboardThemeState.resolveNightMode(
                keyboardUiMode, applicationUiMode, imeUiMode);
        publishResolvedNightMode(resolved, keyboard);
        return resolved;
    }

    private void publishResolvedNightMode(int resolved, View keyboard) {
        if (!KeyboardThemeState.isDefined(resolved)) return;
        int previous = lastResolvedNightMode;
        if (resolved == previous) return;
        lastResolvedNightMode = resolved;
        nativeSingleKeyPaintSignature = Long.MIN_VALUE;
        View activeKeyboard = nativeSingleKeyActiveKeyboardRef.get();
        if (activeKeyboard != null && activeKeyboard != keyboard) activeKeyboard.postInvalidate();
        if (keyboard != null) keyboard.postInvalidate();
        if (previous != Configuration.UI_MODE_NIGHT_UNDEFINED) {
            logInfo("keyboard label theme refreshed: " + previous + " -> " + resolved);
        }
    }

    private KeyboardRuntimeState runtimeState(View keyboard) {
        View active = activeKeyboardRuntimeViewRef.get();
        KeyboardRuntimeState state = activeKeyboardRuntimeState;
        if (active == keyboard && state != null) return state;
        synchronized (keyboardRuntimeStates) {
            state = keyboardRuntimeStates.get(keyboard);
            if (state == null) {
                state = new KeyboardRuntimeState(keyboard.getClass().getName());
                keyboardRuntimeStates.put(keyboard, state);
            }
        }
        activeKeyboardRuntimeViewRef = new WeakReference<>(keyboard);
        activeKeyboardRuntimeState = state;
        return state;
    }

    private boolean refreshHandwritingState(View keyboard, KeyboardRuntimeState state, boolean force) {
        if (keyboard == null || state == null) return false;
        long now = SystemClock.uptimeMillis();
        if (state.shouldRefreshHandwriting(now, force)) {
            boolean previous = state.handwriting();
            boolean current = KeyboardCompat.isHandwritingContext(keyboard);
            state.updateHandwriting(current, now);
            if (current != previous) keyboard.postInvalidate();
        }
        return state.handwriting();
    }

    private static KeyboardLabelSnapshot initialKeyboardLabelSnapshot() {
        Config config = new Config();
        config.rebuildActionMap();
        return KeyboardLabelSnapshot.from(config);
    }

    private void prepareKeyboardLabelPaint(View keyboard, int nightMode) {
        float scaledDensity = keyboard.getResources().getDisplayMetrics().scaledDensity;
        float estimatedKeyHeight = keyboard.getHeight() / 4f;
        float keyHeightBased = estimatedKeyHeight * 0.145f;
        float textSize = Math.max(5.8f * scaledDensity, Math.min(8.0f * scaledDensity, keyHeightBased));
        boolean night = KeyboardThemeState.isNight(nightMode);
'''
text = replace_once(text, old_theme, new_theme, 'theme + runtime helpers')

# Reuse a single FontMetrics object instead of allocating one per key label.
metrics_old = '        Paint.FontMetrics metrics = keyboardLabelPaint.getFontMetrics();\n'
metrics_new = ('        keyboardLabelPaint.getFontMetrics(keyboardLabelMetrics);\n'
               '        Paint.FontMetrics metrics = keyboardLabelMetrics;\n')
metric_count = text.count(metrics_old)
if metric_count < 2:
    raise RuntimeError(f'FontMetrics reuse: expected at least 2 matches, got {metric_count}')
text = text.replace(metrics_old, metrics_new)

# Make sure the old one-argument paint preparation is completely gone.
if 'prepareKeyboardLabelPaint(keyboard);' in text:
    raise RuntimeError('stale prepareKeyboardLabelPaint(keyboard) call remains')
if 'nativeSingleKeyLabelCache' in text:
    raise RuntimeError('stale nativeSingleKeyLabelCache reference remains')
if 'NATIVE_SINGLE_KEY_LABEL_CACHE_LIMIT' in text:
    raise RuntimeError('stale native label cache limit remains')

MAIN.write_text(text, encoding='utf-8')
print('MainHook hot-path optimization patch applied')
