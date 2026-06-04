import psycopg2

import pandas as pd

# 1. Подключение к PostgreSQL
conn = None

try:
    conn = psycopg2.connect(
            host="localhost",
            port=5435,
            database="student_task",
            user="postgres",
            password="student"
        )

    print("Соединение установлено успешно!")

    # 2. SQL-запрос с JOIN таблиц prices и products
    query = """
        SELECT 
            p.id AS product_id,
            p.name,
            p.category,
            pr.price,
            pr.created_at
        FROM prices pr
        JOIN products p ON pr.product_id = p.id
        ORDER BY p.id, pr.price;
    """

    df = pd.read_sql(query, conn)

    print("\n--- Данные загружены ---")
    print(f"Загружено записей: {len(df)}")
    print(df.head())

    # Проверка, что данные есть
    if df.empty:
        print("\nВ таблицах нет данных для анализа.")
    else:
        # 3. Базовые статистики по колонке price
        price = df["price"]

        mean_price = price.mean()
        median_price = price.median()
        std_price = price.std()
        min_price = price.min()
        max_price = price.max()

        print("\n--- Общая статистика цен ---")
        print(f"Среднее значение: {mean_price:.2f} руб.")
        print(f"Медиана: {median_price:.2f} руб.")
        print(f"Стандартное отклонение: {std_price:.2f} руб.")
        print(f"Минимальная цена: {min_price:.2f} руб.")
        print(f"Максимальная цена: {max_price:.2f} руб.")

        # 4. Квартили и IQR
        Q1 = price.quantile(0.25)
        Q2 = price.quantile(0.50)
        Q3 = price.quantile(0.75)
        IQR = Q3 - Q1

        print("\n--- Квартили и межквартильный размах ---")
        print(f"Q1, первый квартиль: {Q1:.2f} руб.")
        print(f"Q2, медиана: {Q2:.2f} руб.")
        print(f"Q3, третий квартиль: {Q3:.2f} руб.")
        print(f"IQR, межквартильный размах: {IQR:.2f} руб.")

        # Товары с ценой выше Q3
        expensive_items = df[df["price"] > Q3]

        print("\n--- Товары с ценой выше Q3 ---")

        if expensive_items.empty:
            print("Товаров с ценой выше Q3 нет.")
        else:
            for _, row in expensive_items.iterrows():
                print(
                    f"Товар: {row['name']}; "
                    f"Категория: {row['category']}; "
                    f"Цена: {row['price']:.2f} руб."
                )

        # 5. Группировка по категориям
        category_stats = df.groupby("category")["price"].agg(
            count="count",
            mean="mean",
            median="median",
            std="std"
        ).round(2).sort_values(by="mean", ascending=False)

        print("\n--- Статистика по категориям ---")
        print(category_stats)

        # 6. Разброс цен по каждому товару
        product_price_range = df.groupby("name")["price"].agg(
            min_price="min",
            max_price="max"
        )

        product_price_range["price_difference"] = (
            product_price_range["max_price"] - product_price_range["min_price"]
        )

        top_5_difference = product_price_range.sort_values(
            by="price_difference",
            ascending=False
        ).head(5)

        print("\n--- Топ-5 товаров с наибольшим разбросом цен ---")
        print(top_5_difference.round(2))

except psycopg2.Error as error:
    print(f"Ошибка подключения или SQL-запроса: {error}")

except Exception as error:
    print(f"Произошла ошибка: {error}")

finally:
    if conn is not None:
        conn.close()
        print("\nСоединение закрыто.")