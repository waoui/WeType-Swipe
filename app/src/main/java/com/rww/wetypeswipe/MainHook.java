package com.rww.wetypeswipe;

import android.content.BroadcastReceiver;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.ContextWrapper;
import android.content.Intent;
import android.content.IntentFilter;
import android.database.Cursor;
import android.inputmethodservice.InputMethodService;
import android.net.Uri;
import android.os.Build;
import android.text.InputType;
import android.util.Log;
import android.view.HapticFeedbackConstants;
import android.view.MotionEvent;
import android.view.View;
import android.view.inputmethod.EditorInfo;
import android.view.inputmethod.ExtractedText;
import android.view.inputmethod.ExtractedTextRequest;
import android.view.inputmethod.InputConnection;

import java.lang.ref.WeakReference;
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
    private static final String MODULE = "com.rww.wetypeswipe";
    private static final String KEYBOARD_BASE = "com.tencent.wetype.plugin.hld.keyboard.selfdraw.n";
    private static final Uri CONFIG_URI = Uri.parse("content://com.rww.wetypeswipe.config/current");

    private final GestureTracker tracker = new GestureTracker();
    private final ConcurrentHashMap<String, Method> methodCache = new ConcurrentHashMap<>();

    private volatile WeakReference<InputMethodService> imeRef = new WeakReference<>(null);
    private volatile WeakReference<Context> contextRef = new WeakReference<>(null);
    private volatile Config cachedConfig = defaultConfig();
    private volatile Class<?> keyboardBaseClass;
    private volatile boolean hooksInstalled;
    private volatile boolean receiverRegistered;
    private volatile boolean configLoaded;
    private volatile boolean injectionReported;
    private BroadcastReceiver configReceiver;

    @Override public void onModuleLoaded(XposedModuleInterface.ModuleLoadedParam param) {
        logInfo("Modern API " + getApiVersion() + " loaded in " + param.getProcessName());
    }

    @Override public void onPackageReady(XposedModuleInterface.PackageReadyParam param) {
        if (!TARGET.equals(param.getPackageName())) return;
        try {
            installHooks();
            logInfo("v1.8 entered target package");
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

        hookAfter(InputMethodService.class.getDeclaredMethod("onCreate"),
                chain -> captureIme(chain.getThisObject()));
        hookBefore(InputMethodService.class.getDeclaredMethod("onStartInput", EditorInfo.class, boolean.class),
                chain -> captureIme(chain.getThisObject()));

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

    private void captureIme(Object object) {
        if (!(object instanceof InputMethodService)) return;
        InputMethodService ime = (InputMethodService) object;
        try {
            if (!TARGET.equals(ime.getPackageName())) return;
        } catch (Throwable ignored) {
            return;
        }

        imeRef = new WeakReference<>(ime);
        contextRef = new WeakReference<>((Context) ime);
        registerConfigReceiver(ime);
        if (!configLoaded) reloadConfigFromProvider(ime);

        if (!injectionReported) {
            injectionReported = true;
            reportAlways(ime, "模块已注入，等待键盘触摸", null, null, null);
        }
    }

    private synchronized void registerConfigReceiver(Context context) {
        if (receiverRegistered) return;
        configReceiver = new BroadcastReceiver() {
            @Override public void onReceive(Context receiverContext, Intent intent) {
                if (intent != null && Config.ACTION_CONFIG_CHANGED.equals(intent.getAction())) {
                    reloadConfigFromProvider(receiverContext);
                }
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

    private void reloadConfigFromProvider(Context context) {
        Cursor cursor = null;
        try {
            cursor = context.getContentResolver().query(CONFIG_URI, null, null, null, null);
            if (cursor == null || !cursor.moveToFirst()) throw new IllegalStateException("empty config cursor");

            Config config = new Config();
            config.selectAll = stringValue(cursor, Config.KEY_SELECT_ALL, "z");
            config.cut = stringValue(cursor, Config.KEY_CUT, "x");
            config.copy = stringValue(cursor, Config.KEY_COPY, "c");
            config.paste = stringValue(cursor, Config.KEY_PASTE, "v");
            config.disabledKeys = stringValue(cursor, Config.KEY_DISABLED_KEYS, "");
            config.thresholdDp = intValue(cursor, Config.KEY_THRESHOLD, 12);
            config.t9ThresholdDp = intValue(cursor, Config.KEY_T9_THRESHOLD, 20);
            for (int digit = 2; digit <= 9; digit++) {
                config.t9Actions[digit] = Config.validAction(
                        intValue(cursor, Config.t9PrefKey(digit), Config.ACTION_NONE));
            }
            config.vibration = intValue(cursor, Config.KEY_VIBRATION, 1) != 0;
            config.diagnostic = intValue(cursor, Config.KEY_DIAGNOSTIC, 0) != 0;
            if (config.thresholdDp < 6) config.thresholdDp = 6;
            if (config.thresholdDp > 40) config.thresholdDp = 40;
            if (config.t9ThresholdDp < 10) config.t9ThresholdDp = 10;
            if (config.t9ThresholdDp > 48) config.t9ThresholdDp = 48;
            config.rebuildActionMap();
            cachedConfig = config;
            configLoaded = true;
            reportDebug(context, "配置已刷新：震动=" + (config.vibration ? "开" : "关"), null, null, null);
        } catch (Throwable throwable) {
            logError("config provider unavailable, keeping current config", throwable);
            reportAlways(context, "配置读取失败，暂用当前配置", null, null, String.valueOf(throwable));
        } finally {
            if (cursor != null) cursor.close();
        }
    }

    private static String stringValue(Cursor cursor, String column, String fallback) {
        int index = cursor.getColumnIndex(column);
        if (index < 0 || cursor.isNull(index)) return fallback;
        String value = cursor.getString(index);
        return value == null ? fallback : value;
    }

    private static int intValue(Cursor cursor, String column, int fallback) {
        int index = cursor.getColumnIndex(column);
        return index < 0 || cursor.isNull(index) ? fallback : cursor.getInt(index);
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
            reportAlways(view.getContext(), "已命中微信输入法键盘触摸链路", null, null, null);
            logInfo("keyboard class cached: " + keyboardBase.getName());
        } else if (!keyboardBase.isInstance(view)) {
            return chain.proceed();
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
        if (!config.hasAnyBinding()) return chain.proceed();

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
            if (requestedAction == Config.ACTION_NONE) {
                tracker.clear(keyboard);
            } else {
                reportDebug(keyboard.getContext(),
                        keyInfo.t9 ? "已识别九宫格按键，等待下滑" : "已识别 26 键按键，等待下滑",
                        keyInfo.display, Config.actionName(requestedAction), null);
            }
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
                final String displayKey = tracker.displayKey;
                final Context context = keyboard.getContext();
                tracker.markTriggered(keyboard);

                proceedWithCancel(chain, event);

                Config latest = cachedConfig;
                if (latest.vibration) {
                    try { keyboard.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP); }
                    catch (Throwable ignored) {}
                }

                reportDebug(context, "已识别下滑手势", displayKey, Config.actionName(requestedAction), null);
                if (requestedAction != Config.ACTION_DISABLE) {
                    keyboard.post(() -> performAction(context, requestedAction, key));
                } else {
                    reportDebug(context, "指定按键下滑已禁用", displayKey, Config.actionName(requestedAction), null);
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
        return String.valueOf(value).trim().toLowerCase(Locale.ROOT)
                .replaceAll("[^a-z0-9]", "");
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
        String letters = value.replaceAll("[^a-z]", "");
        if (letters.equals("abc")) return "2";
        if (letters.equals("def")) return "3";
        if (letters.equals("ghi")) return "4";
        if (letters.equals("jkl")) return "5";
        if (letters.equals("mno")) return "6";
        if (letters.equals("pqrs")) return "7";
        if (letters.equals("tuv")) return "8";
        if (letters.equals("wxyz")) return "9";
        return null;
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

    private void performAction(Context context, int action, String key) {
        String actionName = Config.actionName(action);
        try {
            InputMethodService ime = imeRef.get();
            if (ime == null) ime = findIme(context);
            if (ime == null) {
                reportAlways(context, "动作失败：未取得输入法服务", key, actionName, null);
                return;
            }
            imeRef = new WeakReference<>(ime);

            EditorInfo editorInfo = ime.getCurrentInputEditorInfo();
            if (editorInfo != null && isPassword(editorInfo.inputType)) {
                reportAlways(context, "密码输入框已禁用快捷操作", key, actionName, null);
                return;
            }

            InputConnection connection = ime.getCurrentInputConnection();
            if (connection == null) {
                reportAlways(context, "动作失败：当前没有输入连接", key, actionName, null);
                return;
            }

            boolean success = performMenuAction(ime, connection, Config.menuIdFor(action));
            if (success) reportDebug(context, actionName + "执行成功", key, actionName, null);
            else reportAlways(context, actionName + "执行失败", key, actionName, "目标输入框不支持该动作");
        } catch (Throwable throwable) {
            logError("action failed", throwable);
            reportAlways(context, actionName + "执行异常", key, actionName, String.valueOf(throwable));
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

    private void reportDebug(Context context, String status, String key, String action, String error) {
        if (!cachedConfig.diagnostic) return;
        reportAlways(context, status, key, action, error);
    }

    private void reportAlways(Context context, String status, String key, String action, String error) {
        if (context == null) context = contextRef.get();
        if (context == null) return;
        try {
            Intent intent = new Intent(Config.ACTION_DIAGNOSTIC);
            intent.setPackage(MODULE);
            if (status != null) intent.putExtra(Config.DIAG_STATUS, status);
            if (key != null) intent.putExtra(Config.DIAG_LAST_KEY, key.toUpperCase(Locale.ROOT));
            if (action != null) intent.putExtra(Config.DIAG_LAST_ACTION, action);
            intent.putExtra(Config.DIAG_LAST_ERROR, error == null ? "" : error);
            context.sendBroadcast(intent);
        } catch (Throwable throwable) {
            logError("diagnostic broadcast failed", throwable);
        }
    }

    private static int dp(View view, int value) {
        return Math.max(1, Math.round(value * view.getResources().getDisplayMetrics().density));
    }

    private void logInfo(String message) {
        try { log(Log.INFO, TAG, message); } catch (Throwable ignored) {}
    }

    private void logError(String message, Throwable throwable) {
        try { log(Log.ERROR, TAG, message, throwable); } catch (Throwable ignored) {}
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
