package com.rww.wetypeswipe;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertNull;

import org.junit.Test;

public class ReflectorHotPathTest {
    @Test public void zeroArgLookupSupportsCachedAndMissingMethods() {
        Reflector reflector = new Reflector();
        ZeroArgTarget target = new ZeroArgTarget();

        assertEquals("ok", reflector.invoke(target, "value"));
        assertEquals("ok", reflector.invoke(target, "value"));
        assertEquals(2, target.calls);
        assertNull(reflector.invoke(target, "missingValue"));
        assertNull(reflector.invoke(target, "missingValue"));
    }

    @Test public void visibleKeyStopsAfterFirstNonNullSecondaryGetter() {
        Reflector reflector = new Reflector();
        KeyResolver resolver = new KeyResolver(reflector);
        LazyButton button = new LazyButton();

        KeyInfo info = resolver.visibleKeyFromButton(button);

        assertNotNull(info);
        assertEquals("a", info.key);
        assertFalse(info.t9);
        assertEquals(1, button.data.subCalls);
        assertEquals(0, button.data.secondaryCalls);
        assertEquals(0, button.data.hintCalls);
        assertEquals(0, button.data.assistCalls);
    }

    static final class ZeroArgTarget {
        int calls;
        String value() {
            calls++;
            return "ok";
        }
    }

    static final class LazyButton {
        final LazyKeyData data = new LazyKeyData();
        LazyKeyData O() { return data; }
    }

    static final class LazyKeyData {
        int subCalls;
        int secondaryCalls;
        int hintCalls;
        int assistCalls;

        String getMainText() { return "a"; }
        String getSubText() {
            subCalls++;
            return "";
        }
        String getSecondaryText() {
            secondaryCalls++;
            return "never";
        }
        String getHintText() {
            hintCalls++;
            return "never";
        }
        String getAssistText() {
            assistCalls++;
            return "never";
        }
    }
}
