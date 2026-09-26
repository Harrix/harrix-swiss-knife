@file:Suppress("LargeClass")

package dev.harrix.hsk.ui.icons

import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.graphics.vector.PathParser
import androidx.compose.ui.unit.dp

object LucideIcons {
    val AddAPhoto: ImageVector by lazy {
        lucide(
            "image-plus",
            "M16 5h6",
            "M19 2v6",
            "M21 11.5v7.5a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2v-14a2 2 0 0 1 2 -2h7.5",
            "M21 15l-3.086 -3.086a2 2 0 0 0 -2.828 0l-9.086 9.086",
            "M7 9A2 2 0 1 0 11 9A2 2 0 1 0 7 9z",
        )
    }

    val ArrowBack: ImageVector by lazy {
        lucide(
            "arrow-left",
            "M12 19l-7 -7l7 -7",
            "M19 12h-14",
            autoMirror = true,
        )
    }

    val ArrowDownward: ImageVector by lazy {
        lucide(
            "arrow-down",
            "M12 5v14",
            "M19 12l-7 7l-7 -7",
        )
    }

    val ArrowUpward: ImageVector by lazy {
        lucide(
            "arrow-up",
            "M5 12l7 -7l7 7",
            "M12 19v-14",
        )
    }

    val AutoFixHigh: ImageVector by lazy {
        lucide(
            "sparkles",
            "M11.017 2.814a1 1 0 0 1 1.966 0l1.051 5.558a2 2 0 0 0 1.594 1.594l5.558 1.051a1 1 0 0 1 0 1.966l-5.5" +
                "58 1.051a2 2 0 0 0 -1.594 1.594l-1.051 5.558a1 1 0 0 1 -1.966 0l-1.051 -5.558a2 2 0 0 0 -1.594 -1.59" +
                "4l-5.558 -1.051a1 1 0 0 1 0 -1.966l5.558 -1.051a2 2 0 0 0 1.594 -1.594z",
            "M20 2v4",
            "M22 4h-4",
            "M2 20A2 2 0 1 0 6 20A2 2 0 1 0 2 20z",
        )
    }

    val BarChart: ImageVector by lazy {
        lucide(
            "chart-column",
            "M3 3v16a2 2 0 0 0 2 2h16",
            "M18 17v-8",
            "M13 17v-12",
            "M8 17v-3",
        )
    }

    val BlurOn: ImageVector by lazy {
        lucide(
            "cloud-fog",
            "M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242",
            "M16 17h-9",
            "M17 21h-8",
        )
    }

    val CalendarMonth: ImageVector by lazy {
        lucide(
            "calendar",
            "M8 2v3",
            "M16 2v3",
            "M5 3H19A2 2 0 0 1 21 5V19A2 2 0 0 1 19 21H5A2 2 0 0 1 3 19V5A2 2 0 0 1 5 3Z",
            "M3 9h18",
        )
    }

    val CheckCircle: ImageVector by lazy {
        lucide(
            "circle-check",
            "M2 12A10 10 0 1 0 22 12A10 10 0 1 0 2 12z",
            "M16 9l-5.5 5.5l-2.5 -2.5",
        )
    }

    val CleaningServices: ImageVector by lazy {
        lucide(
            "broom",
            "M13.5 10.5l8.5 -8.5",
            "M14.734 13.841a2 2 0 0-0.314-2.42L12.58 9.58a2 2 0 0-2.421-0.314l-7.657 4.461A1 1 0 2.3 15.3l6.403 6" +
                ".403a1 1 0 1.571-0.204z",
            "M5 18l2 -2",
            "M7.699 10.7l5.602 5.601",
        )
    }

    val Close: ImageVector by lazy {
        lucide(
            "x",
            "M18 6l-12 12",
            "M6 6l12 12",
        )
    }

