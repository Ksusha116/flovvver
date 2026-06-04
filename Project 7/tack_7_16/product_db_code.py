import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from sqlalchemy import create_engine


# -----------------------------------------------------------------------------
# БЛОК 1. ПОДКЛЮЧЕНИЕ К БАЗЕ ДАННЫХ
# -----------------------------------------------------------------------------

DB_HOST = "localhost"
DB_PORT = 5435
DB_NAME = ("student_task")
DB_USER = "postgres"
DB_PASSWORD = "student"

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

try:
    engine = create_engine(DATABASE_URL)
    print("✓ Подключение установлено")

    # -------------------------------------------------------------------------
    # Запрос 1. Все цены товаров вместе с названием и категорией
    # -------------------------------------------------------------------------
    df_prices = pd.read_sql("""
        SELECT
            p.id AS product_id,
            p.name AS product_name,
            p.category,
            pr.price,
            pr.created_at
        FROM prices pr
        JOIN products p ON pr.product_id = p.id
        ORDER BY p.id, pr.price;
    """, engine)

    # -------------------------------------------------------------------------
    # Запрос 2. Статистика по категориям товаров
    # -------------------------------------------------------------------------
    df_categories = pd.read_sql("""
        SELECT
            p.category,
            COUNT(DISTINCT p.id) AS products_count,
            COUNT(pr.id) AS price_records,
            COALESCE(ROUND(AVG(pr.price)::numeric, 2), 0) AS avg_price,
            COALESCE(ROUND(MIN(pr.price)::numeric, 2), 0) AS min_price,
            COALESCE(ROUND(MAX(pr.price)::numeric, 2), 0) AS max_price
        FROM products p
        LEFT JOIN prices pr ON p.id = pr.product_id
        GROUP BY p.category
        ORDER BY avg_price DESC;
    """, engine)

    # -------------------------------------------------------------------------
    # Запрос 3. Количество поставщиков по категориям
    # -------------------------------------------------------------------------
    df_suppliers = pd.read_sql("""
        SELECT
            p.category,
            COUNT(s.id) AS suppliers_count,
            COUNT(DISTINCT p.id) AS products_count
        FROM products p
        LEFT JOIN suppliers s ON p.id = s.product_id
        GROUP BY p.category
        ORDER BY suppliers_count DESC;
    """, engine)

    # -------------------------------------------------------------------------
    # Запрос 4. Разброс цен по каждому товару
    # -------------------------------------------------------------------------
    df_spread = pd.read_sql("""
        SELECT
            p.id AS product_id,
            p.name AS product_name,
            p.category,
            COALESCE(ROUND(MIN(pr.price)::numeric, 2), 0) AS min_price,
            COALESCE(ROUND(MAX(pr.price)::numeric, 2), 0) AS max_price,
            COALESCE(ROUND((MAX(pr.price) - MIN(pr.price))::numeric, 2), 0) AS price_spread,
            COUNT(pr.id) AS price_records
        FROM products p
        LEFT JOIN prices pr ON p.id = pr.product_id
        GROUP BY p.id, p.name, p.category
        ORDER BY price_spread DESC;
    """, engine)

    # -------------------------------------------------------------------------
    # Запрос 5. Товары без цен
    # -------------------------------------------------------------------------
    df_missing_prices = pd.read_sql("""
        SELECT
            p.id AS product_id,
            p.name AS product_name,
            p.category
        FROM products p
        LEFT JOIN prices pr ON p.id = pr.product_id
        WHERE pr.id IS NULL
        ORDER BY p.id;
    """, engine)

    # -------------------------------------------------------------------------
    # Запрос 6. Товары без поставщиков
    # -------------------------------------------------------------------------
    df_missing_suppliers = pd.read_sql("""
        SELECT
            p.id AS product_id,
            p.name AS product_name,
            p.category
        FROM products p
        LEFT JOIN suppliers s ON p.id = s.product_id
        WHERE s.id IS NULL
        ORDER BY p.id;
    """, engine)

    print("\n--- Данные загружены ---")
    print(f"Записей о ценах: {len(df_prices)}")
    print(f"Категорий товаров: {len(df_categories)}")
    print(f"Товаров без цен: {len(df_missing_prices)}")
    print(f"Товаров без поставщиков: {len(df_missing_suppliers)}")

