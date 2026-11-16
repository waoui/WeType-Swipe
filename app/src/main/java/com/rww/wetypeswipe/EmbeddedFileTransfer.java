package com.rww.wetypeswipe;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.net.Uri;
import android.util.Log;
import android.widget.Toast;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

/**
 * Android Storage Access Framework bridge for an embedded settings Dialog hosted by
 * a real WeType Activity. The MainHook ActivityResult hooks forward only our request codes.
 * No module-app-side file picker or second editable configuration is required.
 */
final class EmbeddedFileTransfer {
    static final int REQUEST_EXPORT = 0x7961;
    static final int REQUEST_IMPORT = 0x7962;
    private static final int MAX_FILE_BYTES = 524288;
    private static final String TAG = "WeTypeSwipeFile";

    interface Importer { void importConfig(Config config); }

    private static Pending pending;

    private static final class Pending {
        final Activity activity;
        final int requestCode;
        final String exportedContent;
        final Importer importer;
        Pending(Activity activity, int requestCode, String exportedContent, Importer importer) {
            this.activity = activity;
            this.requestCode = requestCode;
            this.exportedContent = exportedContent;
            this.importer = importer;
        }
    }

    private EmbeddedFileTransfer() {}

    static synchronized void exportText(Activity activity, Config config) {
        if (pending != null) {
            Toast.makeText(activity, "已有文件操作正在进行", Toast.LENGTH_SHORT).show();
            return;
        }
        String content = ConfigBackup.exportText(ConfigSnapshot.copyOf(config));
        Intent picker = new Intent(Intent.ACTION_CREATE_DOCUMENT);
        picker.addCategory(Intent.CATEGORY_OPENABLE);
        picker.setType("text/plain");
        picker.putExtra(Intent.EXTRA_TITLE, "WeType-Swipe-内置配置备份.txt");
        start(activity, REQUEST_EXPORT, picker, content, null);
    }

    static synchronized void importText(Activity activity, Importer importer) {
        if (pending != null) {
            Toast.makeText(activity, "已有文件操作正在进行", Toast.LENGTH_SHORT).show();
            return;
        }
        Intent picker = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        picker.addCategory(Intent.CATEGORY_OPENABLE);
        picker.setType("text/plain");
        start(activity, REQUEST_IMPORT, picker, null, importer);
    }

    private static void start(Activity activity, int requestCode, Intent picker,
                              String export, Importer importer) {
        pending = new Pending(activity, requestCode, export, importer);
        try {
            activity.startActivityForResult(picker, requestCode);
        } catch (RuntimeException error) {
            pending = null;
            Log.e(TAG, "Failed to open SAF file picker", error);
            Toast.makeText(activity, "无法打开系统文件选择器：" + error.getMessage(),
                    Toast.LENGTH_LONG).show();
        }
    }

    static boolean handleResult(Activity activity, int requestCode, int resultCode, Intent data) {
        final Pending request;
        synchronized (EmbeddedFileTransfer.class) {
            if (pending == null || pending.activity != activity
                    || pending.requestCode != requestCode) return false;
            request = pending;
            pending = null;
        }
        if (resultCode != Activity.RESULT_OK || data == null || data.getData() == null) return true;
        Uri uri = data.getData();
        try {
            if (requestCode == REQUEST_EXPORT) {
                try (OutputStream stream = activity.getContentResolver().openOutputStream(uri, "wt")) {
                    if (stream == null) throw new java.io.IOException("文件不可写");
                    stream.write(request.exportedContent.getBytes(StandardCharsets.UTF_8));
                    stream.flush();
                }
                Toast.makeText(activity, "内置配置 TXT 已导出", Toast.LENGTH_LONG).show();
            } else {
                ByteArrayOutputStream bytes = new ByteArrayOutputStream();
                try (InputStream stream = activity.getContentResolver().openInputStream(uri)) {
                    if (stream == null) throw new java.io.IOException("文件不可读取");
                    byte[] buffer = new byte[4096];
                    int count;
                    while ((count = stream.read(buffer)) != -1) {
                        if (count == 0) continue;
                        if (bytes.size() + count > MAX_FILE_BYTES) {
                            throw new java.io.IOException("备份文件超过 512KB 限制");
                        }
                        bytes.write(buffer, 0, count);
                    }
                }
                String text = new String(bytes.toByteArray(), StandardCharsets.UTF_8);
                if (text.startsWith("\ufeff")) text = text.substring(1);
                Config imported = ConfigBackup.importText(text);
                new AlertDialog.Builder(activity)
                        .setTitle("确认从 TXT 导入内置配置？")
                        .setMessage("格式与内容已通过校验。确认后覆盖微信输入法当前全部上下滑映射、标签、文本和手势选项。建议先备份。")
                        .setNegativeButton("取消", null)
                        .setPositiveButton("确认导入", (dialog, which) -> {
                            try {
                                if (request.importer == null) {
                                    throw new IllegalStateException("导入回调已失效");
                                }
                                request.importer.importConfig(imported);
                                Toast.makeText(activity, "配置已导入并应用", Toast.LENGTH_LONG).show();
                            } catch (Exception error) {
                                Log.e(TAG, "Failed to apply validated imported config", error);
                                Toast.makeText(activity, "导入保存失败：" + error.getMessage(),
                                        Toast.LENGTH_LONG).show();
                            }
                        })
                        .show();
            }
        } catch (Exception error) {
            Log.e(TAG, "Embedded config file operation failed", error);
            Toast.makeText(activity, "文件操作失败，原有配置未覆盖：" + error.getMessage(),
                    Toast.LENGTH_LONG).show();
        }
        return true;
    }

    static synchronized void abandonFor(Activity activity) {
        if (pending != null && pending.activity == activity) pending = null;
    }
}
