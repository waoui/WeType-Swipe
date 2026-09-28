package com.rww.wetypeswipe;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotSame;

import java.util.HashMap;
import java.util.Map;
import org.junit.Test;

public final class ConfigCodecTest {
    @Test public void allFieldsRoundTripThroughOneCodec() {
        Config source = new Config();
        int index = 0;
        for (int action : ActionRegistry.qwertyActions()) {
            ActionRegistry.setKey(source, action, String.valueOf((char) ('a' + index++)));
        }
        source.disabledKeys = "yz";
        source.thresholdDp = 23;
        source.t9ThresholdDp = 37;
        source.vibration = false;
        source.showKeyLabels = false;
        source.showTriggerHint = true;
        source.revision = 81;
        source.qwertyLabels[0] = "标签";
        source.qwertyTexts[1] = "固定文本🙂";
        source.t9Actions[2] = Config.ACTION_OPEN_CLIPBOARD;
        source.t9Labels[2] = "剪贴";
        source.t9Texts[3] = "T9文本";
        source.rebuildActionMap();

        MapStore store = new MapStore();
        ConfigCodec.write(store, source);
        Config restored = ConfigCodec.read(store);

        for (int action : ActionRegistry.qwertyActions()) {
            assertEquals(ActionRegistry.keyFor(source, action), ActionRegistry.keyFor(restored, action));
        }
        assertEquals("yz", restored.disabledKeys);
        assertEquals(23, restored.thresholdDp);
        assertEquals(37, restored.t9ThresholdDp);
        assertEquals(false, restored.vibration);
        assertEquals(false, restored.showKeyLabels);
        assertEquals(true, restored.showTriggerHint);
        assertEquals(81, restored.revision);
        assertEquals("标签", restored.qwertyLabels[0]);
        assertEquals("固定文本🙂", restored.qwertyTexts[1]);
        assertEquals(Config.ACTION_OPEN_CLIPBOARD, restored.t9Actions[2]);
        assertEquals("剪贴", restored.t9Labels[2]);
        assertEquals("T9文本", restored.t9Texts[3]);
    }

    @Test public void copyIsDeepEnoughForMutableArrays() {
        Config source = new Config();
        source.qwertyLabels[0] = "原值";
        source.t9Texts[2] = "原文本";
        Config copy = ConfigCodec.copyOf(source);
        assertNotSame(source, copy);
        copy.qwertyLabels[0] = "变化";
        copy.t9Texts[2] = "变化";
        assertEquals("原值", source.qwertyLabels[0]);
        assertEquals("原文本", source.t9Texts[2]);
    }

    private static final class MapStore implements ConfigCodec.Reader, ConfigCodec.Writer {
        private final Map<String, Object> values = new HashMap<>();
        @Override public String getString(String key, String fallback) {
            Object value = values.get(key); return value instanceof String ? (String) value : fallback;
        }
        @Override public int getInt(String key, int fallback) {
            Object value = values.get(key); return value instanceof Integer ? (Integer) value : fallback;
        }
        @Override public boolean getBoolean(String key, boolean fallback) {
            Object value = values.get(key); return value instanceof Boolean ? (Boolean) value : fallback;
        }
        @Override public void putString(String key, String value) { values.put(key, value); }
        @Override public void putInt(String key, int value) { values.put(key, value); }
        @Override public void putBoolean(String key, boolean value) { values.put(key, value); }
    }
}
