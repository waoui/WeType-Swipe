from pathlib import Path
import runpy

runpy.run_path("tools/patch_v111_test17_settings_ui.py", run_name="__main__")

path = Path("app/src/main/java/com/rww/wetypeswipe/MainHook.java")
text = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str, name: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{name}: expected 1 match, found {count}")
    text = text.replace(old, new, 1)


replace_once(
    '            config.vibration = intent.getBooleanExtra(Config.KEY_VIBRATION, true);\n'
    '            config.revision = intent.getIntExtra(Config.KEY_REVISION, 0);',
    '            config.vibration = intent.getBooleanExtra(Config.KEY_VIBRATION, true);\n'
    '            config.showKeyLabels = intent.getBooleanExtra(Config.KEY_SHOW_KEY_LABELS, true);\n'
    '            config.showTriggerHint = intent.getBooleanExtra(Config.KEY_SHOW_TRIGGER_HINT, true);\n'
    '            config.revision = intent.getIntExtra(Config.KEY_REVISION, 0);',
    "intent display flags")

replace_once(
    '                    .putBoolean(Config.KEY_VIBRATION, config.vibration)\n'
    '                    .putInt(Config.KEY_REVISION, config.revision);',
    '                    .putBoolean(Config.KEY_VIBRATION, config.vibration)\n'
    '                    .putBoolean(Config.KEY_SHOW_KEY_LABELS, config.showKeyLabels)\n'
    '                    .putBoolean(Config.KEY_SHOW_TRIGGER_HINT, config.showTriggerHint)\n'
    '                    .putInt(Config.KEY_REVISION, config.revision);',
    "target cache display flags")

replace_once(
    '            config.vibration = prefs.getBoolean(Config.KEY_VIBRATION, true);\n'
    '            config.revision = prefs.getInt(Config.KEY_REVISION, 0);',
    '            config.vibration = prefs.getBoolean(Config.KEY_VIBRATION, true);\n'
    '            config.showKeyLabels = prefs.getBoolean(Config.KEY_SHOW_KEY_LABELS, true);\n'
    '            config.showTriggerHint = prefs.getBoolean(Config.KEY_SHOW_TRIGGER_HINT, true);\n'
    '            config.revision = prefs.getInt(Config.KEY_REVISION, 0);',
    "cache display flags")

replace_once(
'''        Config config = cachedConfig;
        if (config == null || !config.hasAnyBinding()) return;
        try {''',
'''        Config config = cachedConfig;
        if (config == null || !config.hasAnyBinding() || !config.showKeyLabels) return;
        try {''',
    "outer label visibility")

replace_once(
'''        if (currentEditorPassword) return;
        String label = nativeSingleKeyLabelCache.get(model);''',
'''        if (currentEditorPassword) return;
        Config displayConfig = cachedConfig;
        if (displayConfig == null || !displayConfig.showKeyLabels) return;
        String label = nativeSingleKeyLabelCache.get(model);''',
    "native label visibility")

replace_once(
'''    private void showKeyboardHint(View keyboard, String keyLabel, int action, boolean executed) {
        if (keyboard == null || action == Config.ACTION_NONE) {''',
'''    private void showKeyboardHint(View keyboard, String keyLabel, int action, boolean executed) {
        Config config = cachedConfig;
        if (config == null || !config.showTriggerHint) {
            hideKeyboardHint(0L);
            return;
        }
        if (keyboard == null || action == Config.ACTION_NONE) {''',
    "trigger hint visibility")

# Both config assignment paths already clear the model-label cache in test16.
assignment = '''cachedConfig = config;
                        nativeSingleKeyLabelCache.clear();'''
replacement = '''cachedConfig = config;
                        nativeSingleKeyLabelCache.clear();
                        View activeKeyboard = nativeSingleKeyActiveKeyboardRef.get();
                        if (activeKeyboard != null) activeKeyboard.postInvalidate();
                        if (!config.showTriggerHint) hideKeyboardHint(0L);'''
count = text.count(assignment)
if count != 1:
    raise RuntimeError(f"receiver assignment: expected 1 match, found {count}")
text = text.replace(assignment, replacement, 1)

assignment = '''cachedConfig = config;
            nativeSingleKeyLabelCache.clear();
            targetCacheLoaded = true;'''
replacement = '''cachedConfig = config;
            nativeSingleKeyLabelCache.clear();
            View activeKeyboard = nativeSingleKeyActiveKeyboardRef.get();
            if (activeKeyboard != null) activeKeyboard.postInvalidate();
            if (!config.showTriggerHint) hideKeyboardHint(0L);
            targetCacheLoaded = true;'''
count = text.count(assignment)
if count != 1:
    raise RuntimeError(f"cache assignment: expected 1 match, found {count}")
text = text.replace(assignment, replacement, 1)

replace_once(
    '            logInfo("v1.11.0-test16 entered target package");',
    '            logInfo("v1.11.0-test17 entered target package");',
    "version log")

path.write_text(text, encoding="utf-8")
print("test17 display visibility logic applied")
