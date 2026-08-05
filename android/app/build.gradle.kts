import java.util.Properties

plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.detekt)
}

fun escapeBuildConfigString(value: String): String = "\"${value.replace("\\", "\\\\").replace("\"", "\\\"")}\""

/**
 * BotHub API key for BuildConfig: env BOTHUB_API_KEY, else monorepo api-keys/bothub-api-key.txt.
 * Never commit the key; empty string is allowed so the APK still builds.
 */
fun resolveBothubApiKey(): String {
    val fromEnv = System.getenv("BOTHUB_API_KEY")?.trim().orEmpty()
    if (fromEnv.isNotEmpty()) {
        return fromEnv
    }
    val keyFile =
        rootProject.projectDir.parentFile
            .resolve("api-keys")
            .resolve("bothub-api-key.txt")
    if (!keyFile.isFile) {
        return ""
    }
    return keyFile
        .readText(Charsets.UTF_8)
        .lineSequence()
        .map { it.trim() }
        .firstOrNull { it.isNotEmpty() && !it.startsWith("#") }
        .orEmpty()
}

fun resolveBothubOptional(
    envName: String,
    propertyName: String,
    default: String,
): String {
    val fromEnv = System.getenv(envName)?.trim().orEmpty()
    if (fromEnv.isNotEmpty()) {
        return fromEnv
    }
    val localProperties = rootProject.file("local.properties")
    if (localProperties.isFile) {
        val props = Properties()
        localProperties.inputStream().use { props.load(it) }
        val fromProps = props.getProperty(propertyName)?.trim().orEmpty()
        if (fromProps.isNotEmpty()) {
            return fromProps
        }
    }
    return default
}

val bothubApiKey = resolveBothubApiKey()
val bothubBaseUrl =
    resolveBothubOptional(
        envName = "BOTHUB_BASE_URL",
        propertyName = "bothub.base_url",
        default = "https://bothub.chat/api/v2/openai/v1",
    )
val bothubModel =
    resolveBothubOptional(
        envName = "BOTHUB_MODEL",
        propertyName = "bothub.model",
        default = "gpt-5.4",
    )
val bothubSpeechModel =
    resolveBothubOptional(
        envName = "BOTHUB_SPEECH_MODEL",
        propertyName = "bothub.speech_model",
        default = "gemini-3.1-flash-lite-preview",
    )

if (bothubApiKey.isEmpty()) {
    logger.warn(
        "BotHub API key is empty. Set BOTHUB_API_KEY or create " +
            "../api-keys/bothub-api-key.txt (relative to android/). " +
            "Speech to Text and other AI utilities will show an error until a key is provided.",
    )
}

val bothubPromptsAssetsDir = layout.buildDirectory.dir("generated/bothubPrompts")

val copyBothubPrompts =
    tasks.register<Copy>("copyBothubPrompts") {
        description =
            "Copy BotHub prompt Markdown from monorepo config/prompts into generated assets"
        from(rootProject.projectDir.parentFile.resolve("config/prompts")) {
            include("text-fix-ru.md", "text-rewrite-ru.md")
        }
        into(bothubPromptsAssetsDir.map { it.dir("prompts") })
    }

android {
    namespace = "dev.harrix.hsk"
    compileSdk = 35

    sourceSets {
        getByName("main") {
            assets.srcDir(bothubPromptsAssetsDir)
        }
    }

    defaultConfig {
        applicationId = "dev.harrix.hsk"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "1.0"

        buildConfigField("String", "BOTHUB_API_KEY", escapeBuildConfigString(bothubApiKey))
        buildConfigField("String", "BOTHUB_BASE_URL", escapeBuildConfigString(bothubBaseUrl))
        buildConfigField("String", "BOTHUB_MODEL", escapeBuildConfigString(bothubModel))
        buildConfigField(
            "String",
            "BOTHUB_SPEECH_MODEL",
            escapeBuildConfigString(bothubSpeechModel),
        )
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro",
            )
            // Debug keystore so release APKs can be sideloaded (same as debug installs).
            // Replace with a dedicated release keystore before Play Store publishing.
            signingConfig = signingConfigs.getByName("debug")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }

    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }

    lint {
        abortOnError = true
        warningsAsErrors = false
    }
}

tasks.named("preBuild").configure {
    dependsOn(copyBothubPrompts)
}

detekt {
    buildUponDefaultConfig = true
    allRules = false
    config.setFrom(files("${rootProject.projectDir}/config/detekt/detekt.yml"))
    parallel = true
}

base {
    archivesName.set("HarrixSwissKnife")
}

dependencies {
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.appcompat)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.lifecycle.runtime.compose)
    implementation(libs.androidx.lifecycle.viewmodel.compose)
    implementation(libs.androidx.lifecycle.viewmodel.ktx)
    implementation(libs.androidx.activity.compose)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.compose.ui)
    implementation(libs.androidx.compose.ui.graphics)
    implementation(libs.androidx.compose.ui.tooling.preview)
    implementation(libs.androidx.compose.material3)
    implementation(libs.androidx.compose.material.icons.extended)
    implementation(libs.material)
    implementation(libs.coil.compose)
    implementation(libs.androidx.exifinterface)
    implementation(libs.okhttp)
    debugImplementation(libs.androidx.compose.ui.tooling)
    detektPlugins(libs.detekt.compose.rules)
}

tasks.named("check") {
    dependsOn("detekt", "lintDebug")
}
