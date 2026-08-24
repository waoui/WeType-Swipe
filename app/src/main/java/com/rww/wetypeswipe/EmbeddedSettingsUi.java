package com.rww.wetypeswipe;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.Dialog;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.text.InputFilter;
import android.text.InputType;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.Window;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.SeekBar;
import android.widget.TextView;
import android.widget.Toast;


final class EmbeddedSettingsUi {
    private static final int PAGE = Color.rgb(245, 247, 250);
    private static final int CARD = Color.WHITE;
    private static final int TEXT = Color.rgb(32, 36, 43);
    private static final int SECONDARY = Color.rgb(101, 109, 122);
    private static final int DIVIDER = Color.rgb(232, 235, 240);
    private static final int ACCENT = Color.rgb(36, 103, 214);
    private static final int ACCENT_SOFT = Color.rgb(232, 240, 254);
    private static final int KEY_IDLE = Color.rgb(247, 249, 252);
    private static final int KEY_STROKE = Color.rgb(218, 223, 232);
    private static final int DANGER = Color.rgb(190, 55, 55);
    private static final int DANGER_SOFT = Color.rgb(255, 237, 237);
    private static final String[] T9_LETTERS = {
            "", "", "ABC", "DEF", "GHI", "JKL", "MNO", "PQRS", "TUV", "WXYZ"
    };

    interface ConfigProvider { Config get(); }
    interface ConfigSaver { void save(Config config); }

    private final Activity activity;
    private final Config config;
    private final ConfigSaver saver;
    private final TextView[] qwertyActionViews = new TextView[26];
    private final LinearLayout[] qwertyKeyViews = new LinearLayout[26];
    private final TextView[] t9ActionViews = new TextView[10];
    private final LinearLayout[] t9KeyViews = new LinearLayout[10];
    private SeekBar qwertyThreshold;
    private SeekBar t9Threshold;
    private TextView qwertyThresholdValue;
    private TextView t9ThresholdValue;
    private CheckBox showLabels;
    private CheckBox showHint;
    private CheckBox vibration;
    private Dialog dialog;

    private EmbeddedSettingsUi(Activity activity, Config config, ConfigSaver saver) {
        this.activity = activity;
        this.config = ConfigSnapshot.copyOf(config);
        this.saver = saver;
    }

    static void show(Activity activity, ConfigProvider provider, ConfigSaver saver) {
        Config source = provider == null ? null : provider.get();
        new EmbeddedSettingsUi(activity, source, saver).showDialog();
    }

    private void showDialog() {
        dialog = new Dialog(activity, android.R.style.Theme_Material_Light_NoActionBar);
        dialog.setContentView(buildPage());
        dialog.setOnShowListener(ignored -> {
            Window window = dialog.getWindow();
            if (window != null) {
                window.setLayout(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT);
                window.setStatusBarColor(Color.WHITE);
                window.setNavigationBarColor(Color.WHITE);
            }
        });
        dialog.show();
        Window window = dialog.getWindow();
        if (window != null) window.setLayout(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT);
    }

    private View buildPage() {
        LinearLayout page = vertical();
        page.setBackgroundColor(PAGE);
        page.addView(buildHeader(), new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        ScrollView scroll = new ScrollView(activity);
        scroll.setFillViewport(true);
        LinearLayout content = vertical();
        content.setPadding(dp(activity, 12), dp(activity, 12), dp(activity, 12), dp(activity, 22));
        content.addView(buildQwertyCard());
        content.addView(buildT9Card());
        content.addView(buildGestureCard());
        content.addView(buildGeneralCard());
        scroll.addView(content);
        page.addView(scroll, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f));
        page.addView(buildSaveBar());
        return page;
    }

    private View buildHeader() {
        LinearLayout header = horizontal();
        header.setGravity(Gravity.CENTER_VERTICAL);
        header.setPadding(dp(activity, 18), dp(activity, 14), dp(activity, 12), dp(activity, 14));
        header.setBackgroundColor(Color.WHITE);

        LinearLayout labels = vertical();
        TextView title = text(activity, "微信输入法下滑快捷键", 21, TEXT);
        title.setTypeface(Typeface.DEFAULT_BOLD);
        labels.addView(title);
        TextView version = text(activity, "v1.11.6 · 内置模块模式", 13, SECONDARY);
        LinearLayout.LayoutParams versionParams = wrap();
        versionParams.topMargin = dp(activity, 4);
        labels.addView(version, versionParams);
        header.addView(labels, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f));

