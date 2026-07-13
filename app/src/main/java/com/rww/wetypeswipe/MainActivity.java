package com.rww.wetypeswipe;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ComponentName;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.Insets;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Build;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowInsets;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.SeekBar;
import android.widget.TextView;
import android.widget.Toast;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Locale;

public final class MainActivity extends Activity {
    private static final String LAUNCHER_ALIAS = "com.rww.wetypeswipe.LauncherAlias";

    private static final int COLOR_PAGE = Color.rgb(245, 247, 250);
    private static final int COLOR_CARD = Color.WHITE;
    private static final int COLOR_TEXT = Color.rgb(32, 36, 43);
    private static final int COLOR_SECONDARY = Color.rgb(101, 109, 122);
    private static final int COLOR_DIVIDER = Color.rgb(232, 235, 240);
    private static final int COLOR_ACCENT = Color.rgb(36, 103, 214);
    private static final int COLOR_ACCENT_SOFT = Color.rgb(232, 240, 254);
    private static final int COLOR_KEY_IDLE = Color.rgb(247, 249, 252);
    private static final int COLOR_KEY_STROKE = Color.rgb(218, 223, 232);
    private static final int COLOR_DANGER = Color.rgb(190, 55, 55);
    private static final int COLOR_DANGER_SOFT = Color.rgb(255, 237, 237);

    private static final int[] QWERTY_ACTIONS = {
            Config.ACTION_SELECT_ALL,
            Config.ACTION_CUT,
            Config.ACTION_COPY,
            Config.ACTION_PASTE,
            Config.ACTION_PARAGRAPH_START,
            Config.ACTION_PARAGRAPH_END,
            Config.ACTION_SELECT_TO_PARAGRAPH_START,
            Config.ACTION_SELECT_TO_PARAGRAPH_END,
            Config.ACTION_OPEN_CLIPBOARD,
            Config.ACTION_OPEN_QUICK_PHRASE
    };

    private static final String[] QWERTY_LABELS = {
            "全选", "剪切", "复制", "粘贴",
            "段首", "段尾", "选至段首", "选至段尾",
            "剪贴板", "快捷发送"
    };

    private static final String[] QWERTY_ROWS = {
            "qwertyuiop",
            "asdfghjkl",
            "zxcvbnm"
    };

    private static final String[] T9_LETTERS = {
            "", "", "ABC", "DEF", "GHI", "JKL", "MNO", "PQRS", "TUV", "WXYZ"
    };

    private SharedPreferences prefs;

    private final String[] qwertyKeys = new String[QWERTY_ACTIONS.length];
    private final TextView[] qwertyActionViews = new TextView[26];
    private final LinearLayout[] qwertyKeyViews = new LinearLayout[26];
    private String disabledKeys = "";

    private final int[] t9Actions = new int[10];
    private final TextView[] t9ActionViews = new TextView[10];
    private final LinearLayout[] t9KeyViews = new LinearLayout[10];

