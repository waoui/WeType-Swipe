package com.rww.wetypeswipe;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.util.Log;

/** Persists config snapshots sent back from the embedded editor in the WeType process. */
public final class ConfigSyncReceiver extends BroadcastReceiver {
    static final String KEY_EXTERNAL_SYNC_PENDING = "_external_sync_pending";
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
            if (incoming.revision < storedRevision) {
                Log.w(TAG, "Ignored older embedded snapshot: incoming="
                        + incoming.revision + ", stored=" + storedRevision);
                return;
            }
            SharedPreferences.Editor editor = prefs.edit();
            ConfigCodec.writeToPreferences(editor, incoming);
            editor.putBoolean(KEY_EXTERNAL_SYNC_PENDING, true);
            if (!editor.commit()) {
                Log.e(TAG, "Embedded settings snapshot commit returned false");
            } else {
                Log.i(TAG, "Embedded settings stored revision=" + incoming.revision
                        + ", previous=" + storedRevision);
            }
        } catch (Throwable error) {
            // Invalid external snapshots must not crash the UI, but failures must be visible.
            Log.e(TAG, "Failed to store embedded settings snapshot", error);
        }
    }
}
