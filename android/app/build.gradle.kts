import groovy.json.JsonSlurper
import java.util.Properties

plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.detekt)
}

fun escapeBuildConfigString(value: String): String = "\"${value.replace("\\", "\\\\").replace("\"", "\\\"")}\""

fun monorepoRoot(): java.io.File = rootProject.projectDir.parentFile

fun readFirstNonEmptyLine(file: java.io.File): String {
    if (!file.isFile) {
        return ""
    }
    return file
        .readText(Charsets.UTF_8)
        .lineSequence()
        .map { it.trim() }
        .firstOrNull { it.isNotEmpty() && !it.startsWith("#") }
        .orEmpty()
}

fun loadLocalProperties(): Properties {
    val props = Properties()
    val localProperties = rootProject.file("local.properties")
    if (localProperties.isFile) {
        localProperties.inputStream().use { props.load(it) }
    }
    return props
}

@Suppress("UNCHECKED_CAST")
fun loadDesktopConfigMap(): Map<String, Any?>? {
    val configFile = monorepoRoot().resolve("config/config.json")
    if (!configFile.isFile) {
        return null
    }
    return runCatching {
        JsonSlurper().parseText(configFile.readText(Charsets.UTF_8)) as Map<String, Any?>
    }.getOrNull()
}

fun mapString(
    map: Map<*, *>?,
    key: String,
): String = map?.get(key)?.toString()?.trim().orEmpty()

fun nestedMap(
    map: Map<*, *>?,
    key: String,
): Map<*, *>? {
    val value = map?.get(key)
    return value as? Map<*, *>
}

fun normalizeProvider(value: String): String {
    val name = value.trim().lowercase()
    return when (name) {
        "bothub", "openai", "openrouter", "anthropic", "gemini" -> name
        "bothub.ru", "bothub_ru", "bothub-ru" -> "bothub.ru"
        "open-router", "open_router" -> "openrouter"
        else -> "bothub"
    }
}

fun resolveSnippetOrLiteral(raw: String): String {
    val value = raw.trim()
    if (value.startsWith("snippet:")) {
        val relative = value.removePrefix("snippet:").trim().replace('\\', '/')
        return readFirstNonEmptyLine(monorepoRoot().resolve(relative))
    }
    return value
}

data class ProviderDefaults(
    val settingsKey: String,
    val apiKeyConfig: String,
    val keyFile: String,
    val envKey: String,
    val defaultBaseUrl: String,
    val defaultModel: String,
    val defaultSpeechModel: String,
)

val providerDefaults =
    mapOf(
        "bothub" to
            ProviderDefaults(
                settingsKey = "bothub",
                apiKeyConfig = "bothub_api_key",
                keyFile = "api-keys/bothub-api-key.txt",
                envKey = "BOTHUB_API_KEY",
                defaultBaseUrl = "https://bothub.chat/api/v2/openai/v1",
                defaultModel = "gpt-5.4",
                defaultSpeechModel = "gemini-3.1-flash-lite-preview",
            ),
        "bothub.ru" to
            ProviderDefaults(
                settingsKey = "bothub_ru",
                apiKeyConfig = "bothub_ru_api_key",
                keyFile = "api-keys/bothub-ru-api-key.txt",
                envKey = "BOTHUB_RU_API_KEY",
                defaultBaseUrl = "https://openai.bothub.ru/v1",
                defaultModel = "gpt-5.4",
                defaultSpeechModel = "gemini-3.1-flash-lite-preview",
            ),
        "openai" to
            ProviderDefaults(
                settingsKey = "openai",
                apiKeyConfig = "openai_api_key",
                keyFile = "api-keys/openai-api-key.txt",
                envKey = "OPENAI_API_KEY",
                defaultBaseUrl = "https://api.openai.com/v1",
                defaultModel = "gpt-4.1",
                defaultSpeechModel = "whisper-1",
            ),
        "openrouter" to
            ProviderDefaults(
                settingsKey = "openrouter",
                apiKeyConfig = "openrouter_api_key",
                keyFile = "api-keys/openrouter-api-key.txt",
                envKey = "OPENROUTER_API_KEY",
                defaultBaseUrl = "https://openrouter.ai/api/v1",
                defaultModel = "openai/gpt-4.1",
                defaultSpeechModel = "openai/whisper-large-v3",
            ),
        "anthropic" to
            ProviderDefaults(
                settingsKey = "anthropic",
                apiKeyConfig = "anthropic_api_key",
                keyFile = "api-keys/anthropic-api-key.txt",
                envKey = "ANTHROPIC_API_KEY",
                defaultBaseUrl = "https://api.anthropic.com",
                defaultModel = "claude-sonnet-4-6",
                defaultSpeechModel = "",
            ),
        "gemini" to
            ProviderDefaults(
                settingsKey = "gemini",
                apiKeyConfig = "gemini_api_key",
                keyFile = "api-keys/gemini-api-key.txt",
                envKey = "GEMINI_API_KEY",
                defaultBaseUrl = "https://generativelanguage.googleapis.com/v1beta",
                defaultModel = "gemini-2.5-flash",
                defaultSpeechModel = "gemini-2.5-flash",
            ),
    )

