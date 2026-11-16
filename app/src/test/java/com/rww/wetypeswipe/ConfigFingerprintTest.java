package com.rww.wetypeswipe;

import static org.junit.Assert.*;
import org.junit.Test;

public final class ConfigFingerprintTest {
    @Test public void ignoresSyncRevisionButDetectsAnyKeyMappingChange() {
        Config c = RecommendedDefaults.create();
        String before = ConfigFingerprint.of(c);
        c.revision = 12345;
        assertEquals(before, ConfigFingerprint.of(c));
        c.openEmbeddedSettings = "";
        c.rebuildActionMap();
        assertNotEquals(before, ConfigFingerprint.of(c));
        c.openEmbeddedSettings = "l";
        c.rebuildActionMap();
        assertEquals(before, ConfigFingerprint.of(c));
    }

    @Test public void detectsIndependentUpAndDownAndT9Changes() {
        Config c = RecommendedDefaults.create();
        String before = ConfigFingerprint.of(c);
        c.upQwertyActions['l' - 'a'] = Config.ACTION_COPY;
        assertNotEquals(before, ConfigFingerprint.of(c));
        String afterUp = ConfigFingerprint.of(c);
        c.upT9Actions[2] = Config.ACTION_INSERT_TEXT;
        c.upT9Texts[2] = "中文🙂\nA:B";
        assertNotEquals(afterUp, ConfigFingerprint.of(c));
    }

    @Test public void deepCopyHasSameFingerprintButTextChangesDiffer() {
        Config c = RecommendedDefaults.create();
        c.qwertyTexts['q' - 'a'] = "一行\n二行";
        Config clone = ConfigSnapshot.copyOf(c);
        assertEquals(ConfigFingerprint.of(c), ConfigFingerprint.of(clone));
        clone.qwertyTexts['q' - 'a'] = "一行\n二行修改";
        assertNotEquals(ConfigFingerprint.of(c), ConfigFingerprint.of(clone));
    }
}
