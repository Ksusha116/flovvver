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
    "postgresql+psycopg2://postgres:student@localhost:5435/student_task"
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/stat/<metric>")
def get_stat(metric):
    try:
        df = pd.read_sql("SELECT price FROM prices", ENGINE)
        df["price"] = pd.to_numeric(df["price"])

        if metric == "mean":
            value = f"{df['price'].mean():.2f}"
            label = "Средняя цена"
        elif metric == "median":
            value = f"{df['price'].median():.2f}"
            label = "Медиана цены"
        elif metric == "total":
            value = int(df["price"].count())
            label = "Всего записей с ценами"
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
            df = pd.read_sql("SELECT price FROM prices", ENGINE)
            df["price"] = pd.to_numeric(df["price"])

            ax.hist(
                df["price"],
                bins=8,
                color="#f0ad4e",
                edgecolor="white"
            )

            median = df["price"].median()

            ax.axvline(
                median,
                color="crimson",
                linestyle="--",
                linewidth=1.5,
                label=f"Медиана: {median:.2f}"
            )

            ax.set_xlabel("Цена")
            ax.set_ylabel("Количество записей")
            ax.set_title("Распределение цен", fontweight="bold")
            ax.legend()

        elif kind == "courses":
            df = pd.read_sql("""
                SELECT p.category AS category,
                       ROUND(AVG(pr.price)::numeric, 2) AS avg_price
                FROM prices pr
                JOIN products p ON pr.product_id = p.id
                GROUP BY p.category
                ORDER BY avg_price DESC
            """, ENGINE)

            df["avg_price"] = pd.to_numeric(df["avg_price"])

            ax.barh(
                df["category"],
                df["avg_price"],
                color="#4a90d9",
                edgecolor="white"
            )

            df_all = pd.read_sql("SELECT price FROM prices", ENGINE)
            df_all["price"] = pd.to_numeric(df_all["price"])
            overall_avg = df_all["price"].mean()

            ax.axvline(
                overall_avg,
                color="darkorange",
                linestyle="--",
                linewidth=1.3,
                label=f"Средняя цена: {overall_avg:.2f}"
            )

            ax.set_xlabel("Средняя цена")
            ax.set_title("Средняя цена по категориям", fontweight="bold")
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