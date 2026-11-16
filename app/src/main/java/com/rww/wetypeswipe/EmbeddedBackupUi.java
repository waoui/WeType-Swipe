package com.rww.wetypeswipe;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

/** One backup section shared by the Activity-hosted embedded UI and IME-overlay fallback. */
final class EmbeddedBackupUi {
    interface Provider { Config current(); }
    interface Importer { void importConfig(Config config); }

    private static final int BLUE = Color.rgb(36, 103, 214);
    private static final int BLUE_SOFT = Color.rgb(232, 240, 254);
    private static final int MUTED = Color.rgb(101, 109, 122);

    private EmbeddedBackupUi() {}

    static void attach(Context context, LinearLayout container, Provider provider, Importer importer) {
        final boolean fileSupported = context instanceof Activity;
        TextView note = text(context,
                fileSupported
                        ? "优先使用 TXT 文件备份（包含当前编辑中尚未保存的修改）；也支持复制配置到剪贴板。"
                        : "当前由输入法悬浮窗口打开：可使用剪贴板备份与恢复。要管理 TXT 文件，请从微信输入法“关于”页进入内置设置。",
                12, MUTED);
        note.setPadding(dp(context, 16), dp(context, 12),
                dp(context, 16), dp(context, 10));
        container.addView(note);

        if (fileSupported) {
            Activity host = (Activity) context;
            LinearLayout files = actions(context);
            TextView exportFile = button(context, "导出 TXT", true);
            files.addView(exportFile, weighted(context));
            exportFile.setOnClickListener(view ->
                    EmbeddedFileTransfer.exportText(host, provider.current()));

            TextView importFile = button(context, "导入 TXT", true);
            LinearLayout.LayoutParams right = weighted(context);
            right.leftMargin = dp(context, 8);
            files.addView(importFile, right);
            importFile.setOnClickListener(view ->
                    EmbeddedFileTransfer.importText(host, importer::importConfig));
            container.addView(files);
        }

        LinearLayout clipboard = actions(context);
        TextView copy = button(context, "复制配置", false);
        clipboard.addView(copy, weighted(context));
        copy.setOnClickListener(view -> {
            try {
                ClipboardManager manager = (ClipboardManager)
                        context.getSystemService(Context.CLIPBOARD_SERVICE);
                if (manager == null) throw new IllegalStateException("剪贴板不可用");
                manager.setPrimaryClip(ClipData.newPlainText("WeType-Swipe 配置备份",
                        ConfigBackup.exportText(provider.current())));
                Toast.makeText(context,
                        "已复制配置，可保存为 UTF-8 TXT 文本", Toast.LENGTH_LONG).show();
            } catch (Exception error) {
                Toast.makeText(context, "复制配置失败：" + error.getMessage(),
                        Toast.LENGTH_LONG).show();
            }
        });

        TextView paste = button(context, "粘贴导入", false);
        LinearLayout.LayoutParams pasteParams = weighted(context);
        pasteParams.leftMargin = dp(context, 8);
        clipboard.addView(paste, pasteParams);
        paste.setOnClickListener(view -> {
            try {
                ClipboardManager manager = (ClipboardManager)
                        context.getSystemService(Context.CLIPBOARD_SERVICE);
                if (manager == null || manager.getPrimaryClip() == null
                        || manager.getPrimaryClip().getItemCount() == 0) {
                    throw new IllegalArgumentException("剪贴板没有配置内容");
                }
                CharSequence raw = manager.getPrimaryClip().getItemAt(0).coerceToText(context);
                Config parsed = ConfigBackup.importText(raw == null ? "" : raw.toString());
                AlertDialog confirm = new AlertDialog.Builder(context)
                        .setTitle("确认从剪贴板导入？")
                        .setMessage("备份格式已通过验证。导入会覆盖微信输入法当前的上下滑、标签、文本和手势选项，建议先备份。")
                        .setNegativeButton("取消", null)
                        .setPositiveButton("确认导入", (dialog, which) -> {
                            try {
                                importer.importConfig(parsed);
                                Toast.makeText(context, "配置已导入并应用",
                                        Toast.LENGTH_LONG).show();
                            } catch (Exception error) {
                                Toast.makeText(context, "导入失败：" + error.getMessage(),
                                        Toast.LENGTH_LONG).show();
                            }
                        })
                        .create();
                ImeDialogCompat.show(context, confirm);
            } catch (Exception error) {
                Toast.makeText(context, "无法导入配置：" + error.getMessage(),
                        Toast.LENGTH_LONG).show();
            }
        });
        container.addView(clipboard);
    }

    private static LinearLayout actions(Context context) {
        LinearLayout row = new LinearLayout(context);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setPadding(dp(context, 12), dp(context, 4),
                dp(context, 12), dp(context, 12));
        return row;
    }

    private static LinearLayout.LayoutParams weighted(Context context) {
        return new LinearLayout.LayoutParams(0, dp(context, 48), 1f);
    }

    private static TextView button(Context context, String title, boolean primary) {
        TextView view = text(context, title, 13,
                primary ? Color.WHITE : BLUE);
        view.setTypeface(Typeface.DEFAULT_BOLD);
        view.setGravity(Gravity.CENTER);
        GradientDrawable bg = new GradientDrawable();
        bg.setColor(primary ? BLUE : BLUE_SOFT);
        bg.setCornerRadius(dp(context, 11));
        view.setBackground(bg);
        view.setClickable(true);
        view.setFocusable(true);
        view.setContentDescription(title);
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
