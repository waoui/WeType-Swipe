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

/** Clipboard backup for an embedded IME screen, which cannot own SAF Activity results. */
final class EmbeddedBackupUi {
    interface Provider { Config current(); }
    interface Importer { void importConfig(Config config); }

    private EmbeddedBackupUi() {}

    static void attach(Context context, LinearLayout container, Provider provider, Importer importer) {
        final boolean supportsFiles = context instanceof Activity;
        TextView heading = text(context, "配置备份与恢复", 16, Color.rgb(32, 43, 62));
        heading.setTypeface(Typeface.DEFAULT_BOLD);
        heading.setPadding(dp(context, 16), dp(context, 14), dp(context, 16), dp(context, 4));
        container.addView(heading);

        TextView note = text(context,
                supportsFiles
                        ? "备份所有上下滑、文字标签和手势选项。导入前会校验，并要求确认。"
                        : "当前为输入法悬浮设置，可使用剪贴板备份；文件操作请从输入法“关于”页进入内置设置。",
                12, Color.rgb(104, 115, 133));
        note.setLineSpacing(dp(context, 2), 1f);
        note.setPadding(dp(context, 16), 0, dp(context, 16), dp(context, 12));
        container.addView(note);

        if (supportsFiles) {
            final Activity activity = (Activity) context;
            LinearLayout fileRow = horizontal(context);
            TextView export = button(context, "导出 TXT 备份", true);
            fileRow.addView(export, new LinearLayout.LayoutParams(0, dp(context, 48), 1f));
            export.setOnClickListener(v ->
                    EmbeddedFileTransfer.exportText(activity, provider.current()));

            TextView importFile = button(context, "从 TXT 恢复", true);
            LinearLayout.LayoutParams importParams =
                    new LinearLayout.LayoutParams(0, dp(context, 48), 1f);
            importParams.leftMargin = dp(context, 8);
            fileRow.addView(importFile, importParams);
            importFile.setOnClickListener(v ->
                    EmbeddedFileTransfer.importText(activity, importer::importConfig));
            container.addView(fileRow);
        }

        LinearLayout clipboardRow = horizontal(context);
        TextView copy = button(context, "复制配置", false);
        clipboardRow.addView(copy, new LinearLayout.LayoutParams(0, dp(context, 46), 1f));
        copy.setOnClickListener(view -> {
            try {
                ClipboardManager clipboard = (ClipboardManager)
                        context.getSystemService(Context.CLIPBOARD_SERVICE);
                if (clipboard == null) throw new IllegalArgumentException("剪贴板不可用");
                clipboard.setPrimaryClip(ClipData.newPlainText("WeType-Swipe 配置备份",
                        ConfigBackup.exportText(provider.current())));
                Toast.makeText(context, "配置已复制，可保存为 UTF-8 文本",
                        Toast.LENGTH_LONG).show();
            } catch (Exception error) {
                Toast.makeText(context, "复制失败：" + error.getMessage(), Toast.LENGTH_LONG).show();
            }
        });

        TextView paste = button(context, "粘贴导入", false);
        LinearLayout.LayoutParams pasteParams = new LinearLayout.LayoutParams(0, dp(context, 46), 1f);
        pasteParams.leftMargin = dp(context, 8);
        clipboardRow.addView(paste, pasteParams);
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
                AlertDialog confirm = new AlertDialog.Builder(context)
                        .setTitle("确认导入配置？")
                        .setMessage("备份已通过格式检查。导入会覆盖全部上下滑、标签、文本和手势设置。建议先保存当前备份。")
                        .setNegativeButton("取消", null)
                        .setPositiveButton("确认导入", (dialog, which) -> {
                            try {
                                importer.importConfig(candidate);
                                Toast.makeText(context, "配置已导入并保存", Toast.LENGTH_LONG).show();
                            } catch (Exception error) {
                                Toast.makeText(context, "导入失败：" + error.getMessage(), Toast.LENGTH_LONG).show();
                            }
                        }).create();
                ImeDialogCompat.show(context, confirm);
            } catch (Exception error) {
                Toast.makeText(context, "无法导入配置：" + error.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
        container.addView(clipboardRow);

        TextView tip = text(context,
                "提示：当前编辑的内容可备份；只有点击底部“保存并应用”才会保存普通编辑。",
                11, Color.rgb(117, 127, 145));
        tip.setPadding(dp(context, 16), dp(context, 9), dp(context, 16), dp(context, 15));
        container.addView(tip);
    }

    private static LinearLayout horizontal(Context context) {
        LinearLayout row = new LinearLayout(context);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setPadding(dp(context, 12), dp(context, 5), dp(context, 12), dp(context, 5));
        return row;
    }

    private static TextView button(Context context, String title, boolean primary) {
        TextView view = text(context, title, 13,
                primary ? Color.WHITE : Color.rgb(36, 103, 214));
        view.setGravity(Gravity.CENTER);
        view.setTypeface(Typeface.DEFAULT_BOLD);
        GradientDrawable bg = new GradientDrawable();
        bg.setColor(primary ? Color.rgb(36, 103, 214) : Color.rgb(232, 240, 254));
        bg.setCornerRadius(dp(context, 10));
        view.setBackground(bg);
        view.setClickable(true);
        view.setFocusable(true);
        view.setMinHeight(dp(context, 46));
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
