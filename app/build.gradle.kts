plugins {
    id("com.android.application")
}

val signingStoreFilePath = System.getenv("SIGNING_STORE_FILE")

android {
    namespace = "com.rww.wetypeswipe"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.rww.wetypeswipe"
        minSdk = 26
        targetSdk = 35
        versionCode = 38
        versionName = "1.11.0"
    }

    signingConfigs {
        if (!signingStoreFilePath.isNullOrBlank()) {
            create("release") {
                storeFile = file(signingStoreFilePath)
                storePassword = System.getenv("SIGNING_STORE_PASSWORD")
                keyAlias = System.getenv("SIGNING_KEY_ALIAS")
                keyPassword = System.getenv("SIGNING_KEY_PASSWORD")
                enableV1Signing = true
                enableV2Signing = true
                enableV3Signing = true
            }
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            if (!signingStoreFilePath.isNullOrBlank()) {
                signingConfig = signingConfigs.getByName("release")
            }
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    packaging {
        resources {
            merges += "META-INF/xposed/*"
        }
    }
}

dependencies {
    compileOnly("io.github.libxposed:api:102.0.0")
}
