package com.rww.wetypeswipe;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.ComponentName;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.view.View;
import android.net.Uri;
import android.os.Bundle;
import android.util.Log;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

/**
 * Minimal maintenance entry. Gesture editing, import and canonical data storage all live
 * inside the WeType process. This Activity never writes ConfigCodec fields.
 */
public final class MainActivity extends Activity {
    private static final String TAG = "WeTypeSwipeMaintenance";
    private static final String TARGET = "com.tencent.wetype";
    private static final String LAUNCHER_ALIAS = "com.rww.wetypeswipe.LauncherAlias";
    private static final String OPEN_EMBEDDED_EXTRA =
            "com.rww.wetypeswipe.extra.OPEN_EMBEDDED_SETTINGS";
    private static final int EXPORT_LEGACY_REQUEST = 4131;
    private SharedPreferences legacyPrefs;

    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        setTitle("WeType-Swipe · 维护与恢复");
        legacyPrefs = getSharedPreferences(Config.PREFS, MODE_PRIVATE);
        getWindow().setStatusBarColor(Color.WHITE);
        getWindow().setNavigationBarColor(Color.WHITE);
        getWindow().getDecorView().setSystemUiVisibility(
                android.view.View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR
                        | android.view.View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);
        setContentView(buildPage());
    }

    private static final int PAGE = Color.rgb(246, 248, 252);
    private static final int INK = Color.rgb(32, 43, 62);
    private static final int MUTED = Color.rgb(105, 115, 134);
    private static final int BLUE = Color.rgb(35, 98, 210);
    private static final int SOFT_BLUE = Color.rgb(231, 239, 255);
    private static final int SEPARATOR = Color.rgb(237, 240, 246);

    private View buildPage() {
        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setClipToPadding(false);
        scroll.setBackgroundColor(PAGE);

        LinearLayout column = vertical();
        column.setPadding(dp(18), dp(22), dp(18), dp(28));
        scroll.addView(column, new ScrollView.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        TextView kicker = text("WETYPE  /  SWIPE", 11, BLUE);
        kicker.setTypeface(Typeface.DEFAULT_BOLD);
        kicker.setLetterSpacing(.12f);
        column.addView(kicker);

        TextView heading = text("模块管理", 27, INK);
        heading.setTypeface(Typeface.DEFAULT_BOLD);
        LinearLayout.LayoutParams headingLp = wrap();
        headingLp.topMargin = dp(6);
        column.addView(heading, headingLp);

        TextView subheading = text(
                "v" + getModuleVersion() + "  ·  单一内置配置",
                13, MUTED);
        LinearLayout.LayoutParams subheadingLp = wrap();
        subheadingLp.topMargin = dp(5);
        subheadingLp.bottomMargin = dp(20);
        column.addView(subheading, subheadingLp);

        LinearLayout hero = vertical();
        hero.setPadding(dp(18), dp(19), dp(18), dp(18));
        GradientDrawable heroBackground = new GradientDrawable(
                GradientDrawable.Orientation.TL_BR,
                new int[]{Color.rgb(35, 100, 217), Color.rgb(24, 62, 152)});
        heroBackground.setCornerRadius(dp(19));
        hero.setBackground(heroBackground);

        TextView status = text("唯一配置入口", 12, Color.rgb(211, 231, 255));
        status.setTypeface(Typeface.DEFAULT_BOLD);
        hero.addView(status);

        TextView heroTitle = text("微信输入法内置设置", 22, Color.WHITE);
        heroTitle.setTypeface(Typeface.DEFAULT_BOLD);
        LinearLayout.LayoutParams heroTitleLp = wrap();
        heroTitleLp.topMargin = dp(8);
        hero.addView(heroTitle, heroTitleLp);

        TextView heroDesc = text(
                "统一管理 26 键、九宫格、上下滑动作和配置备份，不再维护第二套设置。",
                13, Color.rgb(233, 241, 255));
        heroDesc.setLineSpacing(dp(3), 1f);
        LinearLayout.LayoutParams descLp = wrap();
        descLp.topMargin = dp(8);
        hero.addView(heroDesc, descLp);

        TextView mainAction = text("打开内置模块设置    ›", 15, BLUE);
        mainAction.setTypeface(Typeface.DEFAULT_BOLD);
        mainAction.setGravity(Gravity.CENTER);
        mainAction.setMinHeight(dp(53));
        mainAction.setBackground(shape(Color.WHITE, 12, 0, 0));
        mainAction.setClickable(true);
        mainAction.setFocusable(true);
        mainAction.setContentDescription("打开微信输入法中的唯一设置界面");
        mainAction.setOnClickListener(v -> openEmbeddedSettings());
        LinearLayout.LayoutParams mainLp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(53));
        mainLp.topMargin = dp(17);
        hero.addView(mainAction, mainLp);

        LinearLayout.LayoutParams heroLp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        heroLp.bottomMargin = dp(16);
        column.addView(hero, heroLp);

        TextView fallback = text("备用入口：微信输入法 → 关于 → 连续点击图标 5 次", 12, MUTED);
        fallback.setPadding(dp(4), 0, dp(4), 0);
        column.addView(fallback);

        sectionTitle(column, "维护与恢复", "以下工具不会修改输入法的实际键位配置");
        LinearLayout tools = vertical();
        tools.setBackground(shape(Color.WHITE, 17, Color.rgb(232, 235, 242), 1));
        addToolRow(tools, "备", "导出旧配置 TXT",
                legacyPrefs.contains(Config.KEY_REVISION)
                        ? "备份升级前的旧模块数据，不是当前生效配置"
                        : "当前没有旧模块配置，建议在内置设置中导出",
                this::exportLegacyBackup, true);
        addToolRow(tools, "诊", "复制诊断信息",
                "复制模块版本、Android 版本与作用域信息",
                this::copyDiagnostics, true);
        addToolRow(tools, "图", "桌面入口设置",
                isIconHidden() ? "桌面图标已隐藏，可从 LSPosed 打开"
                        : "桌面图标已显示，支持隐藏",
                this::confirmToggleIcon, false);
        column.addView(tools);

        sectionTitle(column, "关于当前架构", null);
        LinearLayout infoCard = vertical();
        infoCard.setPadding(dp(16), dp(14), dp(16), dp(14));
        infoCard.setBackground(shape(Color.WHITE, 15, Color.rgb(232, 235, 242), 1));

        TextView one = text("配置存储位置", 12, MUTED);
        infoCard.addView(one);
        TextView two = text("微信输入法内部私有存储", 15, INK);
        two.setTypeface(Typeface.DEFAULT_BOLD);
        LinearLayout.LayoutParams twoLp = wrap();
        twoLp.topMargin = dp(3);
        infoCard.addView(two, twoLp);

        View divider = new View(this);
        divider.setBackgroundColor(SEPARATOR);
        LinearLayout.LayoutParams dividerLp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(1));
        dividerLp.topMargin = dp(13);
        dividerLp.bottomMargin = dp(12);
        infoCard.addView(divider, dividerLp);

        TextView info = text("此页面只负责维护与故障恢复。"
                + "如需修改键位、导入或导出当前配置，请使用上方入口。"
                + "旧模块配置保留供回滚，不会自动覆盖输入法内的设置。", 12, MUTED);
        info.setLineSpacing(dp(4), 1f);
        infoCard.addView(info);
        column.addView(infoCard);
        return scroll;
    }

    private void sectionTitle(LinearLayout parent, String heading, String subtitle) {
        LinearLayout group = vertical();
        LinearLayout.LayoutParams gp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        gp.topMargin = dp(19);
        gp.bottomMargin = dp(9);
        parent.addView(group, gp);

        TextView label = text(heading, 16, INK);
        label.setTypeface(Typeface.DEFAULT_BOLD);
        group.addView(label);
        if (subtitle != null) {
            TextView note = text(subtitle, 12, MUTED);
            LinearLayout.LayoutParams np = wrap();
            np.topMargin = dp(3);
            group.addView(note, np);
        }
    }

    private void addToolRow(LinearLayout group, String glyph, String title,
                            String subtitle, Runnable action, boolean withDivider) {
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setGravity(Gravity.CENTER_VERTICAL);
        row.setPadding(dp(14), dp(13), dp(12), dp(13));
        row.setMinimumHeight(dp(72));
        row.setClickable(true);
        row.setFocusable(true);
        row.setContentDescription(title + "，" + subtitle);
        row.setOnClickListener(v -> action.run());

        TextView icon = text(glyph, 15, BLUE);
        icon.setTypeface(Typeface.DEFAULT_BOLD);
        icon.setGravity(Gravity.CENTER);
        icon.setBackground(shape(SOFT_BLUE, 10, 0, 0));
        row.addView(icon, new LinearLayout.LayoutParams(dp(38), dp(38)));

        LinearLayout labels = vertical();
        LinearLayout.LayoutParams labelsLp = new LinearLayout.LayoutParams(
                0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f);
        labelsLp.leftMargin = dp(12);
        row.addView(labels, labelsLp);

        TextView name = text(title, 14, INK);
        name.setTypeface(Typeface.DEFAULT_BOLD);
        labels.addView(name);
        TextView description = text(subtitle, 11, MUTED);
        LinearLayout.LayoutParams descriptionLp = wrap();
        descriptionLp.topMargin = dp(3);
        labels.addView(description, descriptionLp);

        TextView chevron = text("›", 23, Color.rgb(153, 164, 183));
        chevron.setGravity(Gravity.CENTER);
        LinearLayout.LayoutParams arrowLp = new LinearLayout.LayoutParams(dp(19), dp(40));
        arrowLp.leftMargin = dp(6);
        row.addView(chevron, arrowLp);
        group.addView(row);

        if (withDivider) {
            View line = new View(this);
            line.setBackgroundColor(SEPARATOR);
            LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT, dp(1));
            lp.leftMargin = dp(64);
            group.addView(line, lp);
        }
    }

    private LinearLayout vertical() {
        LinearLayout column = new LinearLayout(this);
        column.setOrientation(LinearLayout.VERTICAL);
        return column;
    }

    private LinearLayout.LayoutParams wrap() {
        return new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
    }

    private GradientDrawable shape(int color, int radius, int stroke, int strokeWidth) {
        GradientDrawable background = new GradientDrawable();
        background.setColor(color);
        background.setCornerRadius(dp(radius));
        if (strokeWidth > 0) background.setStroke(dp(strokeWidth), stroke);
        return background;
    }

    private void openEmbeddedSettings() {
        try {
            Intent target = getPackageManager().getLaunchIntentForPackage(TARGET);
            if (target == null) {
                Toast.makeText(this,
                        "未找到微信输入法启动入口，请在输入法“关于”页连续点击图标 5 次",
                        Toast.LENGTH_LONG).show();
                return;
            }
            target.putExtra(OPEN_EMBEDDED_EXTRA, true);
            target.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
            startActivity(target);
        } catch (RuntimeException error) {
            Log.e(TAG, "Unable to open target embedded settings", error);
            Toast.makeText(this,
                    "内置设置无法启动，请检查 LSPosed 作用域，并尝试输入法关于页五击入口",
                    Toast.LENGTH_LONG).show();
        }
    }

    private void exportLegacyBackup() {
        if (!legacyPrefs.contains(Config.KEY_REVISION)) {
            Toast.makeText(this,
                    "没有需要迁移的旧模块配置；请从微信输入法内置设置导出当前配置",
                    Toast.LENGTH_LONG).show();
            return;
        }
        try {
            Intent choose = new Intent(Intent.ACTION_CREATE_DOCUMENT);
            choose.addCategory(Intent.CATEGORY_OPENABLE);
            choose.setType("text/plain");
            choose.putExtra(Intent.EXTRA_TITLE, "WeType-Swipe-旧模块配置备份.txt");
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
            String backup = ConfigBackup.exportText(ConfigCodec.fromPreferences(legacyPrefs));
            stream.write(backup.getBytes(StandardCharsets.UTF_8));
            stream.flush();
            Toast.makeText(this, "旧模块配置已备份，源数据未删除", Toast.LENGTH_LONG).show();
        } catch (Exception error) {
            Log.e(TAG, "Failed to export legacy config", error);
            Toast.makeText(this, "旧配置备份失败：" + error.getMessage(),
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
                + "\nLegacy backup available: " + legacyPrefs.contains(Config.KEY_REVISION);
        ClipboardManager clipboard = (ClipboardManager)
                getSystemService(CLIPBOARD_SERVICE);
        if (clipboard == null) {
            Toast.makeText(this, "剪贴板不可用", Toast.LENGTH_LONG).show();
            return;
        }
        clipboard.setPrimaryClip(ClipData.newPlainText("WeType-Swipe 诊断", details));
        Toast.makeText(this, "诊断信息已复制（不包含实际配置文本）", Toast.LENGTH_SHORT).show();
    }

    private void confirmToggleIcon() {
        new AlertDialog.Builder(this)
                .setTitle("切换桌面图标显示状态")
                .setMessage("隐藏桌面图标后，仍可从 LSPosed 模块列表进入本维护页面。")
                .setNegativeButton("取消", null)
                .setPositiveButton(isIconHidden() ? "显示图标" : "隐藏图标",
                        (dialog, which) -> {
                            boolean hide = !isIconHidden();
                            ComponentName name = new ComponentName(this, LAUNCHER_ALIAS);
                            int state = hide
                                    ? PackageManager.COMPONENT_ENABLED_STATE_DISABLED
                                    : PackageManager.COMPONENT_ENABLED_STATE_ENABLED;
                            getPackageManager().setComponentEnabledSetting(
                                    name, state, PackageManager.DONT_KILL_APP);
                            Toast.makeText(this, hide ? "桌面图标已隐藏" : "桌面图标已恢复",
                                    Toast.LENGTH_SHORT).show();
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

    private TextView text(String content, int size, int color) {
        TextView view = new TextView(this);
        view.setText(content);
        view.setTextSize(size);
        view.setTextColor(color);
        return view;
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }
}
