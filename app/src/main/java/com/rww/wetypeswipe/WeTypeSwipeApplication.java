package com.rww.wetypeswipe;

import android.app.Activity;
import android.app.Application;
import android.os.Bundle;

/** Refreshes an already-created standalone settings Activity after an embedded save. */
public final class WeTypeSwipeApplication extends Application
        implements Application.ActivityLifecycleCallbacks {

    @Override public void onCreate() {
        super.onCreate();
        registerActivityLifecycleCallbacks(this);
    }

    @Override public void onActivityCreated(Activity activity, Bundle savedInstanceState) {
        if (!(activity instanceof MainActivity)) return;
        // A newly-created MainActivity loads preferences in onCreate(), so no second rebuild is needed.
        getSharedPreferences(Config.PREFS, MODE_PRIVATE)
                .edit()
                .remove(ConfigSyncReceiver.KEY_EXTERNAL_SYNC_PENDING)
                .apply();
    }

    @Override public void onActivityResumed(Activity activity) {
        if (!(activity instanceof MainActivity)) return;
        boolean pending = getSharedPreferences(Config.PREFS, MODE_PRIVATE)
                .getBoolean(ConfigSyncReceiver.KEY_EXTERNAL_SYNC_PENDING, false);
        if (!pending) return;

        getSharedPreferences(Config.PREFS, MODE_PRIVATE)
                .edit()
                .remove(ConfigSyncReceiver.KEY_EXTERNAL_SYNC_PENDING)
                .commit();
        activity.recreate();
    }

    @Override public void onActivityStarted(Activity activity) {}
    @Override public void onActivityPaused(Activity activity) {}
    @Override public void onActivityStopped(Activity activity) {}
    @Override public void onActivitySaveInstanceState(Activity activity, Bundle outState) {}
    @Override public void onActivityDestroyed(Activity activity) {}
}
