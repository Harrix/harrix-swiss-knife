package dev.harrix.hsk.gallery

import android.content.Context
import android.database.Cursor
import android.location.Geocoder
import android.net.Uri
import android.os.Build
import android.provider.MediaStore
import androidx.exifinterface.media.ExifInterface
import java.util.Locale
import kotlin.math.roundToInt

private const val GoogleMapsSearchUrl = "https://www.google.com/maps/search/?api=1&query=%s,%s"

enum class PhotoCaptureMode {
    Landscape,
    Portrait,
    Night,
}

/** Rich file / EXIF summary for Gallery Cleaner and Photo Editor (Samsung Gallery–like). */
data class PhotoFileDetails(
    val displayName: String?,
    val relativePath: String?,
    val sizeBytes: Long,
    val width: Int?,
    val height: Int?,
    val megapixels: Float?,
    val deviceLabel: String?,
    val captureMode: PhotoCaptureMode?,
    val iso: String?,
    val focalLengthLabel: String?,
    val exposureBiasLabel: String?,
    val apertureLabel: String?,
    val shutterLabel: String?,
    val locationLabel: String?,
    val latitude: Double?,
    val longitude: Double?,
) {
    val hasMapLocation: Boolean
        get() = latitude != null && longitude != null

    /** `48.858370, 2.294481` style coordinates line. */
    fun coordinatesLabel(): String? {
        val lat = latitude ?: return null
        val lng = longitude ?: return null
        return String.format(Locale.US, "%.6f, %.6f", lat, lng)
    }

    /** Google Maps search URL with a pin at the capture coordinates. */
    fun googleMapsUri(): Uri? {
        val lat = latitude ?: return null
        val lng = longitude ?: return null
        return Uri.parse(String.format(Locale.US, GoogleMapsSearchUrl, lat, lng))
    }

    /**
     * Static map preview URL with a red pin (OpenStreetMap tiles; opens in Google Maps on tap).
     */
    fun staticMapPreviewUrl(
        widthPx: Int = 640,
        heightPx: Int = 360,
    ): String? {
        val lat = latitude ?: return null
        val lng = longitude ?: return null
        val w = widthPx.coerceIn(120, 1280)
        val h = heightPx.coerceIn(120, 1280)
        return String.format(
            Locale.US,
            "https://staticmap.openstreetmap.de/staticmap.php?center=%f,%f&zoom=15&size=%dx%d&markers=%f,%f,red-pushpin",
            lat,
            lng,
            w,
            h,
            lat,
            lng,
        )
    }

    val resolutionLabel: String?
        get() {
            val w = width ?: return null
            val h = height ?: return null
            if (w <= 0 || h <= 0) {
                return null
            }
            return "${w}x$h"
        }

    val megapixelsLabel: String?
        get() {
            val mp = megapixels ?: return null
            if (mp <= 0f) {
                return null
            }
            val rounded =
                if (mp >= 10f) {
                    mp.roundToInt().toString()
                } else {
                    String.format(Locale.US, "%.1f", mp).trimEnd('0').trimEnd('.')
                }
            return "${rounded}MP"
        }

    /** `7.32 MB | 3000x4000 | 12MP` style summary. */
    fun fileStatsLine(sizeFormatter: (Long) -> String): String? {
        val parts =
            listOfNotNull(
                sizeBytes.takeIf { it > 0L }?.let(sizeFormatter),
                resolutionLabel,
                megapixelsLabel,
            )
        return parts.takeIf { it.isNotEmpty() }?.joinToString(" | ")
    }

    /** `ISO 32 | 115mm | 0.0ev | F3.4 | 1/1365 s` style summary. */
    fun cameraSettingsLine(): String? {
        val parts =
            listOfNotNull(
                iso?.let { "ISO $it" },
                focalLengthLabel,
                exposureBiasLabel,
                apertureLabel,
                shutterLabel,
            )
        return parts.takeIf { it.isNotEmpty() }?.joinToString(" | ")
    }
}

