-- Recover / recreate Media Sorter database schema

PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS deleted_files;
DROP TABLE IF EXISTS bin_assignments;
DROP TABLE IF EXISTS reviewed_files;

PRAGMA foreign_keys = ON;

CREATE TABLE reviewed_files (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL UNIQUE,
    reviewed_at TEXT NOT NULL,
    size INTEGER,
    mtime REAL
);

CREATE TABLE bin_assignments (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL,
    bin_id TEXT NOT NULL,
    dest_path TEXT NOT NULL,
    mode TEXT NOT NULL CHECK (mode IN ('copy', 'move')),
    assigned_at TEXT NOT NULL,
    UNIQUE (path, bin_id)
);

CREATE TABLE deleted_files (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL,
    deleted_at TEXT NOT NULL,
    size INTEGER
);

CREATE INDEX idx_bin_assignments_path ON bin_assignments (path);
CREATE INDEX idx_reviewed_files_path ON reviewed_files (path);
