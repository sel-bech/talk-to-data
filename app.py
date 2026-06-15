import streamlit as st
import pandas as pd
from utils.db import get_engine, get_schema, run_query
from utils.ai_engine import generate_sql, generate_summary
from utils.visualizer import create_chart

# ─────────────────────────────────────────
# PAGE CONFIGURATION
# Must be the first Streamlit command
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Talk to Data",
    page_icon="🗄️",
    layout="wide"         # wide = use full browser width
)

# ─────────────────────────────────────────
# LOAD DATABASE (cached so it loads once)
# ─────────────────────────────────────────
@st.cache_resource
def load_db():
    """
    @st.cache_resource = Streamlit decorator that runs this
    function ONCE and reuses the result on every page refresh.
    Without this, we'd reconnect to the database on every click.
    
    'decorator' = a special tag starting with @ that adds
    extra behavior to a function automatically.
    """
    engine = get_engine("data/chinook.db")
    schema = get_schema(engine)
    return engine, schema

engine, schema = load_db()

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.title("🗄️ Talk to Data")
    st.markdown("Ask questions about the **Chinook music store** database in plain English.")
    
    st.divider()
    
    st.subheader("📋 Available Tables")
    tables = [
        "🎵 Artist", "💿 Album", "🎶 Track",
        "👤 Customer", "🧾 Invoice", "💰 InvoiceLine",
        "👔 Employee", "🎸 Genre"
    ]
    for table in tables:
        st.markdown(f"- {table}")
    
    st.divider()
    
    st.subheader("💡 Example Questions")
    examples = [
        "Which country has the most customers?",
        "Top 5 best selling artists?",
        "Total revenue per genre?",
        "How many tracks per album on average?",
        "Which employee has the most customers?"
    ]
    for example in examples:
        # When user clicks an example, it fills the input box
        if st.button(example, use_container_width=True):
            st.session_state.question = example

# ─────────────────────────────────────────
# MAIN PAGE
# ─────────────────────────────────────────
st.title("🗄️ Talk to Data")
st.markdown("Type a question in plain English — get SQL, charts, and insights automatically.")

st.divider()

# ─────────────────────────────────────────
# QUESTION INPUT
# ─────────────────────────────────────────

# session_state = Streamlit's way of remembering values
# between interactions. Like short-term memory for the app.
if "question" not in st.session_state:
    st.session_state.question = ""

question = st.text_input(
    label="Ask a question about your data:",
    placeholder="e.g. Which country has the most customers?",
    value=st.session_state.question
)

col1, col2 = st.columns([1, 5])
with col1:
    ask_button = st.button("🔍 Ask", type="primary", use_container_width=True)
with col2:
    clear_button = st.button("🗑️ Clear", use_container_width=True)

if clear_button:
    st.session_state.question = ""
    st.rerun()

# ─────────────────────────────────────────
# PROCESSING & RESULTS
# ─────────────────────────────────────────
if ask_button and question.strip():

    # Show a spinner while we process
    # 'spinner' = animated loading circle shown to user while
    # we wait for Gemini and the database to respond
    with st.spinner("🤖 Thinking..."):

        # STEP 1: Generate SQL
        sql_result = generate_sql(schema, question)

    if not sql_result["success"]:
        st.error(f"❌ Could not generate SQL: {sql_result['error']}")
        st.stop()

    sql = sql_result["sql"]

    # STEP 2: Run the SQL
    try:
        with st.spinner("⚙️ Running query..."):
            df = run_query(engine, sql)
    except Exception as e:
        st.error(f"❌ Query failed: {str(e)}")
        st.code(sql, language="sql")
        st.info("💡 Try rephrasing your question.")
        st.stop()

    # STEP 3: Show results
    if df.empty:
        st.warning("⚠️ The query returned no results. Try a different question.")
        st.stop()

    # ── Generated SQL (collapsible) ──
    with st.expander("🔧 View Generated SQL", expanded=False):
        """
        'expander' = a collapsible section. Collapsed by default
        so the UI looks clean, but user can click to see the SQL.
        """
        st.code(sql, language="sql")

    st.divider()

    # ── Chart + Table side by side ──
    col_chart, col_table = st.columns([3, 2])

    with col_chart:
        st.subheader("📊 Chart")
        with st.spinner("📈 Creating chart..."):
            fig = create_chart(question, df)

        if fig:
            # st.plotly_chart = renders an interactive Plotly chart
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📋 Showing as table (data too complex for a chart)")

    with col_table:
        st.subheader("📋 Data Table")
        st.dataframe(
            df,
            use_container_width=True,
            height=400
        )

    st.divider()

    # ── AI Summary ──
    st.subheader("💡 Key Insights")
    with st.spinner("✍️ Generating summary..."):
        summary = generate_summary(question, sql, df)
    st.info(summary)

    # ── Stats row ──
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Rows returned", df.shape[0])
    m2.metric("Columns", df.shape[1])
    m3.metric("Question length", f"{len(question)} chars")

elif ask_button and not question.strip():
    st.warning("⚠️ Please type a question first.")