    private SeekBar threshold;
    private SeekBar t9Threshold;
    private TextView thresholdValue;
    private TextView t9ThresholdValue;
    private CheckBox showKeyLabels;
    private CheckBox showTriggerHint;
    private CheckBox vibration;
    private CheckBox hideIcon;

    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        setTitle("微信输入法下滑快捷键");
        prefs = getSharedPreferences(Config.PREFS, MODE_PRIVATE);
        loadUiState();
        configureWindow();
        setContentView(buildPage());
    }

    @Override protected void onResume() {
        super.onResume();
        if (hideIcon != null) hideIcon.setChecked(isLauncherIconHidden());
    }

    private void configureWindow() {
        getWindow().setStatusBarColor(Color.WHITE);
        getWindow().setNavigationBarColor(Color.WHITE);
        getWindow().getDecorView().setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR | View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);
    }

    private View buildPage() {
        LinearLayout page = vertical();
        page.setBackgroundColor(COLOR_PAGE);
        applySystemBarInsets(page);

        page.addView(buildHeader(), new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setClipToPadding(false);

        LinearLayout content = vertical();
        content.setPadding(dp(12), dp(12), dp(12), dp(22));
        scroll.addView(content);

        content.addView(buildQwertyCard());
        content.addView(buildT9Card());
        content.addView(buildGestureCard());
        content.addView(buildGeneralCard());

        page.addView(scroll, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f));
        page.addView(buildSaveBar(), new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
        return page;
    }

    private void applySystemBarInsets(View root) {
        root.setOnApplyWindowInsetsListener((view, insets) -> {
            int top;
            int bottom;
            if (Build.VERSION.SDK_INT >= 30) {
                Insets bars = insets.getInsets(WindowInsets.Type.systemBars());
                top = bars.top;
                bottom = bars.bottom;
            } else {
                top = insets.getSystemWindowInsetTop();
                bottom = insets.getSystemWindowInsetBottom();
            }
            view.setPadding(0, top, 0, bottom);
            return insets;
        });
        root.requestApplyInsets();
    }

    private View buildHeader() {
        LinearLayout header = vertical();
        header.setPadding(dp(18), dp(14), dp(18), dp(14));
        header.setBackgroundColor(Color.WHITE);

        TextView title = text("微信输入法下滑快捷键", 21, COLOR_TEXT);
        title.setTypeface(Typeface.DEFAULT_BOLD);
        header.addView(title);

        TextView version = text("v1.11.0 · 按键功能文字与显示选项", 13, COLOR_SECONDARY);
        LinearLayout.LayoutParams versionParams = wrap();
        versionParams.topMargin = dp(4);
        header.addView(version, versionParams);
        return header;
    }

    private View buildQwertyCard() {
        LinearLayout card = createCard(
                "26 键快捷操作",
                "按照真实键盘排列展示。点击字母键，直接选择该键下滑时执行的动作。",
                true);

        LinearLayout keyboard = vertical();
        keyboard.setPadding(dp(6), dp(9), dp(6), dp(9));

        for (int rowIndex = 0; rowIndex < QWERTY_ROWS.length; rowIndex++) {
            LinearLayout row = horizontal();
            row.setGravity(Gravity.CENTER);

            if (rowIndex == 1) addKeyboardSpacer(row, 0.45f);
            if (rowIndex == 2) addKeyboardSpacer(row, 1.35f);

            String letters = QWERTY_ROWS[rowIndex];
            for (int i = 0; i < letters.length(); i++) {
                char key = letters.charAt(i);
                LinearLayout keyView = buildQwertyKey(key);
                LinearLayout.LayoutParams keyParams = new LinearLayout.LayoutParams(0, dp(62), 1f);
                keyParams.setMargins(dp(2), dp(3), dp(2), dp(3));
                row.addView(keyView, keyParams);
            }

            if (rowIndex == 1) addKeyboardSpacer(row, 0.45f);
            if (rowIndex == 2) addKeyboardSpacer(row, 1.35f);
            keyboard.addView(row, new LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
        }
        card.addView(keyboard);

        card.addView(divider());
        LinearLayout tools = horizontal();
        tools.setPadding(dp(12), dp(10), dp(12), dp(12));

        TextView defaults = smallAction("恢复默认 Z/X/C/V", false);
        defaults.setOnClickListener(v -> restoreQwertyDefaults());
        tools.addView(defaults, new LinearLayout.LayoutParams(0, dp(42), 1f));

        TextView clear = smallAction("清空 26 键", true);
        LinearLayout.LayoutParams clearParams = new LinearLayout.LayoutParams(0, dp(42), 1f);
        clearParams.leftMargin = dp(8);
        tools.addView(clear, clearParams);
        clear.setOnClickListener(v -> confirmClearQwerty());
        card.addView(tools);
        return card;
    }

    private void addKeyboardSpacer(LinearLayout row, float weight) {
        View spacer = new View(this);
        row.addView(spacer, new LinearLayout.LayoutParams(0, dp(1), weight));
    }

    private LinearLayout buildQwertyKey(char letter) {
        int index = letter - 'a';
        LinearLayout key = vertical();
        key.setGravity(Gravity.CENTER);
        key.setPadding(dp(1), dp(4), dp(1), dp(4));
        key.setClickable(true);
        key.setFocusable(true);

        TextView letterView = text(String.valueOf(Character.toUpperCase(letter)), 15, COLOR_TEXT);
        letterView.setTypeface(Typeface.DEFAULT_BOLD);
        letterView.setGravity(Gravity.CENTER);
        key.addView(letterView);

        TextView actionView = text("—", 9, COLOR_SECONDARY);
        actionView.setGravity(Gravity.CENTER);
        actionView.setMaxLines(1);
        actionView.setSingleLine(true);
        LinearLayout.LayoutParams actionParams = wrap();
        actionParams.topMargin = dp(3);
        key.addView(actionView, actionParams);

        qwertyKeyViews[index] = key;
        qwertyActionViews[index] = actionView;
        updateQwertyKeyView(letter);
        key.setOnClickListener(v -> showQwertyActionDialog(letter));
        return key;
    }

    private View buildT9Card() {
        LinearLayout card = createCard(
                "九宫格快捷操作",
                "按照九宫格键盘排列展示。2–9 可设置，1 保持普通输入。",
                true);

        LinearLayout keyboard = vertical();
        keyboard.setPadding(dp(12), dp(9), dp(12), dp(9));

        int[][] rows = {
                {1, 2, 3},
                {4, 5, 6},
                {7, 8, 9}
        };
        for (int[] digits : rows) {
            LinearLayout row = horizontal();
            row.setGravity(Gravity.CENTER);
            for (int digit : digits) {
                View key = buildT9Key(digit);
                LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(0, dp(72), 1f);
                params.setMargins(dp(4), dp(4), dp(4), dp(4));
                row.addView(key, params);
            }
            keyboard.addView(row, new LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
        }
        card.addView(keyboard);

        card.addView(divider());
        LinearLayout tools = horizontal();
        tools.setPadding(dp(12), dp(10), dp(12), dp(12));
        TextView clear = smallAction("清空九宫格映射", true);
        tools.addView(clear, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(42)));
        clear.setOnClickListener(v -> confirmClearT9());
        card.addView(tools);
        return card;
    }

    private View buildT9Key(int digit) {
        LinearLayout key = vertical();
        key.setGravity(Gravity.CENTER);
        key.setPadding(dp(6), dp(5), dp(6), dp(5));

        if (digit < 0) {
            String symbol = digit == -1 ? "*" : "#";
            TextView symbolView = text(symbol, 20, COLOR_SECONDARY);
            symbolView.setGravity(Gravity.CENTER);
            key.addView(symbolView);
            key.setBackground(rounded(COLOR_KEY_IDLE, 12, 1, COLOR_KEY_STROKE));
            return key;
        }

        TextView digitView = text(String.valueOf(digit), 20, COLOR_TEXT);
        digitView.setTypeface(Typeface.DEFAULT_BOLD);
        digitView.setGravity(Gravity.CENTER);
        key.addView(digitView);

        TextView letters = text(digit >= 2 ? T9_LETTERS[digit] : "", 10, COLOR_SECONDARY);
        letters.setGravity(Gravity.CENTER);
        key.addView(letters);

        if (digit >= 2 && digit <= 9) {
            TextView action = text("—", 10, COLOR_SECONDARY);
            action.setGravity(Gravity.CENTER);
            action.setMaxLines(1);
            action.setSingleLine(true);
            LinearLayout.LayoutParams actionParams = wrap();
            actionParams.topMargin = dp(2);
            key.addView(action, actionParams);
            t9KeyViews[digit] = key;
            t9ActionViews[digit] = action;
            updateT9View(digit);
            key.setClickable(true);
            key.setFocusable(true);
            key.setOnClickListener(v -> showT9ActionDialog(digit));
        } else {
            TextView note = text("普通键", 9, COLOR_SECONDARY);
            note.setGravity(Gravity.CENTER);
            LinearLayout.LayoutParams noteParams = wrap();
            noteParams.topMargin = dp(2);
            key.addView(note, noteParams);
            key.setBackground(rounded(COLOR_KEY_IDLE, 12, 1, COLOR_KEY_STROKE));
        }
        return key;
    }

    private View buildGestureCard() {
        LinearLayout card = createCard("手势设置", "距离越大越不容易误触。", true);

        int qwertyValue = clamp(prefs.getInt(Config.KEY_THRESHOLD, 12), 6, 40, 12);
        int t9Value = clamp(prefs.getInt(Config.KEY_T9_THRESHOLD, 20), 10, 48, 20);

        LinearLayout qwertyBlock = vertical();
        qwertyBlock.setPadding(dp(16), dp(12), dp(16), dp(8));
        LinearLayout qwertyHeader = horizontal();
        qwertyHeader.setGravity(Gravity.CENTER_VERTICAL);
        qwertyHeader.addView(text("26 键触发距离", 15, COLOR_TEXT),
                new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f));
        thresholdValue = valueBadge(qwertyValue + " dp");
        qwertyHeader.addView(thresholdValue);
        qwertyBlock.addView(qwertyHeader);
        threshold = createThreshold(qwertyValue, 6, 40,
                value -> thresholdValue.setText(value + " dp"));
        qwertyBlock.addView(threshold);
        card.addView(qwertyBlock);

        card.addView(divider());

        LinearLayout t9Block = vertical();
        t9Block.setPadding(dp(16), dp(12), dp(16), dp(8));
        LinearLayout t9Header = horizontal();
        t9Header.setGravity(Gravity.CENTER_VERTICAL);
        t9Header.addView(text("九宫格触发距离", 15, COLOR_TEXT),
                new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f));
        t9ThresholdValue = valueBadge(t9Value + " dp");
        t9Header.addView(t9ThresholdValue);
        t9Block.addView(t9Header);
        t9Threshold = createThreshold(t9Value, 10, 48,
                value -> t9ThresholdValue.setText(value + " dp"));
        t9Block.addView(t9Threshold);
        card.addView(t9Block);
        return card;
    }

    private View buildGeneralCard() {
        LinearLayout card = createCard("通用设置", null, false);

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

        vibration = new CheckBox(this);
        vibration.setText("触发快捷操作时额外震动");
        vibration.setTextSize(15);
        vibration.setTextColor(COLOR_TEXT);
        vibration.setPadding(dp(12), dp(6), dp(12), dp(6));
        vibration.setChecked(prefs.getBoolean(Config.KEY_VIBRATION, true));
        card.addView(vibration, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(54)));

        card.addView(divider());

        hideIcon = new CheckBox(this);
        hideIcon.setText("隐藏桌面图标");
        hideIcon.setTextSize(15);
        hideIcon.setTextColor(COLOR_TEXT);
        hideIcon.setPadding(dp(12), dp(6), dp(12), dp(6));
        hideIcon.setChecked(isLauncherIconHidden());
        card.addView(hideIcon, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(54)));

        TextView note = text("隐藏后可从 LSPosed 的模块设置页面重新进入。", 12, COLOR_SECONDARY);
        note.setPadding(dp(18), 0, dp(18), dp(14));
        card.addView(note);
        return card;
    }

    private View buildSaveBar() {
        LinearLayout bar = vertical();
        bar.setPadding(dp(12), dp(9), dp(12), dp(11));
        bar.setBackgroundColor(Color.WHITE);
        bar.setElevation(dp(10));

        Button save = new Button(this);
        save.setText("保存并应用配置");
        save.setTextSize(16);
        save.setTextColor(Color.WHITE);
        save.setTypeface(Typeface.DEFAULT_BOLD);
        save.setAllCaps(false);
        save.setBackground(rounded(COLOR_ACCENT, 12, 0, 0));
        save.setOnClickListener(v -> save());
        bar.addView(save, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(50)));
        return bar;
    }

    private LinearLayout createCard(String title, String subtitle, boolean showHeaderDivider) {
        LinearLayout card = vertical();
        card.setBackground(rounded(COLOR_CARD, 16, 0, 0));
        card.setElevation(dp(1));
        LinearLayout.LayoutParams cardParams = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        cardParams.bottomMargin = dp(12);
        card.setLayoutParams(cardParams);

        LinearLayout header = vertical();
        header.setPadding(dp(16), dp(14), dp(16), subtitle == null ? dp(12) : dp(11));
        TextView titleView = text(title, 18, COLOR_TEXT);
        titleView.setTypeface(Typeface.DEFAULT_BOLD);
        header.addView(titleView);
        if (subtitle != null && !subtitle.isEmpty()) {
            TextView subtitleView = text(subtitle, 12, COLOR_SECONDARY);
            LinearLayout.LayoutParams subtitleParams = wrap();
            subtitleParams.topMargin = dp(4);
            header.addView(subtitleView, subtitleParams);
        }
        card.addView(header);
        if (showHeaderDivider) card.addView(divider());
        return card;
    }

    private void showQwertyActionDialog(char letter) {
        String key = String.valueOf(letter);
        int currentAction = actionForQwertyKey(key);
        int selected = Config.menuPositionForAction(currentAction);

        AlertDialog dialog = new AlertDialog.Builder(this)
                .setTitle(Character.toUpperCase(letter) + " 键下滑执行")
                .setSingleChoiceItems(Config.ACTION_MENU_LABELS, selected, null)
                .setNegativeButton("取消", null)
                .create();
        dialog.setOnShowListener(ignored -> dialog.getListView().setOnItemClickListener(
                (parent, view, position, id) -> {
                    int action = Config.actionForMenuPosition(position);
                    assignQwertyAction(key, action);
                    dialog.dismiss();
                }));
        dialog.show();
    }

    private void assignQwertyAction(String key, int action) {
        String movedFrom = null;
        int previousAction = actionForQwertyKey(key);

        for (int i = 0; i < qwertyKeys.length; i++) {
            if (key.equals(qwertyKeys[i])) qwertyKeys[i] = "";
        }
        disabledKeys = disabledKeys.replace(key, "");

        if (action == Config.ACTION_DISABLE) {
            disabledKeys = normalizedKeys(disabledKeys + key);
        } else if (action != Config.ACTION_NONE) {
            int actionIndex = actionIndexFor(action);
            if (actionIndex >= 0) {
                String oldKey = qwertyKeys[actionIndex];
                if (oldKey != null && !oldKey.isEmpty() && !oldKey.equals(key)) {
                    movedFrom = oldKey.toUpperCase(Locale.ROOT);
                }
                qwertyKeys[actionIndex] = key;
            }
        }

        updateAllQwertyViews();
        if (movedFrom != null) {
            Toast.makeText(this,
                    "“" + Config.actionName(action) + "”已从 " + movedFrom + " 转移到 "
                            + key.toUpperCase(Locale.ROOT),
                    Toast.LENGTH_SHORT).show();
        } else if (previousAction != action) {
            Toast.makeText(this,
                    key.toUpperCase(Locale.ROOT) + " → " + Config.actionName(action),
                    Toast.LENGTH_SHORT).show();
        }
    }

    private int actionIndexFor(int action) {
        for (int i = 0; i < QWERTY_ACTIONS.length; i++) {
            if (QWERTY_ACTIONS[i] == action) return i;
        }
        return -1;
    }

    private int actionForQwertyKey(String key) {
        if (key == null || key.length() != 1) return Config.ACTION_NONE;
        if (disabledKeys.indexOf(key) >= 0) return Config.ACTION_DISABLE;
        for (int i = 0; i < qwertyKeys.length; i++) {
            if (key.equals(qwertyKeys[i])) return QWERTY_ACTIONS[i];
        }
        return Config.ACTION_NONE;
    }

    private void showT9ActionDialog(int digit) {
        int current = Config.menuPositionForAction(t9Actions[digit]);
        AlertDialog dialog = new AlertDialog.Builder(this)
                .setTitle(Config.t9Label(digit) + " 下滑执行")
                .setSingleChoiceItems(Config.ACTION_MENU_LABELS, current, null)
                .setNegativeButton("取消", null)
                .create();
        dialog.setOnShowListener(ignored -> dialog.getListView().setOnItemClickListener(
                (parent, view, position, id) -> {
                    t9Actions[digit] = Config.actionForMenuPosition(position);
                    updateT9View(digit);
                    dialog.dismiss();
                }));
        dialog.show();
    }

    private void restoreQwertyDefaults() {
        Arrays.fill(qwertyKeys, "");
        qwertyKeys[0] = "z";
        qwertyKeys[1] = "x";
        qwertyKeys[2] = "c";
        qwertyKeys[3] = "v";
        disabledKeys = "";
        updateAllQwertyViews();
        Toast.makeText(this, "已恢复默认映射，点击底部按钮保存", Toast.LENGTH_SHORT).show();
    }

    private void confirmClearQwerty() {
        new AlertDialog.Builder(this)
                .setTitle("清空 26 键映射？")
                .setMessage("将清空全部快捷功能和禁用下滑按键，保存前仍可重新设置。")
                .setNegativeButton("取消", null)
                .setPositiveButton("清空", (dialog, which) -> {
                    Arrays.fill(qwertyKeys, "");
                    disabledKeys = "";
                    updateAllQwertyViews();
                })
                .show();
    }

    private void confirmClearT9() {
        new AlertDialog.Builder(this)
                .setTitle("清空九宫格映射？")
                .setMessage("2–9 将全部恢复为未绑定，保存前仍可重新设置。")
                .setNegativeButton("取消", null)
                .setPositiveButton("清空", (dialog, which) -> {
                    for (int digit = 2; digit <= 9; digit++) {
                        t9Actions[digit] = Config.ACTION_NONE;
                        updateT9View(digit);
                    }
                })
                .show();
    }

    private void loadUiState() {
        qwertyKeys[0] = normalizedKey(prefs.getString(Config.KEY_SELECT_ALL, "z"));
        qwertyKeys[1] = normalizedKey(prefs.getString(Config.KEY_CUT, "x"));
        qwertyKeys[2] = normalizedKey(prefs.getString(Config.KEY_COPY, "c"));
        qwertyKeys[3] = normalizedKey(prefs.getString(Config.KEY_PASTE, "v"));
        qwertyKeys[4] = normalizedKey(prefs.getString(Config.KEY_PARAGRAPH_START, ""));
        qwertyKeys[5] = normalizedKey(prefs.getString(Config.KEY_PARAGRAPH_END, ""));
        qwertyKeys[6] = normalizedKey(prefs.getString(Config.KEY_SELECT_TO_PARAGRAPH_START, ""));
        qwertyKeys[7] = normalizedKey(prefs.getString(Config.KEY_SELECT_TO_PARAGRAPH_END, ""));
        qwertyKeys[8] = normalizedKey(prefs.getString(Config.KEY_OPEN_CLIPBOARD, ""));
        qwertyKeys[9] = normalizedKey(prefs.getString(Config.KEY_OPEN_QUICK_PHRASE, ""));
        disabledKeys = normalizedKeys(prefs.getString(Config.KEY_DISABLED_KEYS, ""));
        for (int digit = 2; digit <= 9; digit++) {
            t9Actions[digit] = Config.validAction(
                    prefs.getInt(Config.t9PrefKey(digit), Config.ACTION_NONE));
        }
    }

    private void save() {
        HashSet<String> used = new HashSet<>();
        for (String key : qwertyKeys) {
            if (!key.isEmpty() && !used.add(key)) {
                Toast.makeText(this, "同一个字母不能绑定多个功能", Toast.LENGTH_SHORT).show();
                return;
            }
        }
        for (int i = 0; i < disabledKeys.length(); i++) {
            if (used.contains(String.valueOf(disabledKeys.charAt(i)))) {
                Toast.makeText(this, "禁用下滑按键不能与快捷功能重复", Toast.LENGTH_SHORT).show();
                return;
            }
        }

        boolean shouldHideIcon = hideIcon.isChecked();
        int revision = prefs.getInt(Config.KEY_REVISION, 0) + 1;
        SharedPreferences.Editor editor = prefs.edit()
                .putString(Config.KEY_SELECT_ALL, qwertyKeys[0])
                .putString(Config.KEY_CUT, qwertyKeys[1])
                .putString(Config.KEY_COPY, qwertyKeys[2])
                .putString(Config.KEY_PASTE, qwertyKeys[3])
                .putString(Config.KEY_PARAGRAPH_START, qwertyKeys[4])
                .putString(Config.KEY_PARAGRAPH_END, qwertyKeys[5])
                .putString(Config.KEY_SELECT_TO_PARAGRAPH_START, qwertyKeys[6])
                .putString(Config.KEY_SELECT_TO_PARAGRAPH_END, qwertyKeys[7])
                .putString(Config.KEY_OPEN_CLIPBOARD, qwertyKeys[8])
                .putString(Config.KEY_OPEN_QUICK_PHRASE, qwertyKeys[9])
                .putString(Config.KEY_DISABLED_KEYS, disabledKeys)
                .remove("text_start")
                .remove("text_end")
                .remove("copy_all")
                .remove("cut_all")
                .putInt(Config.KEY_THRESHOLD, threshold.getProgress() + 6)
                .putInt(Config.KEY_T9_THRESHOLD, t9Threshold.getProgress() + 10)
                .putBoolean(Config.KEY_VIBRATION, vibration.isChecked())
                .putBoolean(Config.KEY_SHOW_KEY_LABELS, showKeyLabels.isChecked())
                .putBoolean(Config.KEY_SHOW_TRIGGER_HINT, showTriggerHint.isChecked())
                .putBoolean(Config.KEY_HIDE_ICON, shouldHideIcon)
                .putInt(Config.KEY_REVISION, revision);

        for (int digit = 2; digit <= 9; digit++) {
            editor.putInt(Config.t9PrefKey(digit), t9Actions[digit]);
        }

        if (!editor.commit()) {
            Toast.makeText(this, "配置保存失败", Toast.LENGTH_SHORT).show();
            return;
        }

        Intent changed = new Intent(Config.ACTION_CONFIG_CHANGED);
        changed.setPackage("com.tencent.wetype");
        changed.putExtra(Config.EXTRA_SNAPSHOT, true);
        changed.putExtra(Config.KEY_SELECT_ALL, qwertyKeys[0]);
        changed.putExtra(Config.KEY_CUT, qwertyKeys[1]);
        changed.putExtra(Config.KEY_COPY, qwertyKeys[2]);
        changed.putExtra(Config.KEY_PASTE, qwertyKeys[3]);
        changed.putExtra(Config.KEY_PARAGRAPH_START, qwertyKeys[4]);
        changed.putExtra(Config.KEY_PARAGRAPH_END, qwertyKeys[5]);
        changed.putExtra(Config.KEY_SELECT_TO_PARAGRAPH_START, qwertyKeys[6]);
        changed.putExtra(Config.KEY_SELECT_TO_PARAGRAPH_END, qwertyKeys[7]);
        changed.putExtra(Config.KEY_OPEN_CLIPBOARD, qwertyKeys[8]);
        changed.putExtra(Config.KEY_OPEN_QUICK_PHRASE, qwertyKeys[9]);
        changed.putExtra(Config.KEY_DISABLED_KEYS, disabledKeys);
        changed.putExtra(Config.KEY_THRESHOLD, threshold.getProgress() + 6);
        changed.putExtra(Config.KEY_T9_THRESHOLD, t9Threshold.getProgress() + 10);
        changed.putExtra(Config.KEY_VIBRATION, vibration.isChecked());
        changed.putExtra(Config.KEY_SHOW_KEY_LABELS, showKeyLabels.isChecked());
        changed.putExtra(Config.KEY_SHOW_TRIGGER_HINT, showTriggerHint.isChecked());
        changed.putExtra(Config.KEY_REVISION, revision);
        for (int digit = 2; digit <= 9; digit++) {
            changed.putExtra(Config.t9PrefKey(digit), t9Actions[digit]);
        }
        sendBroadcast(changed);

        setLauncherIconHidden(shouldHideIcon);
        Toast.makeText(this,
                shouldHideIcon
                        ? "已保存并隐藏桌面图标，可从 LSPosed 模块设置重新进入"
                        : "配置已保存并同步到微信输入法",
                Toast.LENGTH_LONG).show();
    }

    private void updateAllQwertyViews() {
        for (char key = 'a'; key <= 'z'; key++) updateQwertyKeyView(key);
    }

    private void updateQwertyKeyView(char letter) {
        int index = letter - 'a';
        LinearLayout keyView = qwertyKeyViews[index];
        TextView actionView = qwertyActionViews[index];
        if (keyView == null || actionView == null) return;

        int action = actionForQwertyKey(String.valueOf(letter));
        actionView.setText(shortActionName(action));
        if (action == Config.ACTION_DISABLE) {
            actionView.setTextColor(COLOR_DANGER);
            keyView.setBackground(rounded(COLOR_DANGER_SOFT, 9, 1, Color.rgb(245, 190, 190)));
        } else if (action == Config.ACTION_NONE) {
            actionView.setTextColor(COLOR_SECONDARY);
            keyView.setBackground(rounded(COLOR_KEY_IDLE, 9, 1, COLOR_KEY_STROKE));
        } else {
            actionView.setTextColor(COLOR_ACCENT);
            keyView.setBackground(rounded(COLOR_ACCENT_SOFT, 9, 1, Color.rgb(190, 210, 245)));
        }
    }

    private void updateT9View(int digit) {
        if (t9ActionViews[digit] == null || t9KeyViews[digit] == null) return;
        int action = t9Actions[digit];
        t9ActionViews[digit].setText(shortActionName(action));
        if (action == Config.ACTION_DISABLE) {
            t9ActionViews[digit].setTextColor(COLOR_DANGER);
            t9KeyViews[digit].setBackground(
                    rounded(COLOR_DANGER_SOFT, 12, 1, Color.rgb(245, 190, 190)));
        } else if (action == Config.ACTION_NONE) {
            t9ActionViews[digit].setTextColor(COLOR_SECONDARY);
            t9KeyViews[digit].setBackground(rounded(COLOR_KEY_IDLE, 12, 1, COLOR_KEY_STROKE));
        } else {
            t9ActionViews[digit].setTextColor(COLOR_ACCENT);
            t9KeyViews[digit].setBackground(
                    rounded(COLOR_ACCENT_SOFT, 12, 1, Color.rgb(190, 210, 245)));
        }
    }

    private String shortActionName(int action) {
        switch (Config.validAction(action)) {
            case Config.ACTION_SELECT_ALL: return "全选";
            case Config.ACTION_CUT: return "剪切";
            case Config.ACTION_COPY: return "复制";
            case Config.ACTION_PASTE: return "粘贴";
            case Config.ACTION_DISABLE: return "禁用";
            case Config.ACTION_PARAGRAPH_START: return "段首";
            case Config.ACTION_PARAGRAPH_END: return "段尾";
            case Config.ACTION_SELECT_TO_PARAGRAPH_START: return "选段首";
            case Config.ACTION_SELECT_TO_PARAGRAPH_END: return "选段尾";
            case Config.ACTION_OPEN_CLIPBOARD: return "剪贴板";
            case Config.ACTION_OPEN_QUICK_PHRASE: return "快捷语";
            default: return "—";
        }
    }

    private String normalizedKey(String value) {
        if (value == null) return "";
        String normalized = value.trim().toLowerCase(Locale.ROOT);
        if (normalized.length() != 1) return "";
        char c = normalized.charAt(0);
        return c >= 'a' && c <= 'z' ? normalized : "";
    }

    private String normalizedKeys(String raw) {
        if (raw == null) return "";
        boolean[] seen = new boolean[26];
        StringBuilder result = new StringBuilder(26);
        raw = raw.toLowerCase(Locale.ROOT);
        for (int i = 0; i < raw.length(); i++) {
            char c = raw.charAt(i);
            if (c < 'a' || c > 'z' || seen[c - 'a']) continue;
            seen[c - 'a'] = true;
            result.append(c);
        }
        return result.toString();
    }

    private boolean isLauncherIconHidden() {
        ComponentName component = new ComponentName(this, LAUNCHER_ALIAS);
        int state = getPackageManager().getComponentEnabledSetting(component);
        if (state == PackageManager.COMPONENT_ENABLED_STATE_DISABLED
                || state == PackageManager.COMPONENT_ENABLED_STATE_DISABLED_USER
                || state == PackageManager.COMPONENT_ENABLED_STATE_DISABLED_UNTIL_USED) return true;
        if (state == PackageManager.COMPONENT_ENABLED_STATE_ENABLED) return false;
        return prefs.getBoolean(Config.KEY_HIDE_ICON, false);
    }

    private void setLauncherIconHidden(boolean hidden) {
        ComponentName component = new ComponentName(this, LAUNCHER_ALIAS);
        int state = hidden
                ? PackageManager.COMPONENT_ENABLED_STATE_DISABLED
                : PackageManager.COMPONENT_ENABLED_STATE_ENABLED;
        getPackageManager().setComponentEnabledSetting(
                component, state, PackageManager.DONT_KILL_APP);
    }

    private interface ThresholdChanged { void onChanged(int value); }

    private SeekBar createThreshold(int value, int min, int max, ThresholdChanged listener) {
        SeekBar seekBar = new SeekBar(this);
        seekBar.setMax(max - min);
        seekBar.setProgress(value - min);
        seekBar.setPadding(0, dp(4), 0, 0);
        seekBar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override public void onProgressChanged(SeekBar bar, int progress, boolean fromUser) {
                listener.onChanged(progress + min);
            }
            @Override public void onStartTrackingTouch(SeekBar bar) {}
            @Override public void onStopTrackingTouch(SeekBar bar) {}
        });
        return seekBar;
    }

    private TextView valueBadge(String value) {
        TextView view = text(value, 13, COLOR_ACCENT);
        view.setGravity(Gravity.CENTER);
        view.setPadding(dp(10), dp(4), dp(10), dp(4));
        view.setBackground(rounded(COLOR_ACCENT_SOFT, 12, 0, 0));
        return view;
    }

    private TextView smallAction(String value, boolean danger) {
        TextView view = text(value, 13, danger ? COLOR_DANGER : COLOR_ACCENT);
        view.setGravity(Gravity.CENTER);
        view.setTypeface(Typeface.DEFAULT_BOLD);
        view.setBackground(rounded(danger ? COLOR_DANGER_SOFT : COLOR_ACCENT_SOFT, 10, 0, 0));
        view.setClickable(true);
        return view;
    }

    private View divider() {
        View divider = new View(this);
        divider.setBackgroundColor(COLOR_DIVIDER);
        divider.setLayoutParams(new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(1)));
        return divider;
    }

    private GradientDrawable rounded(int fillColor, int radiusDp, int strokeWidthDp, int strokeColor) {
        GradientDrawable drawable = new GradientDrawable();
        drawable.setColor(fillColor);
        drawable.setCornerRadius(dp(radiusDp));
        if (strokeWidthDp > 0) drawable.setStroke(dp(strokeWidthDp), strokeColor);
        return drawable;
    }

    private TextView text(String value, int sp, int color) {
        TextView textView = new TextView(this);
        textView.setText(value);
        textView.setTextSize(sp);
        textView.setTextColor(color);
        return textView;
    }

    private LinearLayout vertical() {
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        return layout;
    }

    private LinearLayout horizontal() {
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.HORIZONTAL);
        return layout;
    }

    private LinearLayout.LayoutParams wrap() {
        return new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
    }

    private static int clamp(int value, int min, int max, int fallback) {
        return value < min || value > max ? fallback : value;
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }
}
