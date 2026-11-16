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
        source.upQwertyActions['z' - 'a'] = Config.ACTION_INSERT_TEXT;
        source.upQwertyTexts['z' - 'a'] = "上滑输入🙂";
        source.upQwertyLabels['z' - 'a'] = "上文";
        source.upT9Actions[3] = Config.ACTION_OPEN_CLIPBOARD;
        source.upT9Labels[3] = "上剪";
        source.upT9Texts[4] = "另一个文本";
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
        assertEquals(Config.ACTION_INSERT_TEXT, restored.actionForUp("z", false));
        assertEquals("上滑输入🙂", restored.textFor("z", false, true));
        assertEquals("上文", restored.upQwertyLabels['z' - 'a']);
        assertEquals(Config.ACTION_OPEN_CLIPBOARD, restored.actionForUp("3", true));
        assertEquals("上剪", restored.upT9Labels[3]);
        assertEquals("另一个文本", restored.upT9Texts[4]);
    }

    @Test public void copyIsDeepEnoughForMutableArrays() {
        Config source = new Config();
        source.qwertyLabels[0] = "原值";
        source.t9Texts[2] = "原文本";
        source.upQwertyActions[0] = Config.ACTION_COPY;
        source.upQwertyTexts[0] = "上滑旧文本";
        source.upT9Labels[2] = "上滑旧标签";
        Config copy = ConfigCodec.copyOf(source);
        assertNotSame(source, copy);
        copy.qwertyLabels[0] = "变化";
        copy.t9Texts[2] = "变化";
        copy.upQwertyActions[0] = Config.ACTION_PASTE;
        copy.upQwertyTexts[0] = "变化";
        copy.upT9Labels[2] = "变化";
        assertEquals("原值", source.qwertyLabels[0]);
        assertEquals("原文本", source.t9Texts[2]);
        assertEquals(Config.ACTION_COPY, source.upQwertyActions[0]);
        assertEquals("上滑旧文本", source.upQwertyTexts[0]);
        assertEquals("上滑旧标签", source.upT9Labels[2]);
    }

    @Test public void legacyPreferencesWithoutUpFieldsStayDownwardOnly() {
        Config legacy = new Config();
        legacy.rebuildActionMap();
        MapStore store = new MapStore();
        ConfigCodec.write(store, legacy);
        for (char key = 'a'; key <= 'z'; key++) {
            store.values.remove(Config.upQwertyActionPrefKey(key));
            store.values.remove(Config.upQwertyTextPrefKey(key));
            store.values.remove(Config.upQwertyLabelPrefKey(key));
        }
        for (int digit = 2; digit <= 9; digit++) {
            store.values.remove(Config.upT9ActionPrefKey(digit));
            store.values.remove(Config.upT9TextPrefKey(digit));
            store.values.remove(Config.upT9LabelPrefKey(digit));
        }
        Config restored = ConfigCodec.read(store);
        assertEquals(Config.ACTION_SELECT_ALL, restored.actionFor("z", false));
        assertEquals(Config.ACTION_NONE, restored.actionForUp("z", false));
        assertEquals(Config.ACTION_NONE, restored.actionForUp("2", true));
    }

    @Test public void upwardOnlyBindingsAreActiveAndKeepDirectionsSeparate() {
        Config c = new Config();
        // Clear old default downward actions.
        for (int action : ActionRegistry.qwertyActions()) ActionRegistry.setKey(c, action, "");
        c.upQwertyActions['q' - 'a'] = Config.ACTION_COPY;
        c.upT9Actions[2] = Config.ACTION_INSERT_TEXT;
        c.upT9Texts[2] = "独立上滑";
        c.rebuildActionMap();
        assertEquals(true, c.hasAnyBinding());
        assertEquals(Config.ACTION_COPY, c.actionForUp("q", false));
        assertEquals(Config.ACTION_NONE, c.actionFor("q", false));
        assertEquals(Config.ACTION_INSERT_TEXT, c.actionForUp("2", true));
        assertEquals("独立上滑", c.textFor("2", true, true));
        assertEquals("", c.textFor("2", true, false));
        assertEquals(Config.ACTION_NONE, c.actionForUp("1", true));
        c.upT9Texts[2] = "";
        assertEquals(Config.ACTION_NONE, c.actionForUp("2", true));
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
