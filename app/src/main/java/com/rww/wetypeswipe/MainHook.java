package com.rww.wetypeswipe;

import android.app.Application;
import android.content.BroadcastReceiver;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.ContextWrapper;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.inputmethodservice.InputMethodService;
import android.os.Build;
import android.text.InputType;
import android.util.Log;
import android.view.HapticFeedbackConstants;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.view.inputmethod.EditorInfo;
import android.view.inputmethod.ExtractedText;
import android.view.inputmethod.ExtractedTextRequest;
import android.view.inputmethod.InputConnection;
import android.view.inputmethod.SurroundingText;

import java.lang.ref.WeakReference;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.ConcurrentHashMap;

import io.github.libxposed.api.XposedInterface;
import io.github.libxposed.api.XposedModule;
import io.github.libxposed.api.XposedModuleInterface;

public final class MainHook extends XposedModule {
    private static final String TAG = "WeTypeSwipe";
    private static final String TARGET = "com.tencent.wetype";
    private static final String KEYBOARD_BASE = "com.tencent.wetype.plugin.hld.keyboard.selfdraw.n";
    private static final int PARAGRAPH_CONTEXT_CHARS = 65_536;

    private final GestureTracker tracker = new GestureTracker();
    private final ConcurrentHashMap<String, Method> methodCache = new ConcurrentHashMap<>();

    private volatile WeakReference<InputMethodService> imeRef = new WeakReference<>(null);
    private volatile Config cachedConfig = defaultConfig();
    private volatile Class<?> keyboardBaseClass;
    private volatile boolean hooksInstalled;
    private volatile boolean receiverRegistered;
    private volatile boolean targetCacheLoaded;
    private volatile int currentSelectionStart = -1;
    private volatile int currentSelectionEnd = -1;
    private volatile Class<?> selectionHookedClass;
    private volatile WeakReference<View> toolbarCarrierRootRef = new WeakReference<>(null);
    private volatile WeakReference<View> toolbarCarrierSourceRef = new WeakReference<>(null);
    private volatile WeakReference<View> toolbarCarrierArgumentRef = new WeakReference<>(null);
    private volatile Object toolbarCarrierCallback;
    private volatile Object toolbarCarrierHolder;
    private volatile Field toolbarCarrierFunctionField;
    private volatile Field toolbarCarrierCategoryField;
    private volatile Field toolbarCarrierGroupField;
    private volatile Method toolbarCarrierInvokeMethod;
    private volatile Object toolbarPermanentCategory;
    private BroadcastReceiver configReceiver;

    @Override public void onModuleLoaded(XposedModuleInterface.ModuleLoadedParam param) {
        logInfo("Modern API " + getApiVersion() + " loaded in " + param.getProcessName());
    }

    @Override public void onPackageReady(XposedModuleInterface.PackageReadyParam param) {
        if (!TARGET.equals(param.getPackageName())) return;
        try {
            installHooks();
            logInfo("v1.10.0 entered target package");
        } catch (Throwable throwable) {
            logError("initialization failed", throwable);
        }
    }

    private static Config defaultConfig() {
        Config config = new Config();
        config.rebuildActionMap();
        return config;
    }

    private synchronized void installHooks() throws Exception {
        if (hooksInstalled) return;

        hookAfter(Application.class.getDeclaredMethod("attach", Context.class),
                chain -> captureApplication(chain.getThisObject()));
        hookAfter(Application.class.getDeclaredMethod("onCreate"),
                chain -> captureApplication(chain.getThisObject()));

        hookAfter(InputMethodService.class.getDeclaredMethod("onCreate"),
                chain -> captureIme(chain.getThisObject()));
        hookBefore(InputMethodService.class.getDeclaredMethod("onStartInput", EditorInfo.class, boolean.class),
                chain -> captureStartInput(chain.getThisObject()));
        hookAfter(InputMethodService.class.getDeclaredMethod("onUpdateSelection",
                        int.class, int.class, int.class, int.class, int.class, int.class),
                this::captureSelection);

        Method dispatchTouchEvent = View.class.getDeclaredMethod("dispatchTouchEvent", MotionEvent.class);
        dispatchTouchEvent.setAccessible(true);
        hook(dispatchTouchEvent)
                .setExceptionMode(XposedInterface.ExceptionMode.PROTECTIVE)
                .intercept(this::interceptDispatchTouch);

        hooksInstalled = true;
        logInfo("stable dispatch hook installed");
    }

    private interface ChainAction {
        void run(XposedInterface.Chain chain) throws Throwable;
    }

    private void hookAfter(Method method, ChainAction action) {
        method.setAccessible(true);
        hook(method).setExceptionMode(XposedInterface.ExceptionMode.PROTECTIVE).intercept(chain -> {
            Object result = chain.proceed();
            action.run(chain);
            return result;
        });
    }

    private void hookBefore(Method method, ChainAction action) {
        method.setAccessible(true);
        hook(method).setExceptionMode(XposedInterface.ExceptionMode.PROTECTIVE).intercept(chain -> {
            action.run(chain);
            return chain.proceed();
        });
    }

    private void captureApplication(Object object) {
        if (!(object instanceof Application)) return;
        Application app = (Application) object;
        try {
            if (!TARGET.equals(app.getPackageName())) return;
        } catch (Throwable ignored) {
            return;
        }
        ensureConfigSync(app);
    }

    private void captureIme(Object object) {
        if (!(object instanceof InputMethodService)) return;
        InputMethodService ime = (InputMethodService) object;
        try {
            if (!TARGET.equals(ime.getPackageName())) return;
        } catch (Throwable ignored) {
            return;
        }

        InputMethodService previousIme = imeRef.get();
        if (previousIme != ime) clearToolbarCarrierCache();
        imeRef = new WeakReference<>(ime);
        ensureConfigSync(ime);
        ensureConcreteSelectionHook(ime.getClass());

    }

