package com.rww.wetypeswipe;

import android.app.AlertDialog;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.graphics.Color;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

/** Clipboard backup for an embedded IME screen, which cannot own SAF Activity results. */
final class EmbeddedBackupUi {
    interface Provider { Config current(); }
    interface Importer { void importConfig(Config config); }

    private EmbeddedBackupUi() {}

    static void attach(Context context, LinearLayout container, Provider provider, Importer importer) {
        TextView heading = text(context, "配置备份与恢复", 15, Color.rgb(32, 36, 43));
        heading.setPadding(dp(context, 18), dp(context, 12), dp(context, 18), dp(context, 8));
        container.addView(heading);
        TextView note = text(context,
                "内置设置支持复制和粘贴配置；需文件保存/读取时使用独立模块设置导出 TXT。",
                12, Color.rgb(101, 109, 122));
        note.setPadding(dp(context, 18), 0, dp(context, 18), dp(context, 10));
        container.addView(note);

        LinearLayout row = new LinearLayout(context);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setPadding(dp(context, 12), dp(context, 6), dp(context, 12), dp(context, 12));
        TextView copy = button(context, "复制配置备份");
        row.addView(copy, new LinearLayout.LayoutParams(0, dp(context, 48), 1f));
        copy.setOnClickListener(view -> {
            try {
                ClipboardManager clipboard = (ClipboardManager)
                        context.getSystemService(Context.CLIPBOARD_SERVICE);
                if (clipboard == null) throw new IllegalArgumentException("剪贴板不可用");
                clipboard.setPrimaryClip(ClipData.newPlainText("WeType-Swipe 配置备份",
                        ConfigBackup.exportText(provider.current())));
                Toast.makeText(context, "配置已复制，可粘贴保存为 UTF-8 TXT",
                        Toast.LENGTH_LONG).show();
            } catch (Exception e) {
                Toast.makeText(context, "配置复制失败：" + e.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
        TextView paste = button(context, "从剪贴板导入");
        LinearLayout.LayoutParams pasteLayout = new LinearLayout.LayoutParams(0, dp(context, 48), 1f);
        pasteLayout.leftMargin = dp(context, 8);
        row.addView(paste, pasteLayout);
        paste.setOnClickListener(view -> {
            try {
                ClipboardManager clipboard = (ClipboardManager)
                        context.getSystemService(Context.CLIPBOARD_SERVICE);
                if (clipboard == null || clipboard.getPrimaryClip() == null
                        || clipboard.getPrimaryClip().getItemCount() < 1) {
                    throw new IllegalArgumentException("剪贴板没有配置文本");
                }
                CharSequence raw = clipboard.getPrimaryClip().getItemAt(0).coerceToText(context);
                Config candidate = ConfigBackup.importText(raw == null ? "" : raw.toString());
                new AlertDialog.Builder(context)
                        .setTitle("确认导入配置？")
                        .setMessage("备份已通过格式检查。导入会覆盖上下滑动作、标签、文本和手势设置。建议先复制旧配置。")
                        .setNegativeButton("取消", null)
                        .setPositiveButton("确认导入", (dialog, which) -> {
                            try {
                                importer.importConfig(candidate);
                                Toast.makeText(context, "配置导入请求已提交", Toast.LENGTH_LONG).show();
                            } catch (Exception error) {
                                Toast.makeText(context, "导入失败：" + error.getMessage(), Toast.LENGTH_LONG).show();
                            }
                        })
                        .show();
            } catch (Exception e) {
                Toast.makeText(context, "配置导入失败：" + e.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
        container.addView(row, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
    }

    private static TextView button(Context context, String title) {
        TextView view = text(context, title, 13, Color.rgb(36, 103, 214));
        view.setGravity(Gravity.CENTER);
        view.setBackgroundColor(Color.rgb(232, 240, 254));
        view.setClickable(true);
        return view;
    }

    private static TextView text(Context context, String title, int size, int color) {
        TextView view = new TextView(context);
        view.setText(title);
        view.setTextSize(size);
        view.setTextColor(color);
        return view;
    }

    private static int dp(Context context, int value) {
        return Math.round(value * context.getResources().getDisplayMetrics().density);
    }
}