    val ContentCopy: ImageVector by lazy {
        lucide(
            "clipboard-copy",
            "M9 2H15A1 1 0 0 1 16 3V5A1 1 0 0 1 15 6H9A1 1 0 0 1 8 5V3A1 1 0 0 1 9 2Z",
            "M8 4h-2a2 2 0 0 0 -2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2 -2v-2",
            "M16 4h2a2 2 0 0 1 2 2v4",
            "M21 14h-10",
            "M15 10l-4 4l4 4",
        )
    }

    val Crop: ImageVector by lazy {
        lucide(
            "crop",
            "M6 2v14a2 2 0 0 0 2 2h14",
            "M18 22v-14a2 2 0 0 0 -2 -2h-14",
        )
    }

    val CropFree: ImageVector by lazy {
        lucide(
            "scan",
            "M3 7v-2a2 2 0 0 1 2 -2h2",
            "M17 3h2a2 2 0 0 1 2 2v2",
            "M21 17v2a2 2 0 0 1 -2 2h-2",
            "M7 21h-2a2 2 0 0 1 -2 -2v-2",
        )
    }

    val CropRotate: ImageVector by lazy {
        lucide(
            "rotate-cw",
            "M21 12a9 9 0 1 1 -9 -9c2.52 0 4.93 1 6.74 2.74l2.26 2.26",
            "M21 3v5h-5",
        )
    }

    val DateRange: ImageVector by lazy {
        lucide(
            "calendar-range",
            "M5 3H19A2 2 0 0 1 21 5V19A2 2 0 0 1 19 21H5A2 2 0 0 1 3 19V5A2 2 0 0 1 5 3Z",
            "M16 2v3",
            "M3 9h18",
            "M8 2v3",
            "M17 13h-6",
            "M13 17h-6",
            "M7 13h0.01",
            "M17 17h0.01",
        )
    }

    val Delete: ImageVector by lazy {
        lucide(
            "trash",
            "M10 11v6",
            "M14 11v6",
            "M19 6v14a2 2 0 0 1 -2 2h-10a2 2 0 0 1 -2 -2v-14",
            "M3 6h18",
            "M8 6v-2a2 2 0 0 1 2 -2h4a2 2 0 0 1 2 2v2",
        )
    }

    val Deselect: ImageVector by lazy {
        lucide(
            "square-dashed",
            "M5 3a2 2 0 0 0 -2 2",
            "M19 3a2 2 0 0 1 2 2",
            "M21 19a2 2 0 0 1 -2 2",
            "M5 21a2 2 0 0 1 -2 -2",
            "M9 3h1",
            "M9 21h1",
            "M14 3h1",
            "M14 21h1",
            "M3 9v1",
            "M21 9v1",
            "M3 14v1",
            "M21 14v1",
        )
    }

    val DirectionsWalk: ImageVector by lazy {
        lucide(
            "footprints",
            "M4 16v-2.38C4 11.5 2.97 10.5 3 8c0.03 -2.72 1.49 -6 4.5 -6C9.37 2 10 3.8 10 5.5c0 3.11 -2 5.66 -2 8." +
                "68v1.82a2 2 0 1 1 -4 0z",
            "M20 20v-2.38c0 -2.12 1.03 -3.12 1 -5.62c-0.03 -2.72 -1.49 -6 -4.5 -6C14.63 6 14 7.8 14 9.5c0 3.11 2 " +
                "5.66 2 8.68v1.82a2 2 0 1 0 4 0z",
            "M16 17h4",
            "M4 13h4",
            autoMirror = true,
        )
    }

    val Done: ImageVector by lazy {
        lucide(
            "check",
            "M20 6l-11 11l-5 -5",
        )
    }

    val FilterAlt: ImageVector by lazy {
        lucide(
            "funnel",
            "M10 20a1 1 0 0 0 0.553 0.895l2 1A1 1 0 0 0 14 21v-7a2 2 0 0 1 0.517 -1.341l7.223 -7.989A1 1 0 0 0 21" +
                " 3h-18a1 1 0 0 0 -0.742 1.67l7.225 7.989A2 2 0 0 1 10 14z",
        )
    }

