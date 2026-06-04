import psycopg2

import pandas as pd

import matplotlib.pyplot as plt

import matplotlib.gridspec as gridspec

from matplotlib.patches import Patch



# -----------------------------------------------------------------------------

# БЛОК 1: ПОДКЛЮЧЕНИЕ И ИЗВЛЕЧЕНИЕ ДАННЫХ

# Здесь всё как обычно — ничего нового.

# -----------------------------------------------------------------------------



try:

    connection = psycopg2.connect(

        host="localhost",

        port="5432",

        user="postgres",

        password="example",

        database="testdb"

    )

    print("✓ Подключение установлено")



    # --- Запрос 1: средний балл и количество сдач по каждому курсу ---

    # Этот DataFrame станет основой для первых двух графиков.



    df_courses = pd.read_sql("""

        SELECT

            c.course_name                AS course,

            ROUND(AVG(e.grade)::numeric, 2) AS avg_grade,

            COUNT(e.enrollment_id)       AS total_enrollments

        FROM enrollments e

        JOIN courses c ON e.course_id = c.course_id

        GROUP BY c.course_name

        ORDER BY avg_grade DESC

    """, connection)



    # --- Запрос 2: количество студентов по году поступления ---

    # Для круговой диаграммы.



    df_years = pd.read_sql("""

        SELECT

            enrollment_year AS year,

            COUNT(student_id) AS students

        FROM students

        GROUP BY enrollment_year

        ORDER BY enrollment_year

    """, connection)



    # --- Запрос 3: все оценки — для гистограммы распределения ---

    # Нам нужен только столбец grade, без лишних данных.



    df_all = pd.read_sql("SELECT grade FROM enrollments", connection)



    # --- Запрос 4: аномалии — студенты без записей об успеваемости ---

    # LEFT JOIN + фильтр по NULL находит студентов, которых нет в enrollments.



    df_missing = pd.read_sql("""

        SELECT

            s.first_name || ' ' || s.last_name AS student,

            s.enrollment_year

        FROM students s

        LEFT JOIN enrollments e ON s.student_id = e.student_id

        WHERE e.enrollment_id IS NULL

        ORDER BY s.enrollment_year, s.last_name

    """, connection)



    print(f"Курсов в выборке:           {len(df_courses)}")

    print(f"Всего записей об оценках:   {len(df_all)}")

    print(f"Студентов без оценок (ан.): {len(df_missing)}")



except Exception as error:

    print(f"Ошибка подключения: {error}")

    raise SystemExit



finally:

    # Закрываем соединение сразу — данные уже в DataFrame, подключение больше не нужно

    connection.close()

    print("✓ Соединение закрыто\n")



# -----------------------------------------------------------------------------

# БЛОК 2: ПОДГОТОВКА ДАННЫХ ДЛЯ ГРАФИКОВ

# Несколько вспомогательных вычислений перед визуализацией.

# -----------------------------------------------------------------------------



# Короткие названия курсов для подписей осей (длинные не влезают)

NAME_MAP = {

    "Основы программирования на Python": "Python",

    "Алгоритмы и структуры данных":      "Алгоритмы",

    "Базы данных и SQL":                  "Базы данных",

    "Веб-разработка (Frontend)":          "Frontend",

    "Администрирование Linux":            "Linux",

    "Математический анализ":              "Матанализ",

    "Дискретная математика":              "Дискр. мат.",

    "Английский язык для IT":             "Английский",

}

df_courses["short_name"] = df_courses["course"].map(NAME_MAP)



# Порог «нормы» — курсы ниже него выделим красным

GRADE_THRESHOLD = 3.8

overall_avg = df_courses["avg_grade"].mean()



# Цвет столбца: синий — норма, красный — ниже порога

bar_colors = [

    "#d9534f" if g < GRADE_THRESHOLD else "#4a90d9"

    for g in df_courses["avg_grade"]

]



# Подписи для круговой диаграммы вида «2023 (10 чел.)»

pie_labels = [

    f"{int(row.year)} ({row.students} чел.)"

    for row in df_years.itertuples()

]



# -----------------------------------------------------------------------------

# БЛОК 3: ПОСТРОЕНИЕ ГРАФИКОВ

#

# Используем GridSpec — более гибкую альтернативу plt.subplots().

# GridSpec позволяет задавать разные размеры для разных подграфиков.

# Схема сетки:

#

#   ┌──────────────────────┬──────────────────┐

#   │                      │                  │

#   │  График 1 (2 колонки)│  График 2        │

#   │  Средний балл        │  Кол-во сдач     │

#   │                      │                  │

#   ├──────────┬───────────┴──────────────────┤

