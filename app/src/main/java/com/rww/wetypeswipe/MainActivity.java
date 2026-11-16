package com.rww.wetypeswipe;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.ComponentName;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.content.res.Configuration;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.graphics.Insets;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.RippleDrawable;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.view.WindowInsets;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

/**
 * Non-editing maintenance entry. WeType owns the authoritative gesture configuration.
 * This UI intentionally has no independent ConfigCodec save or live key binding editor.
 */
public final class MainActivity extends Activity {
    private static final String TAG = "WeTypeSwipeMaintenance";
    private static final String TARGET = "com.tencent.wetype";
    private static final String LAUNCHER_ALIAS = "com.rww.wetypeswipe.LauncherAlias";
    private static final String OPEN_EMBEDDED_EXTRA =
            "com.rww.wetypeswipe.extra.OPEN_EMBEDDED_SETTINGS";
    private static final int EXPORT_LEGACY_REQUEST = 4131;

    private SharedPreferences legacyPrefs;
    private boolean dark;
    private int pageColor;
    private int cardColor;
    private int primaryText;
    private int secondaryText;
    private int dividerColor;
    private int accentColor;
    private int softColor;

    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        setTitle("滑动快捷键 · 维护中心");
        legacyPrefs = getSharedPreferences(Config.PREFS, MODE_PRIVATE);
        configurePalette();
        setContentView(buildPage());
    }

    private void configurePalette() {
        dark = (getResources().getConfiguration().uiMode
                & Configuration.UI_MODE_NIGHT_MASK) == Configuration.UI_MODE_NIGHT_YES;
        pageColor = dark ? Color.rgb(17, 22, 32) : Color.rgb(245, 247, 251);
        cardColor = dark ? Color.rgb(29, 36, 49) : Color.WHITE;
        primaryText = dark ? Color.rgb(242, 246, 252) : Color.rgb(29, 39, 56);
        secondaryText = dark ? Color.rgb(172, 184, 201) : Color.rgb(105, 117, 134);
        dividerColor = dark ? Color.rgb(54, 63, 79) : Color.rgb(233, 238, 245);
        accentColor = dark ? Color.rgb(100, 159, 255) : Color.rgb(37, 105, 220);
        softColor = dark ? Color.rgb(39, 56, 78) : Color.rgb(232, 241, 255);

        getWindow().setStatusBarColor(pageColor);
        getWindow().setNavigationBarColor(pageColor);
        getWindow().getDecorView().setSystemUiVisibility(dark ? 0
                : View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR
                        | View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);
    }

    private View buildPage() {
        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setClipToPadding(false);
        scroll.setBackgroundColor(pageColor);
        // On edge-to-edge ROMs avoid obscuring the header and last action, but do
        // not double-apply padding when Android already fits the decor to system bars.
        scroll.setOnApplyWindowInsetsListener((view, insets) -> {
            final int status, navigation;
            if (Build.VERSION.SDK_INT >= 30) {
                Insets bars = insets.getInsets(WindowInsets.Type.systemBars());
                status = bars.top;
                navigation = bars.bottom;
            } else {
                status = insets.getSystemWindowInsetTop();
                navigation = insets.getSystemWindowInsetBottom();
            }
            int[] location = new int[2];
            view.getLocationOnScreen(location);
            int topPadding = Math.max(0, status - location[1]);
            int rootHeight = view.getRootView().getHeight();
            int bottomPadding = rootHeight <= 0 ? 0
                    : Math.max(0, location[1] + view.getHeight()
                            - (rootHeight - navigation));
            view.setPadding(0, topPadding, 0, bottomPadding);
            return insets;
        });

        LinearLayout content = vertical();
        content.setPadding(dp(18), dp(22), dp(18), dp(28));
        scroll.addView(content);

        TextView eyebrow = label("WE TYPE · SWIPE", 11, accentColor, true);
        eyebrow.setLetterSpacing(.08f);
        content.addView(eyebrow);
        TextView title = label("模块维护中心", 25, primaryText, true);
        LinearLayout.LayoutParams titleParams = wrap();
        titleParams.topMargin = dp(7);
        content.addView(title, titleParams);

        TextView subtitle = label("键位设置统一在微信输入法内完成", 14, secondaryText, false);
        LinearLayout.LayoutParams subtitleParams = wrap();
        subtitleParams.topMargin = dp(6);
        subtitleParams.bottomMargin = dp(20);
        content.addView(subtitle, subtitleParams);

        LinearLayout hero = vertical();
        hero.setPadding(dp(18), dp(19), dp(18), dp(19));
        hero.setBackground(rounded(accentColor, 18, 0, 0));
        hero.setClickable(true);
        hero.setFocusable(true);
        hero.setContentDescription("打开微信输入法内置模块设置");
        TextView caption = label("唯一配置入口", 12, Color.rgb(221, 235, 255), true);
        hero.addView(caption);
        TextView primary = label("打开内置模块设置  ›", 19, Color.WHITE, true);
        LinearLayout.LayoutParams primaryParams = wrap();
        primaryParams.topMargin = dp(7);
        hero.addView(primary, primaryParams);
        TextView hint = label("26 键 · 九宫格 · 上下滑 · 备份恢复",
                12, Color.rgb(224, 235, 255), false);
        LinearLayout.LayoutParams hintParams = wrap();
        hintParams.topMargin = dp(6);
        hero.addView(hint, hintParams);
        hero.setOnClickListener(v -> openEmbeddedSettings());
        LinearLayout.LayoutParams heroParams = fill();
        heroParams.bottomMargin = dp(18);
        content.addView(hero, heroParams);

        LinearLayout status = card();
        TextView statusTitle = label("配置来源", 15, primaryText, true);
        status.addView(statusTitle);
        TextView statusText = label("微信输入法内部配置 · 唯一生效来源", 13, accentColor, true);
        LinearLayout.LayoutParams statusParams = wrap();
        statusParams.topMargin = dp(6);
        status.addView(statusText, statusParams);
        TextView statusTip = label("此页面不保存第二份按键配置。修改或导出当前配置，请进入上方内置设置。",
                12, secondaryText, false);
        LinearLayout.LayoutParams tipParams = wrap();
        tipParams.topMargin = dp(7);
        status.addView(statusTip, tipParams);
        LinearLayout.LayoutParams statusCardParams = fill();
        statusCardParams.bottomMargin = dp(20);
        content.addView(status, statusCardParams);

        addSectionHeading(content, "维护工具");
        LinearLayout tools = vertical();
        tools.setBackground(rounded(cardColor, 16, dividerColor, dp(1)));
        boolean hasLegacy = hasLegacyBackup();
        addTool(tools, "导出旧版模块配置",
                hasLegacy ? "保存旧版历史备份 TXT，不是当前生效配置"
                          : "未检测到旧版独立配置，可从内置设置备份当前配置",
                () -> exportLegacyBackup());
        tools.addView(separator());
        addTool(tools, "复制诊断信息", "仅复制版本与环境信息，不含输入内容",
                () -> copyDiagnostics());
        tools.addView(separator());
        addTool(tools, isIconHidden() ? "显示桌面图标" : "隐藏桌面图标",
                "隐藏后仍可通过 LSPosed 打开维护中心",
                () -> confirmToggleIcon());
        LinearLayout.LayoutParams toolsParams = fill();
        toolsParams.bottomMargin = dp(20);
        content.addView(tools, toolsParams);

        addSectionHeading(content, "版本与恢复");
        LinearLayout about = card();
        about.addView(label("版本  " + getModuleVersion(), 14, primaryText, true));
        TextView revision = label("旧版独立配置备份  " + (hasLegacy ? "可用" : "未检测到"),
                12, secondaryText, false);
        LinearLayout.LayoutParams revisionParams = wrap();
        revisionParams.topMargin = dp(7);
        about.addView(revision, revisionParams);
        TextView recovery = label(
                "备用入口：微信输入法 → 关于 → 连续点击图标 5 次。"
                        + "\n如果新内置入口失效，请先确认 LSPosed 已启用且作用域包含微信输入法。",
                12, secondaryText, false);
        LinearLayout.LayoutParams recoveryParams = wrap();
        recoveryParams.topMargin = dp(12);
        about.addView(recovery, recoveryParams);
        content.addView(about, fill());

        return scroll;
    }

    private LinearLayout card() {
        LinearLayout card = vertical();
        card.setPadding(dp(17), dp(16), dp(17), dp(16));
        card.setBackground(rounded(cardColor, 16, dividerColor, dp(1)));
        return card;
    }

    private void addSectionHeading(LinearLayout content, String title) {
        TextView heading = label(title, 14, secondaryText, true);
        LinearLayout.LayoutParams params = wrap();
        params.leftMargin = dp(3);
        params.bottomMargin = dp(10);
        content.addView(heading, params);
    }

    private void addTool(LinearLayout container, String title, String description, Runnable onClick) {
        LinearLayout row = vertical();
        row.setPadding(dp(16), dp(15), dp(16), dp(15));
        row.setMinimumHeight(dp(68));
        row.setClickable(true);
        row.setFocusable(true);
        row.setContentDescription(title + "。 " + description);
        row.setBackground(new RippleDrawable(
                ColorStateList.valueOf(dark ? Color.argb(45, 180, 200, 250)
                        : Color.argb(35, 38, 105, 220)), null, null));
        row.addView(label(title + "  ›", 15, primaryText, true));
        TextView note = label(description, 12, secondaryText, false);
        LinearLayout.LayoutParams params = wrap();
        params.topMargin = dp(4);
        row.addView(note, params);
        row.setOnClickListener(v -> onClick.run());
        container.addView(row, fill());
    }

    private View separator() {
        View view = new View(this);
        view.setBackgroundColor(dividerColor);
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(1));
        params.leftMargin = dp(16);
        params.rightMargin = dp(16);
        view.setLayoutParams(params);
        return view;
    }

    private void openEmbeddedSettings() {
        try {
            Intent target = getPackageManager().getLaunchIntentForPackage(TARGET);
            if (target == null) {
                Toast.makeText(this,
                        "未找到微信输入法启动入口；请从输入法“关于”页连续点击图标 5 次",
                        Toast.LENGTH_LONG).show();
                return;
            }
            target.putExtra(OPEN_EMBEDDED_EXTRA, true);
            target.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
            startActivity(target);
        } catch (RuntimeException error) {
            Log.e(TAG, "Unable to open target embedded settings", error);
            Toast.makeText(this,
                    "无法启动内置设置，请检查 LSPosed 作用域；或从微信输入法关于页五击进入",
                    Toast.LENGTH_LONG).show();
        }
    }

    private boolean hasLegacyBackup() {
        return legacyPrefs.contains(Config.KEY_REVISION);
    }

    private void exportLegacyBackup() {
        if (!hasLegacyBackup()) {
            Toast.makeText(this, "没有旧版独立配置，当前配置请从内置设置导出",
                    Toast.LENGTH_LONG).show();
            return;
        }
        try {
            Intent choose = new Intent(Intent.ACTION_CREATE_DOCUMENT);
            choose.addCategory(Intent.CATEGORY_OPENABLE);
            choose.setType("text/plain");
            choose.putExtra(Intent.EXTRA_TITLE, "WeType-Swipe-旧模块历史配置.txt");
            startActivityForResult(choose, EXPORT_LEGACY_REQUEST);
        } catch (RuntimeException error) {
            Log.e(TAG, "Failed to open legacy backup picker", error);
            Toast.makeText(this, "无法选择备份文件位置：" + error.getMessage(),
                    Toast.LENGTH_LONG).show();
        }
    }

    @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode != EXPORT_LEGACY_REQUEST || resultCode != RESULT_OK
                || data == null || data.getData() == null) return;
        Uri uri = data.getData();
        try (OutputStream stream = getContentResolver().openOutputStream(uri, "wt")) {
            if (stream == null) throw new java.io.IOException("无法打开输出文件");
            stream.write(ConfigBackup.exportText(ConfigCodec.fromPreferences(legacyPrefs))
                    .getBytes(StandardCharsets.UTF_8));
            stream.flush();
            Toast.makeText(this, "旧版配置已导出，模块内原始备份仍保留", Toast.LENGTH_LONG).show();
        } catch (Exception error) {
            Log.e(TAG, "Failed to export legacy config", error);
            Toast.makeText(this, "历史配置导出失败：" + error.getMessage(),
                    Toast.LENGTH_LONG).show();
        }
    }

    private String getModuleVersion() {
        try {
            String name = getPackageManager().getPackageInfo(getPackageName(), 0).versionName;
            return name == null ? "unknown" : name;
        } catch (PackageManager.NameNotFoundException error) {
            Log.w(TAG, "Unable to read installed module version", error);
            return "unknown";
        }
    }

    private void copyDiagnostics() {
        String details = "WeType-Swipe " + getModuleVersion()
                + "\nAndroid API " + android.os.Build.VERSION.SDK_INT
                + "\nModule package: " + getPackageName()
                + "\nTarget: " + TARGET
                + "\nLegacy backup available: " + hasLegacyBackup();
        ClipboardManager clipboard = (ClipboardManager) getSystemService(CLIPBOARD_SERVICE);
        if (clipboard == null) {
            Toast.makeText(this, "剪贴板不可用", Toast.LENGTH_LONG).show();
            return;
        }
        clipboard.setPrimaryClip(ClipData.newPlainText("WeType-Swipe 诊断", details));
        Toast.makeText(this, "诊断信息已复制，不含按键文字或账号信息", Toast.LENGTH_SHORT).show();
    }

    private void confirmToggleIcon() {
        new AlertDialog.Builder(this)
                .setTitle(isIconHidden() ? "显示模块桌面图标？" : "隐藏模块桌面图标？")
                .setMessage("隐藏后仍可通过 LSPosed 模块列表进入维护中心。")
                .setNegativeButton("取消", null)
                .setPositiveButton(isIconHidden() ? "显示图标" : "隐藏图标",
                        (dialog, which) -> {
                            try {
                                boolean hide = !isIconHidden();
                                ComponentName component = new ComponentName(this, LAUNCHER_ALIAS);
                                int state = hide
                                        ? PackageManager.COMPONENT_ENABLED_STATE_DISABLED
                                        : PackageManager.COMPONENT_ENABLED_STATE_ENABLED;
                                getPackageManager().setComponentEnabledSetting(
                                        component, state, PackageManager.DONT_KILL_APP);
                                Toast.makeText(this,
                                        hide ? "桌面图标已隐藏" : "桌面图标已显示",
                                        Toast.LENGTH_SHORT).show();
                                setContentView(buildPage());
                            } catch (RuntimeException error) {
                                Log.e(TAG, "Failed to toggle launcher icon", error);
                                Toast.makeText(this, "桌面图标设置失败：" + error.getMessage(),
                                        Toast.LENGTH_LONG).show();
                            }
                        })
                .show();
    }

    private boolean isIconHidden() {
        int state = getPackageManager().getComponentEnabledSetting(
                new ComponentName(this, LAUNCHER_ALIAS));
        return state == PackageManager.COMPONENT_ENABLED_STATE_DISABLED
                || state == PackageManager.COMPONENT_ENABLED_STATE_DISABLED_USER
                || state == PackageManager.COMPONENT_ENABLED_STATE_DISABLED_UNTIL_USED;
    }

    private LinearLayout vertical() {
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        return layout;
    }

    private LinearLayout.LayoutParams fill() {
        return new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
    }

    private LinearLayout.LayoutParams wrap() {
        return new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
    }

    private TextView label(String value, int sp, int color, boolean bold) {
        TextView view = new TextView(this);
        view.setText(value);
        view.setTextSize(sp);
        view.setTextColor(color);
        view.setTypeface(bold ? Typeface.DEFAULT_BOLD : Typeface.DEFAULT);
        view.setLineSpacing(dp(2), 1f);
        return view;
    }

    private GradientDrawable rounded(int color, int radius, int strokeColor, int strokeWidth) {
        GradientDrawable drawable = new GradientDrawable();
        drawable.setColor(color);
        drawable.setCornerRadius(dp(radius));
        if (strokeWidth > 0) drawable.setStroke(strokeWidth, strokeColor);
        return drawable;
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }
}
