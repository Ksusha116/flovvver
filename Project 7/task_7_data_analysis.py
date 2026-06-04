import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path

# -----------------------------------------------------------------------------
# БЛОК 0. НАСТРОЙКИ ПОДКЛЮЧЕНИЯ
# -----------------------------------------------------------------------------

DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "user": "postgres",
    "password": "example",
    "database": "testdb",
}

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = BASE_DIR / "products_charts.png"

# Файлы с INSERT-данными должны лежать рядом с этим Python-файлом
SQL_FILES = [
    BASE_DIR / "task_5-9_products.sql",
    BASE_DIR / "task_5-9_suppliers.sql",
    BASE_DIR / "task_5-9_prices.sql",
]


# -----------------------------------------------------------------------------
# БЛОК 1. СОЗДАНИЕ ТАБЛИЦ И ЗАГРУЗКА ДАННЫХ
# -----------------------------------------------------------------------------

def create_tables(connection):
    """Создаём таблицы products, suppliers, prices."""
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id SERIAL PRIMARY KEY,
                name       VARCHAR(150) NOT NULL,
                category   VARCHAR(100) NOT NULL
            );

            CREATE TABLE IF NOT EXISTS suppliers (
                supplier_id SERIAL PRIMARY KEY,
                name        VARCHAR(150) NOT NULL,
                product_id  INTEGER NOT NULL REFERENCES products(product_id)
            );

            CREATE TABLE IF NOT EXISTS prices (
                price_id   SERIAL PRIMARY KEY,
                product_id INTEGER NOT NULL REFERENCES products(product_id),
                price      NUMERIC(12, 2) NOT NULL CHECK (price > 0)
            );
        """)
    connection.commit()


def load_data(connection):
    """Очищаем таблицы и заново загружаем данные из SQL-файлов."""
    for file_path in SQL_FILES:
        if not file_path.exists():
            raise FileNotFoundError(f"Не найден файл: {file_path.name}")

    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE prices, suppliers, products RESTART IDENTITY CASCADE;")

        for file_path in SQL_FILES:
            sql_text = file_path.read_text(encoding="utf-8")
            cursor.execute(sql_text)

    connection.commit()


# -----------------------------------------------------------------------------
# БЛОК 2. ПОДКЛЮЧЕНИЕ К БАЗЕ И SQL-ЗАПРОСЫ
# -----------------------------------------------------------------------------

try:
    connection = psycopg2.connect(**DB_CONFIG)
    print("✓ Подключение к базе данных установлено")

    create_tables(connection)
    load_data(connection)
    print("✓ Таблицы созданы, данные загружены")

    # 1) Количество товаров по категориям
    df_categories = pd.read_sql("""
        SELECT
            category,
            COUNT(*) AS products_count
        FROM products
        GROUP BY category
        ORDER BY products_count DESC, category;
    """, connection)

    # 2) Средняя цена по категориям
    df_avg_category_price = pd.read_sql("""
        SELECT
            p.category,
            ROUND(AVG(pr.price)::numeric, 2) AS avg_price
        FROM products p
        JOIN prices pr ON p.product_id = pr.product_id
        GROUP BY p.category
        ORDER BY avg_price DESC;
    """, connection)

    # 3) Средняя цена каждого товара
    df_products_price = pd.read_sql("""
        SELECT
            p.name AS product,
            p.category,
            ROUND(AVG(pr.price)::numeric, 2) AS avg_price,
            MIN(pr.price) AS min_price,
            MAX(pr.price) AS max_price,
            COUNT(pr.price_id) AS price_records
        FROM products p
        LEFT JOIN prices pr ON p.product_id = pr.product_id
        GROUP BY p.product_id, p.name, p.category
        ORDER BY avg_price DESC NULLS LAST;
    """, connection)

    # 4) Количество поставщиков по товарам
    df_suppliers = pd.read_sql("""
        SELECT
            p.name AS product,
            COUNT(s.supplier_id) AS suppliers_count
        FROM products p
        LEFT JOIN suppliers s ON p.product_id = s.product_id
        GROUP BY p.product_id, p.name
        ORDER BY suppliers_count DESC, p.name;
    """, connection)

    # 5) Аномалии: товары без цены
    df_no_price = pd.read_sql("""
        SELECT
            p.name AS product,
            p.category
        FROM products p
        LEFT JOIN prices pr ON p.product_id = pr.product_id
        WHERE pr.price_id IS NULL
        ORDER BY p.category, p.name;
    """, connection)

    # 6) Аномалии: товары без поставщика
    df_no_supplier = pd.read_sql("""
        SELECT
            p.name AS product,
            p.category
        FROM products p
        LEFT JOIN suppliers s ON p.product_id = s.product_id
        WHERE s.supplier_id IS NULL
        ORDER BY p.category, p.name;
    """, connection)

    print("\nКоличество товаров по категориям:")
    print(df_categories)

    print("\nСредняя цена по категориям:")
    print(df_avg_category_price)

    print("\nТовары без цены:")
    print(df_no_price if len(df_no_price) > 0 else "Нет")

    print("\nТовары без поставщика:")
    print(df_no_supplier if len(df_no_supplier) > 0 else "Нет")

except Exception as error:
    print(f"Ошибка: {error}")
    raise SystemExit

finally:
    try:
        connection.close()
        print("\n✓ Соединение с базой закрыто")
    except NameError:
        pass


# -----------------------------------------------------------------------------
# БЛОК 3. ПОДГОТОВКА ДАННЫХ ДЛЯ ГРАФИКОВ
# -----------------------------------------------------------------------------

# Для графика дорогих товаров берём только товары, у которых есть цена
products_with_price = df_products_price.dropna(subset=["avg_price"]).copy()
top_products = products_with_price.head(10).sort_values("avg_price")

# Общая средняя цена по товарам
overall_avg_price = products_with_price["avg_price"].mean()


# -----------------------------------------------------------------------------
# БЛОК 4. ПОСТРОЕНИЕ ГРАФИКОВ
# -----------------------------------------------------------------------------

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
})

fig = plt.figure(figsize=(16, 10))
fig.suptitle("Анализ базы данных товаров", fontsize=16, fontweight="bold")

gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)

ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
ax3 = fig.add_subplot(gs[1, 0])
ax4 = fig.add_subplot(gs[1, 1])

# График 1. Количество товаров по категориям
bars1 = ax1.bar(df_categories["category"], df_categories["products_count"])
ax1.set_title("Количество товаров по категориям", fontweight="bold")
ax1.set_ylabel("Количество товаров")
ax1.tick_params(axis="x", rotation=35)

for bar in bars1:
    ax1.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.05,
        int(bar.get_height()),
        ha="center"
    )

# График 2. Средняя цена по категориям
bars2 = ax2.bar(df_avg_category_price["category"], df_avg_category_price["avg_price"])
ax2.set_title("Средняя цена по категориям", fontweight="bold")
ax2.set_ylabel("Средняя цена, руб.")
ax2.tick_params(axis="x", rotation=35)

for bar in bars2:
    ax2.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 500,
        f"{bar.get_height():.0f}",
        ha="center",
        fontsize=9
    )

# График 3. Топ-10 дорогих товаров
bars3 = ax3.barh(top_products["product"], top_products["avg_price"])
ax3.set_title("Топ-10 товаров по средней цене", fontweight="bold")
ax3.set_xlabel("Средняя цена, руб.")
ax3.axvline(overall_avg_price, linestyle="--", label=f"Средняя: {overall_avg_price:.0f} руб.")
ax3.legend(fontsize=8)

for bar in bars3:
    ax3.text(
        bar.get_width() + 500,
        bar.get_y() + bar.get_height() / 2,
        f"{bar.get_width():.0f}",
        va="center",
        fontsize=9
    )

# График 4. Количество поставщиков по товарам
supplier_top = df_suppliers.head(10).sort_values("suppliers_count")
bars4 = ax4.barh(supplier_top["product"], supplier_top["suppliers_count"])
ax4.set_title("Количество поставщиков по товарам", fontweight="bold")
ax4.set_xlabel("Количество поставщиков")

for bar in bars4:
    ax4.text(
        bar.get_width() + 0.03,
        bar.get_y() + bar.get_height() / 2,
        int(bar.get_width()),
        va="center",
        fontsize=9
    )

# Текст с аномалиями под графиками
fig.text(
    0.5,
    0.01,
    f"Аномалии: товаров без цены — {len(df_no_price)}; товаров без поставщика — {len(df_no_supplier)}",
    ha="center",
    fontsize=10
)

plt.savefig(OUTPUT_FILE, dpi=150, bbox_inches="tight")
print(f"\n✓ График сохранён в файл: {OUTPUT_FILE}")
plt.show()
