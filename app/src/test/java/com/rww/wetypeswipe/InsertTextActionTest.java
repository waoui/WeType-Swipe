package com.rww.wetypeswipe;

import static org.junit.Assert.*;
import org.junit.Test;

public final class InsertTextActionTest {
    @Test public void qwertyCustomTextCanBeBoundToMultipleKeys() {
        Config config = new Config();
        EmbeddedConfigEditor.assignQwertyText(config, "a", "hello");
        EmbeddedConfigEditor.assignQwertyText(config, "s", "world");
        assertEquals(Config.ACTION_INSERT_TEXT, EmbeddedConfigEditor.actionForQwerty(config, "a"));
        assertEquals(Config.ACTION_INSERT_TEXT, EmbeddedConfigEditor.actionForQwerty(config, "s"));
        assertEquals("hello", config.textFor("a", false));
        assertEquals("world", config.textFor("s", false));
    }

    @Test public void t9CustomTextIsIndependentPerDigit() {
        Config config = new Config();
        EmbeddedConfigEditor.assignT9Text(config, 2, "固定回复");
        EmbeddedConfigEditor.assignT9Text(config, 3, "123");
        assertEquals(Config.ACTION_INSERT_TEXT, config.actionFor("2", true));
        assertEquals(Config.ACTION_INSERT_TEXT, config.actionFor("3", true));
        assertEquals("固定回复", config.textFor("2", true));
        assertEquals("123", config.textFor("3", true));
    }

    @Test public void textLengthIsCappedAtOneThousandCodePoints() {
        StringBuilder value = new StringBuilder();
        for (int i = 0; i < 1100; i++) value.append("😀");
        String normalized = Config.normalizeInsertedText(value.toString());
        assertEquals(1000, normalized.codePointCount(0, normalized.length()));
    }
}
