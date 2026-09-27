package com.rww.wetypeswipe;

import java.lang.reflect.Field;
import java.lang.reflect.Modifier;

final class ToolbarCarrierLayout {
    private ToolbarCarrierLayout() {}

    static final class Fields {
        final Field function;
        final Field category;
        final Field group;
        final Object permanentCategory;
        final boolean weType4Layout;

        Fields(Field function, Field category, Field group,
               Object permanentCategory, boolean weType4Layout) {
            this.function = function;
            this.category = category;
            this.group = group;
            this.permanentCategory = permanentCategory;
            this.weType4Layout = weType4Layout;
        }
    }

    static Fields resolve(Class<?> holderClass) {
        if (holderClass == null) return null;

        Fields known = named(holderClass, "f", "g", "h", false);
        if (known != null) return known;

        known = named(holderClass, "g", "h", "i", true);
        if (known != null) return known;

        // Obfuscated field names may move again. The toolbar holder layout has a stable
        // shape: function int -> source enum (contains Permanent) -> group int.
        for (Class<?> type = holderClass; type != null; type = type.getSuperclass()) {
            Field[] fields;
            try {
                fields = type.getDeclaredFields();
            } catch (Throwable ignored) {
                continue;
            }
            for (int categoryIndex = 0; categoryIndex < fields.length; categoryIndex++) {
                Field category = fields[categoryIndex];
                if (Modifier.isStatic(category.getModifiers()) || !category.getType().isEnum()) continue;
                Object permanent = enumConstant(category.getType(), "Permanent");
                if (permanent == null) continue;

                Field function = nearestInt(fields, categoryIndex, -1);
                Field group = nearestInt(fields, categoryIndex, 1);
                if (function == null || group == null) continue;
                makeAccessible(function);
                makeAccessible(category);
                makeAccessible(group);
                return new Fields(function, category, group, permanent, false);
            }
        }
        return null;
    }

    private static Fields named(Class<?> holderClass, String functionName,
                                String categoryName, String groupName,
                                boolean weType4Layout) {
        Field function = findField(holderClass, functionName);
        Field category = findField(holderClass, categoryName);
        Field group = findField(holderClass, groupName);
        if (function == null || category == null || group == null) return null;
        if (function.getType() != int.class || group.getType() != int.class
                || !category.getType().isEnum()) return null;
        Object permanent = enumConstant(category.getType(), "Permanent");
        if (permanent == null) return null;
        return new Fields(function, category, group, permanent, weType4Layout);
    }

    private static Field findField(Class<?> type, String name) {
        for (Class<?> current = type; current != null; current = current.getSuperclass()) {
            try {
                Field field = current.getDeclaredField(name);
                makeAccessible(field);
                return field;
            } catch (NoSuchFieldException ignored) {
            } catch (Throwable ignored) {
                return null;
            }
        }
        return null;
    }

    private static Field nearestInt(Field[] fields, int start, int direction) {
        for (int index = start + direction; index >= 0 && index < fields.length; index += direction) {
            Field field = fields[index];
            if (Modifier.isStatic(field.getModifiers())) continue;
            if (field.getType() == int.class) return field;
        }
        return null;
    }

    private static Object enumConstant(Class<?> type, String name) {
        if (type == null || !type.isEnum()) return null;
        try {
            Object[] constants = type.getEnumConstants();
            if (constants == null) return null;
            for (Object constant : constants) {
                if (constant instanceof Enum && name.equals(((Enum<?>) constant).name())) {
                    return constant;
                }
            }
        } catch (Throwable ignored) {
        }
        return null;
    }

    private static void makeAccessible(Field field) {
        try {
            field.setAccessible(true);
        } catch (Throwable ignored) {
        }
    }
}
