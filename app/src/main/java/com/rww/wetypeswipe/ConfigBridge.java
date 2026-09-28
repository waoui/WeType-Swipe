package com.rww.wetypeswipe;

import android.annotation.SuppressLint;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.os.Build;

/** Owns cross-process config synchronization and the target-process cache. */
final class ConfigBridge {
    private static final String MODULE_PACKAGE = "com.rww.wetypeswipe";
    private static final String MODULE_SYNC_RECEIVER = MODULE_PACKAGE + ".ConfigSyncReceiver";

    interface Listener {
        void onConfigChanged(Config config);
        void info(String message);
        void error(String message, Throwable throwable);
    }

    private final String targetPackage;
    private final Listener listener;
    private volatile Config current = defaultConfig();
    private volatile boolean receiverRegistered;
    private volatile boolean targetCacheLoaded;
    private BroadcastReceiver configReceiver;

    ConfigBridge(String targetPackage, Listener listener) {
        this.targetPackage = targetPackage;
        this.listener = listener;
    }

    Config current() { return current; }
    boolean isLoaded() { return targetCacheLoaded; }

    void ensureSync(Context context) {
        if (context == null) return;
        Context stable = stableContext(context);
        registerReceiver(stable);
        loadFromTargetCache(stable);
    }

    synchronized void applyEmbedded(Context context, Config config) {
        if (context == null || config == null) return;
        try {
            int currentRevision = current == null ? 0 : current.revision;
            config.revision = Math.max(config.revision, currentRevision) + 1;
            config.rebuildActionMap();
            setCurrent(config, true);

            Context stable = stableContext(context);
            persistTargetCache(stable, config);

            Intent changed = new Intent(Config.ACTION_CONFIG_CHANGED);
            changed.setPackage(targetPackage);
            ConfigSnapshot.putInto(changed, config);
            stable.sendBroadcast(changed);

            // The embedded editor runs in the WeType process, while the standalone editor
            // persists settings in the module app sandbox. Mirror every embedded save back to
            // the module package so both entry points keep one effective configuration.
            Intent moduleSync = new Intent(Config.ACTION_CONFIG_CHANGED);
            moduleSync.setClassName(MODULE_PACKAGE, MODULE_SYNC_RECEIVER);
            ConfigSnapshot.putInto(moduleSync, config);
            stable.sendBroadcast(moduleSync);

            listener.info("embedded settings saved revision=" + config.revision);
        } catch (Throwable throwable) {
            listener.error("embedded settings save failed", throwable);
        }
    }

    @SuppressLint("UnspecifiedRegisterReceiverFlag")
    private synchronized void registerReceiver(Context context) {
        if (receiverRegistered || context == null) return;
        configReceiver = new BroadcastReceiver() {
            @Override public void onReceive(Context receiverContext, Intent intent) {
                if (intent == null || !Config.ACTION_CONFIG_CHANGED.equals(intent.getAction())) return;
                if (intent.getBooleanExtra(Config.EXTRA_SNAPSHOT, false)) {
                    try {
                        Config config = ConfigCodec.fromIntent(intent);
                        setCurrent(config, true);
                        persistTargetCache(receiverContext, config);
                        return;
                    } catch (Throwable throwable) {
                        listener.error("config snapshot parse failed", throwable);
                    }
                }
                loadFromTargetCache(receiverContext);
            }
        };
        try {
            IntentFilter filter = new IntentFilter(Config.ACTION_CONFIG_CHANGED);
            if (Build.VERSION.SDK_INT >= 33) {
                context.registerReceiver(configReceiver, filter, Context.RECEIVER_EXPORTED);
            } else {
                context.registerReceiver(configReceiver, filter);
            }
            receiverRegistered = true;
        } catch (Throwable throwable) {
            listener.error("config receiver registration failed", throwable);
        }
    }

    private synchronized void persistTargetCache(Context context, Config config) {
        try {
            SharedPreferences.Editor editor = context.getSharedPreferences(
                    Config.TARGET_CACHE_PREFS, Context.MODE_PRIVATE).edit();
            ConfigCodec.writeToPreferences(editor, config);
            editor.commit();
        } catch (Throwable throwable) {
            listener.error("target config cache write failed", throwable);
        }
    }

    private synchronized void loadFromTargetCache(Context context) {
        try {
            SharedPreferences prefs = context.getSharedPreferences(
                    Config.TARGET_CACHE_PREFS, Context.MODE_PRIVATE);
            if (!prefs.contains(Config.KEY_REVISION)) {
                targetCacheLoaded = false;
                return;
            }
            setCurrent(ConfigCodec.fromPreferences(prefs), true);
        } catch (Throwable throwable) {
            targetCacheLoaded = false;
            listener.error("target config cache load failed", throwable);
        }
    }

    private void setCurrent(Config config, boolean loaded) {
        if (config == null) return;
        current = config;
        targetCacheLoaded = loaded;
        if (listener != null) listener.onConfigChanged(config);
    }

    private static Context stableContext(Context context) {
        Context app = context.getApplicationContext();
        return app == null ? context : app;
    }

    private static Config defaultConfig() {
        Config config = new Config();
        config.rebuildActionMap();
        return config;
    }
}
