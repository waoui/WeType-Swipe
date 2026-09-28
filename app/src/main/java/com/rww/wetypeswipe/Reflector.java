package com.rww.wetypeswipe;

import android.view.MotionEvent;

import java.lang.reflect.Method;
import java.util.concurrent.ConcurrentHashMap;

/** Cached reflection helper optimized for WeType's very hot zero-arg key-model calls. */
final class Reflector {
    private static final Method MISSING_METHOD = missingSentinel();

    private final ConcurrentHashMap<Class<?>, ConcurrentHashMap<String, Method>> zeroArgCache =
            new ConcurrentHashMap<>();
    private final ConcurrentHashMap<Class<?>, ConcurrentHashMap<String, Method>> touchBooleanCache =
            new ConcurrentHashMap<>();
    private final ConcurrentHashMap<Class<?>, ConcurrentHashMap<String, Method>> genericCache =
            new ConcurrentHashMap<>();

    Object invoke(Object target, String name) {
        if (target == null || name == null) return null;
        try {
            Method method = cachedMethod(zeroArgCache, target.getClass(), name, new Class<?>[0]);
            return method == null ? null : method.invoke(target);
        } catch (Throwable ignored) {
            return null;
        }
    }

    Object invoke(Object target, String name, MotionEvent event, boolean value) {
        if (target == null || name == null) return null;
        try {
            Method method = cachedMethod(touchBooleanCache, target.getClass(), name,
                    new Class<?>[]{MotionEvent.class, boolean.class});
            return method == null ? null : method.invoke(target, event, value);
        } catch (Throwable ignored) {
            return null;
        }
    }

    Object invoke(Object target, String name, Object... args) {
        if (target == null || name == null) return null;
        try {
            Class<?>[] parameterTypes = new Class<?>[args.length];
            for (int i = 0; i < args.length; i++) {
                Object arg = args[i];
                if (arg instanceof MotionEvent) parameterTypes[i] = MotionEvent.class;
                else if (arg instanceof Boolean) parameterTypes[i] = boolean.class;
                else if (arg instanceof Integer) parameterTypes[i] = int.class;
                else parameterTypes[i] = arg == null ? Object.class : arg.getClass();
            }
            String key = name + signature(parameterTypes);
            Method method = cachedMethod(genericCache, target.getClass(), key, parameterTypes, name);
            return method == null ? null : method.invoke(target, args);
        } catch (Throwable ignored) {
            return null;
        }
    }

    private static Method cachedMethod(
            ConcurrentHashMap<Class<?>, ConcurrentHashMap<String, Method>> cache,
            Class<?> type, String key, Class<?>[] parameterTypes) {
        return cachedMethod(cache, type, key, parameterTypes, key);
    }

    private static Method cachedMethod(
            ConcurrentHashMap<Class<?>, ConcurrentHashMap<String, Method>> cache,
            Class<?> type, String key, Class<?>[] parameterTypes, String methodName) {
        ConcurrentHashMap<String, Method> methods =
                cache.computeIfAbsent(type, ignored -> new ConcurrentHashMap<>());
        Method cached = methods.get(key);
        if (cached != null) return cached == MISSING_METHOD ? null : cached;

        Method resolved = findMethod(type, methodName, parameterTypes);
        Method value = resolved == null ? MISSING_METHOD : resolved;
        Method previous = methods.putIfAbsent(key, value);
        Method actual = previous == null ? value : previous;
        return actual == MISSING_METHOD ? null : actual;
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

    private static Method missingSentinel() {
        try {
            Method method = Reflector.class.getDeclaredMethod("missing");
            method.setAccessible(true);
            return method;
        } catch (NoSuchMethodException impossible) {
            throw new ExceptionInInitializerError(impossible);
        }
    }

    @SuppressWarnings("unused")
    private static void missing() {}
}