    val FilterAltOff: ImageVector by lazy {
        lucide(
            "funnel-x",
            "M12.531 3h-9.531a1 1 0 0 0 -0.742 1.67l7.225 7.989A2 2 0 0 1 10 14v6a1 1 0 0 0 0.553 0.895l2 1A1 1 0" +
                " 0 0 14 21v-7a2 2 0 0 1 0.517 -1.341l0.427 -0.473",
            "M16.5 3.5l5 5",
            "M21.5 3.5l-5 5",
        )
    }

    val FilterCenterFocus: ImageVector by lazy {
        lucide(
            "crosshair",
            "M2 12A10 10 0 1 0 22 12A10 10 0 1 0 2 12z",
            "M22 12h-4",
            "M6 12h-4",
            "M12 6v-4",
            "M12 22v-4",
        )
    }

    val FitScreen: ImageVector by lazy {
        lucide(
            "fullscreen",
            "M3 7v-2a2 2 0 0 1 2 -2h2",
            "M17 3h2a2 2 0 0 1 2 2v2",
            "M21 17v2a2 2 0 0 1 -2 2h-2",
            "M7 21h-2a2 2 0 0 1 -2 -2v-2",
            "M8 8H16A1 1 0 0 1 17 9V15A1 1 0 0 1 16 16H8A1 1 0 0 1 7 15V9A1 1 0 0 1 8 8Z",
        )
    }

    val FitnessCenter: ImageVector by lazy {
        lucide(
            "dumbbell",
            "M17.596 12.768a2 2 0 1 0 2.829 -2.829l-1.768 -1.767a2 2 0 0 0 2.828 -2.829l-2.828 -2.828a2 2 0 0 0 -" +
                "2.829 2.828l-1.767 -1.768a2 2 0 1 0 -2.829 2.829z",
            "M2.5 21.5l1.4 -1.4",
            "M20.1 3.9l1.4 -1.4",
            "M5.343 21.485a2 2 0 1 0 2.829 -2.828l1.767 1.768a2 2 0 1 0 2.829 -2.829l-6.364 -6.364a2 2 0 1 0 -2.8" +
                "29 2.829l1.768 1.767a2 2 0 0 0 -2.828 2.829z",
            "M9.6 14.4l4.8 -4.8",
        )
    }

    val FolderOpen: ImageVector by lazy {
        lucide(
            "folder-open",
            "M6 14l1.5 -2.9A2 2 0 0 1 9.24 10h10.76a2 2 0 0 1 1.94 2.5l-1.54 6a2 2 0 0 1 -1.95 1.5h-14.45a2 2 0 0" +
                " 1 -2 -2v-13a2 2 0 0 1 2 -2h3.9a2 2 0 0 1 1.69 0.9l0.81 1.2a2 2 0 0 0 1.67 0.9h5.93a2 2 0 0 1 2 2v2",
        )
    }

    val Info: ImageVector by lazy {
        lucide(
            "info",
            "M2 12A10 10 0 1 0 22 12A10 10 0 1 0 2 12z",
            "M12 16v-4",
            "M12 8h0.01",
        )
    }

    val KeyboardArrowDown: ImageVector by lazy {
        lucide(
            "chevron-down",
            "M6 9l6 6l6 -6",
        )
    }

    val KeyboardArrowRight: ImageVector by lazy {
        lucide(
            "chevron-right",
            "M9 18l6 -6l-6 -6",
            autoMirror = true,
        )
    }

    val KeyboardArrowUp: ImageVector by lazy {
        lucide(
            "chevron-up",
            "M18 15l-6 -6l-6 6",
        )
    }

    val List: ImageVector by lazy {
        lucide(
            "list",
            "M3 5h0.01",
            "M3 12h0.01",
            "M3 19h0.01",
            "M8 5h13",
            "M8 12h13",
            "M8 19h13",
            autoMirror = true,
        )
    }