    private void captureStartInput(Object object) {
        currentSelectionStart = -1;
        currentSelectionEnd = -1;
        captureIme(object);
    }

    private void captureSelection(XposedInterface.Chain chain) {
        try {
            Object object = chain.getThisObject();
            if (!(object instanceof InputMethodService)) return;
            int start = ((Number) chain.getArg(2)).intValue();
            int end = ((Number) chain.getArg(3)).intValue();
            if (start >= 0 && end >= 0) {
                currentSelectionStart = start;
                currentSelectionEnd = end;
            }
        } catch (Throwable throwable) {
            logError("selection tracking failed", throwable);
        }
    }

    private synchronized void ensureConcreteSelectionHook(Class<?> imeClass) {
        if (imeClass == null || imeClass == InputMethodService.class || selectionHookedClass == imeClass) return;
        try {
            Method method = findMethod(imeClass, "onUpdateSelection", new Class<?>[]{
                    int.class, int.class, int.class, int.class, int.class, int.class});
            if (method == null || method.getDeclaringClass() == InputMethodService.class) return;
            hookAfter(method, this::captureSelection);
            selectionHookedClass = imeClass;
            logInfo("selection hook installed for " + imeClass.getName());
        } catch (Throwable throwable) {
            logError("concrete selection hook failed", throwable);
        }
    }

    private synchronized void registerConfigReceiver(Context context) {
        if (receiverRegistered || context == null) return;
        configReceiver = new BroadcastReceiver() {
            @Override public void onReceive(Context receiverContext, Intent intent) {
                if (intent == null || !Config.ACTION_CONFIG_CHANGED.equals(intent.getAction())) return;
                if (intent.getBooleanExtra(Config.EXTRA_SNAPSHOT, false)) {
                    Config config = configFromIntent(intent);
                    if (config != null) {
                        cachedConfig = config;
                        targetCacheLoaded = true;
                        persistTargetCache(receiverContext, config);
                        return;
                    }
                }
                loadConfigFromTargetCache(receiverContext);
            }
        };
        try {
            IntentFilter filter = new IntentFilter(Config.ACTION_CONFIG_CHANGED);
            if (Build.VERSION.SDK_INT >= 33) {
                context.registerReceiver(configReceiver, filter, Context.RECEIVER_EXPORTED);
            } else {
                context.registerReceiver(configReceiver, filter);
            }
            receiverRegistered = true;
        } catch (Throwable throwable) {
            logError("config receiver registration failed", throwable);
        }
    }

    private void ensureConfigSync(Context context) {
        if (context == null) return;
        Context stableContext = context.getApplicationContext();
        if (stableContext == null) stableContext = context;
        registerConfigReceiver(stableContext);
        loadConfigFromTargetCache(stableContext);
    }

    private Config configFromIntent(Intent intent) {
        try {
            Config config = new Config();
            config.selectAll = intent.getStringExtra(Config.KEY_SELECT_ALL);
            config.cut = intent.getStringExtra(Config.KEY_CUT);
            config.copy = intent.getStringExtra(Config.KEY_COPY);
            config.paste = intent.getStringExtra(Config.KEY_PASTE);
            config.paragraphStart = intent.getStringExtra(Config.KEY_PARAGRAPH_START);
            config.paragraphEnd = intent.getStringExtra(Config.KEY_PARAGRAPH_END);
            config.selectToParagraphStart = intent.getStringExtra(Config.KEY_SELECT_TO_PARAGRAPH_START);
            config.selectToParagraphEnd = intent.getStringExtra(Config.KEY_SELECT_TO_PARAGRAPH_END);
            config.openClipboard = intent.getStringExtra(Config.KEY_OPEN_CLIPBOARD);
            config.openQuickPhrase = intent.getStringExtra(Config.KEY_OPEN_QUICK_PHRASE);
            config.disabledKeys = intent.getStringExtra(Config.KEY_DISABLED_KEYS);
            if (config.selectAll == null) config.selectAll = "z";
            if (config.cut == null) config.cut = "x";
            if (config.copy == null) config.copy = "c";
            if (config.paste == null) config.paste = "v";
            if (config.paragraphStart == null) config.paragraphStart = "";
            if (config.paragraphEnd == null) config.paragraphEnd = "";
            if (config.selectToParagraphStart == null) config.selectToParagraphStart = "";
            if (config.selectToParagraphEnd == null) config.selectToParagraphEnd = "";
            if (config.openClipboard == null) config.openClipboard = "";
            if (config.openQuickPhrase == null) config.openQuickPhrase = "";
            if (config.disabledKeys == null) config.disabledKeys = "";
            config.thresholdDp = clamp(intent.getIntExtra(Config.KEY_THRESHOLD, 12), 6, 40, 12);
            config.t9ThresholdDp = clamp(intent.getIntExtra(Config.KEY_T9_THRESHOLD, 20), 10, 48, 20);
            config.vibration = intent.getBooleanExtra(Config.KEY_VIBRATION, true);
            config.revision = intent.getIntExtra(Config.KEY_REVISION, 0);
            for (int digit = 2; digit <= 9; digit++) {
                config.t9Actions[digit] = Config.validAction(
                        intent.getIntExtra(Config.t9PrefKey(digit), Config.ACTION_NONE));
            }
            config.rebuildActionMap();
            return config;
        } catch (Throwable throwable) {
            logError("config snapshot parse failed", throwable);
            return null;
        }
    }

