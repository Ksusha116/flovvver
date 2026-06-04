import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
from flask import Flask, render_template, jsonify, send_file
from sqlalchemy import create_engine

app = Flask(__name__)
matplotlib.rcParams['font.family'] = 'DejaVu Sans'

ENGINE = create_engine(
    "postgresql+psycopg2://postgres:example@localhost:5432/testdb"
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/stat/<metric>")
def get_stat(metric):
    try:
        df = pd.read_sql("SELECT grade FROM enrollments", ENGINE)

        if metric == "mean":
            value = f"{df['grade'].mean():.2f}"
            label = "Средний балл"
        elif metric == "median":
            value = f"{df['grade'].median():.2f}"
            label = "Медиана оценок"
        elif metric == "total":
            value = int(df["grade"].count())
            label = "Всего записей"
        else:
            return jsonify({"error": "Неизвестная метрика"}), 400

        return jsonify({"label": label, "value": value})

    except Exception as e:
        print(f"ERROR в /api/stat/{metric}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/chart/<kind>")
def get_chart(kind):
    try:
        fig, ax = plt.subplots(figsize=(8, 5))

        if kind == "histogram":
            df = pd.read_sql("SELECT grade FROM enrollments", ENGINE)
            grade_counts = df["grade"].value_counts().sort_index()

            ax.bar(
                grade_counts.index,
                grade_counts.values,
                color="#f0ad4e",
                edgecolor="white",
                width=0.5
            )

            median = df["grade"].median()
            ax.axvline(
                median,
                color="crimson",
                linestyle="--",
                linewidth=1.5,
                label=f"Медиана: {median}"
            )

            ax.set_xlabel("Оценка")
            ax.set_ylabel("Количество записей")
            ax.set_title("Распределение оценок", fontweight="bold")
            ax.set_xticks([2, 3, 4, 5])
            ax.legend()

        elif kind == "courses":
            df = pd.read_sql("""
                SELECT c.course_name AS course,
                       ROUND(AVG(e.grade)::numeric, 2) AS avg_grade
                FROM enrollments e
                JOIN courses c ON e.course_id = c.course_id
                GROUP BY c.course_name
                ORDER BY avg_grade DESC
            """, ENGINE)

            short_names = df["course"].str[:12]

            ax.barh(
                short_names,
                df["avg_grade"],
                color="#4a90d9",
                edgecolor="white"
            )

            df_all = pd.read_sql("SELECT grade FROM enrollments", ENGINE)
            overall_avg = df_all["grade"].mean()

            ax.axvline(
                overall_avg,
                color="darkorange",
                linestyle="--",
                linewidth=1.3,
                label=f"Среднее: {overall_avg:.2f}"
            )

            ax.set_xlabel("Средний балл")
            ax.set_title("Средний балл по курсам", fontweight="bold")
            ax.set_xlim(0, 5.5)
            ax.legend(loc="lower right")

        else:
            plt.close(fig)
            return jsonify({"error": "Неизвестный тип графика"}), 400

        plt.tight_layout()

        buf = BytesIO()
        plt.savefig(buf, format="png", dpi=120, bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)

        return send_file(buf, mimetype="image/png")

    except Exception as e:
        print(f"ERROR в /api/chart/{kind}: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)