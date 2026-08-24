package com.rww.wetypeswipe;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

public final class EmbeddedConfigEditorTest {
    @Test public void assigningActionMovesItAndClearsPreviousBinding() {
        Config config = new Config();
        config.rebuildActionMap();

        EmbeddedConfigEditor.assignQwerty(config, "a", Config.ACTION_COPY);

        assertEquals("a", config.copy);
        assertEquals(Config.ACTION_COPY, EmbeddedConfigEditor.actionForQwerty(config, "a"));
        assertEquals(Config.ACTION_NONE, EmbeddedConfigEditor.actionForQwerty(config, "c"));
    }

    @Test public void disableAndRestoreDefaultsRemainDeterministic() {
        Config config = new Config();
        EmbeddedConfigEditor.assignQwerty(config, "q", Config.ACTION_DISABLE);
        assertEquals(Config.ACTION_DISABLE, EmbeddedConfigEditor.actionForQwerty(config, "q"));

        EmbeddedConfigEditor.restoreDefaults(config);
        assertEquals(Config.ACTION_SELECT_ALL, EmbeddedConfigEditor.actionForQwerty(config, "z"));
        assertEquals(Config.ACTION_CUT, EmbeddedConfigEditor.actionForQwerty(config, "x"));
        assertEquals(Config.ACTION_COPY, EmbeddedConfigEditor.actionForQwerty(config, "c"));
        assertEquals(Config.ACTION_PASTE, EmbeddedConfigEditor.actionForQwerty(config, "v"));
        assertEquals(Config.ACTION_NONE, EmbeddedConfigEditor.actionForQwerty(config, "q"));
    }

    @Test public void clearRemovesEveryQwertyAction() {
        Config config = new Config();
        config.documentEnd = "e";
        config.disabledKeys = "q";
        EmbeddedConfigEditor.clearQwerty(config);

        for (char key = 'a'; key <= 'z'; key++) {
            assertEquals(Config.ACTION_NONE,
                    EmbeddedConfigEditor.actionForQwerty(config, String.valueOf(key)));
        }
    }
}
