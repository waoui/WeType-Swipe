plugins {
    id("com.android.application")
}

android {
    namespace = "com.rww.wetypeswipe"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.rww.wetypeswipe"
        minSdk = 26
        targetSdk = 35
        versionCode = 9
        versionName = "1.8.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
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
