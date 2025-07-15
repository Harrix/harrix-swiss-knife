import csv

# Словарь переводов на английский (можно расширить при необходимости)
translations = {
    "Газировка": "Soda",
    "Творожок": "Cottage cheese",
    "Кофе": "Coffee",
    "Нектар": "Nectar",
    "Чай": "Tea",
    "Помидоры": "Tomatoes",
    "Огурцы": "Cucumbers",
    "Майонез": "Mayonnaise",
    "Котлета говяжья": "Beef cutlet",
    "Котлета куриная": "Chicken cutlet",
    "Гречка": "Buckwheat",
    "Кетчуп": "Ketchup",
    "Шоколад": "Chocolate",
    "Конфеты": "Candies",
    "Кола": "Cola",
    "Сосиски": "Sausages",
    "Морковь": "Carrot",
    "Чеснок": "Garlic",
    "Капуста": "Cabbage",
    "Растительное масло": "Vegetable oil",
    "Сахар": "Sugar",
    "Тирияки": "Teriyaki",
    "Яйцо": "Egg",
    "Молоко топленое": "Baked milk",
    "Хлеб": "Bread",
    "Колбаса": "Sausage",
    "Яйца": "Eggs",
    "Сок виноградный": "Grape juice"
}

def convert_date(date_str):
    """Конвертирует дату из формата DD.MM.YYYY в YYYY-MM-DD"""
    try:
        day, month, year = date_str.split(".")
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    except:
        return date_str

def safe_float(value):
    """Безопасно конвертирует строку в float, заменяя запятые на точки"""
    if not value or value.strip() == "":
        return None
    try:
        return float(value.replace(",", "."))
    except:
        return None

def format_value(value, is_string=False):
    """Форматирует значение для SQL"""
    if value is None:
        return "NULL"
    if is_string:
        # Экранируем одинарные кавычки
        escaped_value = str(value).replace("'", "''")
        return f"'{escaped_value}'"
    return str(value)

def generate_batch_sql_inserts(filename, batch_size=5000):
    """Генерирует SQL INSERT запросы батчами по batch_size записей"""
    batch_queries = []
    current_batch_values = []

    try:
        with open(filename, encoding="utf-8") as file:
            reader = csv.reader(file, delimiter="\t")
            next(reader)  # Пропускаем заголовок

            for row_num, row in enumerate(reader, start=2):
                if len(row) < 7:
                    print(f"Предупреждение: строка {row_num} содержит недостаточно колонок")
                    continue

                # Извлекаем данные из строки
                name = row[0].strip() if row[0] else None
                portion_calories = safe_float(row[3])
                weight = safe_float(row[4])
                calculated_calories = safe_float(row[5])
                date_str = row[6].strip() if row[6] else None

                # Проверяем обязательные поля
                if not calculated_calories or not date_str:
                    print(f"Предупреждение: строка {row_num} пропущена - отсутствуют обязательные данные")
                    continue

                # Конвертируем дату
                formatted_date = convert_date(date_str)

                # Получаем английское название
                name_en = translations.get(name) if name else None

                # Формируем VALUES для этой записи
                values = f"({format_value(formatted_date, True)}, {format_value(weight)}, {format_value(portion_calories)}, {format_value(calculated_calories)}, {format_value(name, True)}, {format_value(name_en, True)})"

                current_batch_values.append(values)

                # Если достигли размера батча, создаем SQL запрос
                if len(current_batch_values) >= batch_size:
                    sql_query = create_batch_insert(current_batch_values)
                    batch_queries.append(sql_query)
                    current_batch_values = []

            # Добавляем оставшиеся записи, если они есть
            if current_batch_values:
                sql_query = create_batch_insert(current_batch_values)
                batch_queries.append(sql_query)

    except FileNotFoundError:
        print(f"Ошибка: файл '{filename}' не найден")
        return []
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return []

    return batch_queries

def create_batch_insert(values_list):
    """Создает один INSERT запрос для батча значений"""
    base_query = "INSERT INTO food_log (date, weight, portion_calories, calculated_calories, name, name_en) VALUES "
    values_string = ",\n    ".join(values_list)
    return base_query + "\n    " + values_string + ";"

# Основная функция
def main():
    filename = "data.txt"  # Замените на имя вашего файла
    batch_size = 5000  # Количество записей в одном INSERT

    print(f"Генерация SQL INSERT запросов батчами по {batch_size} записей...")
    batch_queries = generate_batch_sql_inserts(filename, batch_size)

    if batch_queries:
        total_records = sum(query.count("(") for query in batch_queries)
        print(f"\nСгенерировано {len(batch_queries)} батчей с общим количеством записей: {total_records}")

        # Выводим информацию о каждом батче
        for i, query in enumerate(batch_queries, 1):
            records_in_batch = query.count("(")
            print(f"\n-- Батч {i} ({records_in_batch} записей)")
            print(query)
            print()

        # Сохраняем в файл
        output_filename = "batch_insert_queries.sql"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write("-- SQL INSERT запросы для таблицы food_log\n")
            f.write(f"-- Батчи по {batch_size} записей\n")
            f.write(f"-- Общее количество батчей: {len(batch_queries)}\n")
            f.write(f"-- Общее количество записей: {total_records}\n\n")

            for i, query in enumerate(batch_queries, 1):
                records_in_batch = query.count("(")
                f.write(f"-- Батч {i} ({records_in_batch} записей)\n")
                f.write(query + "\n\n")

        print(f"SQL запросы сохранены в файл: {output_filename}")

        # Дополнительно создаем отдельные файлы для каждого батча (опционально)
        create_separate_files = input("Создать отдельные файлы для каждого батча? (y/n): ").lower() == "y"
        if create_separate_files:
            for i, query in enumerate(batch_queries, 1):
                batch_filename = f"batch_{i:03d}_insert.sql"
                with open(batch_filename, "w", encoding="utf-8") as f:
                    records_in_batch = query.count("(")
                    f.write(f"-- Батч {i} ({records_in_batch} записей)\n")
                    f.write(query + "\n")
                print(f"Создан файл: {batch_filename}")
    else:
        print("Не удалось сгенерировать SQL запросы")

if __name__ == "__main__":
    main()
