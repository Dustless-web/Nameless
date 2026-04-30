import streamlit as st

def apply_neo_brutalism_styles():
    """Injects high-contrast, stark shadow CSS for the Neo-Brutalism look."""
    st.markdown("""
    <style>
        /* Base Page Styling */
        .stApp {
            background-color: #faf9f6;
            font-family: 'Space Mono', 'Courier New', monospace;
        }
        
        /* Headers with Pink/Teal Shadows */
        h1 {
            color: #000 !important;
            text-transform: uppercase;
            font-weight: 900 !important;
            border-bottom: 5px solid #000;
            padding-bottom: 10px;
            text-shadow: 4px 4px 0px #ff2a75;
            margin-bottom: 30px !important;
        }
        
        h2, h3 {
            color: #000 !important;
            text-transform: uppercase;
            font-weight: 800 !important;
            text-shadow: 2px 2px 0px #03c988;
        }

        /* Metric Box Styling */
        div[data-testid="stMetric"] {
            background-color: #ffde59; /* Yellow */
            border: 4px solid #000;
            padding: 20px;
            box-shadow: 8px 8px 0px #000;
        }
        
        /* Second column metric is Pink */
        div[data-testid="column"]:nth-of-type(2) div[data-testid="stMetric"] {
            background-color: #ff2a75; 
        }

        /* Metric Text formatting */
        div[data-testid="stMetricLabel"] * {
            color: #000 !important;
            font-weight: 900 !important;
            font-size: 18px !important;
        }
        
        div[data-testid="stMetricValue"] * {
            color: #000 !important;
            font-weight: 900 !important;
            font-size: 40px !important;
        }

        /* Tables & Charts */
        div[data-testid="stDataFrame"] > div {
            border: 4px solid #000;
            box-shadow: 6px 6px 0px #000;
        }
        
        hr { border-top: 4px solid #000 !important; }
    </style>
    """, unsafe_allow_html=True)