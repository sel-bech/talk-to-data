import os
import re
from dotenv import load_dotenv
import google.generativeai as genai
from prompts.sql_prompt import build_sql_prompt, build_summary_prompt

# Load our secret API key from the .env file
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create the Gemini model object once, reuse it for all requests
model = genai.GenerativeModel("gemini-2.5-flash-lite")


def clean_sql(raw_response: str) -> str:
    """
    Gemini sometimes wraps SQL in markdown code blocks like:
```sql
    SELECT * FROM ...
```
    This function strips all that away and returns clean SQL only.
    
    'regex' (re module) = a powerful tool for finding/replacing
    patterns in text. Think of it as an advanced Ctrl+F.
    """
    # Remove markdown code blocks if present
    cleaned = re.sub(r"```(?:sql)?", "", raw_response)
    cleaned = re.sub(r"```", "", cleaned)
    
    # Remove any leading/trailing whitespace or newlines
    cleaned = cleaned.strip()
    
    return cleaned


def is_safe_sql(sql: str) -> bool:
    """
    Basic safety check — we only allow SELECT queries.
    We never want the AI to accidentally DELETE or DROP our data.
    
    'upper()' = converts text to uppercase so we can check
    regardless of how Gemini capitalized the SQL.
    """
    sql_upper = sql.upper().strip()
    
    # Block any dangerous SQL commands
    dangerous_keywords = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "TRUNCATE", "CREATE"]
    
    for keyword in dangerous_keywords:
        if keyword in sql_upper:
            return False
    
    # Must start with SELECT
    if not sql_upper.startswith("SELECT"):
        return False
    
    return True


def generate_sql(schema: str, user_question: str) -> dict:
    """
    Main function — takes the schema and user question,
    asks Gemini to write SQL, cleans it, checks it's safe,
    and returns it.
    
    Returns a 'dict' (dictionary) with either:
    - {"success": True,  "sql": "SELECT ..."}
    - {"success": False, "error": "reason why it failed"}
    
    'dict' = a key-value store in Python. Like a real dictionary:
    you look up a word (key) and get its definition (value).
    Example: {"name": "Ahmed", "age": 25}
    """
    try:
        # Build the prompt
        prompt = build_sql_prompt(schema, user_question)
        
        # Send to Gemini and wait for response
        response = model.generate_content(prompt)
        
        # Get the text from the response
        raw_sql = response.text
        
        # Clean it (remove markdown etc.)
        sql = clean_sql(raw_sql)
        
        # Safety check
        if not is_safe_sql(sql):
            return {
                "success": False,
                "error": "Generated query contains unsafe operations. Only SELECT queries are allowed."
            }
        
        return {"success": True, "sql": sql}
    
    except Exception as e:
        # If ANYTHING goes wrong, catch the error and return it
        # instead of crashing the whole app
        return {"success": False, "error": str(e)}


def generate_summary(user_question: str, sql: str, results_df) -> str:
    """
    Takes the query results (as a pandas DataFrame) and asks
    Gemini to summarize them in plain English.
    
    We convert the DataFrame to a string so Gemini can read it.
    """
    try:
        # Convert the dataframe table to a readable text format
        # head(20) = only take first 20 rows so we don't send too much text
        results_as_text = results_df.head(20).to_string(index=False)
        
        # Build the summary prompt
        prompt = build_summary_prompt(user_question, sql, results_as_text)
        
        # Ask Gemini to summarize
        response = model.generate_content(prompt)
        
        return response.text
    
    except Exception as e:
        return f"Could not generate summary: {str(e)}"