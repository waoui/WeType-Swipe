package com.rww.wetypeswipe;

import android.content.ContentProvider;
import android.content.ContentValues;
import android.content.SharedPreferences;
import android.database.Cursor;
import android.database.MatrixCursor;
import android.net.Uri;

public final class ConfigProvider extends ContentProvider {
    private static final String[] COLUMNS = {
            Config.KEY_SELECT_ALL,
            Config.KEY_CUT,
            Config.KEY_COPY,
            Config.KEY_PASTE,
            Config.KEY_DISABLED_KEYS,
            Config.KEY_THRESHOLD,
            Config.KEY_T9_THRESHOLD,
            Config.KEY_T9_2,
            Config.KEY_T9_3,
            Config.KEY_T9_4,
            Config.KEY_T9_5,
            Config.KEY_T9_6,
            Config.KEY_T9_7,
            Config.KEY_T9_8,
            Config.KEY_T9_9,
            Config.KEY_VIBRATION,
            Config.KEY_DIAGNOSTIC
    };

    @Override public boolean onCreate() {
        return true;
    }

    @Override public Cursor query(Uri uri, String[] projection, String selection,
                                  String[] selectionArgs, String sortOrder) {
        SharedPreferences prefs = getContext().getSharedPreferences(Config.PREFS, 0);
        MatrixCursor cursor = new MatrixCursor(COLUMNS, 1);
        cursor.addRow(new Object[]{
                prefs.getString(Config.KEY_SELECT_ALL, "z"),
                prefs.getString(Config.KEY_CUT, "x"),
                prefs.getString(Config.KEY_COPY, "c"),
                prefs.getString(Config.KEY_PASTE, "v"),
                prefs.getString(Config.KEY_DISABLED_KEYS, ""),
                prefs.getInt(Config.KEY_THRESHOLD, 12),
                prefs.getInt(Config.KEY_T9_THRESHOLD, 20),
                prefs.getInt(Config.KEY_T9_2, Config.ACTION_NONE),
                prefs.getInt(Config.KEY_T9_3, Config.ACTION_NONE),
                prefs.getInt(Config.KEY_T9_4, Config.ACTION_NONE),
                prefs.getInt(Config.KEY_T9_5, Config.ACTION_NONE),
                prefs.getInt(Config.KEY_T9_6, Config.ACTION_NONE),
                prefs.getInt(Config.KEY_T9_7, Config.ACTION_NONE),
                prefs.getInt(Config.KEY_T9_8, Config.ACTION_NONE),
                prefs.getInt(Config.KEY_T9_9, Config.ACTION_NONE),
                prefs.getBoolean(Config.KEY_VIBRATION, true) ? 1 : 0,
                prefs.getBoolean(Config.KEY_DIAGNOSTIC, false) ? 1 : 0
        });
        return cursor;
    }

    @Override public String getType(Uri uri) {
        return "vnd.android.cursor.item/vnd.com.rww.wetypeswipe.config";
    }

    @Override public Uri insert(Uri uri, ContentValues values) {
        throw new UnsupportedOperationException("read only");
    }

    @Override public int delete(Uri uri, String selection, String[] selectionArgs) {
        throw new UnsupportedOperationException("read only");
    }

    @Override public int update(Uri uri, ContentValues values, String selection, String[] selectionArgs) {
        throw new UnsupportedOperationException("read only");
    }
}
