CREATE TABLE "songs" (
	"_id" INTEGER NOT NULL,
	"level_id" TEXT NOT NULL UNIQUE,
	"title" TEXT NOT NULL,
	"pack" TEXT NOT NULL DEFAULT '',
	"is_official" INTEGER NOT NULL DEFAULT 1,
	PRIMARY KEY("_id" AUTOINCREMENT)
);

CREATE TABLE "song_modes" (
	"_id" INTEGER NOT NULL,
	"level_id" TEXT NOT NULL,
	"characteristic" TEXT NOT NULL DEFAULT 'Standard',
	"difficulty" INTEGER NOT NULL,
	PRIMARY KEY("_id" AUTOINCREMENT),
	UNIQUE("level_id", "characteristic", "difficulty")
);

CREATE TABLE "sync_runs" (
	"_id" INTEGER NOT NULL,
	"source" TEXT NOT NULL,
	"observed_at" TEXT NOT NULL,
	"backup_path" TEXT,
	"note" TEXT NOT NULL DEFAULT '',
	PRIMARY KEY("_id" AUTOINCREMENT)
);

CREATE TABLE "clears_current" (
	"_id" INTEGER NOT NULL,
	"level_id" TEXT NOT NULL,
	"characteristic" TEXT NOT NULL DEFAULT 'Standard',
	"difficulty" INTEGER NOT NULL,
	"source" TEXT NOT NULL,
	"max_rank" INTEGER NOT NULL DEFAULT 0,
	"rank_name" TEXT NOT NULL DEFAULT '',
	"full_combo" INTEGER NOT NULL DEFAULT 0,
	"high_score" INTEGER NOT NULL DEFAULT 0,
	"play_count" INTEGER NOT NULL DEFAULT 0,
	"observed_at" TEXT NOT NULL,
	"sync_run_id" INTEGER,
	PRIMARY KEY("_id" AUTOINCREMENT),
	UNIQUE("level_id", "characteristic", "difficulty", "source")
);

CREATE TABLE "clears_history" (
	"_id" INTEGER NOT NULL,
	"level_id" TEXT NOT NULL,
	"characteristic" TEXT NOT NULL DEFAULT 'Standard',
	"difficulty" INTEGER NOT NULL,
	"source" TEXT NOT NULL,
	"max_rank" INTEGER NOT NULL DEFAULT 0,
	"rank_name" TEXT NOT NULL DEFAULT '',
	"full_combo" INTEGER NOT NULL DEFAULT 0,
	"high_score" INTEGER NOT NULL DEFAULT 0,
	"play_count" INTEGER NOT NULL DEFAULT 0,
	"observed_at" TEXT NOT NULL,
	"sync_run_id" INTEGER,
	PRIMARY KEY("_id" AUTOINCREMENT)
);

CREATE INDEX "idx_clears_current_source" ON "clears_current" ("source");
CREATE INDEX "idx_clears_current_level" ON "clears_current" ("level_id");
CREATE INDEX "idx_clears_history_observed" ON "clears_history" ("observed_at");
CREATE INDEX "idx_song_modes_level" ON "song_modes" ("level_id");
