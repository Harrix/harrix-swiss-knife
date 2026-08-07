package dev.harrix.hsk.gallery

import android.content.ContentValues
import android.content.Context
import android.net.Uri
import android.provider.MediaStore
import androidx.exifinterface.media.ExifInterface
import java.io.ByteArrayInputStream
import java.io.File
import java.text.SimpleDateFormat
import java.util.Locale

/**
 * Copies EXIF from a source image onto recompressed bytes.
 * Bitmap.compress strips metadata; Dropbox and galleries then fall back to file timestamps.
 */
internal object ExifPreserver {
    /**
     * Write [encoded] to a temp file, copy tags from [sourceUri], set orientation to
     * normal and dimensions to [width]×[height], return the resulting bytes.
     * On any failure returns [encoded] unchanged.
     */
    fun withPreservedExif(
        context: Context,
        sourceUri: Uri,
        mimeType: String,
        encoded: ByteArray,
        width: Int,
        height: Int,
        fileExtension: String,
    ): ByteArray {
        if (!ExifInterface.isSupportedMimeType(mimeType)) {
            return encoded
        }
        val temp =
            try {
                File.createTempFile("hsk_exif_", ".$fileExtension", context.cacheDir)
            } catch (_: Exception) {
                return encoded
            }
        try {
            temp.writeBytes(encoded)
            val sourceExif =
                try {
                    context.contentResolver.openInputStream(sourceUri)?.use { input ->
                        ExifInterface(input)
                    }
                } catch (_: Exception) {
                    null
                } ?: return encoded
            val destExif =
                try {
                    ExifInterface(temp)
                } catch (_: Exception) {
                    return encoded
                }
            for (tag in TAGS_TO_COPY) {
                val value = sourceExif.getAttribute(tag) ?: continue
                runCatching { destExif.setAttribute(tag, value) }
            }
            destExif.setAttribute(
                ExifInterface.TAG_ORIENTATION,
                ExifInterface.ORIENTATION_NORMAL.toString(),
            )
            destExif.setAttribute(ExifInterface.TAG_IMAGE_WIDTH, width.toString())
            destExif.setAttribute(ExifInterface.TAG_IMAGE_LENGTH, height.toString())
            destExif.setAttribute(ExifInterface.TAG_PIXEL_X_DIMENSION, width.toString())
            destExif.setAttribute(ExifInterface.TAG_PIXEL_Y_DIMENSION, height.toString())
            try {
                destExif.saveAttributes()
            } catch (_: Exception) {
                return encoded
            }
            return temp.readBytes()
        } catch (_: Exception) {
            return encoded
        } finally {
            runCatching { temp.delete() }
        }
    }

    fun dateTakenMillisFromBytes(bytes: ByteArray): Long? = try {
        dateTakenMillisFromExif(ExifInterface(ByteArrayInputStream(bytes)))
    } catch (_: Exception) {
        null
    }

    fun syncMediaStoreDateTaken(
        context: Context,
        uri: Uri,
        bytes: ByteArray,
    ) {
        if (uri.authority != MediaStore.AUTHORITY) {
            return
        }
        val takenMs = dateTakenMillisFromBytes(bytes) ?: return
        runCatching {
            val values =
                ContentValues().apply {
                    put(MediaStore.Images.Media.DATE_TAKEN, takenMs)
                }
            context.contentResolver.update(uri, values, null, null)
        }
    }

    private fun dateTakenMillisFromExif(exif: ExifInterface): Long? {
        val gpsMs = exif.gpsDateTime
        if (gpsMs != null && gpsMs >= 0L) {
            return gpsMs
        }
        val raw =
            exif.getAttribute(ExifInterface.TAG_DATETIME_ORIGINAL)
                ?: exif.getAttribute(ExifInterface.TAG_DATETIME_DIGITIZED)
                ?: exif.getAttribute(ExifInterface.TAG_DATETIME)
                ?: return null
        return runCatching {
            SimpleDateFormat("yyyy:MM:dd HH:mm:ss", Locale.US).parse(raw)?.time
        }.getOrNull()
    }

