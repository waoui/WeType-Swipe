package com.rww.wetypeswipe;

import static org.junit.Assert.assertEquals;
import org.junit.Test;

public final class EmbeddedConfigEditorUpTest {
    @Test public void qwertyUpDoesNotReplaceDownOrOtherUpKeys() {
        Config config = new Config();
        EmbeddedConfigEditor.assignQwertyUp(config, 'z', Config.ACTION_PASTE);
        EmbeddedConfigEditor.assignQwertyUp(config, 'x', Config.ACTION_PASTE);
        assertEquals(Config.ACTION_SELECT_ALL, config.actionFor("z", false));
        assertEquals(Config.ACTION_CUT, config.actionFor("x", false));
        assertEquals(Config.ACTION_PASTE, config.actionForUp("z", false));
        assertEquals(Config.ACTION_PASTE, config.actionForUp("x", false));
        EmbeddedConfigEditor.assignQwertyUpText(config, 'z', "上滑文本🙂");
        assertEquals(Config.ACTION_INSERT_TEXT, config.actionForUp("z", false));
        assertEquals("上滑文本🙂", config.textFor("z", false, true));
        assertEquals(Config.ACTION_SELECT_ALL, config.actionFor("z", false));
        EmbeddedConfigEditor.clearQwertyUp(config);
        assertEquals(Config.ACTION_NONE, config.actionForUp("z", false));
        assertEquals(Config.ACTION_SELECT_ALL, config.actionFor("z", false));
    }

    @Test public void t9UpStaysIndependentOfDownAndCanClear() {
        Config config = new Config();
        config.t9Actions[2] = Config.ACTION_COPY;
        EmbeddedConfigEditor.assignT9UpText(config, 2, "另一条文本");
        assertEquals(Config.ACTION_COPY, config.actionFor("2", true));
        assertEquals(Config.ACTION_INSERT_TEXT, config.actionForUp("2", true));
        EmbeddedConfigEditor.assignT9Up(config, 2, Config.ACTION_OPEN_CLIPBOARD);
        assertEquals("", config.textFor("2", true, true));
        assertEquals(Config.ACTION_OPEN_CLIPBOARD, config.actionForUp("2", true));
        EmbeddedConfigEditor.clearT9Up(config);
        assertEquals(Config.ACTION_COPY, config.actionFor("2", true));
        assertEquals(Config.ACTION_NONE, config.actionForUp("2", true));
    }
}
