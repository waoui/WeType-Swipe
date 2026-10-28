#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


config = ROOT / "app/src/main/java/com/rww/wetypeswipe/Config.java"

replace_once(
    config,
    '''    static final String KEY_SELECT_TO_PARAGRAPH_START = "select_to_paragraph_start";
    static final String KEY_SELECT_TO_PARAGRAPH_END = "select_to_paragraph_end";
    static final String KEY_OPEN_CLIPBOARD = "open_clipboard";
''',
    '''    static final String KEY_SELECT_TO_PARAGRAPH_START = "select_to_paragraph_start";
    static final String KEY_SELECT_TO_PARAGRAPH_END = "select_to_paragraph_end";
    static final String KEY_DOCUMENT_START = "document_start";
    static final String KEY_DOCUMENT_END = "document_end";
    static final String KEY_SELECT_TO_DOCUMENT_START = "select_to_document_start";
    static final String KEY_SELECT_TO_DOCUMENT_END = "select_to_document_end";
    static final String KEY_OPEN_CLIPBOARD = "open_clipboard";
''',
)

replace_once(
    config,
    '''    static final int ACTION_UNDO = 14;
    static final int ACTION_REDO = 15;
''',
    '''    static final int ACTION_UNDO = 14;
    static final int ACTION_REDO = 15;
    static final int ACTION_DOCUMENT_START = 16;
    static final int ACTION_DOCUMENT_END = 17;
    static final int ACTION_SELECT_TO_DOCUMENT_START = 18;
    static final int ACTION_SELECT_TO_DOCUMENT_END = 19;
''',
)

replace_once(
    config,
    '''            "段首", "段尾", "选至段首", "选至段尾",
            "剪贴板", "快捷发送", "撤销", "重做", "禁用下滑"
''',
    '''            "段首", "段尾", "选至段首", "选至段尾",
            "文首", "文尾", "选至文首", "选至文尾",
            "剪贴板", "快捷发送", "撤销", "重做", "禁用下滑"
''',
)

replace_once(
    config,
    '''            ACTION_SELECT_TO_PARAGRAPH_START,
            ACTION_SELECT_TO_PARAGRAPH_END,
            ACTION_OPEN_CLIPBOARD,
''',
    '''            ACTION_SELECT_TO_PARAGRAPH_START,
            ACTION_SELECT_TO_PARAGRAPH_END,
            ACTION_DOCUMENT_START,
            ACTION_DOCUMENT_END,
            ACTION_SELECT_TO_DOCUMENT_START,
            ACTION_SELECT_TO_DOCUMENT_END,
            ACTION_OPEN_CLIPBOARD,
''',
)

replace_once(
    config,
    '''    String selectToParagraphStart = "";
    String selectToParagraphEnd = "";
    String openClipboard = "";
''',
    '''    String selectToParagraphStart = "";
    String selectToParagraphEnd = "";
    String documentStart = "";
    String documentEnd = "";
    String selectToDocumentStart = "";
    String selectToDocumentEnd = "";
    String openClipboard = "";
''',
)

replace_once(
    config,
    '''        bind(selectToParagraphStart, ACTION_SELECT_TO_PARAGRAPH_START);
        bind(selectToParagraphEnd, ACTION_SELECT_TO_PARAGRAPH_END);
        bind(openClipboard, ACTION_OPEN_CLIPBOARD);
''',
    '''        bind(selectToParagraphStart, ACTION_SELECT_TO_PARAGRAPH_START);
        bind(selectToParagraphEnd, ACTION_SELECT_TO_PARAGRAPH_END);
        bind(documentStart, ACTION_DOCUMENT_START);
        bind(documentEnd, ACTION_DOCUMENT_END);
        bind(selectToDocumentStart, ACTION_SELECT_TO_DOCUMENT_START);
        bind(selectToDocumentEnd, ACTION_SELECT_TO_DOCUMENT_END);
        bind(openClipboard, ACTION_OPEN_CLIPBOARD);
''',
)