except Exception as error:
    print(f"Ошибка подключения или загрузки данных: {error}")
    raise SystemExit


# -----------------------------------------------------------------------------
# БЛОК 2. ПРОВЕРКА И ПОДГОТОВКА ДАННЫХ
# -----------------------------------------------------------------------------

if df_prices.empty:
    print("Нет данных о ценах. Невозможно построить графики.")
    raise SystemExit

# Переводим числовые колонки в нормальный числовой тип
df_prices["price"] = pd.to_numeric(df_prices["price"])
df_categories["avg_price"] = pd.to_numeric(df_categories["avg_price"])
df_categories["products_count"] = pd.to_numeric(df_categories["products_count"])
df_spread["price_spread"] = pd.to_numeric(df_spread["price_spread"])
df_spread["price_records"] = pd.to_numeric(df_spread["price_records"])


# -----------------------------------------------------------------------------
# БЛОК 3. РАСЧЁТ СТАТИСТИЧЕСКИХ МЕТРИК
# -----------------------------------------------------------------------------

price = df_prices["price"]

mean_price = price.mean()
median_price = price.median()
std_price = price.std()
min_price = price.min()
max_price = price.max()

q1 = price.quantile(0.25)
q2 = price.quantile(0.50)
q3 = price.quantile(0.75)
iqr = q3 - q1

lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.5 * iqr

df_expensive_outliers = df_prices[df_prices["price"] > upper_bound]
df_cheap_outliers = df_prices[df_prices["price"] < lower_bound]

print("\n--- Общая статистика цен ---")
print(f"Средняя цена: {mean_price:.2f} руб.")
print(f"Медиана: {median_price:.2f} руб.")
print(f"Стандартное отклонение: {std_price:.2f} руб.")
print(f"Минимальная цена: {min_price:.2f} руб.")
print(f"Максимальная цена: {max_price:.2f} руб.")

print("\n--- Квартили и межквартильный размах ---")
print(f"Q1: {q1:.2f} руб.")
print(f"Q2, медиана: {q2:.2f} руб.")
print(f"Q3: {q3:.2f} руб.")
print(f"IQR: {iqr:.2f} руб.")
print(f"Нижняя граница выбросов: {lower_bound:.2f} руб.")
print(f"Верхняя граница выбросов: {upper_bound:.2f} руб.")


# -----------------------------------------------------------------------------
# БЛОК 4. ОБОСНОВАНИЕ ВЫБОРА ГРАФИКОВ
# -----------------------------------------------------------------------------

print("\n--- Обоснование выбора графиков ---")
print("1. Средняя цена по категориям показана столбчатой диаграммой, потому что сравниваются категории товаров.")
print("2. Количество товаров по категориям также удобно показывать столбчатой диаграммой.")
print("3. Распределение цен показано гистограммой, потому что нужно увидеть, как часто встречаются разные уровни цен.")
print("4. Топ товаров по разбросу цен показан горизонтальной столбчатой диаграммой, потому что названия товаров длинные.")


# -----------------------------------------------------------------------------
# БЛОК 5. ПОДГОТОВКА ДАННЫХ ДЛЯ ГРАФИКОВ
# -----------------------------------------------------------------------------

top_spread = (
    df_spread[df_spread["price_records"] >= 2]
    .sort_values(by="price_spread", ascending=False)
    .head(10)
)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
    "figure.dpi": 130,
})


# -----------------------------------------------------------------------------
# БЛОК 6. ПОСТРОЕНИЕ ГРАФИКОВ
# -----------------------------------------------------------------------------

fig = plt.figure(figsize=(16, 10))
fig.suptitle(
    "Анализ базы данных интернет-магазина",
    fontsize=15,
    fontweight="bold",
    y=0.98
)