    private synchronized void persistTargetCache(Context context, Config config) {
        try {
            SharedPreferences.Editor editor = context.getSharedPreferences(
                    Config.TARGET_CACHE_PREFS, Context.MODE_PRIVATE).edit()
                    .putString(Config.KEY_SELECT_ALL, config.selectAll)
                    .putString(Config.KEY_CUT, config.cut)
                    .putString(Config.KEY_COPY, config.copy)
                    .putString(Config.KEY_PASTE, config.paste)
                    .putString(Config.KEY_PARAGRAPH_START, config.paragraphStart)
                    .putString(Config.KEY_PARAGRAPH_END, config.paragraphEnd)
                    .putString(Config.KEY_SELECT_TO_PARAGRAPH_START, config.selectToParagraphStart)
                    .putString(Config.KEY_SELECT_TO_PARAGRAPH_END, config.selectToParagraphEnd)
                    .putString(Config.KEY_OPEN_CLIPBOARD, config.openClipboard)
                    .putString(Config.KEY_OPEN_QUICK_PHRASE, config.openQuickPhrase)
                    .putString(Config.KEY_DISABLED_KEYS, config.disabledKeys)
                    .putInt(Config.KEY_THRESHOLD, config.thresholdDp)
                    .putInt(Config.KEY_T9_THRESHOLD, config.t9ThresholdDp)
                    .putBoolean(Config.KEY_VIBRATION, config.vibration)
                    .putInt(Config.KEY_REVISION, config.revision);
            for (int digit = 2; digit <= 9; digit++) {
                editor.putInt(Config.t9PrefKey(digit), config.t9Actions[digit]);
            }
            editor.commit();
        } catch (Throwable throwable) {
            logError("target config cache write failed", throwable);
        }
    }

    private synchronized void loadConfigFromTargetCache(Context context) {
        try {
            SharedPreferences prefs = context.getSharedPreferences(
                    Config.TARGET_CACHE_PREFS, Context.MODE_PRIVATE);
            if (!prefs.contains(Config.KEY_REVISION)) {
                targetCacheLoaded = false;
                return;
            }
            Config config = new Config();
            config.selectAll = prefs.getString(Config.KEY_SELECT_ALL, "z");
            config.cut = prefs.getString(Config.KEY_CUT, "x");
            config.copy = prefs.getString(Config.KEY_COPY, "c");
            config.paste = prefs.getString(Config.KEY_PASTE, "v");
            config.paragraphStart = prefs.getString(Config.KEY_PARAGRAPH_START, "");
            config.paragraphEnd = prefs.getString(Config.KEY_PARAGRAPH_END, "");
            config.selectToParagraphStart = prefs.getString(Config.KEY_SELECT_TO_PARAGRAPH_START, "");
            config.selectToParagraphEnd = prefs.getString(Config.KEY_SELECT_TO_PARAGRAPH_END, "");
            config.openClipboard = prefs.getString(Config.KEY_OPEN_CLIPBOARD, "");
            config.openQuickPhrase = prefs.getString(Config.KEY_OPEN_QUICK_PHRASE, "");
            config.disabledKeys = prefs.getString(Config.KEY_DISABLED_KEYS, "");
            config.thresholdDp = clamp(prefs.getInt(Config.KEY_THRESHOLD, 12), 6, 40, 12);
            config.t9ThresholdDp = clamp(prefs.getInt(Config.KEY_T9_THRESHOLD, 20), 10, 48, 20);
            config.vibration = prefs.getBoolean(Config.KEY_VIBRATION, true);
            config.revision = prefs.getInt(Config.KEY_REVISION, 0);
            for (int digit = 2; digit <= 9; digit++) {
                config.t9Actions[digit] = Config.validAction(
                        prefs.getInt(Config.t9PrefKey(digit), Config.ACTION_NONE));
            }
            config.rebuildActionMap();
            cachedConfig = config;
            targetCacheLoaded = true;
        } catch (Throwable throwable) {
            targetCacheLoaded = false;
            logError("target config cache load failed", throwable);
        }
    }

    private static int clamp(int value, int min, int max, int fallback) {
        return value < min || value > max ? fallback : value;
    }

    private Object interceptDispatchTouch(XposedInterface.Chain chain) throws Throwable {
        Object target = chain.getThisObject();
        Object eventObject = chain.getArg(0);
        if (!(target instanceof View) || !(eventObject instanceof MotionEvent)) return chain.proceed();

        View view = (View) target;
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

        if (event.getActionMasked() == MotionEvent.ACTION_DOWN && !targetCacheLoaded) {
            ensureConfigSync(view.getContext());
        }
        return interceptKeyboardTouch(chain, view, event);
    }

    private static Class<?> findKeyboardBase(Class<?> type) {
        for (int i = 0; type != null && i < 12; i++, type = type.getSuperclass()) {
            if (KEYBOARD_BASE.equals(type.getName())) return type;
        }
        return null;
    }

