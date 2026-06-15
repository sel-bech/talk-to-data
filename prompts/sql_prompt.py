def build_chart_prompt(user_question: str, columns: list, sample_data: str) -> str:
    """
    Asks Gemini to look at our data columns and decide
    which chart type fits best.
    
    'columns' = list of column names e.g. ["Country", "total_customers"]
    'sample_data' = first few rows as text so Gemini understands the data shape
    """
    prompt = f"""
You are a data visualization expert.

A user asked: "{user_question}"

The query returned a table with these columns: {columns}

Here is a sample of the data:
{sample_data}

Choose the BEST chart type to visualize this data.
Reply with ONLY one word from this list: bar, line, pie, table

Rules:
- bar → comparing values across categories (countries, artists, genres)
- line → data over time (months, years, dates)
- pie → percentages or proportions (max 8 categories)
- table → more than 8 columns, or complex mixed data

Reply with one word only.
"""
    return prompt

def build_sql_prompt(schema: str, user_question: str) -> str:
    """
    Builds the prompt we send to Gemini.
    We give it:
    1. The database schema (so it knows what tables/columns exist)
    2. The user's question (what they want to know)
    And we tell it exactly what to return.
    """
    prompt = f"""
You are an expert SQL analyst. You are working with a SQLite database.

Here is the database schema (the structure of all tables and columns):
{schema}

The user asked this question:
"{user_question}"

Your job:
1. Write a single valid SQLite SQL query that answers the question
2. Return ONLY the raw SQL query — no explanation, no markdown, no backticks
3. Make sure all column names and table names match the schema exactly
4. Always use LIMIT 100 unless the user asks for more

Return only the SQL query, nothing else.
"""
    return prompt


def build_summary_prompt(user_question: str, sql: str, results: str) -> str:
    """
    After we run the SQL and get results, we send ANOTHER prompt
    to Gemini asking it to explain the results in plain English.
    """
    prompt = f"""
You are a data analyst assistant. A user asked a question about a database.

User question: "{user_question}"

SQL query that was run:
{sql}

Query results:
{results}

Write a short, clear summary (2-4 sentences) of what the results show.
Highlight the most important finding. Use simple language, no technical jargon.
"""
    return prompt