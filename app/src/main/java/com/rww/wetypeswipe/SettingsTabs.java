package com.rww.wetypeswipe;

import android.app.Activity;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

/** Shared, accessible navigation for standalone and embedded settings. */
final class SettingsTabs {
    private static final String[] TITLES = {"26 键", "九宫格", "手势与选项"};
    private static final int TEXT_MUTED = Color.rgb(91, 103, 122);
    private static final int ACCENT = Color.rgb(36, 103, 214);
    private static final int TRACK = Color.rgb(237, 241, 247);

    private final Activity activity;
    private final ScrollView scroll;
    private final View[] pages;
    private final TextView[] buttons = new TextView[TITLES.length];

    private SettingsTabs(Activity activity, ScrollView scroll, View[] pages) {
        this.activity = activity;
        this.scroll = scroll;
        this.pages = pages;
    }

    static View create(Activity activity, ScrollView scroll, View qwerty, View t9, View options) {
        SettingsTabs tabs = new SettingsTabs(activity, scroll, new View[]{qwerty, t9, options});
        return tabs.build();
    }

    private View build() {
        LinearLayout host = new LinearLayout(activity);
        host.setOrientation(LinearLayout.HORIZONTAL);
        host.setPadding(dp(4), dp(4), dp(4), dp(4));
        host.setBackground(shape(TRACK, 15));

        LinearLayout outer = new LinearLayout(activity);
        outer.setPadding(dp(12), dp(8), dp(12), dp(8));
        outer.setBackgroundColor(Color.WHITE);
        outer.addView(host, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(52)));

        for (int i = 0; i < buttons.length; i++) {
            final int index = i;
            TextView button = new TextView(activity);
            button.setText(TITLES[i]);
            button.setTextSize(14);
            button.setGravity(Gravity.CENTER);
            button.setSingleLine(true);
            button.setMaxLines(1);
            button.setContentDescription(TITLES[i] + "设置");
            button.setClickable(true);
            button.setFocusable(true);
            button.setOnClickListener(v -> select(index));
            LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(0,
                    ViewGroup.LayoutParams.MATCH_PARENT, 1f);
            host.addView(button, params);
            buttons[i] = button;
        }
        select(0);
        return outer;
    }

    private void select(int active) {
        for (int i = 0; i < buttons.length; i++) {
            boolean selected = i == active;
            pages[i].setVisibility(selected ? View.VISIBLE : View.GONE);
            TextView button = buttons[i];
            button.setSelected(selected);
            button.setTextColor(selected ? ACCENT : TEXT_MUTED);
            button.setTypeface(selected ? Typeface.DEFAULT_BOLD : Typeface.DEFAULT);
            button.setBackground(selected ? shape(Color.WHITE, 12) : null);
            button.setElevation(selected ? dp(2) : 0f);
        }
        scroll.scrollTo(0, 0);
    }

    private GradientDrawable shape(int color, int radiusDp) {
        GradientDrawable background = new GradientDrawable();
        background.setColor(color);
        background.setCornerRadius(dp(radiusDp));
        return background;
    }

    private int dp(int value) {
        return Math.round(value * activity.getResources().getDisplayMetrics().density);
    }
}
