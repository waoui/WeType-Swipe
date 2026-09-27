package com.rww.wetypeswipe;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

public final class ToolbarCarrierLayoutTest {
    private enum Source {
        Invalid,
        Temporary,
        Advanced,
        Permanent,
        RecentlyUsed
    }

    private static final class LegacyHolder {
        int f;
        Source g = Source.Temporary;
        int h;
    }

    private static final class WeType4Holder {
        Object f;
        int g;
        Source h = Source.Temporary;
        int i;
    }

    private static final class FutureObfuscatedHolder {
        Object p;
        int q;
        Source r = Source.Temporary;
        int s;
        Object t;
    }

    @Test public void resolvesLegacyFieldLayout() {
        ToolbarCarrierLayout.Fields fields = ToolbarCarrierLayout.resolve(LegacyHolder.class);
        assertNotNull(fields);
        assertEquals("f", fields.function.getName());
        assertEquals("g", fields.category.getName());
        assertEquals("h", fields.group.getName());
        assertEquals(Source.Permanent, fields.permanentCategory);
        assertFalse(fields.weType4Layout);
    }

    @Test public void resolvesWeType4FieldLayout() {
        ToolbarCarrierLayout.Fields fields = ToolbarCarrierLayout.resolve(WeType4Holder.class);
        assertNotNull(fields);
        assertEquals("g", fields.function.getName());
        assertEquals("h", fields.category.getName());
        assertEquals("i", fields.group.getName());
        assertEquals(Source.Permanent, fields.permanentCategory);
        assertTrue(fields.weType4Layout);
    }

    @Test public void fallsBackToStructuralLayout() {
        ToolbarCarrierLayout.Fields fields = ToolbarCarrierLayout.resolve(FutureObfuscatedHolder.class);
        assertNotNull(fields);
        assertEquals("q", fields.function.getName());
        assertEquals("r", fields.category.getName());
        assertEquals("s", fields.group.getName());
        assertEquals(Source.Permanent, fields.permanentCategory);
    }
}
