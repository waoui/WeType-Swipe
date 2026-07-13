from pathlib import Path
import re
import runpy

runpy.run_path("tools/patch_v111_test16_hot_path_final.py", run_name="__main__")


def sub_required(text: str, pattern: str, replacement: str, name: str, flags: int = 0) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=flags)
    if count != 1:
        raise RuntimeError(f"{name}: {count}")
    return updated


# Config keys and runtime flags.
config_path = Path("app/src/main/java/com/rww/wetypeswipe/Config.java")
config = config_path.read_text(encoding="utf-8")
config = sub_required(
    config,
    r'(static final String KEY_VIBRATION = "vibration";\n)',
    r'\1    static final String KEY_SHOW_KEY_LABELS = "show_key_labels";\n'
    r'    static final String KEY_SHOW_TRIGGER_HINT = "show_trigger_hint";\n',
    "config keys")
config = sub_required(
    config,
    r'(boolean vibration = true;\n)',
    r'\1    boolean showKeyLabels = true;\n    boolean showTriggerHint = true;\n',
    "config flags")
config_path.write_text(config, encoding="utf-8")

# Settings UI and save/broadcast values.
activity_path = Path("app/src/main/java/com/rww/wetypeswipe/MainActivity.java")
activity = activity_path.read_text(encoding="utf-8")
activity = sub_required(
    activity,
    r'(private CheckBox vibration;\n)',
    r'private CheckBox showKeyLabels;\n    private CheckBox showTriggerHint;\n    \1',
    "activity fields")

ui = '''        showKeyLabels = new CheckBox(this);
        showKeyLabels.setText("显示按键底部功能文字");
        showKeyLabels.setTextSize(15);
        showKeyLabels.setTextColor(COLOR_TEXT);
        showKeyLabels.setPadding(dp(12), dp(6), dp(12), dp(6));
        showKeyLabels.setChecked(prefs.getBoolean(Config.KEY_SHOW_KEY_LABELS, true));
        card.addView(showKeyLabels, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(54)));
        card.addView(divider());

        showTriggerHint = new CheckBox(this);
        showTriggerHint.setText("显示下滑触发提示");
        showTriggerHint.setTextSize(15);
        showTriggerHint.setTextColor(COLOR_TEXT);
        showTriggerHint.setPadding(dp(12), dp(6), dp(12), dp(6));
        showTriggerHint.setChecked(prefs.getBoolean(Config.KEY_SHOW_TRIGGER_HINT, true));
        card.addView(showTriggerHint, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(54)));

        TextView displayNote = text("关闭后只隐藏提示，不影响下滑功能。", 12, COLOR_SECONDARY);
        displayNote.setPadding(dp(18), 0, dp(18), dp(12));
        card.addView(displayNote);
        card.addView(divider());

'''
activity = sub_required(
    activity,
    r'(private View buildGeneralCard\(\) \{\n\s*LinearLayout card = createCard\("通用设置", null, false\);\n\n)',
    r'\1' + ui,
    "general settings UI")
activity = sub_required(
    activity,
    r'(\.putBoolean\(Config\.KEY_VIBRATION, vibration\.isChecked\(\)\)\n)',
    r'\1                .putBoolean(Config.KEY_SHOW_KEY_LABELS, showKeyLabels.isChecked())\n'
    r'                .putBoolean(Config.KEY_SHOW_TRIGGER_HINT, showTriggerHint.isChecked())\n',
    "save display prefs")
activity = sub_required(
    activity,
    r'(changed\.putExtra\(Config\.KEY_VIBRATION, vibration\.isChecked\(\)\);\n)',
    r'\1        changed.putExtra(Config.KEY_SHOW_KEY_LABELS, showKeyLabels.isChecked());\n'
    r'        changed.putExtra(Config.KEY_SHOW_TRIGGER_HINT, showTriggerHint.isChecked());\n',
    "broadcast display prefs")
activity = sub_required(
    activity,
    r'v1\.11\.0-test16 · 原生绘制热路径优化',
    'v1.11.0-test17 · 显示选项开关',
    "activity version")
activity_path.write_text(activity, encoding="utf-8")

# Target-process configuration and rendering gates.
hook_path = Path("app/src/main/java/com/rww/wetypeswipe/MainHook.java")
hook = hook_path.read_text(encoding="utf-8")
hook = sub_required(
    hook,
    r'(config\.vibration = intent\.getBooleanExtra\(Config\.KEY_VIBRATION, true\);\n)',
    r'\1            config.showKeyLabels = intent.getBooleanExtra(Config.KEY_SHOW_KEY_LABELS, true);\n'
    r'            config.showTriggerHint = intent.getBooleanExtra(Config.KEY_SHOW_TRIGGER_HINT, true);\n',
    "intent flags")
hook = sub_required(
    hook,
    r'(\.putBoolean\(Config\.KEY_VIBRATION, config\.vibration\)\n)',
    r'\1                    .putBoolean(Config.KEY_SHOW_KEY_LABELS, config.showKeyLabels)\n'
    r'                    .putBoolean(Config.KEY_SHOW_TRIGGER_HINT, config.showTriggerHint)\n',
    "cache persist flags")
hook = sub_required(
    hook,
    r'(config\.vibration = prefs\.getBoolean\(Config\.KEY_VIBRATION, true\);\n)',
    r'\1            config.showKeyLabels = prefs.getBoolean(Config.KEY_SHOW_KEY_LABELS, true);\n'
    r'            config.showTriggerHint = prefs.getBoolean(Config.KEY_SHOW_TRIGGER_HINT, true);\n',
    "cache load flags")
hook = sub_required(
    hook,
    r'if \(config == null \|\| !config\.hasAnyBinding\(\)\) return;',
    'if (config == null || !config.hasAnyBinding() || !config.showKeyLabels) return;',
    "outer render gate")
hook = sub_required(
    hook,
    r'(if \(currentEditorPassword\) return;\n)',
    r'\1        Config displayConfig = cachedConfig;\n'
    r'        if (displayConfig == null || !displayConfig.showKeyLabels) return;\n',
    "native render gate")
hook = sub_required(
    hook,
    r'(private void showKeyboardHint\(View keyboard, String keyLabel, int action, boolean executed\) \{\n)',
    r'\1        Config displayConfig = cachedConfig;\n'
    r'        if (displayConfig == null || !displayConfig.showTriggerHint) {\n'
    r'            hideKeyboardHint(0L);\n'
    r'            return;\n'
    r'        }\n',
    "hint gate")
hook = sub_required(
    hook,
    r'v1\.11\.0-test16 entered target package',
    'v1.11.0-test17 entered target package',
    "hook version")
hook_path.write_text(hook, encoding="utf-8")

build_path = Path("app/build.gradle.kts")
build = build_path.read_text(encoding="utf-8")
build = re.sub(r'versionCode\s*=\s*\d+', 'versionCode = 38', build, count=1)
build = re.sub(r'versionName\s*=\s*"[^"]+"', 'versionName = "1.11.0-test17"', build, count=1)
build_path.write_text(build, encoding="utf-8")

print("v1.11.0-test17 robust display toggles applied")
