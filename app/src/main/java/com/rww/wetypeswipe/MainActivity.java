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
import android.net.Uri;
import android.os.Bundle;
import android.util.Log;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.Button;
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

    private android.view.View buildPage() {
        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setBackgroundColor(Color.rgb(245, 247, 250));
        LinearLayout content = new LinearLayout(this);
        content.setOrientation(LinearLayout.VERTICAL);
        content.setPadding(dp(20), dp(26), dp(20), dp(26));
        scroll.addView(content);

        TextView title = text("模块维护与恢复", 22, Color.rgb(32, 36, 43));
        title.setGravity(Gravity.CENTER);
        content.addView(title);
        TextView introduction = text(
                "从 v1.13.0 起，只有微信输入法内置模块设置可以编辑配置。\n"
                        + "本页面不保存第二份手势设置，避免两边显示不一致。",
                14, Color.rgb(97, 104, 116));
        introduction.setPadding(0, dp(14), 0, dp(18));
        content.addView(introduction);

        addAction(content, "打开微信输入法内置模块设置", () -> openEmbeddedSettings());
        addAction(content, "导出旧模块配置 TXT（迁移备份）", () -> exportLegacyBackup());
        addAction(content, "复制诊断信息", () -> copyDiagnostics());
        addAction(content, "桌面图标显示／隐藏", () -> confirmToggleIcon());

        String revision = legacyPrefs.contains(Config.KEY_REVISION)
                ? String.valueOf(legacyPrefs.getInt(Config.KEY_REVISION, 0)) : "无";
        String note = "模块版本：" + BuildConfig.VERSION_NAME
                + "\n旧模块本地配置修订号：" + revision
                + "\n注意：旧修订号不代表当前微信输入法的生效配置。"
                + "\n如果内置设置入口失效，可在微信输入法“关于”页连续点击图标 5 次。"
                + "\n升级前的旧配置仍保存在模块私有存储中，不会自动删除。";
        TextView details = text(note, 12, Color.rgb(101, 109, 122));
        details.setPadding(dp(4), dp(18), dp(4), 0);
        content.addView(details);

        return scroll;
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

    private void copyDiagnostics() {
        String details = "WeType-Swipe " + BuildConfig.VERSION_NAME
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

    private void addAction(LinearLayout container, String caption, Runnable callback) {
        Button button = new Button(this);
        button.setText(caption);
        button.setAllCaps(false);
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(52));
        params.bottomMargin = dp(8);
        container.addView(button, params);
        button.setOnClickListener(view -> callback.run());
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