    /**
     * Tags copied from the original after recompress.
     * Skips orientation/size (rewritten here), thumbnail offsets, and MakerNote
     * (often oversized / breaks [ExifInterface.saveAttributes]).
     */
    private val TAGS_TO_COPY =
        arrayOf(
            ExifInterface.TAG_APERTURE_VALUE,
            ExifInterface.TAG_ARTIST,
            ExifInterface.TAG_BITS_PER_SAMPLE,
            ExifInterface.TAG_BODY_SERIAL_NUMBER,
            ExifInterface.TAG_BRIGHTNESS_VALUE,
            ExifInterface.TAG_CAMERA_OWNER_NAME,
            ExifInterface.TAG_CFA_PATTERN,
            ExifInterface.TAG_COLOR_SPACE,
            ExifInterface.TAG_COMPONENTS_CONFIGURATION,
            ExifInterface.TAG_COMPRESSED_BITS_PER_PIXEL,
            ExifInterface.TAG_CONTRAST,
            ExifInterface.TAG_COPYRIGHT,
            ExifInterface.TAG_CUSTOM_RENDERED,
            ExifInterface.TAG_DATETIME,
            ExifInterface.TAG_DATETIME_DIGITIZED,
            ExifInterface.TAG_DATETIME_ORIGINAL,
            ExifInterface.TAG_DEVICE_SETTING_DESCRIPTION,
            ExifInterface.TAG_DIGITAL_ZOOM_RATIO,
            ExifInterface.TAG_DNG_VERSION,
            ExifInterface.TAG_EXIF_VERSION,
            ExifInterface.TAG_EXPOSURE_BIAS_VALUE,
            ExifInterface.TAG_EXPOSURE_INDEX,
            ExifInterface.TAG_EXPOSURE_MODE,
            ExifInterface.TAG_EXPOSURE_PROGRAM,
            ExifInterface.TAG_EXPOSURE_TIME,
            ExifInterface.TAG_FILE_SOURCE,
            ExifInterface.TAG_FLASH,
            ExifInterface.TAG_FLASHPIX_VERSION,
            ExifInterface.TAG_FLASH_ENERGY,
            ExifInterface.TAG_FOCAL_LENGTH,
            ExifInterface.TAG_FOCAL_LENGTH_IN_35MM_FILM,
            ExifInterface.TAG_FOCAL_PLANE_RESOLUTION_UNIT,
            ExifInterface.TAG_FOCAL_PLANE_X_RESOLUTION,
            ExifInterface.TAG_FOCAL_PLANE_Y_RESOLUTION,
            ExifInterface.TAG_F_NUMBER,
            ExifInterface.TAG_GAIN_CONTROL,
            ExifInterface.TAG_GAMMA,
            ExifInterface.TAG_GPS_ALTITUDE,
            ExifInterface.TAG_GPS_ALTITUDE_REF,
            ExifInterface.TAG_GPS_AREA_INFORMATION,
            ExifInterface.TAG_GPS_DATESTAMP,
            ExifInterface.TAG_GPS_DEST_BEARING,
            ExifInterface.TAG_GPS_DEST_BEARING_REF,
            ExifInterface.TAG_GPS_DEST_DISTANCE,
            ExifInterface.TAG_GPS_DEST_DISTANCE_REF,
            ExifInterface.TAG_GPS_DEST_LATITUDE,
            ExifInterface.TAG_GPS_DEST_LATITUDE_REF,
            ExifInterface.TAG_GPS_DEST_LONGITUDE,
            ExifInterface.TAG_GPS_DEST_LONGITUDE_REF,
            ExifInterface.TAG_GPS_DIFFERENTIAL,
            ExifInterface.TAG_GPS_DOP,
            ExifInterface.TAG_GPS_H_POSITIONING_ERROR,
            ExifInterface.TAG_GPS_IMG_DIRECTION,
            ExifInterface.TAG_GPS_IMG_DIRECTION_REF,
            ExifInterface.TAG_GPS_LATITUDE,
            ExifInterface.TAG_GPS_LATITUDE_REF,
            ExifInterface.TAG_GPS_LONGITUDE,
            ExifInterface.TAG_GPS_LONGITUDE_REF,
            ExifInterface.TAG_GPS_MAP_DATUM,
            ExifInterface.TAG_GPS_MEASURE_MODE,
            ExifInterface.TAG_GPS_PROCESSING_METHOD,
            ExifInterface.TAG_GPS_SATELLITES,
            ExifInterface.TAG_GPS_SPEED,
            ExifInterface.TAG_GPS_SPEED_REF,
            ExifInterface.TAG_GPS_STATUS,
            ExifInterface.TAG_GPS_TIMESTAMP,
            ExifInterface.TAG_GPS_TRACK,
            ExifInterface.TAG_GPS_TRACK_REF,
            ExifInterface.TAG_GPS_VERSION_ID,
            ExifInterface.TAG_IMAGE_DESCRIPTION,
            ExifInterface.TAG_IMAGE_UNIQUE_ID,
            ExifInterface.TAG_INTEROPERABILITY_INDEX,
            ExifInterface.TAG_ISO_SPEED,
            ExifInterface.TAG_ISO_SPEED_LATITUDE_YYY,
            ExifInterface.TAG_ISO_SPEED_LATITUDE_ZZZ,
            ExifInterface.TAG_ISO_SPEED_RATINGS,
            ExifInterface.TAG_LENS_MAKE,
            ExifInterface.TAG_LENS_MODEL,
            ExifInterface.TAG_LENS_SERIAL_NUMBER,
            ExifInterface.TAG_LENS_SPECIFICATION,
            ExifInterface.TAG_LIGHT_SOURCE,
            ExifInterface.TAG_MAKE,
            ExifInterface.TAG_MAX_APERTURE_VALUE,
            ExifInterface.TAG_METERING_MODE,
            ExifInterface.TAG_MODEL,
            ExifInterface.TAG_OECF,
            ExifInterface.TAG_OFFSET_TIME,
            ExifInterface.TAG_OFFSET_TIME_DIGITIZED,
            ExifInterface.TAG_OFFSET_TIME_ORIGINAL,
            ExifInterface.TAG_PHOTOGRAPHIC_SENSITIVITY,
            ExifInterface.TAG_PHOTOMETRIC_INTERPRETATION,
            ExifInterface.TAG_PLANAR_CONFIGURATION,
            ExifInterface.TAG_PRIMARY_CHROMATICITIES,
            ExifInterface.TAG_RECOMMENDED_EXPOSURE_INDEX,
            ExifInterface.TAG_REFERENCE_BLACK_WHITE,
            ExifInterface.TAG_RELATED_SOUND_FILE,
            ExifInterface.TAG_RESOLUTION_UNIT,
            ExifInterface.TAG_ROWS_PER_STRIP,
            ExifInterface.TAG_SAMPLES_PER_PIXEL,
            ExifInterface.TAG_SATURATION,
            ExifInterface.TAG_SCENE_CAPTURE_TYPE,
            ExifInterface.TAG_SCENE_TYPE,
            ExifInterface.TAG_SENSING_METHOD,
            ExifInterface.TAG_SENSITIVITY_TYPE,
            ExifInterface.TAG_SHARPNESS,
            ExifInterface.TAG_SHUTTER_SPEED_VALUE,
            ExifInterface.TAG_SOFTWARE,
            ExifInterface.TAG_SPATIAL_FREQUENCY_RESPONSE,
            ExifInterface.TAG_SPECTRAL_SENSITIVITY,
            ExifInterface.TAG_STANDARD_OUTPUT_SENSITIVITY,
            ExifInterface.TAG_SUBJECT_AREA,
            ExifInterface.TAG_SUBJECT_DISTANCE,
            ExifInterface.TAG_SUBJECT_DISTANCE_RANGE,
            ExifInterface.TAG_SUBJECT_LOCATION,
            ExifInterface.TAG_SUBSEC_TIME,
            ExifInterface.TAG_SUBSEC_TIME_DIGITIZED,
            ExifInterface.TAG_SUBSEC_TIME_ORIGINAL,
            ExifInterface.TAG_TRANSFER_FUNCTION,
            ExifInterface.TAG_USER_COMMENT,
            ExifInterface.TAG_WHITE_BALANCE,
            ExifInterface.TAG_WHITE_POINT,
            ExifInterface.TAG_XMP,
            ExifInterface.TAG_X_RESOLUTION,
            ExifInterface.TAG_Y_CB_CR_COEFFICIENTS,
            ExifInterface.TAG_Y_CB_CR_POSITIONING,
            ExifInterface.TAG_Y_CB_CR_SUB_SAMPLING,
            ExifInterface.TAG_Y_RESOLUTION,
        )
}
