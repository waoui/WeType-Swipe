package com.rww.wetypeswipe;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

public final class ConfigTest {
    @Test public void defaultBindingsRemainStable() {
        Config config = new Config();
        config.rebuildActionMap();

        assertEquals(Config.ACTION_SELECT_ALL, config.actionFor("z", false));
        assertEquals(Config.ACTION_CUT, config.actionFor("x", false));
        assertEquals(Config.ACTION_COPY, config.actionFor("c", false));
        assertEquals(Config.ACTION_PASTE, config.actionFor("v", false));
        assertEquals(Config.ACTION_NONE, config.actionFor("2", true));
        assertTrue(config.hasAnyBinding());
    }

    @Test public void disabledKeysDoNotOverrideAssignedActions() {
        Config config = new Config();
        config.disabledKeys = "azza";
        config.rebuildActionMap();

        assertEquals(Config.ACTION_SELECT_ALL, config.actionFor("z", false));
        assertEquals(Config.ACTION_DISABLE, config.actionFor("a", false));
    }

    @Test public void menuPositionsRoundTrip() {
        for (int position = 0; position < Config.ACTION_MENU_LABELS.length; position++) {
            int action = Config.actionForMenuPosition(position);
            assertEquals(position, Config.menuPositionForAction(action));
        }
    }

    @Test public void labelNormalizationIsUnicodeSafe() {
        assertEquals("", Config.normalizeLabelValue(null));
        assertEquals(Config.LABEL_HIDDEN,
                Config.normalizeLabelValue(Config.LABEL_HIDDEN));
        assertEquals("A B", Config.normalizeLabelValue("  A\nB  "));
        assertEquals("😀甲乙丙", Config.normalizeLabelValue("😀甲乙丙丁"));
    }

    @Test public void configuredLabelsOverrideAutomaticLabels() {
        Config config = new Config();
        config.qwertyLabels['c' - 'a'] = "自定";
        config.qwertyLabels['v' - 'a'] = Config.LABEL_HIDDEN;

        assertEquals("自定", config.labelFor("c", false, Config.ACTION_COPY));
        assertEquals("", config.labelFor("v", false, Config.ACTION_PASTE));
        assertEquals("全复制", config.labelFor("a", false, Config.ACTION_COPY_ALL));
        assertEquals("", Config.shortActionLabel(Config.ACTION_NONE));
    }
}