#   │          │                              │

#   │ График 3 │  График 4                    │

#   │ Круговая │  Гистограмма оценок          │

#   │          │                              │

#   └──────────┴──────────────────────────────┘

# -----------------------------------------------------------------------------



plt.rcParams.update({

    "font.family":       "DejaVu Sans",  # поддерживает кириллицу

    "font.size":         10,

    "axes.spines.top":   False,          # убираем верхнюю рамку

    "axes.spines.right": False,          # и правую — выглядит чище

    "axes.grid":         True,

    "grid.alpha":        0.3,

    "grid.linestyle":    "--",

    "figure.dpi":        130,

})



fig = plt.figure(figsize=(16, 10))

fig.suptitle("Анализ учебной базы данных", fontsize=15, fontweight="bold", y=1.01)



# GridSpec(rows, cols) — сетка 2×3, соотношение строк 5:4, колонок 2:1:2

gs = gridspec.GridSpec(2, 3, figure=fig,

                       height_ratios=[5, 4],

                       width_ratios=[2, 1, 2],

                       hspace=0.45, wspace=0.35)



# ax1 занимает первую строку, первые две колонки

ax1 = fig.add_subplot(gs[0, 0:2])

# ax2 — первая строка, третья колонка

ax2 = fig.add_subplot(gs[0, 2])

# ax3 — вторая строка, первая колонка

ax3 = fig.add_subplot(gs[1, 0])

# ax4 — вторая строка, оставшиеся две колонки

ax4 = fig.add_subplot(gs[1, 1:3])





# ── ГРАФИК 1: Горизонтальная столбчатая диаграмма — средний балл по курсам ──

#

# Почему горизонтальная?

#   Длинные текстовые подписи на вертикальном графике пришлось бы вращать

#   под углом, что снижает читаемость. На горизонтальном они идут слева

#   и читаются естественно.



bars1 = ax1.barh(

    df_courses["short_name"],   # категории на оси Y

    df_courses["avg_grade"],    # значения на оси X

    color=bar_colors,

    edgecolor="white",

    height=0.6,

)



# Подпись значения на конце каждого столбца

for bar, val in zip(bars1, df_courses["avg_grade"]):

    ax1.text(

        bar.get_width() + 0.04,              # X: немного правее конца столбца

        bar.get_y() + bar.get_height() / 2,  # Y: по центру высоты столбца

        f"{val:.2f}",

        va="center", fontsize=9,

    )



# Пунктирная вертикальная линия — общее среднее по всем курсам

ax1.axvline(overall_avg, color="darkorange", linestyle="--",

            linewidth=1.3, label=f"Среднее: {overall_avg:.2f}")



ax1.set_xlim(2, 5.4)

ax1.set_xlabel("Средний балл")

ax1.set_title("Средний балл по курсам", fontweight="bold", pad=8)



# Легенда цветов — вручную через Patch (стандартная легенда тут не работает,

# потому что цвет задан напрямую столбцам, а не через label=)

legend_patches = [

    Patch(facecolor="#4a90d9", label=f"Норма (≥ {GRADE_THRESHOLD})"),

    Patch(facecolor="#d9534f", label="Ниже нормы"),

]

ax1.legend(handles=legend_patches, fontsize=8, loc="lower right")





# ── ГРАФИК 2: Вертикальная столбчатая диаграмма — количество сдач по курсам ──

#

# Показывает «популярность» курсов — сколько студентов их сдавали.

# Дополняет График 1: высокий средний балл + мало сдач = ненадёжная статистика.



bars2 = ax2.bar(

    df_courses["short_name"],

    df_courses["total_enrollments"],

    color="#5cb85c",

    edgecolor="white",

    width=0.6,

)



# Подпись значения над каждым столбцом

for bar in bars2:

    ax2.text(

        bar.get_x() + bar.get_width() / 2,  # X: по центру столбца

        bar.get_height() + 0.15,            # Y: чуть выше вершины

        str(int(bar.get_height())),

        ha="center", fontsize=9,

    )



ax2.set_ylim(0, max(df_courses["total_enrollments"]) + 2.5)

ax2.set_ylabel("Количество сдач")

ax2.set_title("Количество сдач\nпо курсам", fontweight="bold", pad=8)



# Поворот подписей оси X чтобы они не накладывались

ax2.set_xticks(range(len(df_courses)))

ax2.set_xticklabels(df_courses["short_name"], rotation=40, ha="right", fontsize=8)





# ── ГРАФИК 3: Круговая диаграмма — студенты по году поступления ──

#

# Круговую диаграмму уместно использовать, когда нужно показать доли

# нескольких категорий от общего. Здесь: какой процент студентов

