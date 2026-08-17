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
    'logInfo("v1.11.6-test1 entered target package; embedded settings entry enabled");',
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
        hookAfter(View.class.getDeclaredMethod("onAttachedToWindow"),
                chain -> captureAttachedView(chain.getThisObject()));

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
        scheduleEmbeddedSettingsEntry(activity, 120L);
        scheduleEmbeddedSettingsEntry(activity, 520L);
    }

    private void captureAttachedView(Object object) {
        if (!(object instanceof TextView)) return;
        TextView textView = (TextView) object;
        CharSequence value;
        try { value = textView.getText(); }
        catch (Throwable ignored) { return; }
        if (!EmbeddedSettingsUi.isAboutMarkerText(value)) return;
        Activity activity = findActivity(textView.getContext());
        if (activity == null) return;
        try {
            if (!TARGET.equals(activity.getPackageName())) return;
        } catch (Throwable ignored) {
            return;
        }
        scheduleEmbeddedSettingsEntry(activity, 80L);
    }

    private static Activity findActivity(Context context) {
        Context current = context;
        for (int depth = 0; current != null && depth < 12; depth++) {
            if (current instanceof Activity) return (Activity) current;
            if (!(current instanceof ContextWrapper)) return null;
            Context base = ((ContextWrapper) current).getBaseContext();
            if (base == current) return null;
            current = base;
        }
        return null;
    }

    private void scheduleEmbeddedSettingsEntry(Activity activity, long delayMs) {
        try {
            View decor = activity.getWindow() == null ? null : activity.getWindow().getDecorView();
            if (decor == null) return;
            decor.postDelayed(() -> {
                try {
                    EmbeddedSettingsUi.ensureAboutEntry(
                            activity,
                            () -> ConfigSnapshot.copyOf(cachedConfig),
                            config -> applyEmbeddedConfig(activity, config));
                } catch (Throwable throwable) {
                    logError("embedded settings entry failed", throwable);
                }
            }, delayMs);
        } catch (Throwable throwable) {
            logError("embedded settings scheduling failed", throwable);
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

main_activity = ROOT / "app/src/main/java/com/rww/wetypeswipe/MainActivity.java"
replace_once(
    main_activity,
    'v1.11.5 · 新增全文导航与跨行选择',
    'v1.11.6-test1 · 新增内置模块设置入口',
)

gradle_properties = ROOT / "gradle.properties"
properties = gradle_properties.read_text(encoding="utf-8")
properties, code_count = re.subn(r"(?m)^VERSION_CODE=.*$", "VERSION_CODE=45", properties, count=1)
properties, name_count = re.subn(r"(?m)^VERSION_NAME=.*$", "VERSION_NAME=1.11.6-test1", properties, count=1)
if code_count != 1 or name_count != 1:
    raise SystemExit("Could not update VERSION_CODE/VERSION_NAME")
gradle_properties.write_text(properties, encoding="utf-8")

print("Applied v1.11.6-test1 embedded settings patch")
