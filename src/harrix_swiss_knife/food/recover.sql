CREATE TABLE "food_items" (
	"_id"	INTEGER,
	"name"	TEXT NOT NULL,
	"name_en"	TEXT,
	"is_drink"	INTEGER NOT NULL DEFAULT 0,
	"calories_per_100g"	REAL DEFAULT NULL,
	"default_portion_weight"	INTEGER DEFAULT NULL,
	"default_portion_calories"	REAL DEFAULT NULL,
	PRIMARY KEY("_id" AUTOINCREMENT)
);

CREATE TABLE "food_log" (
	"_id"	INTEGER,
	"date"	TEXT,
	"weight"	INTEGER DEFAULT NULL,
	"portion_calories"	REAL DEFAULT NULL,
	"calories_per_100g"	REAL DEFAULT NULL,
	"name"	TEXT DEFAULT NULL,
	"name_en"	TEXT DEFAULT NULL,
	"is_drink"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("_id" AUTOINCREMENT)
);

INSERT INTO food_items (name, name_en, is_drink, calories_per_100g, default_portion_weight, default_portion_calories) VALUES
('Абрикос', 'Apricot', 0, 48, NULL, NULL),
('Ананас', 'Pineapple', 0, 50, NULL, NULL),
('Апельсин', 'Orange', 0, 43, NULL, NULL),
('Арахис', 'Peanuts', 0, 567, NULL, NULL),
('Арбуз', 'Watermelon', 0, 30, NULL, NULL),
('Базилик', 'Basil', 0, 22, NULL, NULL),
('Банан', 'Banana', 0, 89, NULL, NULL),
('Бекон жареный', 'Fried bacon', 0, 468, NULL, NULL),
('Борщ', 'Borscht', 0, 49, NULL, NULL),
('Виноград кишмиш белый', 'White grapes', 0, 40, NULL, NULL),
('Глинтвейн', 'Mulled wine', 1, 132, NULL, NULL),
('Говядина', 'Beef', 0, 250, NULL, NULL),
('Говядина вареная', 'Boiled beef', 0, 254, NULL, NULL),
('Голубика', 'Blueberry', 0, 57, NULL, NULL),
('Горошек', 'Peas', 0, 50, NULL, NULL),
('Грейпфрут', 'Grapefruit', 0, 42, NULL, NULL),
('Гречка вареная', 'Boiled buckwheat', 0, 88, NULL, NULL),
('Груша', 'Pear', 0, 57, NULL, NULL),
('Дыня Колхозница', 'Kolkhoznitsa melon', 0, 39, NULL, NULL),
('Дыня Торпеда', 'Torpedo melon', 0, 34, NULL, NULL),
('Жаркое с курицей', 'Chicken stew', 0, 113, NULL, NULL),
('Жимолость', 'Honeysuckle', 0, 30, NULL, NULL),
('Зефир в шоколаде', 'Chocolate marshmallow', 0, 396, 30, NULL),
('Индейка вареная', 'Boiled turkey', 0, 130, NULL, NULL),
('Кабачок', 'Zucchini', 0, 24, NULL, NULL),
('Какао порошок', 'Cocoa powder', 0, 228, NULL, NULL),
('Капуста', 'Cabbage', 0, 25, NULL, NULL),
('Капуста краснокочанная', 'Red cabbage', 0, 31, NULL, NULL),
('Картофельное пюре', 'Mashed potatoes', 0, 88, NULL, NULL),
('Картошка', 'Potatoes', 0, 77, NULL, NULL),
('Картошка вареная', 'Boiled potatoes', 0, 82, NULL, NULL),
('Киви', 'Kiwi', 0, 61, NULL, NULL),
('Клубника', 'Strawberry', 0, 33, NULL, NULL),
('Кокос мякоть', 'Coconut meat', 0, 354, NULL, NULL),
('Кокосовая стружка', 'Coconut flakes', 0, 660, NULL, NULL),
('Кофе Капучино без сахара', 'Cappuccino no sugar', 1, 53, NULL, NULL),
('Кофе Латте', 'Latte', 1, 44, NULL, NULL),
('Кофе Флэт Уайт', 'Flat White', 1, 42, NULL, NULL),
('Курица вареная', 'Boiled chicken', 0, 170, NULL, NULL),
('Курица филе', 'Chicken breast', 0, 110, NULL, NULL),
('Лимон', 'Lemon', 0, 29, NULL, NULL),
('Лук зеленый', 'Green onion', 0, 19, NULL, NULL),
('Лук репчатый', 'Onion', 0, 40, NULL, NULL),
('Макароны отварные', 'Boiled pasta', 0, 112, NULL, NULL),
('Малина', 'Raspberry', 0, 53, NULL, NULL),
('Манго', 'Mango', 0, 70, NULL, NULL),
('Мандарин', 'Mandarin', 0, 53, NULL, NULL),
('Маракуйя', 'Passion fruit', 0, 97, NULL, NULL),
('Масло оливковое', 'Olive oil', 0, 884, NULL, NULL),
('Масло сливочное', 'Butter', 0, 750, NULL, NULL),
('Морковь', 'Carrot', 0, 32, NULL, NULL),
('Морковь вареная', 'Boiled carrot', 0, 35, NULL, NULL),
('Морс', 'Fruit drink', 1, 52, NULL, NULL),
('Несквик', 'Nesquik', 0, 379, NULL, NULL),
('Овсянка', 'Oatmeal', 0, 102, NULL, NULL),
('Огурцы', 'Cucumber', 0, 15, NULL, NULL),
('Окорочок гриль', 'Grilled chicken leg', 0, 181, NULL, NULL),
('Орех арахис', 'Peanuts', 0, 567, NULL, NULL),
('Орех бразильский', 'Brazil nuts', 0, 656, NULL, NULL),
('Орех грецкий', 'Walnuts', 0, 654, NULL, NULL),
('Орех кедровый', 'Pine nuts', 0, 680, NULL, NULL),
('Орех кешью', 'Cashew nuts', 0, 553, NULL, NULL),
('Орех макадамия', 'Macadamia nuts', 0, 718, NULL, NULL),
('Орех миндаль', 'Almonds', 0, 649, NULL, NULL),
('Орех пекан', 'Pecan nuts', 0, 691, NULL, NULL),
('Орех фисташки', 'Pistachios', 0, 562, NULL, NULL),
('Орех фундук', 'Hazelnuts', 0, 628, NULL, NULL),
('Перец болгарский', 'Bell pepper', 0, 27, NULL, NULL),
('Перец острый', 'Hot pepper', 0, 40, NULL, NULL),
('Персик', 'Peach', 0, 39, NULL, NULL),
('Персики плоские инжирные', 'Flat peaches', 0, 60, NULL, NULL),
('Петрушка', 'Parsley', 0, 47, NULL, NULL),
('Печенье Юбилейное', 'Jubilee cookies', 0, NULL, NULL, 52),
('Пицца', 'Pizza', 0, 266, NULL, NULL),
('Помидоры', 'Tomatoes', 0, 20, NULL, NULL),
('Растительное масло', 'Vegetable oil', 0, 899, NULL, NULL),
('Редис', 'Radish', 0, 16, NULL, NULL),
('Редька зеленая', 'Green radish', 0, 32, NULL, NULL),
('Рис вареный', 'Boiled rice', 0, 116, NULL, NULL),
('Салат айсберг', 'Iceberg lettuce', 0, 14, NULL, NULL),
('Салат латук', 'Lettuce', 0, 15, NULL, NULL),
('Салат Оливье', 'Olivier salad', 0, 160, NULL, NULL),
('Салат Столичный', 'Capital salad', 0, 217, NULL, NULL),
('Сахар', 'Sugar', 0, 387, NULL, NULL),
('Свекла', 'Beetroot', 0, 43, NULL, NULL),
('Свинина', 'Pork', 0, 242, NULL, NULL),
('Сгущенка', 'Condensed milk', 0, 330, NULL, NULL),
('Слива', 'Plum', 0, 46, NULL, NULL),
('Сливки 10%', 'Cream 10%', 1, 119, NULL, NULL),
('Сливки 20%', 'Cream 20%', 1, 205, NULL, NULL),
('Сосиска в тесте', 'Sausage in dough', 0, 287, NULL, NULL),
('Соус тартар', 'Tartar sauce', 0, 340, NULL, NULL),
('Стейк миньон', 'Filet mignon', 0, 267, NULL, NULL),
('Стейк рибай', 'Ribeye steak', 0, 291, NULL, NULL),
('Творог 0,5%', 'Cottage cheese 0.5%', 0, 90, NULL, NULL),
('Творог 2%', 'Cottage cheese 2%', 0, 103, NULL, NULL),
('Тефтели', 'Meatballs', 0, 197, NULL, NULL),
('Укроп', 'Dill', 0, 38, NULL, NULL),
('Уксус', 'Vinegar', 0, 18, NULL, NULL),
('Финики', 'Dates', 0, 282, NULL, NULL),
('Харчо', 'Kharcho soup', 0, 44, NULL, NULL),
('Хинкали', 'Khinkali', 0, 234, NULL, NULL),
('Хурма', 'Persimmon', 0, 127, NULL, NULL),
('Черешня', 'Cherry', 0, 50, NULL, NULL),
('Черная смородина', 'Black currant', 0, 44, NULL, NULL),
('Чеснок', 'Garlic', 0, 143, NULL, NULL),
('Шампиньоны', 'Mushrooms', 0, 22, NULL, NULL),
('Шаурма', 'Shawarma', 0, 174, NULL, NULL),
('Шаурма с говядиной', 'Beef shawarma', 0, 192, NULL, NULL),
('Шашлык из курицы', 'Chicken kebab', 0, 142, NULL, NULL),
('Шашлык из свинины', 'Pork kebab', 0, 326, NULL, NULL),
('Шпинат зеленый', 'Green spinach', 0, 22, NULL, NULL),
('Яблоко', 'Apple', 0, 47, NULL, NULL),
('Яйцо вареное', 'Boiled egg', 0, 155, NULL, NULL);