fun resolveProviderId(
    localProps: Properties,
    desktopConfig: Map<String, Any?>?,
): String {
    val fromEnv = System.getenv("AI_PROVIDER")?.trim().orEmpty()
    if (fromEnv.isNotEmpty()) {
        return normalizeProvider(fromEnv)
    }
    val fromProps = localProps.getProperty("ai.provider")?.trim().orEmpty()
    if (fromProps.isNotEmpty()) {
        return normalizeProvider(fromProps)
    }
    val fromConfig = mapString(nestedMap(desktopConfig, "ai"), "provider")
    if (fromConfig.isNotEmpty()) {
        return normalizeProvider(fromConfig)
    }
    return "bothub"
}

fun resolveSpeechProviderId(
    chatProvider: String,
    localProps: Properties,
    desktopConfig: Map<String, Any?>?,
): String {
    val fromEnv = System.getenv("AI_SPEECH_PROVIDER")?.trim().orEmpty()
    if (fromEnv.isNotEmpty()) {
        return normalizeProvider(fromEnv)
    }
    val fromProps = localProps.getProperty("ai.speech_provider")?.trim().orEmpty()
    if (fromProps.isNotEmpty()) {
        return normalizeProvider(fromProps)
    }
    val fromConfig = mapString(nestedMap(desktopConfig, "ai"), "speech_provider")
    if (fromConfig.isNotEmpty()) {
        return normalizeProvider(fromConfig)
    }
    return chatProvider
}

fun resolveProviderApiKey(
    provider: String,
    localProps: Properties,
    desktopConfig: Map<String, Any?>?,
): String {
    val defaults = providerDefaults.getValue(provider)
    val fromEnv = System.getenv(defaults.envKey)?.trim().orEmpty()
    if (fromEnv.isNotEmpty()) {
        return fromEnv
    }
    val propKey = "${defaults.settingsKey}.api_key"
    val fromProps = localProps.getProperty(propKey)?.trim().orEmpty()
    if (fromProps.isNotEmpty()) {
        return fromProps
    }
    val fromConfigRaw = mapString(desktopConfig, defaults.apiKeyConfig)
    if (fromConfigRaw.isNotEmpty()) {
        val resolved = resolveSnippetOrLiteral(fromConfigRaw)
        if (resolved.isNotEmpty()) {
            return resolved
        }
    }
    return readFirstNonEmptyLine(monorepoRoot().resolve(defaults.keyFile))
}

fun resolveProviderSetting(
    provider: String,
    field: String,
    envName: String,
    propertyName: String,
    default: String,
    localProps: Properties,
    desktopConfig: Map<String, Any?>?,
): String {
    val fromEnv = System.getenv(envName)?.trim().orEmpty()
    if (fromEnv.isNotEmpty()) {
        return fromEnv
    }
    val fromProps = localProps.getProperty(propertyName)?.trim().orEmpty()
    if (fromProps.isNotEmpty()) {
        return fromProps
    }
    val section = nestedMap(desktopConfig, providerDefaults.getValue(provider).settingsKey)
    val fromConfig = mapString(section, field)
    if (fromConfig.isNotEmpty()) {
        return fromConfig
    }
    return default
}

