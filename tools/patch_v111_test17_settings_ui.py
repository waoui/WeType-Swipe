from pathlib import Path
import runpy

runpy.run_path("tools/patch_v111_test16_hot_path_final.py", run_name="__main__")


def replace(path: str, old: str, new: str, count: int = 1) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    actual = text.count(old)
    if actual != count:
        raise RuntimeError(f"{path}: expected {count} matches, found {actual}")
    file.write_text(text.replace(old, new, count), encoding="utf-8")


config = "app/src/main/java/com/rww/wetypeswipe/Config.java"
replace(config,
        '    static final String KEY_VIBRATION = "vibration";\n'
        '    static final String KEY_HIDE_ICON = "hide_icon";',
        '    static final String KEY_VIBRATION = "vibration";\n'
        '    static final String KEY_SHOW_KEY_LABELS = "show_key_labels";\n'
        '    static final String KEY_SHOW_TRIGGER_HINT = "show_trigger_hint";\n'
        '    static final String KEY_HIDE_ICON = "hide_icon";')
replace(config,
        '    boolean vibration = true;\n    int revision = 0;',
        '    boolean vibration = true;\n'
        '    boolean showKeyLabels = true;\n'
        '    boolean showTriggerHint = true;\n'
        '    int revision = 0;')

activity = "app/src/main/java/com/rww/wetypeswipe/MainActivity.java"
replace(activity,
        '    private CheckBox vibration;\n    private CheckBox hideIcon;',
        '    private CheckBox showKeyLabels;\n'
        '    private CheckBox showTriggerHint;\n'
        '    private CheckBox vibration;\n'
        '    private CheckBox hideIcon;')

replace(activity,
'''        LinearLayout card = createCard("通用设置", null, false);

        vibration = new CheckBox(this);''',
'''        LinearLayout card = createCard("通用设置", null, false);

        showKeyLabels = new CheckBox(this);
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

        vibration = new CheckBox(this);''')

replace(activity,
        '                .putBoolean(Config.KEY_VIBRATION, vibration.isChecked())\n'
        '                .putBoolean(Config.KEY_HIDE_ICON, shouldHideIcon)',
        '                .putBoolean(Config.KEY_VIBRATION, vibration.isChecked())\n'
        '                .putBoolean(Config.KEY_SHOW_KEY_LABELS, showKeyLabels.isChecked())\n'
        '                .putBoolean(Config.KEY_SHOW_TRIGGER_HINT, showTriggerHint.isChecked())\n'
        '                .putBoolean(Config.KEY_HIDE_ICON, shouldHideIcon)')

replace(activity,
        '        changed.putExtra(Config.KEY_VIBRATION, vibration.isChecked());\n'
        '        changed.putExtra(Config.KEY_REVISION, revision);',
        '        changed.putExtra(Config.KEY_VIBRATION, vibration.isChecked());\n'
        '        changed.putExtra(Config.KEY_SHOW_KEY_LABELS, showKeyLabels.isChecked());\n'
        '        changed.putExtra(Config.KEY_SHOW_TRIGGER_HINT, showTriggerHint.isChecked());\n'
        '        changed.putExtra(Config.KEY_REVISION, revision);')

print("test17 settings UI and config keys applied")
