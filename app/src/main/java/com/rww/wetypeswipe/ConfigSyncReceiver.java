package com.rww.wetypeswipe;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.util.Log;

/**
 * Migration-only receiver: the module APK no longer owns editable settings.
 * Its historical preferences are kept untouched for user recovery or old-version rollback.
 */
public final class ConfigSyncReceiver extends BroadcastReceiver {
    private static final String TAG = "WeTypeSwipeMigration";
    private static final String TARGET_PACKAGE = "com.tencent.wetype";

    @Override public void onReceive(Context context, Intent intent) {
        if (context == null || intent == null
                || !Config.ACTION_LEGACY_CONFIG_REQUEST.equals(intent.getAction())) return;

        String token = intent.getStringExtra(Config.EXTRA_MIGRATION_TOKEN);
        if (token == null || token.length() < 16 || token.length() > 128) return;

        try {
            SharedPreferences legacy = context.getSharedPreferences(
                    Config.PREFS, Context.MODE_PRIVATE);
            // A launcher icon setting alone is not a gesture configuration.
            if (!legacy.contains(Config.KEY_REVISION)) {
                Log.i(TAG, "No previously saved standalone config to migrate");
                return;
            }
            Config snapshot = ConfigCodec.fromPreferences(legacy);
            Intent reply = new Intent(Config.ACTION_LEGACY_CONFIG_RESPONSE);
            reply.setPackage(TARGET_PACKAGE);
            reply.putExtra(Config.EXTRA_MIGRATION_TOKEN, token);
            ConfigSnapshot.putInto(reply, snapshot);
            context.sendBroadcast(reply);
            Log.i(TAG, "Sent read-only legacy migration snapshot revision="
                    + snapshot.revision);
        } catch (Throwable error) {
            Log.e(TAG, "Legacy config migration response failed", error);
        }
    }
}