gs = gridspec.GridSpec(
    2,
    2,
    figure=fig,
    hspace=0.45,
    wspace=0.30
)

ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
ax3 = fig.add_subplot(gs[1, 0])
ax4 = fig.add_subplot(gs[1, 1])


# -----------------------------------------------------------------------------
# ГРАФИК 1. Средняя цена по категориям
# -----------------------------------------------------------------------------

bars1 = ax1.bar(
    df_categories["category"],
    df_categories["avg_price"],
    edgecolor="white",
    width=0.6
)

for bar, val in zip(bars1, df_categories["avg_price"]):
    ax1.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + max(df_categories["avg_price"]) * 0.01,
        f"{val:.0f}",
        ha="center",
        fontsize=8
    )

ax1.axhline(
    mean_price,
    linestyle="--",
    linewidth=1.3,
    label=f"Общее среднее: {mean_price:.2f} руб."
)

ax1.set_title("Средняя цена по категориям", fontweight="bold", pad=8)
ax1.set_ylabel("Средняя цена, руб.")
ax1.set_xticks(range(len(df_categories)))
ax1.set_xticklabels(df_categories["category"], rotation=35, ha="right")
ax1.legend(fontsize=8)


# -----------------------------------------------------------------------------
# ГРАФИК 2. Количество товаров по категориям
# -----------------------------------------------------------------------------

bars2 = ax2.bar(
    df_categories["category"],
    df_categories["products_count"],
    edgecolor="white",
    width=0.6
)

for bar, val in zip(bars2, df_categories["products_count"]):
    ax2.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.1,
        str(int(val)),
        ha="center",
        fontsize=9
    )

ax2.set_title("Количество товаров по категориям", fontweight="bold", pad=8)
ax2.set_ylabel("Количество товаров")
ax2.set_xticks(range(len(df_categories)))
ax2.set_xticklabels(df_categories["category"], rotation=35, ha="right")


# -----------------------------------------------------------------------------
# ГРАФИК 3. Распределение цен
# -----------------------------------------------------------------------------

ax3.hist(
    df_prices["price"],
    bins=10,
    edgecolor="white"
)

ax3.axvline(
    mean_price,
    linestyle="--",
    linewidth=1.5,
    label=f"Среднее: {mean_price:.2f}"
)

ax3.axvline(
    median_price,
    linestyle=":",
    linewidth=2,
    label=f"Медиана: {median_price:.2f}"
)

ax3.axvline(
    q3,
    linestyle="-.",
    linewidth=1.5,
    label=f"Q3: {q3:.2f}"
)

ax3.set_title("Распределение цен товаров", fontweight="bold", pad=8)
ax3.set_xlabel("Цена, руб.")
ax3.set_ylabel("Количество записей")
ax3.legend(fontsize=8)

stats_text = (
    f"Всего цен: {len(df_prices)}\n"
    f"Среднее: {mean_price:.2f}\n"
    f"Медиана: {median_price:.2f}\n"
    f"Ст. откл.: {std_price:.2f}\n"
    f"IQR: {iqr:.2f}"
)

ax3.text(
    0.97,
    0.95,
    stats_text,
    transform=ax3.transAxes,
    va="top",
    ha="right",
    fontsize=8,
    bbox={
        "boxstyle": "round,pad=0.4",
        "facecolor": "lightyellow",
        "edgecolor": "lightgray",
        "alpha": 0.8
    }
)


# -----------------------------------------------------------------------------
# ГРАФИК 4. Топ-10 товаров по разбросу цен
# -----------------------------------------------------------------------------

if not top_spread.empty:
    bars4 = ax4.barh(
        top_spread["product_name"],
        top_spread["price_spread"],
        edgecolor="white",
        height=0.6
    )

    max_spread = max(top_spread["price_spread"])

    for bar, val in zip(bars4, top_spread["price_spread"]):
        ax4.text(
            bar.get_width() + max_spread * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{val:.2f}",
            va="center",
            fontsize=8
        )

    ax4.set_title("Топ-10 товаров по разбросу цен", fontweight="bold", pad=8)
    ax4.set_xlabel("Разница между max и min ценой, руб.")
    ax4.invert_yaxis()
