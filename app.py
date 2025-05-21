import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Dark Theme Streamlit Config
st.set_page_config(page_title="Sales Dashboard", layout="centered")

# Dark Mode CSS
st.markdown("""
    <style>
        html, body, .stApp {
            background-color: #0e1117;  /* Dark background */
            color: #ffffff;             /* White text */
        }
        .main {
            background-color: #1e2130;  /* Darker container */
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
        }
        h1, h2, h3 {
            color: #a6d8ff;             /* Light blue headers */
        }
        .stMarkdown {
            color: #e0e0e0 !important;
        }
        .stDataFrame {
            background-color: #1e2130 !important;
        }
    </style>
""", unsafe_allow_html=True)

def get_db_engine():
    """Create PostgreSQL engine with SSL"""
    DB_URL = os.getenv("DATABASE_URL")
    if not DB_URL:
        st.error("❌ Database URL not found")
        st.stop()
    
    return create_engine(
        DB_URL,
        connect_args={
            "options": "-c client_encoding=utf8",
            "sslmode": "require"
        }
    )

@st.cache_data(ttl=300)
def load_data():
    """Load product sales data"""
    try:
        query = text("""
            SELECT "Product", COUNT(*) AS count
            FROM sales_data
            GROUP BY "Product";
        """)
        with engine.connect() as connection:
            result = connection.execute(query)
            return pd.DataFrame(result.mappings().all())
    except Exception as e:
        st.error(f"⚠️ Database error: {e}")
        return pd.DataFrame()

# Main App
with st.container():
    st.markdown('<div class="main">', unsafe_allow_html=True)
    
    engine = get_db_engine()
    df = load_data()

    st.title("📊 Sales Dashboard")
    st.subheader("🔥 Top Selling Products")

    if not df.empty:
        # Modern color scale with good contrast
        fig = px.bar(
            df,
            x="Product",
            y="count",
            title="Product Popularity",
            color="count",
            color_continuous_scale=px.colors.sequential.Plasma,  # High-contrast
            text="count",
            height=500
        )
        
        # Dark theme adjustments
        fig.update_layout(
            plot_bgcolor='#1e2130',
            paper_bgcolor='#1e2130',
            font=dict(color='white'),
            xaxis=dict(
                tickangle=-45,
                tickfont=dict(size=12, color='#a6d8ff'),
                gridcolor='#2a2f3d'
            ),
            yaxis=dict(
                gridcolor='#2a2f3d',
                tickfont=dict(color='#a6d8ff')
            ),
            coloraxis_colorbar=dict(
                title='Sales Count',
                tickfont=dict(color='white')
            ),
            title_font=dict(size=24, color='#a6d8ff'),
            hoverlabel=dict(
                bgcolor='#2a2f3d',
                font=dict(color='white')
            )
        )
        
        # Improve bar text visibility
        fig.update_traces(
            texttemplate='%{text}',
            textposition='outside',
            textfont=dict(color='white', size=12),
            marker_line_color='rgba(255,255,255,0.3)',
            marker_line_width=1
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data found")

    st.markdown('</div>', unsafe_allow_html=True)