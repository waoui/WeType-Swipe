package com.rww.wetypeswipe;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNull;

import org.junit.Test;

public final class DocumentNavigatorTest {
    @Test public void collapsedCursorMovesAcrossWholeDocument() {
        assertTarget(Config.ACTION_DOCUMENT_START, 12, 12, 80, 0, 0);
        assertTarget(Config.ACTION_DOCUMENT_END, 12, 12, 80, 80, 80);
        assertTarget(Config.ACTION_SELECT_TO_DOCUMENT_START, 12, 12, 80, 0, 12);
        assertTarget(Config.ACTION_SELECT_TO_DOCUMENT_END, 12, 12, 80, 12, 80);
    }

    @Test public void existingSelectionExpandsWithoutDiscardingItsOtherEdge() {
        assertTarget(Config.ACTION_SELECT_TO_DOCUMENT_START, 20, 35, 100, 0, 35);
        assertTarget(Config.ACTION_SELECT_TO_DOCUMENT_END, 20, 35, 100, 20, 100);
    }

    @Test public void indicesAreClampedToKnownDocumentBounds() {
        assertTarget(Config.ACTION_SELECT_TO_DOCUMENT_START, -5, 120, 90, 0, 90);
        assertTarget(Config.ACTION_SELECT_TO_DOCUMENT_END, -5, 120, 90, 0, 90);
        assertNull(DocumentNavigator.resolve(Config.ACTION_COPY, 1, 1, 10));
    }

    private static void assertTarget(int action, int left, int right, int documentEnd,
                                     int expectedStart, int expectedEnd) {
        DocumentNavigator.Target target = DocumentNavigator.resolve(action, left, right, documentEnd);
        assertEquals(expectedStart, target.start);
        assertEquals(expectedEnd, target.end);
    }
}
