from utils.db import get_engine, get_schema, run_query

# Step 1: connect to the database
engine = get_engine("data/chinook.db")
print("✅ Connected to database!\n")

# Step 2: read and print the schema
schema = get_schema(engine)
print("📋 DATABASE SCHEMA:")
print(schema)

# Step 3: run a simple query to make sure it works
print("\n🔍 TEST QUERY — First 5 customers:")
df = run_query(engine, "SELECT FirstName, LastName, Country FROM Customer LIMIT 5")
print(df)