replace_once(
    config,
    '''        return action >= ACTION_NONE && action <= ACTION_REDO
''',
    '''        return action >= ACTION_NONE && action <= ACTION_SELECT_TO_DOCUMENT_END
''',
)

replace_once(
    config,
    '''            case ACTION_SELECT_TO_PARAGRAPH_START: return "选前";
            case ACTION_SELECT_TO_PARAGRAPH_END: return "选后";
            case ACTION_OPEN_CLIPBOARD: return "剪贴";
''',
    '''            case ACTION_SELECT_TO_PARAGRAPH_START: return "选前";
            case ACTION_SELECT_TO_PARAGRAPH_END: return "选后";
            case ACTION_DOCUMENT_START: return "文首";
            case ACTION_DOCUMENT_END: return "文尾";
            case ACTION_SELECT_TO_DOCUMENT_START: return "选文首";
            case ACTION_SELECT_TO_DOCUMENT_END: return "选文尾";
            case ACTION_OPEN_CLIPBOARD: return "剪贴";
''',
)

replace_once(
    config,
    '''            case ACTION_SELECT_TO_PARAGRAPH_START: return "选至段首";
            case ACTION_SELECT_TO_PARAGRAPH_END: return "选至段尾";
            case ACTION_OPEN_CLIPBOARD: return "剪贴板";
''',
    '''            case ACTION_SELECT_TO_PARAGRAPH_START: return "选至段首";
            case ACTION_SELECT_TO_PARAGRAPH_END: return "选至段尾";
            case ACTION_DOCUMENT_START: return "文首";
            case ACTION_DOCUMENT_END: return "文尾";
            case ACTION_SELECT_TO_DOCUMENT_START: return "选至文首";
            case ACTION_SELECT_TO_DOCUMENT_END: return "选至文尾";
            case ACTION_OPEN_CLIPBOARD: return "剪贴板";
''',
)

main_activity = ROOT / "app/src/main/java/com/rww/wetypeswipe/MainActivity.java"

replace_once(
    main_activity,
    '''            Config.ACTION_OPEN_QUICK_PHRASE,
            Config.ACTION_UNDO,
            Config.ACTION_REDO
''',
    '''            Config.ACTION_OPEN_QUICK_PHRASE,
            Config.ACTION_UNDO,
            Config.ACTION_REDO,
            Config.ACTION_DOCUMENT_START,
            Config.ACTION_DOCUMENT_END,
            Config.ACTION_SELECT_TO_DOCUMENT_START,
            Config.ACTION_SELECT_TO_DOCUMENT_END
''',
)

replace_once(
    main_activity,
    '''            "剪贴板", "快捷发送", "撤销", "重做"
''',
    '''            "剪贴板", "快捷发送", "撤销", "重做",
            "文首", "文尾", "选至文首", "选至文尾"
''',
)

replace_once(
    main_activity,
    'v1.11.4 · 新增撤销与重做',
    'v1.11.5-test1 · 新增全文导航与跨行选择',
)

replace_once(
    main_activity,
    '''        qwertyKeys[12] = normalizedKey(prefs.getString(Config.KEY_UNDO, ""));
        qwertyKeys[13] = normalizedKey(prefs.getString(Config.KEY_REDO, ""));
        disabledKeys = normalizedKeys(prefs.getString(Config.KEY_DISABLED_KEYS, ""));
''',
    '''        qwertyKeys[12] = normalizedKey(prefs.getString(Config.KEY_UNDO, ""));
        qwertyKeys[13] = normalizedKey(prefs.getString(Config.KEY_REDO, ""));
        qwertyKeys[14] = normalizedKey(prefs.getString(Config.KEY_DOCUMENT_START, ""));
        qwertyKeys[15] = normalizedKey(prefs.getString(Config.KEY_DOCUMENT_END, ""));
        qwertyKeys[16] = normalizedKey(prefs.getString(Config.KEY_SELECT_TO_DOCUMENT_START, ""));
        qwertyKeys[17] = normalizedKey(prefs.getString(Config.KEY_SELECT_TO_DOCUMENT_END, ""));
        disabledKeys = normalizedKeys(prefs.getString(Config.KEY_DISABLED_KEYS, ""));
''',
)

