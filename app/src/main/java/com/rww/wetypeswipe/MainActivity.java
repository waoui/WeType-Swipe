package com.rww.wetypeswipe;

import android.app.Activity;
import android.content.ComponentName;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.graphics.Typeface;
import android.os.Bundle;
import android.text.InputFilter;
import android.text.InputType;
import android.view.Gravity;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.SeekBar;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import java.util.HashSet;
import java.util.Locale;

public final class MainActivity extends Activity {
    private static final String LAUNCHER_ALIAS = "com.rww.wetypeswipe.LauncherAlias";

    private SharedPreferences prefs;
    private EditText selectAll, cut, copy, paste, disabledKeys;
    private SeekBar threshold, t9Threshold;
    private TextView thresholdValue, t9ThresholdValue;
    private CheckBox vibration;
    private CheckBox hideIcon;
    private final Spinner[] t9Spinners = new Spinner[10];

    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        setTitle("微信输入法下滑快捷键");
        prefs = getSharedPreferences(Config.PREFS, MODE_PRIVATE);

        ScrollView scroll = new ScrollView(this);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(20), dp(18), dp(20), dp(24));
        scroll.addView(root);

        TextView title = text("微信输入法下滑快捷键", 22);
        title.setTypeface(Typeface.DEFAULT_BOLD);
        root.addView(title);

        TextView version = text("v1.8.6 · Modern Xposed API 102 · 九宫格配置缓存同步", 13);
        version.setPadding(0, dp(4), 0, dp(12));
        root.addView(version);

        addSection(root, "26 键配置");
        TextView note = text(
                "功能项填写一个 A-Z 字母，留空表示关闭。未绑定按键完全放行；禁用下滑可填写多个字母。",
                14);
        note.setPadding(0, 0, 0, dp(8));
        root.addView(note);

        selectAll = addSingleKeyRow(root, "全选", prefs.getString(Config.KEY_SELECT_ALL, "z"));
        cut = addSingleKeyRow(root, "剪切", prefs.getString(Config.KEY_CUT, "x"));
        copy = addSingleKeyRow(root, "复制", prefs.getString(Config.KEY_COPY, "c"));
        paste = addSingleKeyRow(root, "粘贴", prefs.getString(Config.KEY_PASTE, "v"));
        disabledKeys = addMultiKeyRow(root, "禁用下滑", prefs.getString(Config.KEY_DISABLED_KEYS, ""));

        int savedThreshold = clamp(prefs.getInt(Config.KEY_THRESHOLD, 12), 6, 40, 12);
        thresholdValue = text("26 键触发距离：" + savedThreshold + " dp", 16);
        thresholdValue.setPadding(0, dp(12), 0, 0);
        root.addView(thresholdValue);
        threshold = addThreshold(root, savedThreshold, 6, 40, value ->
                thresholdValue.setText("26 键触发距离：" + value + " dp"));

        addSection(root, "九宫格配置");
        TextView t9Note = text(
                "自动识别 2–9 实体键。九宫格映射与 26 键完全独立；正常点击仍由微信输入法处理。",
                14);
        t9Note.setPadding(0, 0, 0, dp(8));
        root.addView(t9Note);

        ArrayAdapter<String> actionAdapter = new ArrayAdapter<>(
                this, android.R.layout.simple_spinner_item, Config.ACTION_LABELS);
        actionAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        for (int digit = 2; digit <= 9; digit++) {
            int action = Config.validAction(prefs.getInt(Config.t9PrefKey(digit), Config.ACTION_NONE));
            t9Spinners[digit] = addT9Row(root, Config.t9Label(digit), actionAdapter, action);
        }

        int savedT9Threshold = clamp(prefs.getInt(Config.KEY_T9_THRESHOLD, 20), 10, 48, 20);
        t9ThresholdValue = text("九宫格触发距离：" + savedT9Threshold + " dp", 16);
        t9ThresholdValue.setPadding(0, dp(12), 0, 0);
        root.addView(t9ThresholdValue);
        t9Threshold = addThreshold(root, savedT9Threshold, 10, 48, value ->
                t9ThresholdValue.setText("九宫格触发距离：" + value + " dp"));

        addSection(root, "通用设置");

        vibration = new CheckBox(this);
        vibration.setText("触发时额外震动");
        vibration.setTextSize(16);
        vibration.setChecked(prefs.getBoolean(Config.KEY_VIBRATION, true));
        root.addView(vibration);

        TextView vibrationNote = text("关闭后模块不会主动调用震动；输入法自身按键震动需在微信输入法设置中关闭。", 12);
        vibrationNote.setPadding(dp(32), 0, 0, dp(4));
        root.addView(vibrationNote);


        hideIcon = new CheckBox(this);
        hideIcon.setText("隐藏桌面图标（隐藏后可从 LSPosed 模块设置进入）");
        hideIcon.setTextSize(16);
        hideIcon.setChecked(isLauncherIconHidden());
        root.addView(hideIcon);

        Button save = new Button(this);
        save.setText("保存配置");
        LinearLayout.LayoutParams buttonParams = new LinearLayout.LayoutParams(-1, dp(52));
        buttonParams.topMargin = dp(14);
        root.addView(save, buttonParams);
        save.setOnClickListener(view -> save());


        TextView footer = text(
                "配置保存时会同步到微信输入法自身缓存；九宫格子进程首次启动即可读取。",
                13);
        footer.setPadding(0, dp(14), 0, 0);
        root.addView(footer);

        setContentView(scroll);
    }

    @Override protected void onResume() {
        super.onResume();
        if (hideIcon != null) hideIcon.setChecked(isLauncherIconHidden());
    }

    private void addSection(LinearLayout root, String value) {
        TextView title = text(value, 18);
        title.setTypeface(Typeface.DEFAULT_BOLD);
        title.setPadding(0, dp(16), 0, dp(8));
        root.addView(title);
    }

    private EditText addSingleKeyRow(LinearLayout root, String label, String value) {
        LinearLayout row = new LinearLayout(this);
        row.setGravity(Gravity.CENTER_VERTICAL);
        TextView title = text("下滑执行" + label, 16);
        row.addView(title, new LinearLayout.LayoutParams(0, dp(52), 1));

        EditText editText = new EditText(this);
        editText.setGravity(Gravity.CENTER);
        editText.setText(value == null ? "" : value.toUpperCase(Locale.ROOT));
        editText.setTextSize(18);
        editText.setSingleLine(true);
        editText.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_CAP_CHARACTERS);
        editText.setFilters(new InputFilter[]{new InputFilter.LengthFilter(1)});
        row.addView(editText, new LinearLayout.LayoutParams(dp(70), dp(52)));
        root.addView(row);
        return editText;
    }

    private EditText addMultiKeyRow(LinearLayout root, String label, String value) {
        LinearLayout row = new LinearLayout(this);
        row.setGravity(Gravity.CENTER_VERTICAL);
        TextView title = text(label + "按键", 16);
        row.addView(title, new LinearLayout.LayoutParams(0, dp(52), 1));

        EditText editText = new EditText(this);
        editText.setGravity(Gravity.CENTER);
        editText.setHint("例如 ABQ");
        editText.setText(value == null ? "" : value.toUpperCase(Locale.ROOT));
        editText.setTextSize(17);
        editText.setSingleLine(true);
        editText.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_CAP_CHARACTERS);
        editText.setFilters(new InputFilter[]{new InputFilter.LengthFilter(26)});
        row.addView(editText, new LinearLayout.LayoutParams(dp(130), dp(52)));
        root.addView(row);
        return editText;
    }

    private Spinner addT9Row(LinearLayout root, String label, ArrayAdapter<String> adapter, int action) {
        LinearLayout row = new LinearLayout(this);
        row.setGravity(Gravity.CENTER_VERTICAL);
        TextView title = text(label, 16);
        row.addView(title, new LinearLayout.LayoutParams(0, dp(52), 1));

        Spinner spinner = new Spinner(this);
        spinner.setAdapter(adapter);
        spinner.setSelection(Config.validAction(action));
        row.addView(spinner, new LinearLayout.LayoutParams(dp(145), dp(52)));
        root.addView(row);
        return spinner;
    }

    private interface ThresholdChanged { void onChanged(int value); }

    private SeekBar addThreshold(LinearLayout root, int value, int min, int max, ThresholdChanged listener) {
        SeekBar seekBar = new SeekBar(this);
        seekBar.setMax(max - min);
        seekBar.setProgress(value - min);
        seekBar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override public void onProgressChanged(SeekBar bar, int progress, boolean fromUser) {
                listener.onChanged(progress + min);
            }
            @Override public void onStartTrackingTouch(SeekBar bar) {}
            @Override public void onStopTrackingTouch(SeekBar bar) {}
        });
        root.addView(seekBar);
        return seekBar;
    }

    private void save() {
        String[] functionKeys = { key(selectAll), key(cut), key(copy), key(paste) };
        HashSet<String> used = new HashSet<>();
        for (String value : functionKeys) {
            if (!value.isEmpty() && !used.add(value)) {
                Toast.makeText(this, "同一个字母不能绑定多个功能", Toast.LENGTH_SHORT).show();
                return;
            }
        }

        String disabled = keys(disabledKeys);
        for (int i = 0; i < disabled.length(); i++) {
            if (used.contains(String.valueOf(disabled.charAt(i)))) {
                Toast.makeText(this, "禁用下滑按键不能与功能绑定重复", Toast.LENGTH_SHORT).show();
                return;
            }
        }

        boolean shouldHideIcon = hideIcon.isChecked();
        int revision = prefs.getInt(Config.KEY_REVISION, 0) + 1;
        SharedPreferences.Editor editor = prefs.edit()
                .putString(Config.KEY_SELECT_ALL, functionKeys[0])
                .putString(Config.KEY_CUT, functionKeys[1])
                .putString(Config.KEY_COPY, functionKeys[2])
                .putString(Config.KEY_PASTE, functionKeys[3])
                .putString(Config.KEY_DISABLED_KEYS, disabled)
                .remove("text_start")
                .remove("text_end")
                .remove("copy_all")
                .remove("cut_all")
                .putInt(Config.KEY_THRESHOLD, threshold.getProgress() + 6)
                .putInt(Config.KEY_T9_THRESHOLD, t9Threshold.getProgress() + 10)
                .putBoolean(Config.KEY_VIBRATION, vibration.isChecked())
                .putBoolean(Config.KEY_HIDE_ICON, shouldHideIcon)
                .putInt(Config.KEY_REVISION, revision);

        for (int digit = 2; digit <= 9; digit++) {
            editor.putInt(Config.t9PrefKey(digit), t9Spinners[digit].getSelectedItemPosition());
        }

        if (!editor.commit()) {
            Toast.makeText(this, "配置保存失败", Toast.LENGTH_SHORT).show();
            return;
        }

        // 将完整配置随显式广播发送给微信输入法的常驻进程。
        // 常驻进程会写入微信输入法自身的私有缓存，后续九宫格 :hld 子进程启动时直接读取。
        Intent changed = new Intent(Config.ACTION_CONFIG_CHANGED);
        changed.setPackage("com.tencent.wetype");
        changed.putExtra(Config.EXTRA_SNAPSHOT, true);
        changed.putExtra(Config.KEY_SELECT_ALL, functionKeys[0]);
        changed.putExtra(Config.KEY_CUT, functionKeys[1]);
        changed.putExtra(Config.KEY_COPY, functionKeys[2]);
        changed.putExtra(Config.KEY_PASTE, functionKeys[3]);
        changed.putExtra(Config.KEY_DISABLED_KEYS, disabled);
        changed.putExtra(Config.KEY_THRESHOLD, threshold.getProgress() + 6);
        changed.putExtra(Config.KEY_T9_THRESHOLD, t9Threshold.getProgress() + 10);
        changed.putExtra(Config.KEY_VIBRATION, vibration.isChecked());
        changed.putExtra(Config.KEY_REVISION, revision);
        for (int digit = 2; digit <= 9; digit++) {
            changed.putExtra(Config.t9PrefKey(digit), t9Spinners[digit].getSelectedItemPosition());
        }
        sendBroadcast(changed);

        setLauncherIconHidden(shouldHideIcon);
        Toast.makeText(this,
                shouldHideIcon ? "已保存并隐藏桌面图标，可从 LSPosed 模块设置重新进入" : "已保存，配置将在输入法中自动生效",
                Toast.LENGTH_LONG).show();
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
        getPackageManager().setComponentEnabledSetting(component, state, PackageManager.DONT_KILL_APP);
    }

    private String key(EditText editText) {
        String value = editText.getText().toString().trim().toLowerCase(Locale.ROOT);
        return value.length() == 1 && value.charAt(0) >= 'a' && value.charAt(0) <= 'z' ? value : "";
    }

    private String keys(EditText editText) {
        String raw = editText.getText().toString().toLowerCase(Locale.ROOT);
        boolean[] seen = new boolean[26];
        StringBuilder result = new StringBuilder(26);
        for (int i = 0; i < raw.length(); i++) {
            char c = raw.charAt(i);
            if (c < 'a' || c > 'z' || seen[c - 'a']) continue;
            seen[c - 'a'] = true;
            result.append(c);
        }
        return result.toString();
    }

    private static int clamp(int value, int min, int max, int fallback) {
        return value < min || value > max ? fallback : value;
    }

    private TextView text(String value, int sp) {
        TextView textView = new TextView(this);
        textView.setText(value);
        textView.setTextSize(sp);
        return textView;
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }
}
