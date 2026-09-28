package com.rww.wetypeswipe;

import android.content.Intent;
import android.content.SharedPreferences;

/** Centralized serialization for module prefs, target-process cache and broadcasts. */
final class ConfigCodec {
    interface Reader {
        String getString(String key, String fallback);
        int getInt(String key, int fallback);
        boolean getBoolean(String key, boolean fallback);
    }

    interface Writer {
        void putString(String key, String value);
        void putInt(String key, int value);
        void putBoolean(String key, boolean value);
    }

    private ConfigCodec() {}

    static Config fromPreferences(SharedPreferences preferences) {
        return read(new Reader() {
            @Override public String getString(String key, String fallback) {
                return preferences.getString(key, fallback);
            }
            @Override public int getInt(String key, int fallback) {
                return preferences.getInt(key, fallback);
            }
            @Override public boolean getBoolean(String key, boolean fallback) {
                return preferences.getBoolean(key, fallback);
            }
        });
    }

    static void writeToPreferences(SharedPreferences.Editor editor, Config config) {
        write(new Writer() {
            @Override public void putString(String key, String value) { editor.putString(key, value); }
            @Override public void putInt(String key, int value) { editor.putInt(key, value); }
            @Override public void putBoolean(String key, boolean value) { editor.putBoolean(key, value); }
        }, config);
    }

    static Config fromIntent(Intent intent) {
        return read(new Reader() {
            @Override public String getString(String key, String fallback) {
                String value = intent.getStringExtra(key);
                return value == null ? fallback : value;
            }
            @Override public int getInt(String key, int fallback) {
                return intent.getIntExtra(key, fallback);
            }
            @Override public boolean getBoolean(String key, boolean fallback) {
                return intent.getBooleanExtra(key, fallback);
            }
        });
    }

    static void putIntoIntent(Intent intent, Config config) {
        intent.putExtra(Config.EXTRA_SNAPSHOT, true);
        write(new Writer() {
            @Override public void putString(String key, String value) { intent.putExtra(key, value); }
            @Override public void putInt(String key, int value) { intent.putExtra(key, value); }
            @Override public void putBoolean(String key, boolean value) { intent.putExtra(key, value); }
        }, config);
    }

    static Config read(Reader reader) {
        Config config = new Config();
        for (int action : ActionRegistry.qwertyActions()) {
            String storageKey = ActionRegistry.storageKey(action);
            String fallback = ActionRegistry.keyFor(config, action);
            ActionRegistry.setKey(config, action, reader.getString(storageKey, fallback));
        }
        config.disabledKeys = reader.getString(Config.KEY_DISABLED_KEYS, "");
        config.thresholdDp = clamp(reader.getInt(Config.KEY_THRESHOLD, 12), 6, 40, 12);
        config.t9ThresholdDp = clamp(reader.getInt(Config.KEY_T9_THRESHOLD, 20), 10, 48, 20);
        config.vibration = reader.getBoolean(Config.KEY_VIBRATION, true);
        config.showKeyLabels = reader.getBoolean(Config.KEY_SHOW_KEY_LABELS, true);
        config.showTriggerHint = reader.getBoolean(Config.KEY_SHOW_TRIGGER_HINT, true);
        config.revision = reader.getInt(Config.KEY_REVISION, 0);
        for (char key = 'a'; key <= 'z'; key++) {
            config.qwertyLabels[key - 'a'] = Config.normalizeLabelValue(
                    reader.getString(Config.qwertyLabelPrefKey(key), ""));
            config.qwertyTexts[key - 'a'] = Config.normalizeInsertedText(
                    reader.getString(Config.qwertyTextPrefKey(key), ""));
        }
        for (int digit = 2; digit <= 9; digit++) {
            config.t9Actions[digit] = Config.validAction(
                    reader.getInt(Config.t9PrefKey(digit), Config.ACTION_NONE));
            config.t9Labels[digit] = Config.normalizeLabelValue(
                    reader.getString(Config.t9LabelPrefKey(digit), ""));
            config.t9Texts[digit] = Config.normalizeInsertedText(
                    reader.getString(Config.t9TextPrefKey(digit), ""));
        }
        config.rebuildActionMap();
        return config;
    }

    static void write(Writer writer, Config config) {
        if (config == null) config = new Config();
        for (int action : ActionRegistry.qwertyActions()) {
            writer.putString(ActionRegistry.storageKey(action), ActionRegistry.keyFor(config, action));
        }
        writer.putString(Config.KEY_DISABLED_KEYS, config.disabledKeys == null ? "" : config.disabledKeys);
        writer.putInt(Config.KEY_THRESHOLD, config.thresholdDp);
        writer.putInt(Config.KEY_T9_THRESHOLD, config.t9ThresholdDp);
        writer.putBoolean(Config.KEY_VIBRATION, config.vibration);
        writer.putBoolean(Config.KEY_SHOW_KEY_LABELS, config.showKeyLabels);
        writer.putBoolean(Config.KEY_SHOW_TRIGGER_HINT, config.showTriggerHint);
        writer.putInt(Config.KEY_REVISION, config.revision);
        for (char key = 'a'; key <= 'z'; key++) {
            writer.putString(Config.qwertyLabelPrefKey(key),
                    Config.normalizeLabelValue(config.qwertyLabels[key - 'a']));
            writer.putString(Config.qwertyTextPrefKey(key),
                    Config.normalizeInsertedText(config.qwertyTexts[key - 'a']));
        }
        for (int digit = 2; digit <= 9; digit++) {
            writer.putInt(Config.t9PrefKey(digit), config.t9Actions[digit]);
            writer.putString(Config.t9LabelPrefKey(digit),
                    Config.normalizeLabelValue(config.t9Labels[digit]));
            writer.putString(Config.t9TextPrefKey(digit),
                    Config.normalizeInsertedText(config.t9Texts[digit]));
        }
    }

    static Config copyOf(Config source) {
        Config target = new Config();
        if (source == null) {
            target.rebuildActionMap();
            return target;
        }
        for (int action : ActionRegistry.qwertyActions()) {
            ActionRegistry.setKey(target, action, ActionRegistry.keyFor(source, action));
        }
        target.disabledKeys = source.disabledKeys;
        target.thresholdDp = source.thresholdDp;
        target.t9ThresholdDp = source.t9ThresholdDp;
        target.vibration = source.vibration;
        target.showKeyLabels = source.showKeyLabels;
        target.showTriggerHint = source.showTriggerHint;
        target.revision = source.revision;
        System.arraycopy(source.t9Actions, 0, target.t9Actions, 0, source.t9Actions.length);
        System.arraycopy(source.qwertyLabels, 0, target.qwertyLabels, 0, source.qwertyLabels.length);
        System.arraycopy(source.t9Labels, 0, target.t9Labels, 0, source.t9Labels.length);
        System.arraycopy(source.qwertyTexts, 0, target.qwertyTexts, 0, source.qwertyTexts.length);
        System.arraycopy(source.t9Texts, 0, target.t9Texts, 0, source.t9Texts.length);
        target.rebuildActionMap();
        return target;
    }

    private static int clamp(int value, int min, int max, int fallback) {
        return value < min || value > max ? fallback : value;
    }
}
