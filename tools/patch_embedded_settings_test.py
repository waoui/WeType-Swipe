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
    'logInfo("v1.11.6-test3 entered target package; verified view-touch settings unlock enabled");',
)

replace_once(
    main_hook,
    '''    private Runnable keyboardHintHideTask;
    private BroadcastReceiver configReceiver;
''',
    '''    private Runnable keyboardHintHideTask;
    private final AboutIconUnlock aboutIconUnlock = new AboutIconUnlock();
    private BroadcastReceiver configReceiver;
''',
)

replace_once(
    main_hook,
    '''    private void captureIme(Object object) {
''',
    '''    private static Activity findActivity(Context context) {
        Context current = context;
        for (int depth = 0; current != null && depth < 16; depth++) {
            if (current instanceof Activity) return (Activity) current;
            if (!(current instanceof ContextWrapper)) return null;
            Context base = ((ContextWrapper) current).getBaseContext();
            if (base == current) return null;
            current = base;
        }
        return null;
    }

    private void tryHandleEmbeddedSettingsUnlock(View source, MotionEvent event) {
        if (source == null || event == null || event.getActionMasked() != MotionEvent.ACTION_UP) return;
        Activity activity = findActivity(source.getContext());
        if (activity == null || activity.isFinishing()) return;
        try {
            if (!TARGET.equals(activity.getPackageName())) return;
            View decor = activity.getWindow() == null ? null : activity.getWindow().getDecorView();
            if (decor == null || decor.getWidth() <= 0 || decor.getHeight() <= 0) return;

            int[] location = new int[2];
            decor.getLocationOnScreen(location);
            float x = event.getRawX() - location[0];
            float y = event.getRawY() - location[1];
            int width = decor.getWidth();
            int height = decor.getHeight();

            // The About logo lives in the upper part of the page. Do not depend on TextView,
            // resource id, Activity name or Compose/native implementation details.
            boolean triggerZone = x >= width * 0.10f && x <= width * 0.90f
                    && y >= height * 0.04f && y <= height * 0.62f;
            if (!triggerZone) {
                aboutIconUnlock.reset();
                return;
            }

            float tolerance = Math.max(dp(source, 48), Math.min(width, height) * 0.12f);
            int before = aboutIconUnlock.tapCount();
            boolean unlocked = aboutIconUnlock.registerTap(
                    SystemClock.elapsedRealtime(), event.getEventTime(), x, y, tolerance);
            int after = aboutIconUnlock.tapCount();
            if (after != before && (after == 1 || after == 6)) {
                logInfo("embedded settings tap progress=" + after + "/7 activity="
                        + activity.getClass().getName());
            }
            if (!unlocked) return;

            decor.post(() -> {
                try {
                    if (activity.isFinishing()) return;
                    EmbeddedSettingsUi.show(
                            activity,
                            () -> ConfigSnapshot.copyOf(cachedConfig),
                            config -> applyEmbeddedConfig(activity, config));
                    logInfo("embedded settings opened by verified global view-touch seven-tap");
                } catch (Throwable throwable) {
                    logError("embedded settings open failed", throwable);
                }
            });
        } catch (Throwable throwable) {
            logError("embedded settings seven-tap failed", throwable);
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

replace_once(
    main_hook,
    '''        View view = (View) target;
        MotionEvent event = (MotionEvent) eventObject;
        Class<?> keyboardBase = keyboardBaseClass;
''',
    '''        View view = (View) target;
        MotionEvent event = (MotionEvent) eventObject;

        // This View.dispatchTouchEvent hook is the same proven chain used by the keyboard
        // gesture feature. Run the hidden settings detector before filtering to keyboard views.
        tryHandleEmbeddedSettingsUnlock(view, event);

        Class<?> keyboardBase = keyboardBaseClass;
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
    "内置模块模式 · v1.11.6-test3",
)

main_activity = ROOT / "app/src/main/java/com/rww/wetypeswipe/MainActivity.java"
replace_once(
    main_activity,
    'v1.11.5 · 新增全文导航与跨行选择',
    'v1.11.6-test3 · 关于图标七击内置设置',
)

gradle_properties = ROOT / "gradle.properties"
properties = gradle_properties.read_text(encoding="utf-8")
properties, code_count = re.subn(r"(?m)^VERSION_CODE=.*$", "VERSION_CODE=47", properties, count=1)
properties, name_count = re.subn(r"(?m)^VERSION_NAME=.*$", "VERSION_NAME=1.11.6-test3", properties, count=1)
if code_count != 1 or name_count != 1:
    raise SystemExit("Could not update VERSION_CODE/VERSION_NAME")
gradle_properties.write_text(properties, encoding="utf-8")

print("Applied v1.11.6-test3 verified global view-touch seven-tap settings patch")
