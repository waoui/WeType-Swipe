#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


main_hook = ROOT / "app/src/main/java/com/rww/wetypeswipe/MainHook.java"

replace_once(
    main_hook,
    "import android.app.Application;\n",
    "import android.app.Activity;\nimport android.app.Application;\n",
)

replace_once(
    main_hook,
    'logInfo("v1.11.5 entered target package; document navigation actions enabled");',
    'logInfo("v1.11.6-test2 entered target package; about icon multi-tap settings enabled");',
)

replace_once(
    main_hook,
    '''    private Runnable keyboardHintHideTask;
    private BroadcastReceiver configReceiver;
''',
    '''    private Runnable keyboardHintHideTask;
    private final AboutIconUnlock aboutIconUnlock = new AboutIconUnlock();
    private volatile WeakReference<Activity> aboutActivityRef = new WeakReference<>(null);
    private BroadcastReceiver configReceiver;
''',
)

replace_once(
    main_hook,
    '''        hookAfter(Application.class.getDeclaredMethod("onCreate"),
                chain -> captureApplication(chain.getThisObject()));

        hookAfter(InputMethodService.class.getDeclaredMethod("onCreate"),
''',
    '''        hookAfter(Application.class.getDeclaredMethod("onCreate"),
                chain -> captureApplication(chain.getThisObject()));

        hookAfter(Activity.class.getDeclaredMethod("onResume"),
                chain -> captureSettingsActivity(chain.getThisObject()));
        hookBefore(Activity.class.getDeclaredMethod("dispatchTouchEvent", MotionEvent.class),
                chain -> captureSettingsTouch(chain.getThisObject(), (MotionEvent) chain.getArg(0)));

        hookAfter(InputMethodService.class.getDeclaredMethod("onCreate"),
''',
)

