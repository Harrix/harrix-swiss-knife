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
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Crosspack', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Dropbox', NULL, _id FROM categories WHERE name = 'IT';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Oculus', NULL, _id FROM categories WHERE name = 'IT';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Orbit', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Schesir', NULL, _id FROM categories WHERE name = 'Pet Care';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Автобус', 'Bus', _id FROM categories WHERE name = 'Transport';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Аптека', 'Pharmacy', _id FROM categories WHERE name = 'Healthcare';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Бананы', 'Bananas', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Банк Москва', NULL, _id FROM categories WHERE name = 'Salary';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Баунти', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Бензин', 'Gasoline', _id FROM categories WHERE name = 'Transport';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Биойгурт', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Биойогурт', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Бургер', 'Burger', _id FROM categories WHERE name = 'Cafe';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Вафли', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Велосипед', NULL, _id FROM categories WHERE name = 'Sports';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Ветчина', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Вкусвилл', 'Vkusvill', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Вкусно и точка', NULL, _id FROM categories WHERE name = 'Cafe';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Вода', 'Drinking water', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Вода Святой Источник питьевая негазированная 6*1.5л', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Газировка', 'Soda', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Горошек', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Губки', NULL, _id FROM categories WHERE name = 'Household Goods';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Гурме', 'Gourmet cat food', _id FROM categories WHERE name = 'Pet Care';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Гурмет', 'Gourmet', _id FROM categories WHERE name = 'Pet Care';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Десерт творожный', 'Curd dessert', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Дирол', 'Dirol gum', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Для мытья посуды', NULL, _id FROM categories WHERE name = 'Household Goods';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Дримис', NULL, _id FROM categories WHERE name = 'Pet Care';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Еда', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Жевательная резинка Dirol Colors XXL ассорти мятных вкусов 19г', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Жевательная резинка Dirol Мята и мелисса 13.6г', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Зарплата', 'Salary', _id FROM categories WHERE name = 'Salary';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Зелень', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Зубная паста', 'Toothpaste', _id FROM categories WHERE name = 'Household Goods';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Интернет', 'Internet', _id FROM categories WHERE name = 'Utilities';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Йогурт', 'Yogurt', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Капуста', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Картофель', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Кафе', 'Cafe', _id FROM categories WHERE name = 'Cafe';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Квартплата', 'Rent / utilities', _id FROM categories WHERE name = 'Utilities';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Кетчуп', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Кефир', 'Kefir', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Кино', 'Cinema', _id FROM categories WHERE name = 'Tickets';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Книга', 'Book', _id FROM categories WHERE name = 'Books';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Кока-кола', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Кока-кола зеро', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Коктейль молочный', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Кола', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Колбаса', 'Sausage', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Кондиционер для белья', NULL, _id FROM categories WHERE name = 'Household Goods';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Конфеты', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Корм', 'Pet food', _id FROM categories WHERE name = 'Pet Care';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Корнишоны', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Котлета куриная с картофельным пюре', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Котлеты', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Кофе', 'Coffee', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Красный крест', NULL, _id FROM categories WHERE name = 'Utilities';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Кредит', NULL, _id FROM categories WHERE name = 'Repayment/Debt';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Кукуруза', 'Corn', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Курица', 'Chicken', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Лекарства', 'Medicine', _id FROM categories WHERE name = 'Healthcare';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Лук', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Майонез', 'Mayonnaise', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Маникюр', 'Manicure', _id FROM categories WHERE name = 'Beauty Services';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Метро', 'Metro', _id FROM categories WHERE name = 'Transport';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Мичурина 5в', NULL, _id FROM categories WHERE name = 'Utilities';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Мобильный банк Сбербанк', 'Sberbank mobile bank', _id FROM categories WHERE name = 'Utilities';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Молоко', 'Milk', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Молоко Parmalat Natura Premium ультрапастеризованное 3.5% 1л', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Молоко топленое', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Морковь', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Мороженое', 'Ice cream', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Мыло', 'Soap', _id FROM categories WHERE name = 'Household Goods';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Напиток Evervess Кола без сахара 2л', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Напиток Добрый Кола без сахара 1.5л', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Напиток Калинов Лимонад Классический вкус Апельсина газированный 1.5л', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Напиток Калинов Лимонад Классический Тархун газированный 1.5л', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Напиток сыворочный', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Наполнитель', NULL, _id FROM categories WHERE name = 'Pet Care';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Наполнитель для кошачьего туалета Барсик впитывающий 15л', NULL, _id FROM categories WHERE name = 'Pet Care';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Нектар', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Обед', 'Lunch', _id FROM categories WHERE name = 'Cafe';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Огурцы', 'Cucumbers', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Огурцы маринованные', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Омичка', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Орбит', 'Orbit gum', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Отель', 'Hotel', _id FROM categories WHERE name = 'Hotels';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Пакет', 'Plastic bag', _id FROM categories WHERE name = 'Household Goods';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Пакет-майка "Вкусвилл" малый', NULL, _id FROM categories WHERE name = 'Household Goods';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Пакеты', NULL, _id FROM categories WHERE name = 'Household Goods';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Парикмахерская', 'Hairdresser', _id FROM categories WHERE name = 'Beauty Services';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Парковка', 'Parking', _id FROM categories WHERE name = 'Transport';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Пельменная', NULL, _id FROM categories WHERE name = 'Cafe';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Пепси', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Петрушка', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Печенье', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Пицца', 'Pizza', _id FROM categories WHERE name = 'Cafe';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Подарок', 'Gift', _id FROM categories WHERE name = 'Gifts';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Помидоры', 'Tomatoes', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Порошок', NULL, _id FROM categories WHERE name = 'Household Goods';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Приправа', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Продажа', 'Sale', _id FROM categories WHERE name = 'Sales';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Продукт творожный', 'Curd product', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Продукт творожный Даниссимо с апельсином и шоколадной крошкой 5.8% 130г', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Продукт творожный Даниссимо со вкусом Фисташковое мороженое 6.5% 130г', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Продукт творожный Даниссимо Черника 5.5% 130г', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Продукты', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Пудинг', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Репетитерство', NULL, _id FROM categories WHERE name = 'Freelance';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Ресторан', 'Restaurant', _id FROM categories WHERE name = 'Cafe';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Роллы', 'Sushi rolls', _id FROM categories WHERE name = 'Cafe';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Салат', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Салат "Коул Слоу" постный', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Салат в горшочке', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Салат листовой', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Салфетки влажные', 'Wet wipes', _id FROM categories WHERE name = 'Household Goods';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Сахар', 'Sugar', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Сбербанк', 'Sberbank', _id FROM categories WHERE name = 'Salary';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Сгущенка', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Северный', NULL, _id FROM categories WHERE name = 'Freelance';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Сервелат', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Сливки', 'Cream', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Сливки Домик в деревне 20% 480г', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Сливки Домик в деревне 20% 480мл', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Сметана', 'Sour cream', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Сок', 'Juice', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Спортзал', 'Gym', _id FROM categories WHERE name = 'Sports';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Столовая', 'Cafeteria', _id FROM categories WHERE name = 'Cafe';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Стрижка', NULL, _id FROM categories WHERE name = 'Beauty Services';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Суши', 'Sushi', _id FROM categories WHERE name = 'Cafe';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Сыр', 'Cheese', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Сырок', 'Glazed curd bar', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Такси', 'Taxi', _id FROM categories WHERE name = 'Transport';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Тархун', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Творог', 'Cottage cheese', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Творог Село Зеленое 5% 200г', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Творожок', 'Curd snack', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Телефон', NULL, _id FROM categories WHERE name = 'Utilities';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Телефон + интернет', NULL, _id FROM categories WHERE name = 'Utilities';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Тепсей', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Теремок', NULL, _id FROM categories WHERE name = 'Cafe';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Тизин', NULL, _id FROM categories WHERE name = 'Healthcare';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Томаты', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Трамвай', 'Tram', _id FROM categories WHERE name = 'Transport';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Троллейбус', 'Trolleybus', _id FROM categories WHERE name = 'Transport';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Туалет', NULL, _id FROM categories WHERE name = 'Services';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Туалетная бумага', 'Toilet paper', _id FROM categories WHERE name = 'Household Goods';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Укроп', 'Dill', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Фанта', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Фарш куриный', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Фриланс', 'Freelance', _id FROM categories WHERE name = 'Freelance';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Хлеб', 'Bread', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Цветы', 'Flowers', _id FROM categories WHERE name = 'Gifts';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Чаевые', 'Tips', _id FROM categories WHERE name = 'Services';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Чай', 'Tea', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Чеснок', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Чипсы', 'Chips', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Шампунь', 'Shampoo', _id FROM categories WHERE name = 'Household Goods';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Шаурма', 'Shawarma', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Шашлык', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Шеба', 'Sheba', _id FROM categories WHERE name = 'Pet Care';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Шефмаркет', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Школа 1532', 'School 1532', _id FROM categories WHERE name = 'Salary';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Школа 2103', NULL, _id FROM categories WHERE name = 'Salary';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Шницель с пюре', NULL, _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Шоколад', 'Chocolate', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Электричество', 'Electricity', _id FROM categories WHERE name = 'Utilities';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Яблоки', 'Apples', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Яйцо', 'Egg', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Яндекс кошелек', NULL, _id FROM categories WHERE name = 'IT';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Яндекс лавка', 'Yandex Lavka', _id FROM categories WHERE name = 'Food';
INSERT INTO standard_items (name, name_en, _id_categories) SELECT 'Яндекс плюс', NULL, _id FROM categories WHERE name = 'IT';
-- End standard_items seed

INSERT INTO settings (key, value) VALUES ('default_currency', '1');
