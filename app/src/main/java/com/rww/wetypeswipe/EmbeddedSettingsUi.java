package com.rww.wetypeswipe;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.Dialog;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.text.InputFilter;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.Window;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.SeekBar;
import android.widget.TextView;
import android.widget.Toast;

import java.util.Locale;

final class EmbeddedSettingsUi {
    private static final String ENTRY_TAG = "wetype_swipe_embedded_settings_entry";
    private static final int PAGE = Color.rgb(245, 247, 250);
    private static final int CARD = Color.WHITE;
    private static final int TEXT = Color.rgb(32, 36, 43);
    private static final int SECONDARY = Color.rgb(101, 109, 122);
    private static final int DIVIDER = Color.rgb(232, 235, 240);
    private static final int ACCENT = Color.rgb(36, 103, 214);
    private static final int KEY_IDLE = Color.rgb(247, 249, 252);
    private static final int KEY_STROKE = Color.rgb(218, 223, 232);

    interface ConfigProvider { Config get(); }
    interface ConfigSaver { void save(Config config); }

    static void ensureAboutEntry(Activity activity, ConfigProvider provider, ConfigSaver saver) {
        if (activity == null || activity.isFinishing()) return;
        View contentView = activity.findViewById(android.R.id.content);
        if (!(contentView instanceof FrameLayout)) return;
        FrameLayout content = (FrameLayout) contentView;
        View existing = content.findViewWithTag(ENTRY_TAG);
        if (!isAboutPage(content)) {
            if (existing != null) content.removeView(existing);
            return;
        }
        if (existing != null) return;

        LinearLayout entry = new LinearLayout(activity);
        entry.setTag(ENTRY_TAG);
        entry.setOrientation(LinearLayout.HORIZONTAL);
        entry.setGravity(Gravity.CENTER_VERTICAL);
        entry.setPadding(dp(activity, 18), dp(activity, 12), dp(activity, 14), dp(activity, 12));
        entry.setClickable(true);
        entry.setFocusable(true);
        entry.setElevation(dp(activity, 5));
        entry.setBackground(rounded(Color.WHITE, dp(activity, 14), Color.rgb(220, 225, 234), 1));

        LinearLayout labels = new LinearLayout(activity);
        labels.setOrientation(LinearLayout.VERTICAL);
        TextView title = text(activity, "下滑快捷键设置", 16, TEXT);
        title.setTypeface(Typeface.DEFAULT_BOLD);
        labels.addView(title);
        TextView subtitle = text(activity, "内置模块设置 · 无需单独安装模块 APK", 12, SECONDARY);
        LinearLayout.LayoutParams subtitleParams = wrap();
        subtitleParams.topMargin = dp(activity, 3);
        labels.addView(subtitle, subtitleParams);
        entry.addView(labels, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f));

        TextView arrow = text(activity, "›", 28, SECONDARY);
        arrow.setGravity(Gravity.CENTER);
        entry.addView(arrow, new LinearLayout.LayoutParams(dp(activity, 34), dp(activity, 42)));
        entry.setOnClickListener(v -> show(activity, provider, saver));