replace_once(
    main_hook,
    '''    private void captureIme(Object object) {
''',
    '''    private void captureSettingsActivity(Object object) {
        if (!(object instanceof Activity)) return;
        Activity activity = (Activity) object;
        try {
            if (!TARGET.equals(activity.getPackageName())) return;
        } catch (Throwable ignored) {
            return;
        }
        ensureConfigSync(activity);
        try {
            if (isAboutSettingsActivity(activity)) {
                aboutActivityRef = new WeakReference<>(activity);
                logInfo("about page detected; tap app icon 7 times to open embedded settings");
            } else if (aboutActivityRef.get() == activity) {
                aboutActivityRef = new WeakReference<>(null);
                aboutIconUnlock.reset();
            }
        } catch (Throwable throwable) {
            logError("about activity detection failed", throwable);
        }
    }

    private void captureSettingsTouch(Object object, MotionEvent event) {
        if (!(object instanceof Activity) || event == null || event.getActionMasked() != MotionEvent.ACTION_UP) return;
        Activity activity = (Activity) object;
        try {
            if (!TARGET.equals(activity.getPackageName())) return;
            Activity cached = aboutActivityRef.get();
            if (cached != activity) {
                if (!isAboutSettingsActivity(activity)) {
                    aboutIconUnlock.reset();
                    return;
                }
                aboutActivityRef = new WeakReference<>(activity);
            }
            if (!isAboutIconTap(activity, event)) {
                aboutIconUnlock.reset();
                return;
            }
            if (!aboutIconUnlock.registerTap(SystemClock.elapsedRealtime())) return;

            View decor = activity.getWindow() == null ? null : activity.getWindow().getDecorView();
            Runnable open = () -> {
                try {
                    if (activity.isFinishing()) return;
                    EmbeddedSettingsUi.show(
                            activity,
                            () -> ConfigSnapshot.copyOf(cachedConfig),
                            config -> applyEmbeddedConfig(activity, config));
                    logInfo("embedded settings opened by about icon seven-tap");
                } catch (Throwable throwable) {
                    logError("embedded settings open failed", throwable);
                }
            };
            if (decor != null) decor.post(open); else open.run();
        } catch (Throwable throwable) {
            logError("about icon multi-tap failed", throwable);
        }
    }

    private static boolean isAboutSettingsActivity(Activity activity) {
        if (activity == null || activity.isFinishing()) return false;
        String className = activity.getClass().getName().toLowerCase(Locale.ROOT);
        View root;
        try {
            root = activity.getWindow() == null ? null : activity.getWindow().getDecorView();
        } catch (Throwable ignored) {
            root = null;
        }
        String pageText = collectPageText(root).replace(" ", "");
        String lowerText = pageText.toLowerCase(Locale.ROOT);
        boolean explicit = pageText.contains("关于微信输入法") || lowerText.contains("aboutwetype");
        boolean hasAbout = pageText.contains("关于") || className.contains("about");
        boolean hasWeType = pageText.contains("微信输入法") || lowerText.contains("wetype");
        boolean hasMeta = pageText.contains("版本") || pageText.contains("隐私")
                || pageText.contains("用户协议") || lowerText.contains("version")
                || lowerText.contains("privacy");
        return explicit || (hasAbout && hasWeType && hasMeta) || (className.contains("about") && hasWeType);
    }

    private static String collectPageText(View view) {
        if (view == null) return "";
        StringBuilder text = new StringBuilder();
        collectPageText(view, text, 0);
        return text.toString();
    }

    private static void collectPageText(View view, StringBuilder out, int depth) {
        if (view == null || out.length() > 12_000 || depth > 40) return;
        if (view instanceof TextView) {
            CharSequence value;
            try { value = ((TextView) view).getText(); }
            catch (Throwable ignored) { value = null; }
            if (value != null && value.length() > 0) out.append(' ').append(value);
        }
        if (!(view instanceof ViewGroup)) return;
        ViewGroup group = (ViewGroup) view;
        int count;
        try { count = group.getChildCount(); }
        catch (Throwable ignored) { return; }
        for (int i = 0; i < count; i++) {
            collectPageText(group.getChildAt(i), out, depth + 1);
        }
    }

    private static boolean isAboutIconTap(Activity activity, MotionEvent event) {
        View root = activity.getWindow() == null ? null : activity.getWindow().getDecorView();
        if (root == null || root.getWidth() <= 0 || root.getHeight() <= 0) return false;
        float x = event.getX();
        float y = event.getY();

        Rect candidate = new Rect();
        int[] bestScore = {Integer.MIN_VALUE};
        findAboutIconCandidate(root, root.getWidth(), root.getHeight(), candidate, bestScore, 0);
        if (bestScore[0] > Integer.MIN_VALUE && candidate.contains(Math.round(x), Math.round(y))) return true;

        int width = root.getWidth();
        int height = root.getHeight();
        Rect fallback = new Rect(width * 15 / 100, height * 7 / 100,
                width * 85 / 100, height * 55 / 100);
        return fallback.contains(Math.round(x), Math.round(y));
    }

    private static void findAboutIconCandidate(View view, int rootWidth, int rootHeight,
                                                Rect bestRect, int[] bestScore, int depth) {
        if (view == null || depth > 40) return;
        try {
            if (view.getVisibility() == View.VISIBLE && view.getAlpha() > 0.01f
                    && view instanceof android.widget.ImageView
                    && view.getWidth() > 0 && view.getHeight() > 0) {
                int[] location = new int[2];
                view.getLocationInWindow(location);
                Rect rect = new Rect(location[0], location[1],
                        location[0] + view.getWidth(), location[1] + view.getHeight());
                int centerX = rect.centerX();
                int centerY = rect.centerY();
                int minSide = Math.min(rect.width(), rect.height());
                int maxSide = Math.max(rect.width(), rect.height());
                int score = 0;
                if (centerX > rootWidth * 20 / 100 && centerX < rootWidth * 80 / 100) score += 300;
                if (centerY > rootHeight * 5 / 100 && centerY < rootHeight * 60 / 100) score += 220;
                if (minSide > 0 && maxSide <= minSide * 3 / 2) score += 180;
                if (minSide >= Math.max(32, rootWidth / 16) && maxSide <= rootWidth * 55 / 100) score += 160;
                CharSequence description = view.getContentDescription();
                String hint = description == null ? "" : description.toString().toLowerCase(Locale.ROOT);
                try {
                    if (view.getId() != View.NO_ID) {
                        hint += " " + view.getResources().getResourceEntryName(view.getId()).toLowerCase(Locale.ROOT);
                    }
                } catch (Throwable ignored) {}
                if (hint.contains("logo") || hint.contains("icon") || hint.contains("wetype")
                        || hint.contains("微信输入法")) score += 500;
                score += Math.min(120, minSide / 2);
                if (score > bestScore[0]) {
                    bestScore[0] = score;
                    bestRect.set(rect);
                }
            }
        } catch (Throwable ignored) {}

        if (!(view instanceof ViewGroup)) return;
        ViewGroup group = (ViewGroup) view;
        int count;
        try { count = group.getChildCount(); }
        catch (Throwable ignored) { return; }
        for (int i = 0; i < count; i++) {
            findAboutIconCandidate(group.getChildAt(i), rootWidth, rootHeight,
                    bestRect, bestScore, depth + 1);
        }
    }

    private synchronized void applyEmbeddedConfig(Context context, Config config) {
        if (context == null || config == null) return;
        try {
            Config current = cachedConfig;
            int currentRevision = current == null ? 0 : current.revision;
            config.revision = Math.max(config.revision, currentRevision) + 1;
            config.rebuildActionMap();
            cachedConfig = config;
            nativeSingleKeyLabelCache.clear();
            targetCacheLoaded = true;

            Context stable = context.getApplicationContext();
            if (stable == null) stable = context;
            persistTargetCache(stable, config);

            Intent changed = new Intent(Config.ACTION_CONFIG_CHANGED);
            changed.setPackage(TARGET);
            ConfigSnapshot.putInto(changed, config);
            stable.sendBroadcast(changed);
            logInfo("embedded settings saved revision=" + config.revision);
        } catch (Throwable throwable) {
            logError("embedded settings save failed", throwable);
        }
    }

    private void captureIme(Object object) {
''',
)

embedded_ui = ROOT / "app/src/main/java/com/rww/wetypeswipe/EmbeddedSettingsUi.java"
replace_once(
    embedded_ui,
    "    private static void show(Activity activity, ConfigProvider provider, ConfigSaver saver) {",
    "    static void show(Activity activity, ConfigProvider provider, ConfigSaver saver) {",
)
replace_once(
    embedded_ui,
    "内置模块模式 · v1.11.6-test1",
    "内置模块模式 · v1.11.6-test2",
)

main_activity = ROOT / "app/src/main/java/com/rww/wetypeswipe/MainActivity.java"
replace_once(
    main_activity,
    'v1.11.5 · 新增全文导航与跨行选择',
    'v1.11.6-test2 · 关于页图标七击设置',
)

gradle_properties = ROOT / "gradle.properties"
properties = gradle_properties.read_text(encoding="utf-8")
properties, code_count = re.subn(r"(?m)^VERSION_CODE=.*$", "VERSION_CODE=46", properties, count=1)
properties, name_count = re.subn(r"(?m)^VERSION_NAME=.*$", "VERSION_NAME=1.11.6-test2", properties, count=1)
if code_count != 1 or name_count != 1:
    raise SystemExit("Could not update VERSION_CODE/VERSION_NAME")
gradle_properties.write_text(properties, encoding="utf-8")

print("Applied v1.11.6-test2 about icon seven-tap settings patch")
