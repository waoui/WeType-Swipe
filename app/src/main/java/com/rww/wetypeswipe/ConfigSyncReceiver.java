package com.rww.wetypeswipe;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;

/** Persists config snapshots sent back from the embedded editor in the WeType process. */
public final class ConfigSyncReceiver extends BroadcastReceiver {
    static final String KEY_EXTERNAL_SYNC_PENDING = "_external_sync_pending";

    @Override public void onReceive(Context context, Intent intent) {
        if (context == null || intent == null) return;
        if (!Config.ACTION_CONFIG_CHANGED.equals(intent.getAction())) return;
        if (!intent.getBooleanExtra(Config.EXTRA_SNAPSHOT, false)) return;

        try {
            Config config = ConfigCodec.fromIntent(intent);
            SharedPreferences.Editor editor = context
                    .getSharedPreferences(Config.PREFS, Context.MODE_PRIVATE)
                    .edit();
            ConfigCodec.writeToPreferences(editor, config);
            editor.putBoolean(KEY_EXTERNAL_SYNC_PENDING, true);
            editor.commit();
        } catch (Throwable ignored) {
            // A malformed cross-process snapshot must never crash the module application.
        }
    }
}
