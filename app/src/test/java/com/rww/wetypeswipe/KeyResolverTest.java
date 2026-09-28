package com.rww.wetypeswipe;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

public final class KeyResolverTest {
    private final KeyResolver resolver = new KeyResolver(new Reflector());

    @Test public void resolvesQwertyFromStableKeyDataMethods() {
        KeyInfo info = resolver.visibleKeyFromButton(new FakeButton(new FakeKeyData("Q", ""), "q_key_q"));
        assertNotNull(info);
        assertEquals("q", info.key);
        assertEquals("Q", info.display);
        assertFalse(info.t9);
    }

    @Test public void resolvesT9FromLetterCluster() {
        KeyInfo info = resolver.visibleKeyFromButton(new FakeButton(new FakeKeyData("2", "ABC"), "t9_key_2"));
        assertNotNull(info);
        assertEquals("2", info.key);
        assertTrue(info.t9);
    }

    public static final class FakeButton {
        private final FakeKeyData data;
        private final String id;
        FakeButton(FakeKeyData data, String id) { this.data = data; this.id = id; }
        public FakeKeyData O() { return data; }
        public String K() { return id; }
    }

    public static final class FakeKeyData {
        private final String main;
        private final String sub;
        FakeKeyData(String main, String sub) { this.main = main; this.sub = sub; }
        public String getMainText() { return main; }
        public String getSubText() { return sub; }
        public String getSecondaryText() { return null; }
        public String getHintText() { return null; }
        public String getAssistText() { return null; }
        public String getId() { return ""; }
    }
}
