package com.rww.wetypeswipe;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotSame;

import org.junit.Test;

public final class ConfigSnapshotTest {
    @Test public void copyIsIndependentAndKeepsAllEmbeddedSettings() {
        Config source = new Config();
        source.selectAll = "a";
        source.documentEnd = "e";
        source.thresholdDp = 27;
        source.t9ThresholdDp = 31;
        source.vibration = false;
        source.showKeyLabels = false;
        source.showTriggerHint = true;
        source.revision = 9;
        source.t9Actions[2] = Config.ACTION_DOCUMENT_END;
        source.qwertyLabels[0] = "自定";
        source.t9Labels[2] = "文尾";
        source.rebuildActionMap();

        Config copy = ConfigSnapshot.copyOf(source);

        assertNotSame(source, copy);
        assertEquals("a", copy.selectAll);
        assertEquals("e", copy.documentEnd);
        assertEquals(27, copy.thresholdDp);
        assertEquals(31, copy.t9ThresholdDp);
        assertEquals(false, copy.vibration);
        assertEquals(false, copy.showKeyLabels);
        assertEquals(true, copy.showTriggerHint);
        assertEquals(9, copy.revision);
        assertEquals(Config.ACTION_DOCUMENT_END, copy.t9Actions[2]);
        assertEquals("自定", copy.qwertyLabels[0]);
        assertEquals("文尾", copy.t9Labels[2]);

        copy.qwertyLabels[0] = "变化";
        assertEquals("自定", source.qwertyLabels[0]);
    }
}
