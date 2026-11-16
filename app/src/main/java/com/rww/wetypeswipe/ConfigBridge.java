package com.rww.wetypeswipe;

import android.annotation.SuppressLint;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.os.Build;
import android.os.SystemClock;

import java.util.UUID;

/**
 * The WeType target-private preferences are the ONLY editable configuration source.
 * The module package is consulted once only if this target has never stored a config.
 */
final class ConfigBridge {
    private static final String MODULE_PACKAGE = "com.rww.wetypeswipe";
    private static final String MODULE_LEGACY_RECEIVER = MODULE_PACKAGE + ".ConfigSyncReceiver";
    private static final long MIGRATION_RETRY_MS = 30_000L;

    interface Listener {
        void onConfigChanged(Config config);
        void info(String message);
        void error(String message, Throwable throwable);
    }

    private final String targetPackage;
    private final Listener listener;
    private volatile Config current = RecommendedDefaults.create();
    private volatile boolean receiverRegistered;
    private volatile boolean targetCacheLoaded;
    private volatile String migrationToken;
    private volatile long lastMigrationRequestTime;
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
        // Never ask the old standalone application to overwrite existing target settings.
        if (!targetCacheLoaded) {
            loadFromTargetCache(stable);
            if (!targetCacheLoaded) requestLegacyMigration(stable);
        }
    }

    synchronized void applyEmbedded(Context context, Config config) {
        if (context == null || config == null) {
            throw new IllegalArgumentException("内置设置配置不可为空");
        }
        Config saved = ConfigSnapshot.copyOf(config);
        saved.revision = Math.max(saved.revision, current.revision) + 1;
        saved.rebuildActionMap();
        Context stable = stableContext(context);
        if (!persistTargetCache(stable, saved)) {
            throw new IllegalStateException("无法保存微信输入法内部配置；原有配置未覆盖");
        }
        migrationToken = null;
        setCurrent(saved, true);
        // Other WeType processes (e.g. IME and UI) update their in-memory snapshots.
        Intent changed = new Intent(Config.ACTION_CONFIG_CHANGED);
        changed.setPackage(targetPackage);
        ConfigSnapshot.putInto(changed, saved);
        stable.sendBroadcast(changed);
        info("embedded config committed as sole source, revision=" + saved.revision);
    }

    @SuppressLint("UnspecifiedRegisterReceiverFlag")
    private synchronized void registerReceiver(Context context) {
        if (receiverRegistered || context == null) return;
        configReceiver = new BroadcastReceiver() {
            @Override public void onReceive(Context receiverContext, Intent intent) {
                if (intent == null) return;
                String action = intent.getAction();
                if (Config.ACTION_LEGACY_CONFIG_RESPONSE.equals(action)) {
                    handleLegacyResponse(receiverContext, intent);
                } else if (Config.ACTION_CONFIG_CHANGED.equals(action)) {
                    if (intent.getBooleanExtra(Config.EXTRA_SNAPSHOT, false)) {
                        try {
                            Config incoming = ConfigCodec.fromIntent(intent);
                            if (targetCacheLoaded && incoming.revision < current.revision) {
                                info("ignored stale intra-WeType snapshot revision=" + incoming.revision);
                                return;
                            }
                            if (persistTargetCache(receiverContext, incoming)) {
                                setCurrent(incoming, true);
                            }
                        } catch (Throwable error) {
                            error("intra-WeType snapshot rejected", error);
                        }
                    } else {
                        loadFromTargetCache(receiverContext);
                    }
                }
            }
        };
        try {
            IntentFilter filter = new IntentFilter();
            filter.addAction(Config.ACTION_CONFIG_CHANGED);
            filter.addAction(Config.ACTION_LEGACY_CONFIG_RESPONSE);
            if (Build.VERSION.SDK_INT >= 33) {
                context.registerReceiver(configReceiver, filter, Context.RECEIVER_EXPORTED);
            } else {
                context.registerReceiver(configReceiver, filter);
            }
            receiverRegistered = true;
        } catch (Throwable error) {
            error("target config receiver registration failed", error);
        }
    }

    private synchronized void requestLegacyMigration(Context context) {
        if (targetCacheLoaded || !receiverRegistered) return;
        long now = SystemClock.elapsedRealtime();
        if (migrationToken != null && now - lastMigrationRequestTime < MIGRATION_RETRY_MS) return;
        migrationToken = UUID.randomUUID().toString();
        lastMigrationRequestTime = now;
        try {
            Intent request = new Intent(Config.ACTION_LEGACY_CONFIG_REQUEST);
            request.setClassName(MODULE_PACKAGE, MODULE_LEGACY_RECEIVER);
            request.putExtra(Config.EXTRA_MIGRATION_TOKEN, migrationToken);
            context.sendBroadcast(request);
            info("requested optional one-time legacy config migration");
        } catch (RuntimeException error) {
            migrationToken = null;
            error("legacy config migration request failed; defaults remain available", error);
        }
    }

    private synchronized void handleLegacyResponse(Context context, Intent intent) {
        String expectedToken = migrationToken;
        if (expectedToken == null
                || !expectedToken.equals(intent.getStringExtra(Config.EXTRA_MIGRATION_TOKEN))
                || !intent.getBooleanExtra(Config.EXTRA_SNAPSHOT, false)) {
            info("ignored unrequested legacy config snapshot");
            return;
        }
        SharedPreferences prefs = context.getSharedPreferences(
                Config.TARGET_CACHE_PREFS, Context.MODE_PRIVATE);
        if (targetCacheLoaded || prefs.contains(Config.KEY_REVISION)) {
            migrationToken = null;
            info("ignored legacy config: authoritative WeType settings already exist");
            return;
        }
        try {
            Config imported = ConfigCodec.fromIntent(intent);
            imported.revision = Math.max(1, imported.revision);
            imported.rebuildActionMap();
            if (!persistTargetCache(context, imported)) return;
            migrationToken = null;
            setCurrent(imported, true);
            // A target may have separate IME and launcher processes. Propagate the
            // migrated snapshot immediately so another live target process is refreshed.
            Intent changed = new Intent(Config.ACTION_CONFIG_CHANGED);
            changed.setPackage(targetPackage);
            ConfigSnapshot.putInto(changed, imported);
            context.sendBroadcast(changed);
            info("legacy module configuration migrated once, revision=" + imported.revision);
        } catch (Throwable error) {
            this.error("legacy configuration migration rejected", error);
        }
    }

    private synchronized boolean persistTargetCache(Context context, Config config) {
        try {
            SharedPreferences.Editor editor = context.getSharedPreferences(
                    Config.TARGET_CACHE_PREFS, Context.MODE_PRIVATE).edit();
            ConfigCodec.writeToPreferences(editor, config);
            if (editor.commit()) return true;
            error("target config commit returned false", null);
        } catch (Throwable throwable) {
            error("target config commit failed", throwable);
        }
        return false;
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
        } catch (Throwable error) {
            error("target config load failed; old preferences remain preserved", error);
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

    private void info(String message) {
        if (listener != null) listener.info(message);
    }

    private void error(String message, Throwable throwable) {
        if (listener != null) listener.error(message, throwable);
    }
}
