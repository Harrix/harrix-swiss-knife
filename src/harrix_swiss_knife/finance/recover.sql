CREATE TABLE "currencies" (
    "_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "code" TEXT NOT NULL UNIQUE,
    "name" TEXT NOT NULL,
    "symbol" TEXT NOT NULL,
    "subdivision" INTEGER NOT NULL DEFAULT 100
);

CREATE TABLE "settings" (
    "_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "key" TEXT NOT NULL UNIQUE,
    "value" TEXT NOT NULL
);

CREATE TABLE "exchange_rates" (
    "_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "_id_currency_from" INTEGER NOT NULL,
    "_id_currency_to" INTEGER NOT NULL,
    "rate" INTEGER NOT NULL,
    "date" TEXT NOT NULL,
    FOREIGN KEY("_id_currency_from") REFERENCES "currencies"("_id"),
    FOREIGN KEY("_id_currency_to") REFERENCES "currencies"("_id")
);

CREATE TABLE "categories" (
	"_id"	INTEGER,
	"name"	TEXT NOT NULL,
	"type"	INTEGER NOT NULL,
	"icon"	TEXT,
	PRIMARY KEY("_id" AUTOINCREMENT)
);

CREATE TABLE "accounts" (
    "_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "name" TEXT NOT NULL UNIQUE,
    "balance" INTEGER NOT NULL DEFAULT 0,
    "_id_currencies" INTEGER NOT NULL,
    "is_liquid" INTEGER NOT NULL DEFAULT 1,
    "is_cash" INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY("_id_currencies") REFERENCES "currencies"("_id")
);

CREATE TABLE "transactions" (
	"_id"	INTEGER,
	"amount"	INTEGER NOT NULL,
	"description"	TEXT NOT NULL,
	"_id_categories"	INTEGER NOT NULL,
	"_id_currencies"	INTEGER NOT NULL,
	"date"	TEXT NOT NULL,
	"tag"	TEXT,
	PRIMARY KEY("_id" AUTOINCREMENT),
	FOREIGN KEY("_id_categories") REFERENCES "categories"("_id"),
	FOREIGN KEY("_id_currencies") REFERENCES "currencies"("_id")
);

CREATE TABLE "currency_exchanges" (
    "_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "_id_currency_from" INTEGER NOT NULL,
    "_id_currency_to" INTEGER NOT NULL,
    "amount_from" INTEGER NOT NULL,
    "amount_to" INTEGER NOT NULL,
    "exchange_rate" INTEGER NOT NULL,
    "fee" INTEGER DEFAULT 0,
    "date" TEXT NOT NULL,
    "description" TEXT,
    FOREIGN KEY("_id_currency_from") REFERENCES "currencies"("_id"),
    FOREIGN KEY("_id_currency_to") REFERENCES "currencies"("_id")
);


INSERT INTO currencies (code, name, symbol, subdivision) VALUES ('RUB', 'Russian Ruble', '₽', 100);
INSERT INTO currencies (code, name, symbol, subdivision) VALUES ('USD', 'US Dollar', '$', 100);
INSERT INTO currencies (code, name, symbol, subdivision) VALUES ('EUR', 'Euro', '€', 100);
INSERT INTO currencies (code, name, symbol, subdivision) VALUES ('CNY', 'Chinese Yuan', '¥', 100);

INSERT INTO categories (name, type, icon) VALUES ('Salary', 1, "💰");
INSERT INTO categories (name, type, icon) VALUES ('Food', 0, "🍔");
INSERT INTO categories (name, type, icon) VALUES ('Transport', 0, "🚗");

INSERT INTO accounts (name, _id_currencies, balance, is_liquid, is_cash) VALUES ('Cash', 1, 0, 1, 1);
INSERT INTO accounts (name, _id_currencies, balance, is_liquid, is_cash) VALUES ('Bank Account', 1, 0, 1, 0);

INSERT INTO settings (key, value) VALUES ('default_currency', 'RUB');