        FrameLayout.LayoutParams params = new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT, Gravity.BOTTOM);
        params.setMargins(dp(activity, 14), dp(activity, 14), dp(activity, 14), dp(activity, 20));
        content.addView(entry, params);
        entry.bringToFront();
    }

    static boolean isAboutMarkerText(CharSequence value) {
        if (value == null) return false;
        String text = value.toString().trim().replace(" ", "");
        return text.contains("关于微信输入法") || text.equals("关于")
                || text.toLowerCase(Locale.ROOT).contains("aboutwetype");
    }

    private static boolean isAboutPage(View root) {
        boolean strong = containsText(root, "关于微信输入法")
                || containsTextIgnoreSpace(root, "About WeType");
        if (strong) return true;
        return containsExactText(root, "关于")
                && containsText(root, "微信输入法")
                && (containsText(root, "版本") || containsText(root, "隐私"));
    }

    private static boolean containsText(View view, String expected) {
        if (view instanceof TextView) {
            CharSequence value = ((TextView) view).getText();
            if (value != null && value.toString().contains(expected)) return true;
        }
        if (view instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) view;
            for (int i = 0; i < group.getChildCount(); i++) {
                if (containsText(group.getChildAt(i), expected)) return true;
            }
        }
        return false;
    }

    private static boolean containsTextIgnoreSpace(View view, String expected) {
        if (view instanceof TextView) {
            CharSequence value = ((TextView) view).getText();
            if (value != null) {
                String normalized = value.toString().replace(" ", "").toLowerCase(Locale.ROOT);
                if (normalized.contains(expected.replace(" ", "").toLowerCase(Locale.ROOT))) return true;
            }
        }
        if (view instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) view;
            for (int i = 0; i < group.getChildCount(); i++) {
                if (containsTextIgnoreSpace(group.getChildAt(i), expected)) return true;
            }
        }
        return false;
    }

    private static boolean containsExactText(View view, String expected) {
        if (view instanceof TextView) {
            CharSequence value = ((TextView) view).getText();
            if (value != null && expected.equals(value.toString().trim())) return true;
        }
        if (view instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) view;
            for (int i = 0; i < group.getChildCount(); i++) {
                if (containsExactText(group.getChildAt(i), expected)) return true;
            }
        }
        return false;
    }

    private final Activity activity;
    private final Config config;
    private final ConfigSaver saver;
    private final TextView[] qwertyActionViews = new TextView[26];
    private final TextView[] t9ActionViews = new TextView[10];
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

    private static void show(Activity activity, ConfigProvider provider, ConfigSaver saver) {
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
        content.setPadding(dp(activity, 12), dp(activity, 12), dp(activity, 12), dp(activity, 24));
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
        header.setPadding(dp(activity, 10), dp(activity, 12), dp(activity, 16), dp(activity, 12));
        header.setBackgroundColor(Color.WHITE);

        TextView close = text(activity, "‹", 32, TEXT);
        close.setGravity(Gravity.CENTER);
        close.setOnClickListener(v -> dialog.dismiss());
        header.addView(close, new LinearLayout.LayoutParams(dp(activity, 46), dp(activity, 46)));

        LinearLayout labels = vertical();
        TextView title = text(activity, "下滑快捷键设置", 20, TEXT);
        title.setTypeface(Typeface.DEFAULT_BOLD);
        labels.addView(title);
        TextView sub = text(activity, "内置模块模式 · v1.11.6-test1", 12, SECONDARY);
        labels.addView(sub);
        header.addView(labels, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f));
        return header;
    }

    private View buildQwertyCard() {
        LinearLayout card = card("26 键快捷操作", "点击按键设置动作，长按设置显示标签。");
        String[] rows = {"qwertyuiop", "asdfghjkl", "zxcvbnm"};
        LinearLayout keyboard = vertical();
        keyboard.setPadding(dp(activity, 6), dp(activity, 8), dp(activity, 6), dp(activity, 8));
        for (int rowIndex = 0; rowIndex < rows.length; rowIndex++) {
            LinearLayout row = horizontal();
            row.setGravity(Gravity.CENTER);
            if (rowIndex == 1) spacer(row, .45f);
            if (rowIndex == 2) spacer(row, 1.35f);
            String letters = rows[rowIndex];
            for (int i = 0; i < letters.length(); i++) {
                char letter = letters.charAt(i);
                LinearLayout key = buildQwertyKey(letter);
                LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(0, dp(activity, 60), 1f);
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
        TextView defaults = actionButton("恢复默认 Z/X/C/V");
        defaults.setOnClickListener(v -> {
            EmbeddedConfigEditor.restoreDefaults(config);
            refreshQwerty();
        });
        tools.addView(defaults, new LinearLayout.LayoutParams(0, dp(activity, 42), 1f));
        TextView clear = actionButton("清空 26 键");
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
        LinearLayout key = vertical();
        key.setGravity(Gravity.CENTER);
        key.setClickable(true);
        key.setFocusable(true);
        key.setBackground(rounded(KEY_IDLE, dp(activity, 8), KEY_STROKE, 1));
        TextView name = text(activity, String.valueOf(Character.toUpperCase(letter)), 15, TEXT);
        name.setTypeface(Typeface.DEFAULT_BOLD);
        name.setGravity(Gravity.CENTER);
        key.addView(name);
        TextView action = text(activity, "—", 9, SECONDARY);
        action.setGravity(Gravity.CENTER);
        action.setMaxLines(1);
        qwertyActionViews[letter - 'a'] = action;
        key.addView(action);
        key.setOnClickListener(v -> showQwertyActionDialog(letter));
        key.setOnLongClickListener(v -> {
            showQwertyLabelDialog(letter);
            return true;
        });
        updateQwerty(letter);
        return key;
    }

    private View buildT9Card() {
        LinearLayout card = card("九宫格快捷操作", "2–9 可独立绑定；长按数字设置标签。");
        LinearLayout grid = vertical();
        grid.setPadding(dp(activity, 10), dp(activity, 8), dp(activity, 10), dp(activity, 10));
        int[][] rows = {{2,3,4,5}, {6,7,8,9}};
        for (int[] digits : rows) {
            LinearLayout row = horizontal();
            for (int digit : digits) {
                LinearLayout key = vertical();
                key.setGravity(Gravity.CENTER);
                key.setBackground(rounded(KEY_IDLE, dp(activity, 9), KEY_STROKE, 1));
                TextView name = text(activity, String.valueOf(digit), 17, TEXT);
                name.setTypeface(Typeface.DEFAULT_BOLD);
                key.addView(name);
                TextView action = text(activity, "—", 10, SECONDARY);
                action.setGravity(Gravity.CENTER);
                t9ActionViews[digit] = action;
                key.addView(action);
                key.setOnClickListener(v -> showT9ActionDialog(digit));
                key.setOnLongClickListener(v -> {
                    showT9LabelDialog(digit);
                    return true;
                });
                LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(0, dp(activity, 66), 1f);
                params.setMargins(dp(activity, 3), dp(activity, 3), dp(activity, 3), dp(activity, 3));
                row.addView(key, params);
                updateT9(digit);
            }
            grid.addView(row);
        }
        card.addView(grid);
        return card;
    }

    private View buildGestureCard() {
        LinearLayout card = card("下滑触发距离", "数值越大，越不容易误触。修改后保存立即生效。");
        qwertyThreshold = slider(card, "26 键", 6, 40, config.thresholdDp, true);
        t9Threshold = slider(card, "九宫格", 10, 48, config.t9ThresholdDp, false);
        return card;
    }

    private SeekBar slider(LinearLayout card, String title, int min, int max, int value, boolean qwerty) {
        LinearLayout row = vertical();
        row.setPadding(dp(activity, 14), dp(activity, 10), dp(activity, 14), dp(activity, 10));
        LinearLayout titleRow = horizontal();
        TextView label = text(activity, title, 14, TEXT);
        titleRow.addView(label, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f));
        TextView valueView = text(activity, value + " dp", 13, ACCENT);
        titleRow.addView(valueView);
        row.addView(titleRow);
        SeekBar seek = new SeekBar(activity);
        seek.setMax(max - min);
        seek.setProgress(Math.max(0, Math.min(max - min, value - min)));
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
        LinearLayout card = card("显示与反馈", "内置模式不提供桌面图标开关，其余设置与独立模块一致。");
        showLabels = checkbox("显示按键功能文字", config.showKeyLabels);
        showHint = checkbox("显示下滑触发提示", config.showTriggerHint);
        vibration = checkbox("模块主动震动", config.vibration);
        card.addView(showLabels);
        card.addView(showHint);
        card.addView(vibration);
        return card;
    }

    private View buildSaveBar() {
        LinearLayout bar = horizontal();
        bar.setPadding(dp(activity, 12), dp(activity, 9), dp(activity, 12), dp(activity, 12));
        bar.setBackgroundColor(Color.WHITE);
        TextView save = text(activity, "保存并应用配置", 16, Color.WHITE);
        save.setTypeface(Typeface.DEFAULT_BOLD);
        save.setGravity(Gravity.CENTER);
        save.setBackground(rounded(ACCENT, dp(activity, 12), ACCENT, 0));
        save.setOnClickListener(v -> save());
        bar.addView(save, new LinearLayout.LayoutParams(0, dp(activity, 50), 1f));
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
                    EmbeddedConfigEditor.assignQwerty(config, key, action);
                    refreshQwerty();
                    picker.dismiss();
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
                    config.t9Actions[digit] = Config.actionForMenuPosition(position);
                    updateT9(digit);
                    picker.dismiss();
                }));
        picker.show();
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
        TextView view = qwertyActionViews[letter - 'a'];
        if (view == null) return;
        int action = EmbeddedConfigEditor.actionForQwerty(config, String.valueOf(letter));
        String name = action == Config.ACTION_NONE ? "—" : Config.shortActionLabel(action);
        if (name == null || name.isEmpty()) name = Config.actionName(action);
        view.setText(name);
    }

    private void updateT9(int digit) {
        TextView view = t9ActionViews[digit];
        if (view == null) return;
        int action = Config.validAction(config.t9Actions[digit]);
        String name = action == Config.ACTION_NONE ? "—" : Config.shortActionLabel(action);
        if (name == null || name.isEmpty()) name = Config.actionName(action);
        view.setText(name);
    }

    private CheckBox checkbox(String title, boolean checked) {
        CheckBox box = new CheckBox(activity);
        box.setText(title);
        box.setTextSize(14);
        box.setTextColor(TEXT);
        box.setChecked(checked);
        box.setPadding(dp(activity, 12), dp(activity, 6), dp(activity, 12), dp(activity, 6));
        return box;
    }

    private LinearLayout card(String title, String subtitle) {
        LinearLayout card = vertical();
        card.setBackground(rounded(CARD, dp(activity, 14), Color.rgb(230, 233, 239), 1));
        LinearLayout.LayoutParams cardParams = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        cardParams.bottomMargin = dp(activity, 12);
        card.setLayoutParams(cardParams);
        LinearLayout head = vertical();
        head.setPadding(dp(activity, 14), dp(activity, 13), dp(activity, 14), dp(activity, 10));
        TextView titleView = text(activity, title, 16, TEXT);
        titleView.setTypeface(Typeface.DEFAULT_BOLD);
        head.addView(titleView);
        TextView subtitleView = text(activity, subtitle, 12, SECONDARY);
        LinearLayout.LayoutParams subParams = wrap();
        subParams.topMargin = dp(activity, 3);
        head.addView(subtitleView, subParams);
        card.addView(head);
        return card;
    }

    private TextView actionButton(String title) {
        TextView button = text(activity, title, 13, ACCENT);
        button.setGravity(Gravity.CENTER);
        button.setBackground(rounded(Color.rgb(246, 249, 255), dp(activity, 9), Color.rgb(210, 222, 246), 1));
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
