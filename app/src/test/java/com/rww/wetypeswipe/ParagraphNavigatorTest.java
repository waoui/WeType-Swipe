package com.rww.wetypeswipe;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

public final class ParagraphNavigatorTest {
    @Test public void noLineBreakUsesAllAvailableContext() {
        assertEquals(5, ParagraphNavigator.distanceToStart("hello"));
        assertEquals(5, ParagraphNavigator.distanceToEnd("world"));
    }

    @Test public void nearestLineBreakDefinesParagraphBoundary() {
        assertEquals(6, ParagraphNavigator.distanceToStart("first\r\nsecond"));
        assertEquals(6, ParagraphNavigator.distanceToEnd("second\r\nthird"));
        assertEquals(0, ParagraphNavigator.distanceToStart("first\n"));
        assertEquals(0, ParagraphNavigator.distanceToEnd("\nnext"));
    }

    @Test public void unicodeParagraphSeparatorsAreSupported() {
        assertEquals(2, ParagraphNavigator.distanceToStart("甲\u2028乙丙"));
        assertEquals(2, ParagraphNavigator.distanceToEnd("乙丙\u2029丁"));
    }

    @Test public void indexClampingHandlesInvalidEditorValues() {
        assertEquals(0, ParagraphNavigator.clampIndex(-1, 10));
        assertEquals(4, ParagraphNavigator.clampIndex(4, 10));
        assertEquals(10, ParagraphNavigator.clampIndex(12, 10));
        assertEquals(0, ParagraphNavigator.clampIndex(2, -1));
    }
}