        TextView close = text(activity, "关闭", 14, ACCENT);
        close.setTypeface(Typeface.DEFAULT_BOLD);
        close.setGravity(Gravity.CENTER);
        close.setPadding(dp(activity, 12), dp(activity, 8), dp(activity, 12), dp(activity, 8));
        close.setBackground(rounded(ACCENT_SOFT, dp(activity, 10), 0, 0));
        close.setOnClickListener(v -> dialog.dismiss());
        header.addView(close, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, dp(activity, 42)));
        return header;
    }

    private View buildQwertyCard() {
        LinearLayout card = createCard(
                "26 键快捷操作",
                "点击设置动作，长按设置该按键显示的自定义标签。",
                true);
        String[] rows = {"qwertyuiop", "asdfghjkl", "zxcvbnm"};
        LinearLayout keyboard = vertical();
        keyboard.setPadding(dp(activity, 6), dp(activity, 9), dp(activity, 6), dp(activity, 9));
        for (int rowIndex = 0; rowIndex < rows.length; rowIndex++) {
            LinearLayout row = horizontal();
            row.setGravity(Gravity.CENTER);
            if (rowIndex == 1) spacer(row, .45f);
            if (rowIndex == 2) spacer(row, 1.35f);
            String letters = rows[rowIndex];
            for (int i = 0; i < letters.length(); i++) {
                char letter = letters.charAt(i);
                LinearLayout key = buildQwertyKey(letter);
                LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(0, dp(activity, 62), 1f);
                params.setMargins(dp(activity, 2), dp(activity, 3), dp(activity, 2), dp(activity, 3));
                row.addView(key, params);
            }
            if (rowIndex == 1) spacer(row, .45f);
            if (rowIndex == 2) spacer(row, 1.35f);
            keyboard.addView(row);
        }
        card.addView(keyboard);
        card.addView(divider());
        LinearLayout tools = horizontal();
        tools.setPadding(dp(activity, 12), dp(activity, 10), dp(activity, 12), dp(activity, 12));
        TextView defaults = smallAction("恢复默认 Z/X/C/V", false);
        defaults.setOnClickListener(v -> {
            EmbeddedConfigEditor.restoreDefaults(config);
            refreshQwerty();
            Toast.makeText(activity, "已恢复默认 Z/X/C/V", Toast.LENGTH_SHORT).show();
        });
        tools.addView(defaults, new LinearLayout.LayoutParams(0, dp(activity, 42), 1f));
        TextView clear = smallAction("清空 26 键", true);
        LinearLayout.LayoutParams clearParams = new LinearLayout.LayoutParams(0, dp(activity, 42), 1f);
        clearParams.leftMargin = dp(activity, 8);
        tools.addView(clear, clearParams);
        clear.setOnClickListener(v -> new AlertDialog.Builder(activity)
                .setTitle("清空 26 键映射？")
                .setNegativeButton("取消", null)
                .setPositiveButton("清空", (d, w) -> {
                    EmbeddedConfigEditor.clearQwerty(config);
                    refreshQwerty();
                }).show());
        card.addView(tools);
        return card;
    }

    private LinearLayout buildQwertyKey(char letter) {
        int index = letter - 'a';
        LinearLayout key = vertical();
        key.setGravity(Gravity.CENTER);
        key.setPadding(dp(activity, 1), dp(activity, 4), dp(activity, 1), dp(activity, 4));
        key.setClickable(true);
        key.setFocusable(true);
        TextView name = text(activity, String.valueOf(Character.toUpperCase(letter)), 15, TEXT);
        name.setTypeface(Typeface.DEFAULT_BOLD);
        name.setGravity(Gravity.CENTER);
        key.addView(name);
        TextView action = text(activity, "—", 9, SECONDARY);
        action.setGravity(Gravity.CENTER);
        action.setMaxLines(1);
        action.setSingleLine(true);
        LinearLayout.LayoutParams actionParams = wrap();
        actionParams.topMargin = dp(activity, 3);
        key.addView(action, actionParams);
        qwertyKeyViews[index] = key;
        qwertyActionViews[index] = action;
        key.setOnClickListener(v -> showQwertyActionDialog(letter));
        key.setOnLongClickListener(v -> {
            showQwertyLabelDialog(letter);
            return true;
        });
        updateQwerty(letter);
        return key;
    }

    private View buildT9Card() {
        LinearLayout card = createCard(
                "九宫格快捷操作",
                "2–9 可设置。点击设置动作，长按设置该按键显示标签。",
                true);
        LinearLayout keyboard = vertical();
        keyboard.setPadding(dp(activity, 12), dp(activity, 9), dp(activity, 12), dp(activity, 9));
        int[][] rows = {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}};
        for (int[] digits : rows) {
            LinearLayout row = horizontal();
            row.setGravity(Gravity.CENTER);
            for (int digit : digits) {
                View key = buildT9Key(digit);
                LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(0, dp(activity, 72), 1f);
                params.setMargins(dp(activity, 4), dp(activity, 4), dp(activity, 4), dp(activity, 4));
                row.addView(key, params);
            }
            keyboard.addView(row);
        }
        card.addView(keyboard);
        card.addView(divider());
        LinearLayout tools = horizontal();
        tools.setPadding(dp(activity, 12), dp(activity, 10), dp(activity, 12), dp(activity, 12));
        TextView clear = smallAction("清空九宫格映射", true);
        tools.addView(clear, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(activity, 42)));
        clear.setOnClickListener(v -> new AlertDialog.Builder(activity)
                .setTitle("清空九宫格映射？")
                .setNegativeButton("取消", null)
                .setPositiveButton("清空", (d, w) -> {
                    for (int digit = 2; digit <= 9; digit++) config.t9Actions[digit] = Config.ACTION_NONE;
                    for (int digit = 2; digit <= 9; digit++) updateT9(digit);
                }).show());
        card.addView(tools);
        return card;
    }

    private View buildT9Key(int digit) {
        LinearLayout key = vertical();
        key.setGravity(Gravity.CENTER);
        key.setPadding(dp(activity, 6), dp(activity, 5), dp(activity, 6), dp(activity, 5));
        TextView digitView = text(activity, String.valueOf(digit), 20, TEXT);
        digitView.setTypeface(Typeface.DEFAULT_BOLD);
        digitView.setGravity(Gravity.CENTER);
        key.addView(digitView);
        TextView letters = text(activity, digit >= 2 ? T9_LETTERS[digit] : "", 10, SECONDARY);
        letters.setGravity(Gravity.CENTER);
        key.addView(letters);
        if (digit >= 2 && digit <= 9) {
            TextView action = text(activity, "—", 10, SECONDARY);
            action.setGravity(Gravity.CENTER);
            action.setMaxLines(1);
            action.setSingleLine(true);
            LinearLayout.LayoutParams actionParams = wrap();
            actionParams.topMargin = dp(activity, 2);
            key.addView(action, actionParams);
            t9KeyViews[digit] = key;
            t9ActionViews[digit] = action;
            key.setClickable(true);
            key.setFocusable(true);
            key.setOnClickListener(v -> showT9ActionDialog(digit));
            key.setOnLongClickListener(v -> {
                showT9LabelDialog(digit);
                return true;
            });
            updateT9(digit);
        } else {
            TextView note = text(activity, "普通键", 9, SECONDARY);
            note.setGravity(Gravity.CENTER);
            LinearLayout.LayoutParams noteParams = wrap();
            noteParams.topMargin = dp(activity, 2);
            key.addView(note, noteParams);
            key.setBackground(rounded(KEY_IDLE, dp(activity, 12), KEY_STROKE, 1));
        }
        return key;
    }

    private View buildGestureCard() {
        LinearLayout card = createCard("手势设置", "距离越大越不容易误触。", true);
        qwertyThreshold = slider(card, "26 键触发距离", 6, 40, config.thresholdDp, true);
        card.addView(divider());
        t9Threshold = slider(card, "九宫格触发距离", 10, 48, config.t9ThresholdDp, false);
        return card;
    }

    private SeekBar slider(LinearLayout card, String title, int min, int max, int value, boolean qwerty) {
        LinearLayout row = vertical();
        row.setPadding(dp(activity, 16), dp(activity, 12), dp(activity, 16), dp(activity, 8));
        LinearLayout titleRow = horizontal();
        titleRow.setGravity(Gravity.CENTER_VERTICAL);
        TextView label = text(activity, title, 15, TEXT);
        titleRow.addView(label, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f));
        TextView valueView = valueBadge(value + " dp");
        titleRow.addView(valueView);
        row.addView(titleRow);
        SeekBar seek = new SeekBar(activity);
        seek.setMax(max - min);
        seek.setProgress(Math.max(0, Math.min(max - min, value - min)));
        seek.setPadding(0, dp(activity, 4), 0, 0);
        seek.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                valueView.setText((progress + min) + " dp");
            }
            @Override public void onStartTrackingTouch(SeekBar seekBar) {}
            @Override public void onStopTrackingTouch(SeekBar seekBar) {}
        });
        row.addView(seek);
        card.addView(row);
        if (qwerty) qwertyThresholdValue = valueView; else t9ThresholdValue = valueView;
        return seek;
    }

    private View buildGeneralCard() {
        LinearLayout card = createCard("通用设置", null, false);
        showLabels = checkbox("显示按键底部功能文字", config.showKeyLabels);
        card.addView(showLabels, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(activity, 54)));
        card.addView(divider());

        showHint = checkbox("显示下滑触发提示", config.showTriggerHint);
        card.addView(showHint, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(activity, 54)));
        TextView displayNote = text(activity, "关闭后只隐藏提示，不影响下滑功能。", 12, SECONDARY);
        displayNote.setPadding(dp(activity, 18), 0, dp(activity, 18), dp(activity, 12));
        card.addView(displayNote);
        card.addView(divider());

        vibration = checkbox("触发快捷操作时额外震动", config.vibration);
        card.addView(vibration, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(activity, 54)));
        card.addView(divider());

        TextView embedded = text(activity, "内置模块设置入口：关于页面连续点击图标 5 次。", 12, SECONDARY);
        embedded.setPadding(dp(activity, 18), dp(activity, 12), dp(activity, 18), dp(activity, 14));
        card.addView(embedded);
        return card;
    }

    private View buildSaveBar() {
        LinearLayout bar = vertical();
        bar.setPadding(dp(activity, 12), dp(activity, 9), dp(activity, 12), dp(activity, 11));
        bar.setBackgroundColor(Color.WHITE);
        bar.setElevation(dp(activity, 10));
        Button save = new Button(activity);
        save.setText("保存并应用配置");
        save.setTextSize(16);
        save.setTextColor(Color.WHITE);
        save.setTypeface(Typeface.DEFAULT_BOLD);
        save.setAllCaps(false);
        save.setBackground(rounded(ACCENT, dp(activity, 12), 0, 0));
        save.setOnClickListener(v -> save());
        bar.addView(save, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(activity, 50)));
        return bar;
    }

    private void save() {
        config.thresholdDp = qwertyThreshold.getProgress() + 6;
        config.t9ThresholdDp = t9Threshold.getProgress() + 10;
        config.showKeyLabels = showLabels.isChecked();
        config.showTriggerHint = showHint.isChecked();
        config.vibration = vibration.isChecked();
        config.rebuildActionMap();
        if (saver != null) saver.save(ConfigSnapshot.copyOf(config));
        Toast.makeText(activity, "内置模块配置已保存并应用", Toast.LENGTH_SHORT).show();
        dialog.dismiss();
    }

    private void showQwertyActionDialog(char letter) {
        String key = String.valueOf(letter);
        int currentAction = EmbeddedConfigEditor.actionForQwerty(config, key);
        int selected = Config.menuPositionForAction(currentAction);
        AlertDialog picker = new AlertDialog.Builder(activity)
                .setTitle(Character.toUpperCase(letter) + " 键下滑执行")
                .setSingleChoiceItems(Config.ACTION_MENU_LABELS, selected, null)
                .setNegativeButton("取消", null)
                .create();
        picker.setOnShowListener(ignored -> picker.getListView().setOnItemClickListener(
                (parent, view, position, id) -> {
                    int action = Config.actionForMenuPosition(position);
                    picker.dismiss();
                    if (action == Config.ACTION_INSERT_TEXT) {
                        int index = letter - 'a';
                        showInsertTextDialog(Character.toUpperCase(letter) + " 键输入内容",
                                config.qwertyTexts[index], value -> {
                                    EmbeddedConfigEditor.assignQwertyText(config, key, value);
                                    refreshQwerty();
                                });
                    } else {
                        EmbeddedConfigEditor.assignQwerty(config, key, action);
                        refreshQwerty();
                    }
                }));
        picker.show();
    }

    private void showT9ActionDialog(int digit) {
        int selected = Config.menuPositionForAction(config.t9Actions[digit]);
        AlertDialog picker = new AlertDialog.Builder(activity)
                .setTitle(Config.t9Label(digit) + " 下滑执行")
                .setSingleChoiceItems(Config.ACTION_MENU_LABELS, selected, null)
                .setNegativeButton("取消", null)
                .create();
        picker.setOnShowListener(ignored -> picker.getListView().setOnItemClickListener(
                (parent, view, position, id) -> {
                    int action = Config.actionForMenuPosition(position);
                    picker.dismiss();
                    if (action == Config.ACTION_INSERT_TEXT) {
                        showInsertTextDialog(Config.t9Label(digit) + " 输入内容", config.t9Texts[digit], value -> {
                            EmbeddedConfigEditor.assignT9Text(config, digit, value);
                            updateT9(digit);
                        });
                    } else {
                        config.t9Actions[digit] = action;
                        EmbeddedConfigEditor.clearT9Text(config, digit);
                        updateT9(digit);
                    }
                }));
        picker.show();
    }

    private interface TextChanged { void apply(String value); }

    private void showInsertTextDialog(String title, String currentValue, TextChanged changed) {
        EditText input = new EditText(activity);
        input.setText(Config.normalizeInsertedText(currentValue));
        input.setHint("最多 1000 个字符，支持换行、符号和 Emoji");
        input.setSingleLine(false);
        input.setMinLines(3);
        input.setMaxLines(8);
        input.setGravity(Gravity.TOP | Gravity.START);
        input.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_MULTI_LINE
                | InputType.TYPE_TEXT_FLAG_CAP_SENTENCES);
        input.setFilters(new InputFilter[]{new InputFilter.LengthFilter(1000)});
        LinearLayout host = vertical();
        host.setPadding(dp(activity, 20), dp(activity, 8), dp(activity, 20), 0);
        host.addView(input);
        AlertDialog edit = new AlertDialog.Builder(activity)
                .setTitle(title)
                .setView(host)
                .setNegativeButton("取消", null)
                .setPositiveButton("保存", null)
                .create();
        edit.setOnShowListener(ignored -> edit.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
            String value = Config.normalizeInsertedText(input.getText().toString());
            if (value.isEmpty()) {
                Toast.makeText(activity, "输入内容不能为空", Toast.LENGTH_SHORT).show();
                return;
            }
            changed.apply(value);
            edit.dismiss();
        }));
        edit.show();
        input.requestFocus();
        input.setSelection(input.length());
    }

    private void showQwertyLabelDialog(char letter) {
        int action = EmbeddedConfigEditor.actionForQwerty(config, String.valueOf(letter));
        showLabelDialog(Character.toUpperCase(letter) + " 键显示标签",
                config.qwertyLabels[letter - 'a'], Config.shortActionLabel(action), value -> {
                    config.qwertyLabels[letter - 'a'] = value;
                    updateQwerty(letter);
                });
    }

    private void showT9LabelDialog(int digit) {
        int action = config.t9Actions[digit];
        showLabelDialog(Config.t9Label(digit) + " 显示标签",
                config.t9Labels[digit], Config.shortActionLabel(action), value -> {
                    config.t9Labels[digit] = value;
                    updateT9(digit);
                });
    }

    private interface LabelChanged { void apply(String value); }

    private void showLabelDialog(String title, String currentValue, String automaticValue, LabelChanged changed) {
        String current = Config.normalizeLabelValue(currentValue);
        int selected = Config.LABEL_HIDDEN.equals(current) ? 2 : (current.isEmpty() ? 0 : 1);
        String auto = automaticValue == null || automaticValue.isEmpty() ? "自动（当前无动作）" : "自动（" + automaticValue + "）";
        String custom = current.isEmpty() || Config.LABEL_HIDDEN.equals(current) ? "自定义文字" : "自定义（" + current + "）";
        String[] options = {auto, custom, "隐藏此按键标签"};
        AlertDialog picker = new AlertDialog.Builder(activity)
                .setTitle(title)
                .setSingleChoiceItems(options, selected, null)
                .setNegativeButton("取消", null)
                .create();
        picker.setOnShowListener(ignored -> picker.getListView().setOnItemClickListener(
                (parent, view, position, id) -> {
                    picker.dismiss();
                    if (position == 0) changed.apply("");
                    else if (position == 2) changed.apply(Config.LABEL_HIDDEN);
                    else showCustomLabelInput(title, current, changed);
                }));
        picker.show();
    }

    private void showCustomLabelInput(String title, String currentValue, LabelChanged changed) {
        EditText input = new EditText(activity);
        String current = Config.normalizeLabelValue(currentValue);
        if (!Config.LABEL_HIDDEN.equals(current)) input.setText(current);
        input.setSingleLine(true);
        input.setHint("最多 4 个字符，留空恢复自动");
        input.setFilters(new InputFilter[]{new InputFilter.LengthFilter(4)});
        input.setSelectAllOnFocus(true);
        LinearLayout host = vertical();
        host.setPadding(dp(activity, 20), dp(activity, 8), dp(activity, 20), 0);
        host.addView(input);
        AlertDialog edit = new AlertDialog.Builder(activity)
                .setTitle(title + " · 自定义")
                .setView(host)
                .setNegativeButton("取消", null)
                .setPositiveButton("保存", null)
                .create();
        edit.setOnShowListener(ignored -> edit.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
            changed.apply(Config.normalizeLabelValue(input.getText().toString()));
            edit.dismiss();
        }));
        edit.show();
    }

    private void refreshQwerty() {
        for (char c = 'a'; c <= 'z'; c++) updateQwerty(c);
    }

    private void updateQwerty(char letter) {
        int index = letter - 'a';
        TextView view = qwertyActionViews[index];
        LinearLayout keyView = qwertyKeyViews[index];
        if (view == null || keyView == null) return;
        int action = EmbeddedConfigEditor.actionForQwerty(config, String.valueOf(letter));
        view.setText(previewLabel(config.qwertyLabels[index], action));
        if (action == Config.ACTION_DISABLE) {
            view.setTextColor(DANGER);
            keyView.setBackground(rounded(DANGER_SOFT, dp(activity, 9), Color.rgb(245, 190, 190), 1));
        } else if (action == Config.ACTION_NONE) {
            view.setTextColor(SECONDARY);
            keyView.setBackground(rounded(KEY_IDLE, dp(activity, 9), KEY_STROKE, 1));
        } else {
            view.setTextColor(ACCENT);
            keyView.setBackground(rounded(ACCENT_SOFT, dp(activity, 9), Color.rgb(190, 210, 245), 1));
        }
    }

    private void updateT9(int digit) {
        TextView view = t9ActionViews[digit];
        LinearLayout keyView = t9KeyViews[digit];
        if (view == null || keyView == null) return;
        int action = Config.validAction(config.t9Actions[digit]);
        view.setText(previewLabel(config.t9Labels[digit], action));
        if (action == Config.ACTION_DISABLE) {
            view.setTextColor(DANGER);
            keyView.setBackground(rounded(DANGER_SOFT, dp(activity, 12), Color.rgb(245, 190, 190), 1));
        } else if (action == Config.ACTION_NONE) {
            view.setTextColor(SECONDARY);
            keyView.setBackground(rounded(KEY_IDLE, dp(activity, 12), KEY_STROKE, 1));
        } else {
            view.setTextColor(ACCENT);
            keyView.setBackground(rounded(ACCENT_SOFT, dp(activity, 12), Color.rgb(190, 210, 245), 1));
        }
    }

    private String previewLabel(String configured, int action) {
        if (action == Config.ACTION_NONE) return "—";
        String normalized = Config.normalizeLabelValue(configured);
        if (Config.LABEL_HIDDEN.equals(normalized)) return "隐藏";
        if (!normalized.isEmpty()) return normalized;
        String shortName = Config.shortActionLabel(action);
        return shortName == null || shortName.isEmpty() ? Config.actionName(action) : shortName;
    }

    private CheckBox checkbox(String title, boolean checked) {
        CheckBox box = new CheckBox(activity);
        box.setText(title);
        box.setTextSize(15);
        box.setTextColor(TEXT);
        box.setChecked(checked);
        box.setPadding(dp(activity, 12), dp(activity, 6), dp(activity, 12), dp(activity, 6));
        return box;
    }

    private LinearLayout createCard(String title, String subtitle, boolean showHeaderDivider) {
        LinearLayout card = vertical();
        card.setBackground(rounded(CARD, dp(activity, 16), 0, 0));
        card.setElevation(dp(activity, 1));
        LinearLayout.LayoutParams cardParams = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        cardParams.bottomMargin = dp(activity, 12);
        card.setLayoutParams(cardParams);
        LinearLayout head = vertical();
        head.setPadding(dp(activity, 16), dp(activity, 14), dp(activity, 16),
                subtitle == null ? dp(activity, 12) : dp(activity, 11));
        TextView titleView = text(activity, title, 18, TEXT);
        titleView.setTypeface(Typeface.DEFAULT_BOLD);
        head.addView(titleView);
        if (subtitle != null && !subtitle.isEmpty()) {
            TextView subtitleView = text(activity, subtitle, 12, SECONDARY);
            LinearLayout.LayoutParams subParams = wrap();
            subParams.topMargin = dp(activity, 4);
            head.addView(subtitleView, subParams);
        }
        card.addView(head);
        if (showHeaderDivider) card.addView(divider());
        return card;
    }

    private TextView valueBadge(String value) {
        TextView view = text(activity, value, 13, ACCENT);
        view.setGravity(Gravity.CENTER);
        view.setPadding(dp(activity, 10), dp(activity, 4), dp(activity, 10), dp(activity, 4));
        view.setBackground(rounded(ACCENT_SOFT, dp(activity, 12), 0, 0));
        return view;
    }

    private TextView smallAction(String title, boolean danger) {
        TextView button = text(activity, title, 13, danger ? DANGER : ACCENT);
        button.setGravity(Gravity.CENTER);
        button.setTypeface(Typeface.DEFAULT_BOLD);
        button.setBackground(rounded(danger ? DANGER_SOFT : ACCENT_SOFT, dp(activity, 10), 0, 0));
        button.setClickable(true);
        return button;
    }

    private View divider() {
        View view = new View(activity);
        view.setBackgroundColor(DIVIDER);
        view.setLayoutParams(new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(activity, 1)));
        return view;
    }

    private void spacer(LinearLayout row, float weight) {
        row.addView(new View(activity), new LinearLayout.LayoutParams(0, dp(activity, 1), weight));
    }

    private static LinearLayout vertical(Activity activity) {
        LinearLayout layout = new LinearLayout(activity);
        layout.setOrientation(LinearLayout.VERTICAL);
        return layout;
    }

    private LinearLayout vertical() { return vertical(activity); }

    private LinearLayout horizontal() {
        LinearLayout layout = new LinearLayout(activity);
        layout.setOrientation(LinearLayout.HORIZONTAL);
        return layout;
    }

    private static TextView text(Activity activity, String value, int sp, int color) {
        TextView view = new TextView(activity);
        view.setText(value);
        view.setTextSize(sp);
        view.setTextColor(color);
        return view;
    }

    private static LinearLayout.LayoutParams wrap() {
        return new LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
    }

    private static GradientDrawable rounded(int color, int radius, int stroke, int strokeWidth) {
        GradientDrawable drawable = new GradientDrawable();
        drawable.setColor(color);
        drawable.setCornerRadius(radius);
        if (strokeWidth > 0) drawable.setStroke(strokeWidth, stroke);
        return drawable;
    }

    private static int dp(Activity activity, int value) {
        return Math.round(value * activity.getResources().getDisplayMetrics().density);
    }
}
