package com.rww.wetypeswipe;

import static org.junit.Assert.*;
import org.junit.Test;

public final class ConfigBackupAndPresetTest {
    @Test public void recommendedPresetFollowsScreenshotAndLKeyOpensSettings() {
        Config c = RecommendedDefaults.create();
        String[] keys = {"a","s","d","f","g","h","j","k","l","z","x","c","v","b","n","m"};
        int[] actions = {
                Config.ACTION_OPEN_CLIPBOARD, Config.ACTION_OPEN_QUICK_PHRASE,
                Config.ACTION_UNDO, Config.ACTION_REDO, Config.ACTION_PARAGRAPH_START,
                Config.ACTION_PARAGRAPH_END, Config.ACTION_DOCUMENT_START,
                Config.ACTION_DOCUMENT_END, Config.ACTION_OPEN_EMBEDDED_SETTINGS,
                Config.ACTION_SELECT_ALL, Config.ACTION_CUT_ALL, Config.ACTION_COPY_ALL,
                Config.ACTION_PASTE, Config.ACTION_DISABLE,
                Config.ACTION_SELECT_TO_DOCUMENT_START, Config.ACTION_SELECT_TO_DOCUMENT_END
        };
        for (int i = 0; i < keys.length; i++) {
            assertEquals("wrong default for " + keys[i], actions[i], c.actionFor(keys[i], false));
        }
        assertEquals(Config.ACTION_NONE, c.actionFor("q", false));
        assertEquals(Config.ACTION_NONE, c.actionForUp("l", false));
        assertEquals(24, Config.ACTION_OPEN_EMBEDDED_SETTINGS);
        assertEquals(Config.ACTION_OPEN_EMBEDDED_SETTINGS,
                Config.actionForMenuPosition(Config.menuPositionForAction(24)));
    }

    @Test public void resetChangesDownOnlyAndPreservesUpT9AndOptions() {
        Config c = new Config();
        c.upQwertyActions['l'-'a'] = Config.ACTION_PASTE;
        c.upT9Actions[2] = Config.ACTION_COPY;
        c.t9Actions[3] = Config.ACTION_CUT;
        c.showKeyLabels = false;
        c.thresholdDp = 23;
        RecommendedDefaults.applyDownQwerty(c);
        assertEquals(Config.ACTION_OPEN_EMBEDDED_SETTINGS, c.actionFor("l", false));
        assertEquals(Config.ACTION_PASTE, c.actionForUp("l", false));
        assertEquals(Config.ACTION_COPY, c.actionForUp("2", true));
        assertEquals(Config.ACTION_CUT, c.actionFor("3", true));
        assertFalse(c.showKeyLabels);
        assertEquals(23, c.thresholdDp);
    }

    @Test public void backupRestoresAllDirectionsAndUnicodeTexts() {
        Config c = RecommendedDefaults.create();
        c.upQwertyActions['l'-'a'] = Config.ACTION_INSERT_TEXT;
        c.upQwertyTexts['l'-'a'] = "第一行\n第二行🙂\\=值";
        c.upQwertyLabels['l'-'a'] = "标💡";
        c.t9Actions[2] = Config.ACTION_COPY;
        c.upT9Actions[2] = Config.ACTION_INSERT_TEXT;
        c.upT9Texts[2] = "上滑九宫格\n:!";
        c.qwertyLabels['z'-'a'] = "全选";
        c.thresholdDp = 22;
        c.t9ThresholdDp = 31;
        c.vibration = false;
        c.revision = 91;
        c.rebuildActionMap();
        String saved = ConfigBackup.exportText(c);
        assertTrue(saved.contains("wetype.config.format=1"));
        Config restored = ConfigBackup.importText(saved);
        assertEquals(c.actionFor("l", false), restored.actionFor("l", false));
        assertEquals(Config.ACTION_INSERT_TEXT, restored.actionForUp("l", false));
        assertEquals(c.textFor("l", false, true), restored.textFor("l", false, true));
        assertEquals("标💡", restored.upQwertyLabels['l'-'a']);
        assertEquals(Config.ACTION_COPY, restored.actionFor("2", true));
        assertEquals(Config.ACTION_INSERT_TEXT, restored.actionForUp("2", true));
        assertEquals("上滑九宫格\n:!", restored.upT9Texts[2]);
        assertEquals("全选", restored.qwertyLabels['z'-'a']);
        assertEquals(22, restored.thresholdDp);
        assertEquals(31, restored.t9ThresholdDp);
        assertFalse(restored.vibration);
        assertEquals(91, restored.revision);
    }

    @Test public void unsupportedOrIncompleteBackupIsRejected() {
        String full = ConfigBackup.exportText(RecommendedDefaults.create());
        rejects(full.replace("wetype.config.format=1", "wetype.config.format=999"));
        rejects("wetype.config.format=1\n");
        rejects(full + "\nunknown_key=unsafe\n");
        rejects(full.replace("up_t9_action_2=0", "up_t9_action_2=999"));
    }

    private static void rejects(String value) {
        try {
            ConfigBackup.importText(value);
            fail("must reject invalid backup");
        } catch (IllegalArgumentException expected) {
            assertNotNull(expected.getMessage());
        }
    }
}