replace_once(
    main_activity,
    '''                .putString(Config.KEY_UNDO, qwertyKeys[12])
                .putString(Config.KEY_REDO, qwertyKeys[13])
                .putString(Config.KEY_DISABLED_KEYS, disabledKeys)
''',
    '''                .putString(Config.KEY_UNDO, qwertyKeys[12])
                .putString(Config.KEY_REDO, qwertyKeys[13])
                .putString(Config.KEY_DOCUMENT_START, qwertyKeys[14])
                .putString(Config.KEY_DOCUMENT_END, qwertyKeys[15])
                .putString(Config.KEY_SELECT_TO_DOCUMENT_START, qwertyKeys[16])
                .putString(Config.KEY_SELECT_TO_DOCUMENT_END, qwertyKeys[17])
                .putString(Config.KEY_DISABLED_KEYS, disabledKeys)
''',
)

replace_once(
    main_activity,
    '''        changed.putExtra(Config.KEY_UNDO, qwertyKeys[12]);
        changed.putExtra(Config.KEY_REDO, qwertyKeys[13]);
        changed.putExtra(Config.KEY_DISABLED_KEYS, disabledKeys);
''',
    '''        changed.putExtra(Config.KEY_UNDO, qwertyKeys[12]);
        changed.putExtra(Config.KEY_REDO, qwertyKeys[13]);
        changed.putExtra(Config.KEY_DOCUMENT_START, qwertyKeys[14]);
        changed.putExtra(Config.KEY_DOCUMENT_END, qwertyKeys[15]);
        changed.putExtra(Config.KEY_SELECT_TO_DOCUMENT_START, qwertyKeys[16]);
        changed.putExtra(Config.KEY_SELECT_TO_DOCUMENT_END, qwertyKeys[17]);
        changed.putExtra(Config.KEY_DISABLED_KEYS, disabledKeys);
''',
)

replace_once(
    main_activity,
    '''            case Config.ACTION_UNDO: return "撤销";
            case Config.ACTION_REDO: return "重做";
            default: return "—";
''',
    '''            case Config.ACTION_UNDO: return "撤销";
            case Config.ACTION_REDO: return "重做";
            case Config.ACTION_DOCUMENT_START: return "文首";
            case Config.ACTION_DOCUMENT_END: return "文尾";
            case Config.ACTION_SELECT_TO_DOCUMENT_START: return "选文首";
            case Config.ACTION_SELECT_TO_DOCUMENT_END: return "选文尾";
            default: return "—";
''',
)

main_hook = ROOT / "app/src/main/java/com/rww/wetypeswipe/MainHook.java"

replace_once(
    main_hook,
    'logInfo("v1.11.4 entered target package; undo/redo actions enabled");',
    'logInfo("v1.11.5-test1 entered target package; document navigation actions enabled");',
)

replace_once(
    main_hook,
    '''            config.selectToParagraphStart = intent.getStringExtra(Config.KEY_SELECT_TO_PARAGRAPH_START);
            config.selectToParagraphEnd = intent.getStringExtra(Config.KEY_SELECT_TO_PARAGRAPH_END);
            config.openClipboard = intent.getStringExtra(Config.KEY_OPEN_CLIPBOARD);
''',
    '''            config.selectToParagraphStart = intent.getStringExtra(Config.KEY_SELECT_TO_PARAGRAPH_START);
            config.selectToParagraphEnd = intent.getStringExtra(Config.KEY_SELECT_TO_PARAGRAPH_END);
            config.documentStart = intent.getStringExtra(Config.KEY_DOCUMENT_START);
            config.documentEnd = intent.getStringExtra(Config.KEY_DOCUMENT_END);
            config.selectToDocumentStart = intent.getStringExtra(Config.KEY_SELECT_TO_DOCUMENT_START);
            config.selectToDocumentEnd = intent.getStringExtra(Config.KEY_SELECT_TO_DOCUMENT_END);
            config.openClipboard = intent.getStringExtra(Config.KEY_OPEN_CLIPBOARD);
''',
)

