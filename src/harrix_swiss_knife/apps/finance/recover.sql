CREATE TABLE "currencies" (
    "_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "code" TEXT NOT NULL UNIQUE,
    "name" TEXT NOT NULL,
    "symbol" TEXT NOT NULL,
    "subdivision" INTEGER NOT NULL DEFAULT 100,
    "ticker" TEXT
);

CREATE TABLE "settings" (
    "_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "key" TEXT NOT NULL UNIQUE,
    "value" TEXT NOT NULL
);

CREATE TABLE "exchange_rates" (
    "_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "_id_currency" INTEGER NOT NULL,
    "rate" REAL NOT NULL,
    "date" TEXT NOT NULL,
    FOREIGN KEY("_id_currency") REFERENCES "currencies"("_id")
);

CREATE TABLE "categories" (
	"_id"	INTEGER,
	"name"	TEXT NOT NULL,
	"type"	INTEGER NOT NULL,
	"icon"	TEXT,
	"name_local"	TEXT,
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
	"description_en"	TEXT,
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
    "exchange_rate" REAL NOT NULL,
    "fee" INTEGER DEFAULT 0,
    "date" TEXT NOT NULL,
    "description" TEXT,
    FOREIGN KEY("_id_currency_from") REFERENCES "currencies"("_id"),
    FOREIGN KEY("_id_currency_to") REFERENCES "currencies"("_id")
);

CREATE TABLE "standard_items" (
    "_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "name" TEXT NOT NULL UNIQUE,
    "name_en" TEXT,
    "_id_categories" INTEGER NOT NULL,
    FOREIGN KEY("_id_categories") REFERENCES "categories"("_id")
);

CREATE INDEX IF NOT EXISTS idx_standard_items_name ON standard_items(name);


INSERT INTO currencies (code, name, symbol, subdivision) VALUES ('RUB', 'Russian Ruble', '₽', 100);
INSERT INTO currencies (code, name, symbol, subdivision) VALUES ('USD', 'US Dollar', '$', 100);
INSERT INTO currencies (code, name, symbol, subdivision) VALUES ('EUR', 'Euro', '€', 100);
INSERT INTO currencies (code, name, symbol, subdivision) VALUES ('CNY', 'Chinese Yuan', '¥', 100);

INSERT INTO categories (name, type, icon, name_local) VALUES ('Appliances', 0, "🔌", 'Бытовая техника');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Beauty Services', 0, "💄", 'Красота');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Books', 0, "📖", 'Книги');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Cafe', 0, "☕", 'Кафе');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Clothing', 0, "👕", 'Одежда');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Education', 0, "📚", 'Образование');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Food', 0, "🍔", 'Еда');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Furniture', 0, "🪑", 'Мебель');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Gifts', 0, "🎁", 'Подарки');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Healthcare', 0, "🏥", 'Здоровье');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Hotels', 0, "🏨", 'Отели');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Household Goods', 0, "🏠", 'Хозтовары');
INSERT INTO categories (name, type, icon, name_local) VALUES ('IT', 0, "💻", 'IT');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Miscellaneous', 0, "❓", 'Разное');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Personal', 0, "👤", 'Личное');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Pet Care', 0, "🐕", 'Питомцы');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Repayment/Debt', 0, "💳", 'Погашение долга');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Revision Expense', 0, "🧾", 'Корректировка расхода');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Services', 0, "🔧", 'Услуги');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Sports', 0, "⚽", 'Спорт');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Stationery', 0, "✏️", 'Канцтовары');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Tickets', 0, "🎫", 'Билеты');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Toys', 0, "🧸", 'Игрушки');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Transport', 0, "🚗", 'Транспорт');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Utilities', 0, "⚡", 'Коммунальные');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Contribution', 1, "🤝", 'Взнос');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Credit', 1, "💳", 'Кредит');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Debt Recovery', 1, "↩️", 'Возврат долга');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Freelance', 1, "💼", 'Фриланс');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Gifts me', 1, "🎉", 'Подарки мне');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Initial Capital', 1, "🏛️", 'Начальный капитал');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Personal Loan', 1, "👥", 'Личный займ');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Revision Income', 1, "🧾", 'Корректировка дохода');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Salary', 1, "💰", 'Зарплата');
INSERT INTO categories (name, type, icon, name_local) VALUES ('Sales', 1, "🛍️", 'Продажи');

INSERT INTO accounts (name, _id_currencies, balance, is_liquid, is_cash) VALUES ('Cash', 1, 0, 1, 1);
INSERT INTO accounts (name, _id_currencies, balance, is_liquid, is_cash) VALUES ('Bank Account', 1, 0, 1, 0);

-- Seed standard_items catalog
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Автобус', 'Bus', _id FROM categories WHERE name = 'Transport';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Аптека', 'Pharmacy', _id FROM categories WHERE name = 'Healthcare';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Вода', 'Drinking water', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Зарплата', 'Salary', _id FROM categories WHERE name = 'Salary';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Квартплата', 'Rent / utilities', _id FROM categories WHERE name = 'Utilities';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Лекарства', 'Medicine', _id FROM categories WHERE name = 'Healthcare';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Метро', 'Metro', _id FROM categories WHERE name = 'Transport';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Подарок', 'Gift', _id FROM categories WHERE name = 'Gifts';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Продажа', 'Sale', _id FROM categories WHERE name = 'Sales';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Репетитерство', 'Tutoring', _id FROM categories WHERE name = 'Freelance';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Такси', 'Taxi', _id FROM categories WHERE name = 'Transport';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Туалет', 'Toilet', _id FROM categories WHERE name = 'Services';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Чаевые', 'Tips', _id FROM categories WHERE name = 'Services';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Чаевые курьеру', 'Tip for courier', _id FROM categories WHERE name = 'Services';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Чаевые таксисту', 'Tip for taxi driver', _id FROM categories WHERE name = 'Transport';
-- End standard_items seed

INSERT INTO settings (key, value) VALUES ('default_currency', '1');
