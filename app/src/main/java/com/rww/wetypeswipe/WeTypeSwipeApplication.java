package com.rww.wetypeswipe;

import android.app.Application;

/**
 * Application process host.
 *
 * The standalone settings Activity now owns live config refresh so a receiver notification
 * updates an already visible screen; the old lifecycle callbacks could clear a pending
 * snapshot before the Activity had a chance to display it.
 */
public final class WeTypeSwipeApplication extends Application {
    @Override public void onCreate() {
        super.onCreate();
    }
}