val localProps = loadLocalProperties()
val desktopConfig = loadDesktopConfigMap()
val aiProvider = resolveProviderId(localProps, desktopConfig)
val aiSpeechProvider = resolveSpeechProviderId(aiProvider, localProps, desktopConfig)
val chatDefaults = providerDefaults.getValue(aiProvider)
val speechDefaults = providerDefaults.getValue(aiSpeechProvider)

val aiApiKey = resolveProviderApiKey(aiProvider, localProps, desktopConfig)
val aiBaseUrl =
    resolveProviderSetting(
        provider = aiProvider,
        field = "base_url",
        envName = "AI_BASE_URL",
        propertyName = "ai.base_url",
        default = chatDefaults.defaultBaseUrl,
        localProps = localProps,
        desktopConfig = desktopConfig,
    )
val aiModel =
    resolveProviderSetting(
        provider = aiProvider,
        field = "model",
        envName = "AI_MODEL",
        propertyName = "ai.model",
        default = chatDefaults.defaultModel,
        localProps = localProps,
        desktopConfig = desktopConfig,
    )
val aiSpeechApiKey =
    if (aiSpeechProvider == aiProvider) {
        aiApiKey
    } else {
        resolveProviderApiKey(aiSpeechProvider, localProps, desktopConfig)
    }
val aiSpeechBaseUrl =
    if (aiSpeechProvider == aiProvider) {
        aiBaseUrl
    } else {
        resolveProviderSetting(
            provider = aiSpeechProvider,
            field = "base_url",
            envName = "AI_SPEECH_BASE_URL",
            propertyName = "ai.speech_base_url",
            default = speechDefaults.defaultBaseUrl,
            localProps = localProps,
            desktopConfig = desktopConfig,
        )
    }
val aiSpeechModel =
    resolveProviderSetting(
        provider = aiSpeechProvider,
        field = "speech_model",
        envName = "AI_SPEECH_MODEL",
        propertyName = "ai.speech_model",
        default = speechDefaults.defaultSpeechModel.ifEmpty { speechDefaults.defaultModel },
        localProps = localProps,
        desktopConfig = desktopConfig,
    )

val bothubEmbeddedApiKey = resolveProviderApiKey("bothub", localProps, desktopConfig)
val bothubEmbeddedBaseUrl =
    resolveProviderSetting(
        provider = "bothub",
        field = "base_url",
        envName = "BOTHUB_BASE_URL",
        propertyName = "bothub.base_url",
        default = providerDefaults.getValue("bothub").defaultBaseUrl,
        localProps = localProps,
        desktopConfig = desktopConfig,
    )
val bothubEmbeddedModel =
    resolveProviderSetting(
        provider = "bothub",
        field = "model",
        envName = "BOTHUB_MODEL",
        propertyName = "bothub.model",
        default = providerDefaults.getValue("bothub").defaultModel,
        localProps = localProps,
        desktopConfig = desktopConfig,
    )
val bothubEmbeddedSpeechModel =
    resolveProviderSetting(
        provider = "bothub",
        field = "speech_model",
        envName = "BOTHUB_SPEECH_MODEL",
        propertyName = "bothub.speech_model",
        default = providerDefaults.getValue("bothub").defaultSpeechModel,
        localProps = localProps,
        desktopConfig = desktopConfig,
    )
val bothubRuEmbeddedApiKey = resolveProviderApiKey("bothub.ru", localProps, desktopConfig)
val bothubRuEmbeddedBaseUrl =
    resolveProviderSetting(
        provider = "bothub.ru",
        field = "base_url",
        envName = "BOTHUB_RU_BASE_URL",
        propertyName = "bothub_ru.base_url",
        default = providerDefaults.getValue("bothub.ru").defaultBaseUrl,
        localProps = localProps,
        desktopConfig = desktopConfig,
    )
val bothubRuEmbeddedModel =
    resolveProviderSetting(
        provider = "bothub.ru",
        field = "model",
        envName = "BOTHUB_RU_MODEL",
        propertyName = "bothub_ru.model",
        default = providerDefaults.getValue("bothub.ru").defaultModel,
        localProps = localProps,
        desktopConfig = desktopConfig,
    )