object PhotoFileDetailsLoader {
    fun load(
        context: Context,
        photo: CameraPhoto,
    ): PhotoFileDetails {
        val appContext = context.applicationContext
        val media = queryMediaStore(appContext, photo.uri)
        val exif = readExif(appContext, photo.uri)

        val width = media.width ?: exif.width
        val height = media.height ?: exif.height
        val megapixels = megapixelsOrNull(width, height)
        val latitude = exif.latitude ?: media.latitude
        val longitude = exif.longitude ?: media.longitude
        val locationLabel = locationLabelOrNull(appContext, latitude, longitude)

        return PhotoFileDetails(
            displayName = media.displayName ?: photo.displayName,
            relativePath = media.relativePath,
            sizeBytes = media.sizeBytes.takeIf { it > 0L } ?: photo.sizeBytes,
            width = width,
            height = height,
            megapixels = megapixels,
            deviceLabel = exif.deviceLabel,
            captureMode = exif.captureMode,
            iso = exif.iso,
            focalLengthLabel = exif.focalLengthLabel,
            exposureBiasLabel = exif.exposureBiasLabel,
            apertureLabel = exif.apertureLabel,
            shutterLabel = exif.shutterLabel,
            locationLabel = locationLabel,
            latitude = latitude,
            longitude = longitude,
        )
    }

    private data class MediaStoreFields(
        val displayName: String?,
        val relativePath: String?,
        val sizeBytes: Long,
        val width: Int?,
        val height: Int?,
        val latitude: Double?,
        val longitude: Double?,
    )

    private data class ExifFields(
        val width: Int?,
        val height: Int?,
        val deviceLabel: String?,
        val captureMode: PhotoCaptureMode?,
        val iso: String?,
        val focalLengthLabel: String?,
        val exposureBiasLabel: String?,
        val apertureLabel: String?,
        val shutterLabel: String?,
        val latitude: Double?,
        val longitude: Double?,
    )

    private fun queryMediaStore(
        context: Context,
        uri: Uri,
    ): MediaStoreFields {
        val projection = mediaStoreProjection()
        return try {
            context.contentResolver.query(uri, projection, null, null, null)?.use { cursor ->
                if (!cursor.moveToFirst()) {
                    return emptyMediaStoreFields()
                }
                readMediaStoreFields(cursor)
            } ?: emptyMediaStoreFields()
        } catch (_: Exception) {
            emptyMediaStoreFields()
        }
    }