    val Map: ImageVector by lazy {
        lucide(
            "map",
            "M14.106 5.553a2 2 0 0 0 1.788 0l3.659 -1.83A1 1 0 0 1 21 4.619v12.764a1 1 0 0 1 -0.553 0.894l-4.553 " +
                "2.277a2 2 0 0 1 -1.788 0l-4.212 -2.106a2 2 0 0 0 -1.788 0l-3.659 1.83A1 1 0 0 1 3 19.381v-12.763a1 1" +
                " 0 0 1 0.553 -0.894l4.553 -2.277a2 2 0 0 1 1.788 0z",
            "M15 5.764v15",
            "M9 3.236v15",
        )
    }

    val Medication: ImageVector by lazy {
        lucide(
            "pill",
            "M10.5 20.5l10 -10a4.95 4.95 0 1 0 -7 -7l-10 10a4.95 4.95 0 1 0 7 7z",
            "M8.5 8.5l7 7",
        )
    }

    val Menu: ImageVector by lazy {
        lucide(
            "menu",
            "M4 5h16",
            "M4 12h16",
            "M4 19h16",
        )
    }

    val Mic: ImageVector by lazy {
        lucide(
            "mic",
            "M12 19v3",
            "M19 10v2a7 7 0 0 1 -14 0v-2",
            "M12 2H12A3 3 0 0 1 15 5V12A3 3 0 0 1 12 15H12A3 3 0 0 1 9 12V5A3 3 0 0 1 12 2Z",
        )
    }

    val MoreHoriz: ImageVector by lazy {
        lucide(
            "ellipsis",
            "M11 12A1 1 0 1 0 13 12A1 1 0 1 0 11 12z",
            "M18 12A1 1 0 1 0 20 12A1 1 0 1 0 18 12z",
            "M4 12A1 1 0 1 0 6 12A1 1 0 1 0 4 12z",
        )
    }

    val MoreVert: ImageVector by lazy {
        lucide(
            "ellipsis-vertical",
            "M11 12A1 1 0 1 0 13 12A1 1 0 1 0 11 12z",
            "M11 5A1 1 0 1 0 13 5A1 1 0 1 0 11 5z",
            "M11 19A1 1 0 1 0 13 19A1 1 0 1 0 11 19z",
        )
    }

    val Movie: ImageVector by lazy {
        lucide(
            "clapperboard",
            "M12.296 3.464l3.02 3.956",
            "M20.2 6l-17.2 5l-0.9 -2.4c-0.3 -1.1 0.3 -2.2 1.3 -2.5l13.5 -4c1.1 -0.3 2.2 0.3 2.5 1.3z",
            "M3 11h18v8a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2z",
            "M6.18 5.276l3.1 3.899",
        )
    }

    val OpenWith: ImageVector by lazy {
        lucide(
            "move",
            "M12 2v20",
            "M15 19l-3 3l-3 -3",
            "M19 9l3 3l-3 3",
            "M2 12h20",
            "M5 9l-3 3l3 3",
            "M9 5l3 -3l3 3",
        )
    }

    val PhotoCamera: ImageVector by lazy {
        lucide(
            "camera",
            "M13.997 4a2 2 0 0 1 1.76 1.05l0.486 0.9A2 2 0 0 0 18.003 7h1.997a2 2 0 0 1 2 2v9a2 2 0 0 1 -2 2h-16a" +
                "2 2 0 0 1 -2 -2v-9a2 2 0 0 1 2 -2h1.997a2 2 0 0 0 1.759 -1.048l0.489 -0.904A2 2 0 0 1 10.004 4z",
            "M9 13A3 3 0 1 0 15 13A3 3 0 1 0 9 13z",
        )
    }

