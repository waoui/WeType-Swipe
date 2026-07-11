package com.rww.wetypeswipe;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;

public final class DiagnosticReceiver extends BroadcastReceiver {
    @Override public void onReceive(Context context, Intent intent) {
        if (intent == null || !Config.ACTION_DIAGNOSTIC.equals(intent.getAction())) return;
        SharedPreferences.Editor e = context.getSharedPreferences(Config.PREFS, 0).edit();
        if (intent.hasExtra(Config.DIAG_STATUS)) e.putString(Config.DIAG_STATUS, intent.getStringExtra(Config.DIAG_STATUS));
        if (intent.hasExtra(Config.DIAG_LAST_KEY)) e.putString(Config.DIAG_LAST_KEY, intent.getStringExtra(Config.DIAG_LAST_KEY));
        if (intent.hasExtra(Config.DIAG_LAST_ACTION)) e.putString(Config.DIAG_LAST_ACTION, intent.getStringExtra(Config.DIAG_LAST_ACTION));
        if (intent.hasExtra(Config.DIAG_LAST_ERROR)) e.putString(Config.DIAG_LAST_ERROR, intent.getStringExtra(Config.DIAG_LAST_ERROR));
        e.putLong(Config.DIAG_UPDATED_AT, System.currentTimeMillis());
        e.apply();
    }
}