    private Object interceptKeyboardTouch(XposedInterface.Chain chain, View keyboard, MotionEvent event) throws Throwable {
        final int maskedAction = event.getActionMasked();
        if (event.getPointerCount() != 1) {
            if (maskedAction == MotionEvent.ACTION_UP || maskedAction == MotionEvent.ACTION_CANCEL) tracker.clear(keyboard);
            return chain.proceed();
        }

        Config config = cachedConfig;
        if (maskedAction != MotionEvent.ACTION_DOWN
                && !config.hasAnyBinding()
                && !tracker.matches(keyboard)) return chain.proceed();

        if (maskedAction == MotionEvent.ACTION_DOWN) {
            tracker.begin(keyboard, event.getX(), event.getY());
            Object result = chain.proceed();

            KeyInfo keyInfo = keyAfterDown(keyboard, event);


            int requestedAction = keyInfo == null
                    ? Config.ACTION_NONE
                    : config.actionFor(keyInfo.key, keyInfo.t9);
            float thresholdPx = dp(keyboard,
                    keyInfo != null && keyInfo.t9 ? config.t9ThresholdDp : config.thresholdDp);
            tracker.setBinding(keyboard, keyInfo, requestedAction, thresholdPx);
            if (requestedAction == Config.ACTION_NONE) tracker.clear(keyboard);
            return result;
        }

        if (!tracker.matches(keyboard)) return chain.proceed();

        if (tracker.triggered) {
            if (maskedAction == MotionEvent.ACTION_UP || maskedAction == MotionEvent.ACTION_CANCEL) tracker.clear(keyboard);
            return Boolean.TRUE;
        }

        if ((maskedAction == MotionEvent.ACTION_MOVE || maskedAction == MotionEvent.ACTION_UP)
                && tracker.action != Config.ACTION_NONE) {
            float deltaX = event.getX() - tracker.downX;
            float deltaY = event.getY() - tracker.downY;
            float horizontalLimit = tracker.t9
                    ? Math.max(tracker.thresholdPx * 0.9f, deltaY * 0.75f)
                    : Math.max(tracker.thresholdPx * 2.5f, deltaY * 1.2f);
            if (deltaY >= tracker.thresholdPx && Math.abs(deltaX) <= horizontalLimit) {
                final int requestedAction = tracker.action;
                final String key = tracker.key;
                final Context context = keyboard.getContext();
                tracker.markTriggered(keyboard);

                proceedWithCancel(chain, event);

                Config latest = cachedConfig;
                if (latest.vibration) {
                    try { keyboard.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP); }
                    catch (Throwable ignored) {}
                }

                if (requestedAction != Config.ACTION_DISABLE) {
                    keyboard.post(() -> performAction(context, keyboard, requestedAction, key));
                }

                if (maskedAction == MotionEvent.ACTION_UP) tracker.clear(keyboard);
                return Boolean.TRUE;
            }
        }