    val PhotoLibrary: ImageVector by lazy {
        lucide(
            "images",
            "M22 11l-1.296 -1.296a2.4 2.4 0 0 0 -3.408 0l-6.296 6.296",
            "M4 8a2 2 0 0 0 -2 2v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2 -2",
            "M12 7A1 1 0 1 0 14 7A1 1 0 1 0 12 7z",
            "M10 2H20A2 2 0 0 1 22 4V14A2 2 0 0 1 20 16H10A2 2 0 0 1 8 14V4A2 2 0 0 1 10 2Z",
        )
    }

    val Place: ImageVector by lazy {
        lucide(
            "map-pin",
            "M20 10c0 4.993 -5.539 10.193 -7.399 11.799a1 1 0 0 1 -1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 1" +
                "6 0",
            "M9 10A3 3 0 1 0 15 10A3 3 0 1 0 9 10z",
        )
    }

    val PlayArrow: ImageVector by lazy {
        lucide(
            "play",
            "M5 5a2 2 0 0 1 3.008 -1.728l11.997 6.998a2 2 0 0 1 0.003 3.458l-12 7A2 2 0 0 1 5 19z",
        )
    }

    val Refresh: ImageVector by lazy {
        lucide(
            "refresh-cw",
            "M3 12a9 9 0 0 1 9 -9a9.75 9.75 0 0 1 6.74 2.74l2.26 2.26",
            "M21 3v5h-5",
            "M21 12a9 9 0 0 1 -9 9a9.75 9.75 0 0 1 -6.74 -2.74l-2.26 -2.26",
            "M8 16h-5v5",
        )
    }

    val Reply: ImageVector by lazy {
        lucide(
            "reply",
            "M20 18v-2a4 4 0 0 0 -4 -4h-12",
            "M9 17l-5 -5l5 -5",
            autoMirror = true,
        )
    }

    val RestartAlt: ImageVector by lazy {
        lucide(
            "rotate-ccw",
            "M3 12a9 9 0 1 0 9 -9a9.75 9.75 0 0 0 -6.74 2.74l-2.26 2.26",
            "M3 3v5h5",
        )
    }

    val Rotate90DegreesCcw: ImageVector by lazy {
        lucide(
            "rotate-ccw",
            "M3 12a9 9 0 1 0 9 -9a9.75 9.75 0 0 0 -6.74 2.74l-2.26 2.26",
            "M3 3v5h5",
        )
    }

    val Rotate90DegreesCw: ImageVector by lazy {
        lucide(
            "rotate-cw",
            "M21 12a9 9 0 1 1 -9 -9c2.52 0 4.93 1 6.74 2.74l2.26 2.26",
            "M21 3v5h-5",
        )
    }

    val Save: ImageVector by lazy {
        lucide(
            "save",
            "M15.2 3a2 2 0 0 1 1.4 0.6l3.8 3.8a2 2 0 0 1 0.6 1.4v10.2a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2v-14a2 2 " +
                "0 0 1 2 -2z",
            "M17 21v-7a1 1 0 0 0 -1 -1h-8a1 1 0 0 0 -1 1v7",
            "M7 3v4a1 1 0 0 0 1 1h7",
        )
    }

    val SaveAs: ImageVector by lazy {
        lucide(
            "save",
            "M15.2 3a2 2 0 0 1 1.4 0.6l3.8 3.8a2 2 0 0 1 0.6 1.4v10.2a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2v-14a2 2 " +
                "0 0 1 2 -2z",
            "M17 21v-7a1 1 0 0 0 -1 -1h-8a1 1 0 0 0 -1 1v7",
            "M7 3v4a1 1 0 0 0 1 1h7",
        )
    }

    val ScreenLockRotation: ImageVector by lazy {
        lucide(
            "rotate-ccw-key",
            "M12 7v6",
            "M12 9h2",
            "M3 12a9 9 0 1 0 9 -9a9.74 9.74 0 0 0 -6.74 2.74l-2.26 2.26",
            "M3 3v5h5",
            "M10 15A2 2 0 1 0 14 15A2 2 0 1 0 10 15z",
        )
    }