replace_once(
    main_hook,
    '''            if (config.selectToParagraphStart == null) config.selectToParagraphStart = "";
            if (config.selectToParagraphEnd == null) config.selectToParagraphEnd = "";
            if (config.openClipboard == null) config.openClipboard = "";
''',
    '''            if (config.selectToParagraphStart == null) config.selectToParagraphStart = "";
            if (config.selectToParagraphEnd == null) config.selectToParagraphEnd = "";
            if (config.documentStart == null) config.documentStart = "";
            if (config.documentEnd == null) config.documentEnd = "";
            if (config.selectToDocumentStart == null) config.selectToDocumentStart = "";
            if (config.selectToDocumentEnd == null) config.selectToDocumentEnd = "";
            if (config.openClipboard == null) config.openClipboard = "";
''',
)

replace_once(
    main_hook,
    '''                    .putString(Config.KEY_SELECT_TO_PARAGRAPH_START, config.selectToParagraphStart)
                    .putString(Config.KEY_SELECT_TO_PARAGRAPH_END, config.selectToParagraphEnd)
                    .putString(Config.KEY_OPEN_CLIPBOARD, config.openClipboard)
''',
    '''                    .putString(Config.KEY_SELECT_TO_PARAGRAPH_START, config.selectToParagraphStart)
                    .putString(Config.KEY_SELECT_TO_PARAGRAPH_END, config.selectToParagraphEnd)
                    .putString(Config.KEY_DOCUMENT_START, config.documentStart)
                    .putString(Config.KEY_DOCUMENT_END, config.documentEnd)
                    .putString(Config.KEY_SELECT_TO_DOCUMENT_START, config.selectToDocumentStart)
                    .putString(Config.KEY_SELECT_TO_DOCUMENT_END, config.selectToDocumentEnd)
                    .putString(Config.KEY_OPEN_CLIPBOARD, config.openClipboard)
''',
)

replace_once(
    main_hook,
    '''            config.selectToParagraphStart = prefs.getString(Config.KEY_SELECT_TO_PARAGRAPH_START, "");
            config.selectToParagraphEnd = prefs.getString(Config.KEY_SELECT_TO_PARAGRAPH_END, "");
            config.openClipboard = prefs.getString(Config.KEY_OPEN_CLIPBOARD, "");
''',
    '''            config.selectToParagraphStart = prefs.getString(Config.KEY_SELECT_TO_PARAGRAPH_START, "");
            config.selectToParagraphEnd = prefs.getString(Config.KEY_SELECT_TO_PARAGRAPH_END, "");
            config.documentStart = prefs.getString(Config.KEY_DOCUMENT_START, "");
            config.documentEnd = prefs.getString(Config.KEY_DOCUMENT_END, "");
            config.selectToDocumentStart = prefs.getString(Config.KEY_SELECT_TO_DOCUMENT_START, "");
            config.selectToDocumentEnd = prefs.getString(Config.KEY_SELECT_TO_DOCUMENT_END, "");
            config.openClipboard = prefs.getString(Config.KEY_OPEN_CLIPBOARD, "");
''',
)

replace_once(
    main_hook,
    '''            boolean success;
            if (isParagraphAction(action)) {
                success = performParagraphAction(connection, action);
''',
    '''            boolean success;
            if (isDocumentAction(action)) {
                success = performDocumentAction(connection, action);
            } else if (isParagraphAction(action)) {
                success = performParagraphAction(connection, action);
''',
)