    private fun mediaStoreProjection(): Array<String> = buildList {
        add(MediaStore.MediaColumns.DISPLAY_NAME)
        add(MediaStore.MediaColumns.SIZE)
        add(MediaStore.MediaColumns.WIDTH)
        add(MediaStore.MediaColumns.HEIGHT)
        @Suppress("DEPRECATION")
        add(MediaStore.Images.ImageColumns.LATITUDE)
        @Suppress("DEPRECATION")
        add(MediaStore.Images.ImageColumns.LONGITUDE)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            add(MediaStore.MediaColumns.RELATIVE_PATH)
        } else {
            @Suppress("DEPRECATION")
            add(MediaStore.MediaColumns.DATA)
        }
    }.toTypedArray()

    private fun emptyMediaStoreFields(): MediaStoreFields = MediaStoreFields(null, null, 0L, null, null, null, null)

    private fun readMediaStoreFields(cursor: Cursor): MediaStoreFields {
        fun col(name: String): Int = cursor.getColumnIndex(name)
        val name =
            col(MediaStore.MediaColumns.DISPLAY_NAME).takeIf { it >= 0 }?.let {
                cursor.getString(it)
            }
        val size =
            col(MediaStore.MediaColumns.SIZE).takeIf { it >= 0 }?.let {
                cursor.getLong(it)
            } ?: 0L
        val width =
            col(MediaStore.MediaColumns.WIDTH).takeIf { it >= 0 }?.let {
                cursor.getInt(it).takeIf { value -> value > 0 }
            }
        val height =
            col(MediaStore.MediaColumns.HEIGHT).takeIf { it >= 0 }?.let {
                cursor.getInt(it).takeIf { value -> value > 0 }
            }

        @Suppress("DEPRECATION")
        val latitude =
            col(MediaStore.Images.ImageColumns.LATITUDE).takeIf { it >= 0 }?.let { index ->
                cursor.getDouble(index).takeUnless { value -> value.isNaN() }
            }

        @Suppress("DEPRECATION")
        val longitude =
            col(MediaStore.Images.ImageColumns.LONGITUDE).takeIf { it >= 0 }?.let { index ->
                cursor.getDouble(index).takeUnless { value -> value.isNaN() }
            }
        // MediaStore may return 0,0 when GPS is missing — treat that as absent.
        val hasGps =
            latitude != null &&
                longitude != null &&
                !(latitude == 0.0 && longitude == 0.0)
        return MediaStoreFields(
            displayName = name,
            relativePath = readRelativePath(cursor, ::col),
            sizeBytes = size.coerceAtLeast(0L),
            width = width,
            height = height,
            latitude = latitude.takeIf { hasGps },
            longitude = longitude.takeIf { hasGps },
        )
    }

    private fun readRelativePath(
        cursor: Cursor,
        col: (String) -> Int,
    ): String? = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
        col(MediaStore.MediaColumns.RELATIVE_PATH).takeIf { it >= 0 }?.let {
            cursor.getString(it)?.trimEnd('/')
        }
    } else {
        @Suppress("DEPRECATION")
        col(MediaStore.MediaColumns.DATA).takeIf { it >= 0 }?.let { index ->
            cursor
                .getString(index)
                ?.substringBeforeLast('/', missingDelimiterValue = "")
                ?.takeIf { it.isNotBlank() }
        }
    }

    private fun megapixelsOrNull(
        width: Int?,
        height: Int?,
    ): Float? {
        if (width == null || height == null) {
            return null
        }
        if (width <= 0 || height <= 0) {
            return null
        }
        return width.toFloat() * height.toFloat() / 1_000_000f
    }

    private fun locationLabelOrNull(
        context: Context,
        latitude: Double?,
        longitude: Double?,
    ): String? {
        if (latitude == null || longitude == null) {
            return null
        }
        // Coordinates are shown as their own row; keep this for a human address only.
        return reverseGeocode(context, latitude, longitude)
    }

    private fun readExif(
        context: Context,
        uri: Uri,
    ): ExifFields {
        val empty =
            ExifFields(
                width = null,
                height = null,
                deviceLabel = null,
                captureMode = null,
                iso = null,
                focalLengthLabel = null,
                exposureBiasLabel = null,
                apertureLabel = null,
                shutterLabel = null,
                latitude = null,
                longitude = null,
            )
        return try {
            context.contentResolver.openInputStream(uri)?.use { input ->
                val exif = ExifInterface(input)
                val width =
                    exif
                        .getAttributeInt(ExifInterface.TAG_IMAGE_WIDTH, 0)
                        .takeIf { it > 0 }
                        ?: exif
                            .getAttributeInt(ExifInterface.TAG_PIXEL_X_DIMENSION, 0)
                            .takeIf { it > 0 }
                val height =
                    exif
                        .getAttributeInt(ExifInterface.TAG_IMAGE_LENGTH, 0)
                        .takeIf { it > 0 }
                        ?: exif
                            .getAttributeInt(ExifInterface.TAG_PIXEL_Y_DIMENSION, 0)
                            .takeIf { it > 0 }
                val make = exif.getAttribute(ExifInterface.TAG_MAKE)?.trim().orEmpty()
                val model = exif.getAttribute(ExifInterface.TAG_MODEL)?.trim().orEmpty()
                val device =
                    when {
                        model.isBlank() && make.isBlank() -> null
                        model.isBlank() -> make
                        make.isBlank() || model.contains(make, ignoreCase = true) -> model
                        else -> "$make $model"
                    }
                val latLong = FloatArray(2)
                val hasLatLong = exif.getLatLong(latLong)
                ExifFields(
                    width = width,
                    height = height,
                    deviceLabel = device,
                    captureMode = sceneCaptureMode(exif),
                    iso = isoLabel(exif),
                    focalLengthLabel = focalLengthLabel(exif),
                    exposureBiasLabel = exposureBiasLabel(exif),
                    apertureLabel = apertureLabel(exif),
                    shutterLabel = shutterLabel(exif),
                    latitude = if (hasLatLong) latLong[0].toDouble() else null,
                    longitude = if (hasLatLong) latLong[1].toDouble() else null,
                )
            } ?: empty
        } catch (_: Exception) {
            empty
        }
    }

    private fun isoLabel(exif: ExifInterface): String? {
        val iso =
            exif.getAttributeInt(ExifInterface.TAG_PHOTOGRAPHIC_SENSITIVITY, 0).takeIf { it > 0 }
                ?: exif
                    .getAttribute(ExifInterface.TAG_ISO_SPEED_RATINGS)
                    ?.substringBefore(',')
                    ?.trim()
                    ?.toIntOrNull()
        return iso?.takeIf { it > 0 }?.toString()
    }

    private fun focalLengthLabel(exif: ExifInterface): String? {
        val focal = exif.getAttributeDouble(ExifInterface.TAG_FOCAL_LENGTH, Double.NaN)
        if (focal.isNaN() || focal <= 0.0) {
            return null
        }
        val text =
            if (focal >= 10.0) {
                focal.roundToInt().toString()
            } else {
                String.format(Locale.getDefault(), "%.1f", focal).trimEnd('0').trimEnd('.')
            }
        return "${text}mm"
    }

    private fun exposureBiasLabel(exif: ExifInterface): String? {
        val bias = exif.getAttributeDouble(ExifInterface.TAG_EXPOSURE_BIAS_VALUE, Double.NaN)
        if (bias.isNaN()) {
            return null
        }
        return String.format(Locale.getDefault(), "%.1fev", bias).replace('.', ',')
    }

    private fun apertureLabel(exif: ExifInterface): String? {
        val aperture = exif.getAttributeDouble(ExifInterface.TAG_F_NUMBER, Double.NaN)
        if (aperture.isNaN() || aperture <= 0.0) {
            return null
        }
        val text =
            String
                .format(Locale.getDefault(), "%.1f", aperture)
                .trimEnd('0')
                .trimEnd('.')
                .replace('.', ',')
        return "F$text"
    }

    private fun shutterLabel(exif: ExifInterface): String? {
        val exposure = exif.getAttributeDouble(ExifInterface.TAG_EXPOSURE_TIME, Double.NaN)
        if (exposure.isNaN() || exposure <= 0.0) {
            return null
        }
        return if (exposure >= 1.0) {
            String.format(Locale.getDefault(), "%.1f s", exposure).replace('.', ',')
        } else {
            val denom = (1.0 / exposure).roundToInt().coerceAtLeast(1)
            "1/$denom s"
        }
    }

    private fun sceneCaptureMode(exif: ExifInterface): PhotoCaptureMode? {
        val type = exif.getAttributeInt(ExifInterface.TAG_SCENE_CAPTURE_TYPE, -1)
        return when (type) {
            1 -> PhotoCaptureMode.Landscape
            2 -> PhotoCaptureMode.Portrait
            3 -> PhotoCaptureMode.Night
            else -> null
        }
    }

    @Suppress("DEPRECATION")
    private fun reverseGeocode(
        context: Context,
        latitude: Double,
        longitude: Double,
    ): String? {
        if (!Geocoder.isPresent()) {
            return null
        }
        return try {
            val geocoder = Geocoder(context, Locale.getDefault())
            val results = geocoder.getFromLocation(latitude, longitude, 1)
            val address = results?.firstOrNull() ?: return null
            val lines =
                (0..address.maxAddressLineIndex).mapNotNull { index ->
                    address.getAddressLine(index)?.takeIf { it.isNotBlank() }
                }
            lines.firstOrNull()
                ?: listOfNotNull(
                    address.thoroughfare,
                    address.subThoroughfare,
                    address.locality,
                    address.countryName,
                ).joinToString(", ").takeIf { it.isNotBlank() }
        } catch (_: Exception) {
            null
        }
    }
}