    val Search: ImageVector by lazy {
        lucide(
            "search",
            "M21 21l-4.34 -4.34",
            "M3 11A8 8 0 1 0 19 11A8 8 0 1 0 3 11z",
        )
    }

    val Security: ImageVector by lazy {
        lucide(
            "shield",
            "M20 13c0 5 -3.5 7.5 -7.66 8.95a1 1 0 0 1 -0.67 -0.01C7.5 20.5 4 18 4 13v-7a1 1 0 0 1 1 -1c2 0 4.5 -1" +
                ".2 6.24 -2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z",
        )
    }

    val SelectAll: ImageVector by lazy {
        lucide(
            "square-check",
            "M5 3H19A2 2 0 0 1 21 5V19A2 2 0 0 1 19 21H5A2 2 0 0 1 3 19V5A2 2 0 0 1 5 3Z",
            "M16 9l-5.5 5.5l-2.5 -2.5",
        )
    }

    val Settings: ImageVector by lazy {
        lucide(
            "settings",
            "M9.671 4.136a2.34 2.34 0 0 1 4.659 0a2.34 2.34 0 0 0 3.319 1.915a2.34 2.34 0 0 1 2.33 4.033a2.34 2.3" +
                "4 0 0 0 0 3.831a2.34 2.34 0 0 1 -2.33 4.033a2.34 2.34 0 0 0 -3.319 1.915a2.34 2.34 0 0 1 -4.659 0a2." +
                "34 2.34 0 0 0 -3.32 -1.915a2.34 2.34 0 0 1 -2.33 -4.033a2.34 2.34 0 0 0 0 -3.831A2.34 2.34 0 0 1 6.3" +
                "5 6.051a2.34 2.34 0 0 0 3.319 -1.915",
            "M9 12A3 3 0 1 0 15 12A3 3 0 1 0 9 12z",
        )
    }

    val Share: ImageVector by lazy {
        lucide(
            "share-2",
            "M15 5A3 3 0 1 0 21 5A3 3 0 1 0 15 5z",
            "M3 12A3 3 0 1 0 9 12A3 3 0 1 0 3 12z",
            "M15 19A3 3 0 1 0 21 19A3 3 0 1 0 15 19z",
            "M8.59 13.51l6.83 3.98",
            "M15.41 6.51l-6.82 3.98",
        )
    }

    val ShortText: ImageVector by lazy {
        lucide(
            "text",
            "M21 5h-18",
            "M15 12h-12",
            "M17 19h-14",
            autoMirror = true,
        )
    }

    val SkipNext: ImageVector by lazy {
        lucide(
            "skip-forward",
            "M21 4v16",
            "M6.029 4.285A2 2 0 0 0 3 6v12a2 2 0 0 0 3.029 1.715l9.997 -5.998a2 2 0 0 0 0.003 -3.432z",
        )
    }

    val Star: ImageVector by lazy {
        lucide(
            "star",
            "M11.525 2.295a0.53 0.53 0 0 1 0.95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166 0.756a0.53 0.53 0" +
                " 0 1 0.294 0.904l-3.736 3.638a2.123 2.123 0 0 0 -0.611 1.878l0.882 5.14a0.53 0.53 0 0 1 -0.771 0.56l" +
                "-4.618 -2.428a2.122 2.122 0 0 0 -1.973 0l-4.617 2.428a0.53 0.53 0 0 1 -0.77 -0.56l0.881 -5.139a2.122" +
                " 2.122 0 0 0 -0.611 -1.879l-3.736 -3.637a0.53 0.53 0 0 1 0.294 -0.906l5.165 -0.755a2.122 2.122 0 0 0" +
                " 1.597 -1.16z",
        )
    }

    val Stop: ImageVector by lazy {
        lucide(
            "square-stop",
            "M5 3H19A2 2 0 0 1 21 5V19A2 2 0 0 1 19 21H5A2 2 0 0 1 3 19V5A2 2 0 0 1 5 3Z",
            "M10 9H14A1 1 0 0 1 15 10V14A1 1 0 0 1 14 15H10A1 1 0 0 1 9 14V10A1 1 0 0 1 10 9Z",
        )
    }