# составляет каждый набор.



pie_colors = ["#7b68ee", "#4a90d9", "#2ecc71"]



wedges, texts, autotexts = ax3.pie(

    df_years["students"],

    labels=None,                # подписи вынесем в легенду

    autopct="%1.0f%%",          # подпись процента внутри сектора

    colors=pie_colors,

    startangle=90,              # «12 часов» — интуитивная точка старта

    wedgeprops={"edgecolor": "white", "linewidth": 1.5},

    pctdistance=0.7,            # расстояние подписи от центра (0 = центр, 1 = край)

)



for autotext in autotexts:

    autotext.set_fontsize(10)

    autotext.set_fontweight("bold")



ax3.set_title("Студенты\nпо году набора", fontweight="bold", pad=8)



# Легенда с числами под диаграммой

ax3.legend(

    wedges, pie_labels,

    loc="lower center",

    bbox_to_anchor=(0.5, -0.22),

    fontsize=8,

    frameon=False,

)





# ── ГРАФИК 4: Гистограмма + линия KDE — распределение оценок ──

#

# Гистограмма (hist) показывает, как часто встречается каждая оценка.

# Столбцы с шириной меньше 1 — для целых оценок лучше сделать их узкими,

# чтобы между ними был зазор и было понятно, что шкала дискретная.

#

# Дополнительно рисуем горизонтальную аннотацию-«стрелку» для аномалии.



grade_counts = df_all["grade"].value_counts().sort_index()



bars4 = ax4.bar(

    grade_counts.index,

    grade_counts.values,

    color="#f0ad4e",

    edgecolor="white",

    width=0.5,

)



# Подпись количества над каждым столбцом

for bar, (grade, cnt) in zip(bars4, grade_counts.items()):

    ax4.text(

        bar.get_x() + bar.get_width() / 2,

        bar.get_height() + 0.3,

        f"{cnt} ({cnt / len(df_all) * 100:.0f}%)",  # «12 (24%)»

        ha="center", fontsize=9,

    )



# Вертикальная линия — медиана

median_grade = df_all["grade"].median()

ax4.axvline(median_grade, color="crimson", linestyle="--",

            linewidth=1.5, label=f"Медиана: {median_grade}")



# Аннотация аномалии: двойка — единственная оценка ниже 3

if 2 in grade_counts.index:

    ax4.annotate(

        f"Аномалия:\n{grade_counts[2]} оценки «2»",

        xy=(2, grade_counts[2]),            # куда указывает стрелка (на столбец)

        xytext=(2.4, grade_counts[2] + 4),  # откуда начинается текст

        arrowprops={"arrowstyle": "->", "color": "crimson"},

        fontsize=8, color="crimson",

    )



ax4.set_xticks([2, 3, 4, 5])

ax4.set_xlabel("Оценка")

ax4.set_ylabel("Количество записей")

ax4.set_title("Распределение оценок", fontweight="bold", pad=8)

ax4.legend(fontsize=8)



# Вспомогательный текст с ключевыми метриками прямо на графике

stats_text = (

    f"Всего оценок: {len(df_all)}\n"

    f"Среднее: {df_all['grade'].mean():.2f}\n"

    f"Ст. откл.: {df_all['grade'].std():.2f}"

)

# ax.text(x, y, ..., transform=ax.transAxes) — координаты в долях осей (0–1),

# удобнее чем координаты данных: текст не «уедет» при изменении масштаба

ax4.text(0.97, 0.95, stats_text,

         transform=ax4.transAxes,

         va="top", ha="right", fontsize=8,

         bbox={"boxstyle": "round,pad=0.4", "facecolor": "lightyellow",

               "edgecolor": "lightgray", "alpha": 0.8})



# Аномалия на отдельном текстовом блоке под всей фигурой

fig.text(

    0.5, -0.03,

    f"⚠ Аномалия: {len(df_missing)} из {df_years['students'].sum()} студентов "

    "не имеют ни одной записи об успеваемости (отсутствуют в таблице enrollments)",

    ha="center", fontsize=9, color="#8b0000",

    bbox={"boxstyle": "round,pad=0.4", "facecolor": "#fff3f3", "edgecolor": "#d9534f"}

)



# -----------------------------------------------------------------------------

# БЛОК 4: СОХРАНЕНИЕ

# bbox_inches="tight" — автоматически обрезает пустые поля вокруг фигуры

# -----------------------------------------------------------------------------



OUTPUT_FILE = "student_charts.png"

plt.savefig(OUTPUT_FILE, bbox_inches="tight", dpi=150)

print(f"✓ График сохранён: {OUTPUT_FILE}")

plt.show()