package com.rww.wetypeswipe;

import android.app.Activity;
import android.graphics.Color;
import android.graphics.Insets;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Build;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowInsets;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

/** Shared, accessible navigation for standalone and embedded settings. */
final class SettingsTabs {
    private static final String MODULE_PACKAGE = "com.rww.wetypeswipe";
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
        installEmbeddedSystemBarGuard(outer);

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

    /**
     * Embedded settings live inside the WeType process. On Android versions enforcing
     * edge-to-edge, the host Dialog may still lay its custom page beneath system bars even
     * when decorFitsSystemWindows(true) was requested. Apply only the actually-overlapped
     * portion as padding so older/fitted hosts are not double-inset.
     */
    private void installEmbeddedSystemBarGuard(View anchor) {
        if (MODULE_PACKAGE.equals(activity.getPackageName())) return;
        anchor.addOnAttachStateChangeListener(new View.OnAttachStateChangeListener() {
            @Override public void onViewAttachedToWindow(View view) {
                if (!(view.getParent() instanceof View)) return;
                View page = (View) view.getParent();
                page.setOnApplyWindowInsetsListener((target, insets) -> {
                    int top;
                    int bottom;
                    if (Build.VERSION.SDK_INT >= 30) {
                        Insets bars = insets.getInsets(WindowInsets.Type.systemBars());
                        top = bars.top;
                        bottom = bars.bottom;
                    } else {
                        top = insets.getSystemWindowInsetTop();
                        bottom = insets.getSystemWindowInsetBottom();
                    }

                    int[] location = new int[2];
                    target.getLocationOnScreen(location);
                    int topPadding = Math.max(0, top - location[1]);

                    int rootHeight = target.getRootView().getHeight();
                    int targetBottom = location[1] + target.getHeight();
                    int bottomPadding = rootHeight > 0
                            ? Math.max(0, targetBottom - (rootHeight - bottom))
                            : 0;

                    target.setPadding(
                            target.getPaddingLeft(),
                            topPadding,
                            target.getPaddingRight(),
                            bottomPadding);
                    return insets;
                });
                page.requestApplyInsets();
                page.post(page::requestApplyInsets);
            }

            @Override public void onViewDetachedFromWindow(View view) {}
        });
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
