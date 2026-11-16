package com.rww.wetypeswipe;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.util.Log;

/** Persists config snapshots sent back from the embedded editor in the WeType process. */
public final class ConfigSyncReceiver extends BroadcastReceiver {
    static final String KEY_EXTERNAL_SYNC_PENDING = "_external_sync_pending";
    static final String KEY_VERSION_CONFLICT = "_external_revision_conflict";
    static final String KEY_MANUAL_SYNC_DEADLINE = "_manual_sync_deadline_ms";
    private static final String TAG = "WeTypeSwipeSync";

    @Override public void onReceive(Context context, Intent intent) {
        if (context == null || intent == null) return;
        if (!Config.ACTION_CONFIG_CHANGED.equals(intent.getAction())) return;
        if (!intent.getBooleanExtra(Config.EXTRA_SNAPSHOT, false)) return;

        try {
            Config incoming = ConfigCodec.fromIntent(intent);
            SharedPreferences prefs = context.getSharedPreferences(
                    Config.PREFS, Context.MODE_PRIVATE);
            int storedRevision = prefs.getInt(Config.KEY_REVISION, -1);
            long deadline = prefs.getLong(KEY_MANUAL_SYNC_DEADLINE, 0L);
            boolean manualPull = deadline > 0 && System.currentTimeMillis() <= deadline;
            if (incoming.revision < storedRevision && !manualPull) {
                prefs.edit().putBoolean(KEY_VERSION_CONFLICT, true).apply();
                Log.w(TAG, "Ignored older embedded snapshot; use manual pull to reconcile: incoming="
                        + incoming.revision + ", stored=" + storedRevision);
                return;
            }
            boolean advancedTargetRevision = manualPull && incoming.revision < storedRevision;
            if (advancedTargetRevision) {
                // The user explicitly chose the active input-method configuration as
                // authoritative. Keep revision monotonic for the next save in both apps.
                incoming.revision = storedRevision + 1;
            }

            SharedPreferences.Editor editor = prefs.edit();
            ConfigCodec.writeToPreferences(editor, incoming);
            editor.putBoolean(KEY_EXTERNAL_SYNC_PENDING, true);
            editor.putBoolean(KEY_VERSION_CONFLICT, false);
            editor.remove(KEY_MANUAL_SYNC_DEADLINE);
            if (!editor.commit()) {
                Log.e(TAG, "Embedded settings snapshot commit returned false");
            } else {
                Log.i(TAG, "Embedded settings stored revision=" + incoming.revision
                        + ", previous=" + storedRevision + ", manual=" + manualPull);
                if (advancedTargetRevision) {
                    Intent changed = new Intent(Config.ACTION_CONFIG_CHANGED);
                    changed.setPackage("com.tencent.wetype");
                    ConfigSnapshot.putInto(changed, incoming);
                    context.sendBroadcast(changed);
                }
            }
        } catch (Throwable error) {
            // Invalid external snapshots must not crash the UI, but failures must be visible.
            Log.e(TAG, "Failed to store embedded settings snapshot", error);
        }
    }
}
