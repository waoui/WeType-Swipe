package com.rww.wetypeswipe;

import java.util.Arrays;

/**
 * Screenshot-based recommended down-swipe preset for clean installs and explicit reset only.
 * Existing persisted user mappings are never overwritten automatically on upgrade.
 */
final class RecommendedDefaults {
    private RecommendedDefaults() {}

    static Config create() {
        Config config = new Config();
        applyDownQwerty(config);
        return config;
    }

    /** Replace QWERTY downward bindings only; leave T9 and all upward bindings intact. */
    static void applyDownQwerty(Config config) {
        if (config == null) return;
        for (int action : ActionRegistry.qwertyActions()) {
            ActionRegistry.setKey(config, action, "");
        }
        Arrays.fill(config.qwertyTexts, "");
        config.disabledKeys = "b";
        Arrays.fill(config.qwertyLabels, "");
        config.qwertyLabels['s' - 'a'] = "常用语";

        bind(config, Config.ACTION_OPEN_CLIPBOARD, "a");
        bind(config, Config.ACTION_OPEN_QUICK_PHRASE, "s");
        bind(config, Config.ACTION_UNDO, "d");
        bind(config, Config.ACTION_REDO, "f");
        bind(config, Config.ACTION_PARAGRAPH_START, "g");
        bind(config, Config.ACTION_PARAGRAPH_END, "h");
        bind(config, Config.ACTION_DOCUMENT_START, "j");
        bind(config, Config.ACTION_DOCUMENT_END, "k");
        bind(config, Config.ACTION_OPEN_EMBEDDED_SETTINGS, "l");
        bind(config, Config.ACTION_SELECT_ALL, "z");
        bind(config, Config.ACTION_CUT_ALL, "x");
        bind(config, Config.ACTION_COPY_ALL, "c");
        bind(config, Config.ACTION_PASTE, "v");
        bind(config, Config.ACTION_SELECT_TO_DOCUMENT_START, "n");
        bind(config, Config.ACTION_SELECT_TO_DOCUMENT_END, "m");
        config.rebuildActionMap();
    }

    private static void bind(Config config, int action, String key) {
        ActionRegistry.setKey(config, action, key);
    }
}