    val TaskAlt: ImageVector by lazy {
        lucide(
            "circle-check",
            "M2 12A10 10 0 1 0 22 12A10 10 0 1 0 2 12z",
            "M16 9l-5.5 5.5l-2.5 -2.5",
        )
    }

    val Today: ImageVector by lazy {
        lucide(
            "calendar-check",
            "M8 2v3",
            "M16 2v3",
            "M5 3H19A2 2 0 0 1 21 5V19A2 2 0 0 1 19 21H5A2 2 0 0 1 3 19V5A2 2 0 0 1 5 3Z",
            "M3 9h18",
            "M9 15l2 2l4 -4",
        )
    }

    val Transform: ImageVector by lazy {
        lucide(
            "scaling",
            "M12 3h-7a2 2 0 0 0 -2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2 -2v-7",
            "M14 15h-5v-5",
            "M16 3h5v5",
            "M21 3l-12 12",
        )
    }

    val Undo: ImageVector by lazy {
        lucide(
            "undo-2",
            "M9 14l-5 -5l5 -5",
            "M4 9h10.5a5.5 5.5 0 0 1 5.5 5.5a5.5 5.5 0 0 1 -5.5 5.5h-3.5",
            autoMirror = true,
        )
    }

    val UploadFile: ImageVector by lazy {
        lucide(
            "upload",
            "M12 3v12",
            "M17 8l-5 -5l-5 5",
            "M21 15v4a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2v-4",
        )
    }

    val VideoLibrary: ImageVector by lazy {
        lucide(
            "library",
            "M16 6l4 14",
            "M12 6v14",
            "M8 8v12",
            "M4 4v16",
        )
    }

    val Videocam: ImageVector by lazy {
        lucide(
            "video",
            "M16 13l5.223 3.482a0.5 0.5 0 0 0 0.777 -0.416v-8.196a0.5 0.5 0 0 0 -0.752 -0.432l-5.248 3.062",
            "M4 6H14A2 2 0 0 1 16 8V16A2 2 0 0 1 14 18H4A2 2 0 0 1 2 16V8A2 2 0 0 1 4 6Z",
        )
    }

    val Visibility: ImageVector by lazy {
        lucide(
            "eye",
            "M2.062 12.348a1 1 0 0 1 0 -0.696a10.75 10.75 0 0 1 19.876 0a1 1 0 0 1 0 0.696a10.75 10.75 0 0 1 -19." +
                "876 0",
            "M9 12A3 3 0 1 0 15 12A3 3 0 1 0 9 12z",
        )
    }

    val VisibilityOff: ImageVector by lazy {
        lucide(
            "eye-off",
            "M10.733 5.076a10.744 10.744 0 0 1 11.205 6.575a1 1 0 0 1 0 0.696a10.747 10.747 0 0 1 -1.444 2.49",
            "M14.084 14.158a3 3 0 0 1 -4.242 -4.242",
            "M17.479 17.499a10.75 10.75 0 0 1 -15.417 -5.151a1 1 0 0 1 0 -0.696a10.75 10.75 0 0 1 4.446 -5.143",
            "M2 2l20 20",
        )
    }
}

private fun lucide(
    name: String,
    vararg paths: String,
    autoMirror: Boolean = false,
): ImageVector = ImageVector.Builder(
    name = name,
    defaultWidth = 24.dp,
    defaultHeight = 24.dp,
    viewportWidth = 24f,
    viewportHeight = 24f,
    autoMirror = autoMirror,
).apply {
    val stroke = SolidColor(Color.Black)
    paths.forEach { data ->
        addPath(
            pathData = PathParser().parsePathString(data).toNodes(),
            stroke = stroke,
            strokeLineWidth = 2f,
            strokeLineCap = StrokeCap.Round,
            strokeLineJoin = StrokeJoin.Round,
        )
    }
}.build()