        Object result = chain.proceed();
        if (maskedAction == MotionEvent.ACTION_UP || maskedAction == MotionEvent.ACTION_CANCEL) tracker.clear(keyboard);
        return result;
    }

    private void proceedWithCancel(XposedInterface.Chain chain, MotionEvent source) throws Throwable {
        MotionEvent cancel = MotionEvent.obtain(source);
        try {
            cancel.setAction(MotionEvent.ACTION_CANCEL);
            List<Object> args = chain.getArgs();
            Object[] cancelArgs = args.toArray(new Object[0]);
            cancelArgs[0] = cancel;
            chain.proceed(cancelArgs);
        } finally {
            cancel.recycle();
        }
    }

    private KeyInfo keyAfterDown(Object keyboard, MotionEvent event) {
        Object button = invoke(keyboard, "getActionButton");
        if (button == null) button = invoke(keyboard, "v1", event, false);
        if (button == null) button = invoke(keyboard, "v1", event, true);
        return keyFromButton(keyboard, button);
    }

    private KeyInfo keyFromButton(Object keyboard, Object button) {
        if (button == null) return null;
        Object keyData = invoke(button, "O");
        if (keyData != null) {
            Object main = invoke(keyData, "getMainText");
            Object secondary = firstNonNull(
                    invoke(keyData, "getSubText"),
                    invoke(keyData, "getSecondaryText"),
                    invoke(keyData, "getHintText"),
                    invoke(keyData, "getAssistText"));
            KeyInfo key = keyFromTexts(main, secondary);
            if (key != null) return key;
            if (isT9Context(keyboard, button, keyData)) {
                String numeric = numericT9Key(main);
                if (numeric != null) return KeyInfo.t9(numeric);
            }

            Object id = invoke(keyData, "getId");
            key = keyFromId(id, keyboard, button, keyData);
            if (key != null) return key;
        }
        return keyFromId(invoke(button, "K"), keyboard, button, keyData);
    }

    private static Object firstNonNull(Object... values) {
        for (Object value : values) if (value != null) return value;
        return null;
    }

    private static KeyInfo keyFromTexts(Object mainValue, Object secondaryValue) {
        String main = normalizeText(mainValue);
        String secondary = normalizeText(secondaryValue);
        String combined = main + secondary;

        String digit = t9DigitFromLetters(combined);
        if (digit != null) return KeyInfo.t9(digit);

        if (main.length() == 1) {
            char c = main.charAt(0);
            if (c >= 'a' && c <= 'z') return KeyInfo.alpha(String.valueOf(c));
        }
        return null;
    }

    private static String normalizeText(Object value) {
        if (value == null) return "";
        String text = String.valueOf(value).trim().toLowerCase(Locale.ROOT);
        StringBuilder clean = null;
        for (int index = 0; index < text.length(); index++) {
            char c = text.charAt(index);
            boolean allowed = (c >= 'a' && c <= 'z') || (c >= '0' && c <= '9');
            if (allowed) {
                if (clean != null) clean.append(c);
            } else if (clean == null) {
                clean = new StringBuilder(text.length());
                clean.append(text, 0, index);
            }
        }
        return clean == null ? text : clean.toString();
    }

    private static String numericT9Key(Object value) {
        String text = normalizeText(value);
        if (text.length() == 1) {
            char c = text.charAt(0);
            if (c >= '2' && c <= '9') return String.valueOf(c);
        }
        return null;
    }

    private static String t9DigitFromLetters(String value) {
        if (value == null || value.isEmpty()) return null;
        if (lettersMatch(value, "abc")) return "2";
        if (lettersMatch(value, "def")) return "3";
        if (lettersMatch(value, "ghi")) return "4";
        if (lettersMatch(value, "jkl")) return "5";
        if (lettersMatch(value, "mno")) return "6";
        if (lettersMatch(value, "pqrs")) return "7";
        if (lettersMatch(value, "tuv")) return "8";
        if (lettersMatch(value, "wxyz")) return "9";
        return null;
    }

    private static boolean lettersMatch(String value, String expected) {
        int matched = 0;
        for (int index = 0; index < value.length(); index++) {
            char c = value.charAt(index);
            if (c < 'a' || c > 'z') continue;
            if (matched >= expected.length() || c != expected.charAt(matched)) return false;
            matched++;
        }
        return matched == expected.length();
    }

    private static KeyInfo keyFromId(Object value, Object keyboard, Object button, Object keyData) {
        if (value == null) return null;
        String text = String.valueOf(value).trim().toLowerCase(Locale.ROOT);

        int index = text.lastIndexOf("_key_");
        String tail = index >= 0 ? text.substring(index + 5) : text;
        if (tail.length() == 1) {
            char c = tail.charAt(0);
            if (c >= 'a' && c <= 'z') return KeyInfo.alpha(String.valueOf(c));
        }
        if (!tail.isEmpty()) {
            char last = tail.charAt(tail.length() - 1);
            if (last >= 'a' && last <= 'z'
                    && (tail.endsWith("_" + last) || tail.endsWith("key" + last))) {
                return KeyInfo.alpha(String.valueOf(last));
            }
        }

        boolean t9Hint = text.contains("t9") || text.contains("nine")
                || isT9Context(keyboard, button, keyData);
        if (t9Hint) {
            for (int i = text.length() - 1; i >= 0; i--) {
                char c = text.charAt(i);
                if (c >= '2' && c <= '9') return KeyInfo.t9(String.valueOf(c));
            }
        }
        return null;
    }

    private static boolean isT9Context(Object... values) {
        for (Object value : values) {
            String name = className(value);
            if (name.contains("t9") || name.contains("nine")) return true;
        }
        return false;
    }

    private static String className(Object value) {
        return value == null ? "" : value.getClass().getName().toLowerCase(Locale.ROOT);
    }

    private Object invoke(Object target, String name, Object... args) {
        if (target == null) return null;
        try {
            Class<?>[] parameterTypes = new Class<?>[args.length];
            for (int i = 0; i < args.length; i++) {
                Object arg = args[i];
                if (arg instanceof MotionEvent) parameterTypes[i] = MotionEvent.class;
                else if (arg instanceof Boolean) parameterTypes[i] = boolean.class;
                else if (arg instanceof Integer) parameterTypes[i] = int.class;
                else parameterTypes[i] = arg == null ? Object.class : arg.getClass();
            }
            String cacheKey = target.getClass().getName() + '#' + name + signature(parameterTypes);
            Method method = methodCache.get(cacheKey);
            if (method == null) {
                method = findMethod(target.getClass(), name, parameterTypes);
                if (method == null) return null;
                Method previous = methodCache.putIfAbsent(cacheKey, method);
                if (previous != null) method = previous;
            }
            return method.invoke(target, args);
        } catch (Throwable ignored) {
            return null;
        }
    }

    private static String signature(Class<?>[] types) {
        StringBuilder value = new StringBuilder(types.length * 12);
        for (Class<?> type : types) value.append(':').append(type.getName());
        return value.toString();
    }

    private static Method findMethod(Class<?> type, String name, Class<?>[] parameterTypes) {
        for (Class<?> current = type; current != null; current = current.getSuperclass()) {
            try {
                Method method = current.getDeclaredMethod(name, parameterTypes);
                method.setAccessible(true);
                return method;
            } catch (NoSuchMethodException ignored) {}
        }
        return null;
    }

    private static final class KeyInfo {
        final String key;
        final String display;
        final boolean t9;

        private KeyInfo(String key, String display, boolean t9) {
            this.key = key;
            this.display = display;
            this.t9 = t9;
        }

        static KeyInfo alpha(String key) {
            return new KeyInfo(key, key.toUpperCase(Locale.ROOT), false);
        }

        static KeyInfo t9(String digit) {
            return new KeyInfo(digit, "九宫格 " + Config.t9Label(digit.charAt(0) - '0'), true);
        }
    }

    private void performAction(Context context, View keyboard, int action, String key) {
        String actionName = Config.actionName(action);
        try {
            InputMethodService ime = imeRef.get();
            if (ime == null) ime = findIme(context);
            if (ime == null) {
                logError("action failed: no input method service", null);
                return;
            }
            imeRef = new WeakReference<>(ime);

            EditorInfo editorInfo = ime.getCurrentInputEditorInfo();
            if (editorInfo != null && isPassword(editorInfo.inputType)) return;

            if (isNativePanelAction(action)) {
                if (!openNativePanel(ime, keyboard, action)) {
                    logError(actionName + " failed: native entry not found", null);
                }
                return;
            }

            InputConnection connection = ime.getCurrentInputConnection();
            if (connection == null) {
                logError("action failed: no input connection", null);
                return;
            }

            boolean success;
            if (isParagraphAction(action)) {
                success = performParagraphAction(connection, action);
            } else {
                success = performMenuAction(ime, connection, Config.menuIdFor(action));
            }
            if (!success) logError(actionName + " failed: target editor rejected action", null);
        } catch (Throwable throwable) {
            logError("action failed", throwable);
        }
    }



    private static boolean isNativePanelAction(int action) {
        return action == Config.ACTION_OPEN_CLIPBOARD
                || action == Config.ACTION_OPEN_QUICK_PHRASE;
    }

    private boolean openNativePanel(InputMethodService ime, View keyboard, int action) {
        View root = keyboardWindowRoot(keyboard);
        if (root == null) root = imeRootView(ime);
        if (root == null) return false;
        return invokeToolbarCommandCarrier(root, action);
    }

    private static View keyboardWindowRoot(View keyboard) {
        if (keyboard == null) return null;
        try {
            View root = keyboard.getRootView();
            return root == null ? keyboard : root;
        } catch (Throwable ignored) {
            return keyboard;
        }
    }

    private static View imeRootView(InputMethodService ime) {
        try {
            if (ime == null || ime.getWindow() == null || ime.getWindow().getWindow() == null) return null;
            return ime.getWindow().getWindow().getDecorView();
        } catch (Throwable ignored) {
            return null;
        }
    }


    private boolean invokeToolbarCommandCarrier(View root, int action) {
        int targetFunction = action == Config.ACTION_OPEN_CLIPBOARD ? 4 : 8;

        for (int attempt = 0; attempt < 2; attempt++) {
            if (!resolveToolbarCommandCarrier(root)) {
                if (attempt == 0) {
                    clearToolbarCarrierCache();
                    continue;
                }
                logError(Config.actionName(action) + " failed: toolbar command carrier unavailable", null);
                return false;
            }

            View source = toolbarCarrierSourceRef.get();
            Object callback = toolbarCarrierCallback;
            Object holder = toolbarCarrierHolder;
            Field functionField = toolbarCarrierFunctionField;
            Field categoryField = toolbarCarrierCategoryField;
            Field groupField = toolbarCarrierGroupField;
            Method invokeMethod = toolbarCarrierInvokeMethod;

            if (source == null || !source.isAttachedToWindow()
                    || callback == null || holder == null
                    || functionField == null || invokeMethod == null) {
                clearToolbarCarrierCache();
                continue;
            }

            Object oldFunction = null;
            Object oldCategory = null;
            Object oldGroup = null;
            boolean functionChanged = false;
            boolean categoryChanged = false;
            boolean groupChanged = false;
            try {
                oldFunction = functionField.get(holder);
                functionField.set(holder, targetFunction);
                functionChanged = true;

                if (categoryField != null && toolbarPermanentCategory != null) {
                    oldCategory = categoryField.get(holder);
                    categoryField.set(holder, toolbarPermanentCategory);
                    categoryChanged = true;
                }
                if (groupField != null) {
                    oldGroup = groupField.get(holder);
                    groupField.set(holder, 6);
                    groupChanged = true;
                }

                View argument = toolbarCarrierArgumentRef.get();
                if (argument == null) argument = source;
                invokeMethod.invoke(callback, argument);
                return true;
            } catch (Throwable throwable) {
                clearToolbarCarrierCache();
                if (attempt == 1) {
                    logError("toolbar-command-carrier failed action=" + Config.actionName(action), throwable);
                    return false;
                }
            } finally {
                try { if (functionChanged) functionField.set(holder, oldFunction); } catch (Throwable ignored) {}
                try { if (categoryChanged) categoryField.set(holder, oldCategory); } catch (Throwable ignored) {}
                try { if (groupChanged) groupField.set(holder, oldGroup); } catch (Throwable ignored) {}
            }
        }
        return false;
    }

    private boolean resolveToolbarCommandCarrier(View root) {
        View cachedRoot = toolbarCarrierRootRef.get();
        View cachedSource = toolbarCarrierSourceRef.get();
        if (cachedRoot == root
                && cachedSource != null && cachedSource.isAttachedToWindow()
                && toolbarCarrierCallback != null
                && toolbarCarrierHolder != null
                && toolbarCarrierFunctionField != null
                && toolbarCarrierInvokeMethod != null) {
            return true;
        }

        clearToolbarCarrierCache();
        Object[] carrier = findToolbarCommandCarrier(root);
        if (carrier == null) return false;

        View source = (View) carrier[0];
        Object callback = carrier[2];
        Object holder = readNamedField(callback, "this$0");
        if (source == null || callback == null || holder == null) return false;

        Field functionField = findNamedField(holder.getClass(), "f");
        if (functionField == null) return false;
        Field categoryField = findNamedField(holder.getClass(), "g");
        Field groupField = findNamedField(holder.getClass(), "h");
        Method invokeMethod = findCompatibleInvoke(callback.getClass());
        if (invokeMethod == null) return false;

        Object permanent = categoryField == null ? null : enumConstant(categoryField.getType(), "Permanent");
        Object capturedView = readNamedField(callback, "$this_apply");
        View argument = capturedView instanceof View ? (View) capturedView : source;

        toolbarCarrierRootRef = new WeakReference<>(root);
        toolbarCarrierSourceRef = new WeakReference<>(source);
        toolbarCarrierArgumentRef = new WeakReference<>(argument);
        toolbarCarrierCallback = callback;
        toolbarCarrierHolder = holder;
        toolbarCarrierFunctionField = functionField;
        toolbarCarrierCategoryField = categoryField;
        toolbarCarrierGroupField = groupField;
        toolbarCarrierInvokeMethod = invokeMethod;
        toolbarPermanentCategory = permanent;
        return true;
    }

    private void clearToolbarCarrierCache() {
        toolbarCarrierRootRef = new WeakReference<>(null);
        toolbarCarrierSourceRef = new WeakReference<>(null);
        toolbarCarrierArgumentRef = new WeakReference<>(null);
        toolbarCarrierCallback = null;
        toolbarCarrierHolder = null;
        toolbarCarrierFunctionField = null;
        toolbarCarrierCategoryField = null;
        toolbarCarrierGroupField = null;
        toolbarCarrierInvokeMethod = null;
        toolbarPermanentCategory = null;
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

    private static boolean isParagraphAction(int action) {
        return action == Config.ACTION_PARAGRAPH_START
                || action == Config.ACTION_PARAGRAPH_END
                || action == Config.ACTION_SELECT_TO_PARAGRAPH_START
                || action == Config.ACTION_SELECT_TO_PARAGRAPH_END;
    }

    private boolean performParagraphAction(InputConnection connection, int action) {
        try {
            try { connection.finishComposingText(); } catch (Throwable ignored) {}

            EditorSnapshot snapshot = readEditorSnapshot(connection);
            if (snapshot == null) return false;

            int paragraphStart = snapshot.left - distanceToParagraphStart(snapshot.before);
            int paragraphEnd = snapshot.right + distanceToParagraphEnd(snapshot.after);
            int targetStart;
            int targetEnd;

            if (action == Config.ACTION_PARAGRAPH_START) {
                targetStart = paragraphStart;
                targetEnd = paragraphStart;
            } else if (action == Config.ACTION_PARAGRAPH_END) {
                targetStart = paragraphEnd;
                targetEnd = paragraphEnd;
            } else if (action == Config.ACTION_SELECT_TO_PARAGRAPH_START) {
                targetStart = paragraphStart;
                targetEnd = snapshot.right;
            } else if (action == Config.ACTION_SELECT_TO_PARAGRAPH_END) {
                targetStart = snapshot.left;
                targetEnd = paragraphEnd;
            } else {
                return false;
            }

            boolean success = connection.setSelection(targetStart, targetEnd);
            if (success) {
                currentSelectionStart = targetStart;
                currentSelectionEnd = targetEnd;
            }
            return success;
        } catch (Throwable throwable) {
            logError("paragraph action failed", throwable);
            return false;
        }
    }

    private EditorSnapshot readEditorSnapshot(InputConnection connection) {
        if (Build.VERSION.SDK_INT >= 31) {
            try {
                SurroundingText surrounding = connection.getSurroundingText(
                        PARAGRAPH_CONTEXT_CHARS, PARAGRAPH_CONTEXT_CHARS, 0);
                if (surrounding != null && surrounding.getText() != null) {
                    String text = surrounding.getText().toString();
                    int relativeStart = clampIndex(surrounding.getSelectionStart(), text.length());
                    int relativeEnd = clampIndex(surrounding.getSelectionEnd(), text.length());
                    int relativeLeft = Math.min(relativeStart, relativeEnd);
                    int relativeRight = Math.max(relativeStart, relativeEnd);
                    int offset = Math.max(0, surrounding.getOffset());
                    return new EditorSnapshot(
                            offset + relativeLeft,
                            offset + relativeRight,
                            text.substring(0, relativeLeft),
                            text.substring(relativeRight),
                            "surrounding");
                }
            } catch (Throwable throwable) {
                logError("surrounding text unavailable", throwable);
            }
        }

        int selectionStart = currentSelectionStart;
        int selectionEnd = currentSelectionEnd;
        if (selectionStart >= 0 && selectionEnd >= 0) {
            try {
                CharSequence before = connection.getTextBeforeCursor(PARAGRAPH_CONTEXT_CHARS, 0);
                CharSequence after = connection.getTextAfterCursor(PARAGRAPH_CONTEXT_CHARS, 0);
                if (before != null && after != null) {
                    return new EditorSnapshot(
                            Math.min(selectionStart, selectionEnd),
                            Math.max(selectionStart, selectionEnd),
                            before.toString(),
                            after.toString(),
                            "cursor-context");
                }
            } catch (Throwable throwable) {
                logError("cursor context unavailable", throwable);
            }
        }

        try {
            ExtractedTextRequest request = new ExtractedTextRequest();
            request.hintMaxChars = PARAGRAPH_CONTEXT_CHARS;
            request.hintMaxLines = 4096;
            ExtractedText extracted = connection.getExtractedText(request, 0);
            if (extracted != null && extracted.text != null) {
                String text = extracted.text.toString();
                int relativeStart = clampIndex(extracted.selectionStart, text.length());
                int relativeEnd = clampIndex(extracted.selectionEnd, text.length());
                int relativeLeft = Math.min(relativeStart, relativeEnd);
                int relativeRight = Math.max(relativeStart, relativeEnd);
                int offset = Math.max(0, extracted.startOffset);
                return new EditorSnapshot(
                        offset + relativeLeft,
                        offset + relativeRight,
                        text.substring(0, relativeLeft),
                        text.substring(relativeRight),
                        "extracted-fallback");
            }
        } catch (Throwable throwable) {
            logError("extracted text fallback unavailable", throwable);
        }
        return null;
    }

    private static int distanceToParagraphStart(String before) {
        for (int index = before.length() - 1; index >= 0; index--) {
            if (isLineBreak(before.charAt(index))) return before.length() - index - 1;
        }
        return before.length();
    }

    private static int distanceToParagraphEnd(String after) {
        for (int index = 0; index < after.length(); index++) {
            if (isLineBreak(after.charAt(index))) return index;
        }
        return after.length();
    }

    private static int clampIndex(int value, int length) {
        if (value < 0) return 0;
        return Math.min(value, length);
    }

    private static boolean isLineBreak(char value) {
        return value == '\n' || value == '\r' || value == '\u2028' || value == '\u2029';
    }

    private static final class EditorSnapshot {
        final int left;
        final int right;
        final String before;
        final String after;
        final String source;

        EditorSnapshot(int left, int right, String before, String after, String source) {
            this.left = Math.max(0, left);
            this.right = Math.max(this.left, right);
            this.before = before == null ? "" : before;
            this.after = after == null ? "" : after;
            this.source = source;
        }
    }

    private boolean performMenuAction(InputMethodService ime, InputConnection connection, int menuId) {
        if (menuId == 0) return false;
        try {
            if (connection.performContextMenuAction(menuId)) return true;
        } catch (Throwable ignored) {}

        try {
            Method method = findMethod(ime.getClass(), "performContextMenuAction", new Class<?>[]{int.class});
            if (method != null) {
                Object result = method.invoke(ime, menuId);
                if (!(result instanceof Boolean) || (Boolean) result) return true;
            }
        } catch (Throwable ignored) {}
        return fallbackMenuAction(ime, connection, menuId);
    }

    private static boolean fallbackMenuAction(InputMethodService ime, InputConnection connection, int menuId) {
        try {
            if (menuId == android.R.id.selectAll) {
                ExtractedText text = getFullText(connection);
                return text != null && text.text != null
                        && connection.setSelection(0, text.startOffset + text.text.length());
            }
            if (menuId == android.R.id.copy || menuId == android.R.id.cut) {
                CharSequence selected = connection.getSelectedText(0);
                if (selected == null || selected.length() == 0) return false;
                ClipboardManager clipboard = (ClipboardManager) ime.getSystemService(Context.CLIPBOARD_SERVICE);
                if (clipboard == null) return false;
                clipboard.setPrimaryClip(ClipData.newPlainText("text", selected));
                return menuId != android.R.id.cut || connection.commitText("", 1);
            }
            if (menuId == android.R.id.paste) {
                ClipboardManager clipboard = (ClipboardManager) ime.getSystemService(Context.CLIPBOARD_SERVICE);
                if (clipboard == null || !clipboard.hasPrimaryClip()
                        || clipboard.getPrimaryClip() == null
                        || clipboard.getPrimaryClip().getItemCount() == 0) return false;
                CharSequence text = clipboard.getPrimaryClip().getItemAt(0).coerceToText(ime);
                return text != null && connection.commitText(text, 1);
            }
        } catch (Throwable ignored) {}
        return false;
    }

    private static ExtractedText getFullText(InputConnection connection) {
        try {
            ExtractedTextRequest request = new ExtractedTextRequest();
            request.hintMaxChars = 1_000_000;
            request.hintMaxLines = 100_000;
            return connection.getExtractedText(request, 0);
        } catch (Throwable ignored) {
            return null;
        }
    }

    private static InputMethodService findIme(Context context) {
        Context current = context;
        for (int i = 0; i < 12 && current != null; i++) {
            if (current instanceof InputMethodService) return (InputMethodService) current;
            if (current instanceof ContextWrapper) {
                Context next = ((ContextWrapper) current).getBaseContext();
                if (next == current) break;
                current = next;
            } else break;
        }
        return null;
    }

    private static boolean isPassword(int inputType) {
        int inputClass = inputType & InputType.TYPE_MASK_CLASS;
        int variation = inputType & InputType.TYPE_MASK_VARIATION;
        if (inputClass == InputType.TYPE_CLASS_TEXT) {
            return variation == InputType.TYPE_TEXT_VARIATION_PASSWORD
                    || variation == InputType.TYPE_TEXT_VARIATION_VISIBLE_PASSWORD
                    || variation == InputType.TYPE_TEXT_VARIATION_WEB_PASSWORD;
        }
        return inputClass == InputType.TYPE_CLASS_NUMBER
                && variation == InputType.TYPE_NUMBER_VARIATION_PASSWORD;
    }

    private static int dp(View view, int value) {
        return Math.max(1, Math.round(value * view.getResources().getDisplayMetrics().density));
    }

    private void logInfo(String message) {
        try { log(Log.INFO, TAG, message); } catch (Throwable ignored) {}
    }

    private void logError(String message, Throwable throwable) {
        try {
            if (throwable == null) log(Log.ERROR, TAG, message);
            else log(Log.ERROR, TAG, message, throwable);
        } catch (Throwable ignored) {}
    }

    private static final class GestureTracker {
        private WeakReference<View> keyboardRef = new WeakReference<>(null);
        private float downX;
        private float downY;
        private float thresholdPx;
        private String key;
        private String displayKey;
        private int action;
        private boolean t9;
        private boolean triggered;
        private boolean active;

        void begin(View keyboard, float x, float y) {
            keyboardRef = new WeakReference<>(keyboard);
            downX = x;
            downY = y;
            thresholdPx = 1f;
            key = null;
            displayKey = null;
            action = Config.ACTION_NONE;
            t9 = false;
            triggered = false;
            active = true;
        }

        void setBinding(View keyboard, KeyInfo keyInfo, int newAction, float threshold) {
            if (!matches(keyboard)) return;
            key = keyInfo == null ? null : keyInfo.key;
            displayKey = keyInfo == null ? null : keyInfo.display;
            action = newAction;
            t9 = keyInfo != null && keyInfo.t9;
            thresholdPx = Math.max(1f, threshold);
        }

        void markTriggered(View keyboard) {
            if (matches(keyboard)) triggered = true;
        }

        void clear(View keyboard) {
            if (!matches(keyboard)) return;
            active = false;
            key = null;
            displayKey = null;
            action = Config.ACTION_NONE;
            t9 = false;
            triggered = false;
        }

        boolean matches(View keyboard) {
            return active && keyboardRef.get() == keyboard;
        }
    }
}