replace_once(
    main_hook,
    '''    private static boolean isParagraphAction(int action) {
''',
    '''    private static boolean isDocumentAction(int action) {
        return action == Config.ACTION_DOCUMENT_START
                || action == Config.ACTION_DOCUMENT_END
                || action == Config.ACTION_SELECT_TO_DOCUMENT_START
                || action == Config.ACTION_SELECT_TO_DOCUMENT_END;
    }

    private boolean performDocumentAction(InputConnection connection, int action) {
        try {
            try { connection.finishComposingText(); } catch (Throwable ignored) {}

            EditorSnapshot snapshot = readEditorSnapshot(connection);
            if (snapshot == null) return false;

            int documentEnd = snapshot.right;
            if (action == Config.ACTION_DOCUMENT_END
                    || action == Config.ACTION_SELECT_TO_DOCUMENT_END) {
                documentEnd = readDocumentEnd(connection);
                if (documentEnd < snapshot.right) return false;
            }

            DocumentNavigator.Target target = DocumentNavigator.resolve(
                    action, snapshot.left, snapshot.right, documentEnd);
            if (target == null) return false;

            boolean success = connection.setSelection(target.start, target.end);
            if (success) {
                currentSelectionStart = target.start;
                currentSelectionEnd = target.end;
            }
            return success;
        } catch (Throwable throwable) {
            logError("document action failed", throwable);
            return false;
        }
    }

    private static int readDocumentEnd(InputConnection connection) {
        ExtractedText extracted = getFullText(connection);
        if (extracted == null || extracted.text == null || extracted.startOffset > 0) return -1;
        return extracted.text.length();
    }

    private static boolean isParagraphAction(int action) {
''',
)

navigator = ROOT / "app/src/main/java/com/rww/wetypeswipe/DocumentNavigator.java"
navigator.write_text('''package com.rww.wetypeswipe;

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
''', encoding="utf-8")

config_test = ROOT / "app/src/test/java/com/rww/wetypeswipe/ConfigTest.java"
replace_once(
    config_test,
    '''    @Test public void labelNormalizationIsUnicodeSafe() {
''',
    '''    @Test public void documentActionsRemainBindableAndKeepStableIds() {
        Config config = new Config();
        config.documentStart = "a";
        config.documentEnd = "b";
        config.selectToDocumentStart = "d";
        config.selectToDocumentEnd = "e";
        config.rebuildActionMap();

        assertEquals(16, Config.ACTION_DOCUMENT_START);
        assertEquals(17, Config.ACTION_DOCUMENT_END);
        assertEquals(18, Config.ACTION_SELECT_TO_DOCUMENT_START);
        assertEquals(19, Config.ACTION_SELECT_TO_DOCUMENT_END);
        assertEquals(Config.ACTION_DOCUMENT_START, config.actionFor("a", false));
        assertEquals(Config.ACTION_DOCUMENT_END, config.actionFor("b", false));
        assertEquals(Config.ACTION_SELECT_TO_DOCUMENT_START, config.actionFor("d", false));
        assertEquals(Config.ACTION_SELECT_TO_DOCUMENT_END, config.actionFor("e", false));
        assertEquals("选文首", Config.shortActionLabel(Config.ACTION_SELECT_TO_DOCUMENT_START));
        assertEquals("选至文尾", Config.actionName(Config.ACTION_SELECT_TO_DOCUMENT_END));
    }

    @Test public void labelNormalizationIsUnicodeSafe() {
''',
)

navigator_test = ROOT / "app/src/test/java/com/rww/wetypeswipe/DocumentNavigatorTest.java"
navigator_test.write_text('''package com.rww.wetypeswipe;

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
''', encoding="utf-8")

gradle_properties = ROOT / "gradle.properties"
properties = gradle_properties.read_text(encoding="utf-8")
properties, code_count = re.subn(r"(?m)^VERSION_CODE=.*$", "VERSION_CODE=44", properties, count=1)
properties, name_count = re.subn(r"(?m)^VERSION_NAME=.*$", "VERSION_NAME=1.11.5-test1", properties, count=1)
if code_count != 1 or name_count != 1:
    raise SystemExit("Could not update VERSION_CODE/VERSION_NAME")
gradle_properties.write_text(properties, encoding="utf-8")

print("Applied v1.11.5-test1 document navigation patch")
