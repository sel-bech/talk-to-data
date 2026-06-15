import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google import genai
import os
from dotenv import load_dotenv
from prompts.sql_prompt import build_chart_prompt

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-2.0-flash"


def detect_chart_type(user_question: str, df: pd.DataFrame) -> str:
    """
    Asks Gemini to pick the best chart type for our data.
    Falls back to 'table' if anything goes wrong.
    
    'fallback' = a safe default we use when something fails.
    Always have a fallback so your app never crashes on the user.
    """
    try:
        columns = list(df.columns)
        sample_data = df.head(5).to_string(index=False)

        prompt = build_chart_prompt(user_question, columns, sample_data)

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        # Clean the response — extract just the chart type word
        chart_type = response.text.strip().lower()

        # Make sure it's one of our valid options
        valid_types = ["bar", "line", "pie", "table"]
        if chart_type not in valid_types:
            return "table"  # fallback

        return chart_type

    except Exception:
        return "table"  # fallback if API fails


def get_best_columns(df: pd.DataFrame) -> tuple:
    """
    Automatically picks which column to use for X axis (categories)
    and which for Y axis (numbers).
    
    'tuple' = a pair of values in Python. Like (x_column, y_column).
    
    We look at the data types of each column:
    - 'object' type = text (names, countries) → good for X axis
    - 'int64' or 'float64' = numbers → good for Y axis
    """
    text_columns = df.select_dtypes(include=["object"]).columns.tolist()
    number_columns = df.select_dtypes(include=["int64", "float64"]).columns.tolist()

    # Pick first text column for X, first number column for Y
    x_col = text_columns[0] if text_columns else df.columns[0]
    y_col = number_columns[0] if number_columns else df.columns[-1]

    return x_col, y_col


def create_chart(user_question: str, df: pd.DataFrame):
    """
    Main function — detects chart type and draws the right chart.
    Returns a Plotly figure object ready to display in Streamlit.
    
    'figure' = Plotly's word for a chart object. We create it here
    and Streamlit will render (draw) it on the page.
    """

    # If dataframe is empty, return None
    if df.empty:
        return None

    # Detect the best chart type
    chart_type = detect_chart_type(user_question, df)

    # Get the best X and Y columns
    x_col, y_col = get_best_columns(df)

    # Build the chart based on detected type
    if chart_type == "bar":
        fig = px.bar(
            df,
            x=x_col,
            y=y_col,
            title=user_question,
            color=x_col,           # different color per bar
            color_discrete_sequence=px.colors.qualitative.Set2
        )

    elif chart_type == "line":
        fig = px.line(
            df,
            x=x_col,
            y=y_col,
            title=user_question,
            markers=True           # show dots on each data point
        )

    elif chart_type == "pie":
        fig = px.pie(
            df,
            names=x_col,
            values=y_col,
            title=user_question,
            color_discrete_sequence=px.colors.qualitative.Set2
        )

    else:
        # For 'table' type, return None — we'll show a dataframe table instead
        return None

    # Clean up the chart layout (appearance)
    fig.update_layout(
        title_font_size=16,
        showlegend=True,
        height=450,
        margin=dict(l=20, r=20, t=60, b=20)  # padding around chart
    )

    return fig