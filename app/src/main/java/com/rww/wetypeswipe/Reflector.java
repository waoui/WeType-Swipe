package com.rww.wetypeswipe;

import android.view.MotionEvent;

import java.lang.reflect.Method;
import java.util.concurrent.ConcurrentHashMap;

/** Small cached reflection helper for obfuscated WeType members. */
final class Reflector {
    private final ConcurrentHashMap<String, Method> methodCache = new ConcurrentHashMap<>();

    Object invoke(Object target, String name, Object... args) {
        if (target == null) return null;
        try {
            Class<?>[] parameterTypes = new Class<?>[args.length];
            for (int i = 0; i < args.length; i++) {
                Object arg = args[i];
                if (arg instanceof MotionEvent) parameterTypes[i] = MotionEvent.class;
                else if (arg instanceof Boolean) parameterTypes[i] = boolean.class;
                else if (arg instanceof Integer) parameterTypes[i] = int.class;
                else parameterTypes[i] = arg == null ? Object.class : arg.getClass();
            }
            String cacheKey = target.getClass().getName() + '#' + name + signature(parameterTypes);
            Method method = methodCache.get(cacheKey);
            if (method == null) {
                method = findMethod(target.getClass(), name, parameterTypes);
                if (method == null) return null;
                Method previous = methodCache.putIfAbsent(cacheKey, method);
                if (previous != null) method = previous;
            }
            return method.invoke(target, args);
        } catch (Throwable ignored) {
            return null;
        }
    }

    static Method findMethod(Class<?> type, String name, Class<?>[] parameterTypes) {
        for (Class<?> current = type; current != null; current = current.getSuperclass()) {
            try {
                Method method = current.getDeclaredMethod(name, parameterTypes);
                method.setAccessible(true);
                return method;
            } catch (NoSuchMethodException ignored) {
            }
        }
        return null;
    }

    private static String signature(Class<?>[] types) {
        StringBuilder value = new StringBuilder(types.length * 12);
        for (Class<?> type : types) value.append(':').append(type.getName());
        return value.toString();
    }
}
