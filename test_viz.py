from utils.db import get_engine, get_schema, run_query
from utils.ai_engine import generate_sql
from utils.visualizer import create_chart, detect_chart_type

engine = get_engine("data/chinook.db")
schema = get_schema(engine)

# Test different types of questions to see different chart types
test_questions = [
    "What are the top 10 countries by number of customers?",
    "What is the total sales amount per genre?",
    "Show me the total revenue per billing country"
]

for question in test_questions:
    print(f"\n{'='*60}")
    print(f"❓ {question}")

    result = generate_sql(schema, question)
    if not result["success"]:
        print(f"❌ SQL Error: {result['error']}")
        continue

    sql = result["sql"]
    print(f"🔧 SQL: {sql}")

    df = run_query(engine, sql)
    print(f"📊 Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print(df.head(3).to_string(index=False))

    chart_type = detect_chart_type(question, df)
    print(f"📈 Detected chart type: {chart_type}")

    fig = create_chart(question, df)
    if fig:
        # Save chart as HTML file so we can open it in browser
        filename = f"test_chart_{test_questions.index(question)+1}.html"
        fig.write_html(filename)
        print(f"✅ Chart saved → open {filename} in your browser to see it!")
    else:
        print("📋 Chart type is table — will show as dataframe in Streamlit")