val bothubRuEmbeddedSpeechModel =
    resolveProviderSetting(
        provider = "bothub.ru",
        field = "speech_model",
        envName = "BOTHUB_RU_SPEECH_MODEL",
        propertyName = "bothub_ru.speech_model",
        default = providerDefaults.getValue("bothub.ru").defaultSpeechModel,
        localProps = localProps,
        desktopConfig = desktopConfig,
    )

// Backward-compatible BotHub BuildConfig fields (active chat provider values).
val bothubApiKey = aiApiKey
val bothubBaseUrl = aiBaseUrl
val bothubModel = aiModel
val bothubSpeechModel = aiSpeechModel

if (aiApiKey.isEmpty()) {
    logger.warn(
        "AI API key is empty for provider '$aiProvider'. Set ${chatDefaults.envKey} or create " +
            "../${chatDefaults.keyFile} (relative to android/), or configure config/config.json. " +
            "Speech to Text and other AI utilities will show an error until a key is provided.",
    )
}

val bothubPromptsAssetsDir = layout.buildDirectory.dir("generated/bothubPrompts")

val copyBothubPrompts =
    tasks.register<Copy>("copyBothubPrompts") {
        description =
            "Copy BotHub prompt Markdown from monorepo config/prompts into generated assets"
        from(rootProject.projectDir.parentFile.resolve("config/prompts")) {
            include("text-fix-ru.md", "text-rewrite-ru.md", "medicine-search.md", "speech-transcription.md")
        }
        into(bothubPromptsAssetsDir.map { it.dir("prompts") })
    }

android {
    namespace = "dev.harrix.hsk"
    compileSdk = 36

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

        buildConfigField("String", "AI_PROVIDER", escapeBuildConfigString(aiProvider))
        buildConfigField("String", "AI_SPEECH_PROVIDER", escapeBuildConfigString(aiSpeechProvider))
        buildConfigField("String", "AI_API_KEY", escapeBuildConfigString(aiApiKey))
        buildConfigField("String", "AI_BASE_URL", escapeBuildConfigString(aiBaseUrl))
        buildConfigField("String", "AI_MODEL", escapeBuildConfigString(aiModel))
        buildConfigField("String", "AI_SPEECH_API_KEY", escapeBuildConfigString(aiSpeechApiKey))
        buildConfigField("String", "AI_SPEECH_BASE_URL", escapeBuildConfigString(aiSpeechBaseUrl))
        buildConfigField("String", "AI_SPEECH_MODEL", escapeBuildConfigString(aiSpeechModel))
        buildConfigField(
            "String",
            "AI_BOTHUB_API_KEY",
            escapeBuildConfigString(bothubEmbeddedApiKey),
        )
        buildConfigField(
            "String",
            "AI_BOTHUB_BASE_URL",
            escapeBuildConfigString(bothubEmbeddedBaseUrl),
        )
        buildConfigField("String", "AI_BOTHUB_MODEL", escapeBuildConfigString(bothubEmbeddedModel))
        buildConfigField(
            "String",
            "AI_BOTHUB_SPEECH_MODEL",
            escapeBuildConfigString(bothubEmbeddedSpeechModel),
        )
        buildConfigField(
            "String",
            "AI_BOTHUB_RU_API_KEY",
            escapeBuildConfigString(bothubRuEmbeddedApiKey),
        )
        buildConfigField(
            "String",
            "AI_BOTHUB_RU_BASE_URL",
            escapeBuildConfigString(bothubRuEmbeddedBaseUrl),
        )
        buildConfigField(
            "String",
            "AI_BOTHUB_RU_MODEL",
            escapeBuildConfigString(bothubRuEmbeddedModel),
        )
        buildConfigField(
            "String",
            "AI_BOTHUB_RU_SPEECH_MODEL",
            escapeBuildConfigString(bothubRuEmbeddedSpeechModel),
        )

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
    implementation(libs.androidx.health.connect)
    debugImplementation(libs.androidx.compose.ui.tooling)
    detektPlugins(libs.detekt.compose.rules)
}

tasks.named("check") {
    dependsOn("detekt", "lintDebug")
}