else:
    ax4.text(
        0.5,
        0.5,
        "Недостаточно данных\nдля расчёта разброса цен",
        ha="center",
        va="center",
        fontsize=11
    )
    ax4.set_title("Топ-10 товаров по разбросу цен", fontweight="bold", pad=8)


# -----------------------------------------------------------------------------
# ОБЩАЯ АННОТАЦИЯ ОБ АНОМАЛИЯХ
# -----------------------------------------------------------------------------

anomaly_text = (
    f"Аномалии: товаров без цен — {len(df_missing_prices)}, "
    f"товаров без поставщиков — {len(df_missing_suppliers)}, "
    f"ценовых выбросов выше верхней границы — {len(df_expensive_outliers)}"
)

fig.text(
    0.5,
    0.02,
    anomaly_text,
    ha="center",
    fontsize=9,
    color="#8b0000",
    bbox={
        "boxstyle": "round,pad=0.4",
        "facecolor": "#fff3f3",
        "edgecolor": "#d9534f"
    }
)


# -----------------------------------------------------------------------------
# БЛОК 7. СОХРАНЕНИЕ ГРАФИКА
# -----------------------------------------------------------------------------

OUTPUT_FILE = "products_charts.png"

plt.savefig(OUTPUT_FILE, bbox_inches="tight", dpi=150)
print(f"\n✓ График сохранён: {OUTPUT_FILE}")


# -----------------------------------------------------------------------------
# БЛОК 8. ВЫВОДЫ ПО ГРАФИКАМ
# -----------------------------------------------------------------------------

most_expensive_category = df_categories.iloc[0]
cheapest_category = df_categories.iloc[-1]

largest_category = df_categories.sort_values(
    by="products_count",
    ascending=False
).iloc[0]

print("\n--- Выводы по графикам ---")

print(
    f"1. Самая дорогая категория по средней цене — "
    f"«{most_expensive_category['category']}», средняя цена "
    f"{most_expensive_category['avg_price']:.2f} руб."
)

print(
    f"2. Самая дешёвая категория по средней цене — "
    f"«{cheapest_category['category']}», средняя цена "
    f"{cheapest_category['avg_price']:.2f} руб."
)

print(
    f"3. Больше всего товаров в категории "
    f"«{largest_category['category']}» — "
    f"{int(largest_category['products_count'])} шт."
)

print(
    f"4. По распределению цен: средняя цена равна {mean_price:.2f} руб., "
    f"медиана равна {median_price:.2f} руб. "
    f"Если среднее выше медианы, значит дорогие товары повышают среднее значение."
)

if not top_spread.empty:
    largest_spread_product = top_spread.iloc[0]

    print(
        f"5. Самый большой разброс цен у товара "
        f"«{largest_spread_product['product_name']}» — "
        f"{largest_spread_product['price_spread']:.2f} руб."
    )
else:
    print("5. Разброс цен по товарам рассчитать не удалось.")

if len(df_expensive_outliers) > 0:
    print("\n6. Обнаружены ценовые выбросы выше верхней границы:")
    print(
        df_expensive_outliers[
            ["product_name", "category", "price"]
        ].to_string(index=False)
    )
else:
    print("\n6. Ценовые выбросы выше верхней границы не обнаружены.")

if len(df_cheap_outliers) > 0:
    print("\n7. Обнаружены ценовые выбросы ниже нижней границы:")
    print(
        df_cheap_outliers[
            ["product_name", "category", "price"]
        ].to_string(index=False)
    )
else:
    print("\n7. Ценовые выбросы ниже нижней границы не обнаружены.")

if len(df_missing_prices) > 0:
    print("\n8. Есть товары без цен:")
    print(df_missing_prices.to_string(index=False))
else:
    print("\n8. Товаров без цен не обнаружено.")

if len(df_missing_suppliers) > 0:
    print("\n9. Есть товары без поставщиков:")
    print(df_missing_suppliers.to_string(index=False))
else:
    print("\n9. Товаров без поставщиков не обнаружено.")

print("\nРабота программы завершена.")

plt.show()