package com.rww.wetypeswipe;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

public class InputMethodActionTest {
    @Test public void actionIdsAppendWithoutRenumbering() {
        assertEquals(20, Config.ACTION_INSERT_TEXT);
        assertEquals(21, Config.ACTION_NEXT_INPUT_METHOD);
        assertEquals(22, Config.ACTION_PREVIOUS_INPUT_METHOD);
        assertEquals(23, Config.ACTION_SHOW_INPUT_METHOD_PICKER);
    }

    @Test public void qwertyInputMethodActionsRoundTrip() {
        Config config = new Config();
        EmbeddedConfigEditor.assignQwerty(config, "q", Config.ACTION_NEXT_INPUT_METHOD);
        EmbeddedConfigEditor.assignQwerty(config, "w", Config.ACTION_PREVIOUS_INPUT_METHOD);
        EmbeddedConfigEditor.assignQwerty(config, "e", Config.ACTION_SHOW_INPUT_METHOD_PICKER);
        assertEquals(Config.ACTION_NEXT_INPUT_METHOD, config.actionFor("q", false));
        assertEquals(Config.ACTION_PREVIOUS_INPUT_METHOD, config.actionFor("w", false));
        assertEquals(Config.ACTION_SHOW_INPUT_METHOD_PICKER, config.actionFor("e", false));
    }

    @Test public void t9InputMethodActionsRemainValid() {
        Config config = new Config();
        config.t9Actions[2] = Config.ACTION_NEXT_INPUT_METHOD;
        config.t9Actions[3] = Config.ACTION_PREVIOUS_INPUT_METHOD;
        config.t9Actions[4] = Config.ACTION_SHOW_INPUT_METHOD_PICKER;
        config.rebuildActionMap();
        assertEquals(Config.ACTION_NEXT_INPUT_METHOD, config.actionFor("2", true));
        assertEquals(Config.ACTION_PREVIOUS_INPUT_METHOD, config.actionFor("3", true));
        assertEquals(Config.ACTION_SHOW_INPUT_METHOD_PICKER, config.actionFor("4", true));
    }
}
