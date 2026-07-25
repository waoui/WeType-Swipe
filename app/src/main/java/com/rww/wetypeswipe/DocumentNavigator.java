package com.rww.wetypeswipe;

final class DocumentNavigator {
    private DocumentNavigator() {}

    static Target resolve(int action, int selectionLeft, int selectionRight, int documentEnd) {
        int safeEnd = Math.max(0, documentEnd);
        int left = clamp(selectionLeft, safeEnd);
        int right = clamp(selectionRight, safeEnd);
        if (left > right) {
            int swap = left;
            left = right;
            right = swap;
        }

        switch (action) {
            case Config.ACTION_DOCUMENT_START:
                return new Target(0, 0);
            case Config.ACTION_DOCUMENT_END:
                return new Target(safeEnd, safeEnd);
            case Config.ACTION_SELECT_TO_DOCUMENT_START:
                return new Target(0, right);
            case Config.ACTION_SELECT_TO_DOCUMENT_END:
                return new Target(left, safeEnd);
            default:
                return null;
        }
    }

    private static int clamp(int value, int max) {
        if (value < 0) return 0;
        return Math.min(value, max);
    }

    static final class Target {
        final int start;
        final int end;

        Target(int start, int end) {
            this.start = start;
            this.end = end;
        }
    }
}
