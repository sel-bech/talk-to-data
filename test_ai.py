from utils.db import get_engine, get_schema, run_query
from utils.ai_engine import generate_sql, generate_summary

# Connect to database
engine = get_engine("data/chinook.db")
schema = get_schema(engine)

# Test questions to try
questions = [
    "Which country has the most customers?",
    "What are the top 5 best selling artists?",
    "What is the total revenue per country?"
]

for question in questions:
    print(f"\n{'='*60}")
    print(f"❓ Question: {question}")
    
    # Step 1: generate SQL
    result = generate_sql(schema, question)
    
    if not result["success"]:
        print(f"❌ Error: {result['error']}")
        continue
    
    sql = result["sql"]
    print(f"\n🔧 Generated SQL:\n{sql}")
    
    # Step 2: run the SQL on the database
    try:
        df = run_query(engine, sql)
        print(f"\n📊 Results ({len(df)} rows):")
        print(df.to_string(index=False))
        
        # Step 3: generate plain English summary
        summary = generate_summary(question, sql, df)
        print(f"\n💡 Summary: {summary}")
        
    except Exception as e:
        print(f"❌ Query failed: {e}")
        print("The AI wrote invalid SQL. This can happen — we'll handle it in the UI.")