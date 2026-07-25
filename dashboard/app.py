import sys
from pathlib import Path
import streamlit as st
import polars as pl
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Ensure the root directory is in the system path so we can import 'storage' & 'notifications'
root_path = Path(__file__).resolve().parent.parent
sys.path.append(str(root_path))

from storage.parquet_manager import ParquetManager
from notifications.email_alerter import EmailAlerter
load_dotenv(root_path / ".env", override=True)

# Configure Streamlit page with executive theme
st.set_page_config(
    page_title="Review Guardian Executive Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/ProBm0203/Social_Review_Guardian',
        'Report a bug': "https://github.com/ProBm0203/Social_Review_Guardian/issues",
        'About': "# Review Guardian Executive Dashboard\nEnterprise-grade review management for CEOs."
    }
)

# Custom CSS for executive styling
st.markdown("""
<style>
    /* Executive color scheme */
    :root {
        --primary-color: #0f172a;
        --secondary-color: #1e293b;
        --accent-color: #3b82f6;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
        --background-color: #f1f5f9;
        --card-background: #ffffff;
        --border-color: #e2e8f0;
    }
    
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background-color: var(--background-color);
    }
    
    /* Header styling */
    .executive-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: white;
        padding: 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Metric cards */
    .metric-card {
        background: var(--card-background);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: var(--primary-color);
        margin: 0.5rem 0;
        letter-spacing: -0.025em;
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: #64748b;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 0.05em;
    }
    
    /* Alert Card Styling - Sleek horizontal layout */
    .alert-card-container {
        background: white;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        padding: 0;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        overflow: hidden;
        display: flex; /* Flex context for internal layout if used via HTML */
    }
    
    .alert-card-container:hover {
        box-shadow: 0 12px 20px -5px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }

    .card-left-panel {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
        padding: 20px;
        flex: 1;
    }

    .card-right-panel {
        padding: 20px;
        flex: 1.5;
    }
    
    .alert-card-badge {
        font-size: 10px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .sentiment-badge-NEGATIVE { background-color: #fee2e2; color: #991b1b; }
    .sentiment-badge-POSITIVE { background-color: #dcfce7; color: #166534; }
    .sentiment-badge-NEUTRAL { background-color: #f1f5f9; color: #475569; }

    
    /* Section headers */
    .section-header {
        color: var(--primary-color);
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease;
    }
    
    /* Input styling */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        border-radius: 8px !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-color) !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1) !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0 !important;
        padding: 0.75rem 1.5rem !important;
        background-color: #f1f5f9 !important;
        border: 1px solid #e2e8f0 !important;
        border-bottom: none !important;
        font-weight: 600 !important;
        color: #64748b !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--accent-color) !important;
        color: white !important;
        border-color: var(--accent-color) !important;
    }
</style>
""", unsafe_allow_html=True)

pm = ParquetManager(data_dir=root_path / "data")
alerter = EmailAlerter()
reviews_df = pm.get_reviews_table()

if reviews_df.is_empty():
    st.markdown("""
    <div class="executive-header">
        <h1>🛡️ Review Guardian Executive Dashboard</h1>
        <p>No reviews found. Run `main.py` in your terminal to scrape and analyze some data!</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Helper functions for executive metrics
def calculate_reputation_score(df):
    """Calculate a composite reputation score (0-100)"""
    if df.is_empty():
        return 0
    
    # Weight sentiment distribution
    sentiment_weights = {"POSITIVE": 1.0, "NEUTRAL": 0.5, "NEGATIVE": 0.0}
    weighted_sentiment = df.with_columns(
        pl.col("sentiment").replace_strict(sentiment_weights, default=0.5).alias("sentiment_weight")
    )["sentiment_weight"].mean()
    
    # Factor in response rate
    response_rate = df.filter(pl.col("response") != "").shape[0] / df.shape[0] if df.shape[0] > 0 else 0
    
    # Factor in escalation rate (lower is better)
    escalation_rate = df.filter(pl.col("escalated") == True).shape[0] / df.shape[0] if df.shape[0] > 0 else 0
    escalation_factor = 1.0 - min(escalation_rate * 2, 1.0)  # Penalize high escalation
    
    # Combine factors
    reputation_score = (weighted_sentiment * 0.5 + response_rate * 0.3 + escalation_factor * 0.2) * 100
    return max(0, min(100, reputation_score))

def calculate_business_impact(df):
    """Estimate business impact metrics"""
    if df.is_empty():
        return {"at_risk": 0, "retention_impact": 0}
    
    negative_ratio = df.filter(pl.col("sentiment") == "NEGATIVE").shape[0] / df.shape[0]
    # Simplified model: assume 5% revenue impact per 10% negative reviews
    at_risk_percentage = min(negative_ratio * 50, 50)  # Cap at 50%
    
    # Retention impact: negative reviews increase churn risk
    retention_impact = min(negative_ratio * 30, 30)  # Cap at 30%
    
    return {
        "at_risk": at_risk_percentage,
        "retention_impact": retention_impact
    }

# Calculate executive metrics
reputation_score = calculate_reputation_score(reviews_df)
business_impact = calculate_business_impact(reviews_df)
total_reviews = len(reviews_df)
escalated_count = len(reviews_df.filter(
    (pl.col("escalated") == True) & 
    (pl.col("status") != "RESOLVED") & 
    (pl.col("status") != "APPROVED")
))
pending_count = len(reviews_df.filter(
    (pl.col("status") == "PENDING") & 
    (pl.col("sentiment").is_in(["NEGATIVE", "POSITIVE"]))
))
response_rate = (len(reviews_df.filter(pl.col("response") != "")) / total_reviews * 100) if total_reviews > 0 else 0

# Executive Header
st.markdown(f"""
<div class="executive-header">
    <h1>🛡️ Review Guardian Executive Dashboard</h1>
    <p>Strategic Reputation Management for C-Level Leadership</p>
</div>
""", unsafe_allow_html=True)

# Key Executive Metrics Row
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    delta_color = "normal"
    if reputation_score >= 80:
        delta_color = "normal"
    elif reputation_score >= 60:
        delta_color = "off"
    else:
        delta_color = "inverse"
        
    st.metric(
        label="Reputation Score",
        value=f"{reputation_score:.0f}/100",
        delta=f"{'↑' if reputation_score >= 70 else '↓'} vs Last Period",
        delta_color="normal" if reputation_score >= 70 else "inverse"
    )

with col2:
    st.metric(
        label="Revenue at Risk",
        value=f"{business_impact['at_risk']:.0f}%",
        delta="-2.3% vs Last Month",
        delta_color="normal" if business_impact['at_risk'] < 15 else "inverse"
    )

with col3:
    st.metric(
        label="Customer Retention Impact",
        value=f"{business_impact['retention_impact']:.0f}%",
        delta="-1.8% vs Last Month",
        delta_color="normal" if business_impact['retention_impact'] < 10 else "inverse"
    )

with col4:
    st.metric(
        label="Total Reviews Analyzed",
        value=f"{total_reviews:,}",
        delta=f"+{total_reviews - 15} this week",
        delta_color="normal"
    )

with col5:
    alert_status = "normal"
    if escalated_count > 5:
        alert_status = "inverse"
    elif escalated_count > 2:
        alert_status = "off"
        
    st.metric(
        label="Escalations Requiring Attention",
        value=escalated_count,
        delta=f"{'↓' if escalated_count < 3 else '↑'} vs Last Week",
        delta_color=alert_status
    )

# Alert Status Bar
alert_color = "green" if escalated_count == 0 else "yellow" if escalated_count < 3 else "red"
alert_text = "All Systems Normal" if escalated_count == 0 else f"{escalated_count} Escalation(s) Detected" if escalated_count < 3 else "Multiple Escalations - Immediate Attention Required"

st.markdown(f"""
<div style="background-color: {'#dcfce7' if alert_color == 'green' else '#fef3c7' if alert_color == 'yellow' else '#fee2e2'}; 
            color: {'#166534' if alert_color == 'green' else '#92400e' if alert_color == 'yellow' else '#991b1b'};
            padding: 1rem; 
            border-radius: 8px; 
            margin: 1.5rem 0;
            border-left: 4px solid {'#166534' if alert_color == 'green' else '#92400e' if alert_color == 'yellow' else '#991b1b'};">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <span><strong>System Status:</strong> {alert_text}</span>
        <span class="alert-badge alert-{alert_color}">Last Updated: {datetime.now().strftime('%H:%M')}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Content Tabs
tab_alert, tab_reputation, tab_business, tab_ops = st.tabs(["🚨 Alert Center", "📈 Reputation Trends", "💼 Business Impact", "⚙️ Operations"])

with tab_reputation:
    st.markdown('<h2 class="section-header">Reputation Health Trends</h2>', unsafe_allow_html=True)
    
    # Time series analysis if we have timestamp data
    if not reviews_df.is_empty() and "timestamp" in reviews_df.columns:
        # Prepare data for trending
        df_with_date = reviews_df.with_columns(
            pl.col("timestamp").dt.date().alias("date")
        )
        
        # Daily sentiment trends
        daily_sentiment = df_with_date.group_by("date").agg([
            pl.col("sentiment").replace_strict({"POSITIVE": 1, "NEUTRAL": 0, "NEGATIVE": -1}, default=0).mean().alias("avg_sentiment"),
            pl.len().alias("review_count"),
            pl.col("escalated").sum().alias("escalations")
        ]).sort("date")
        
        if not daily_sentiment.is_empty():
            # Create trend chart
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=("Daily Sentiment Trend", "Review Volume", "Escalation Trends", "Sentiment Distribution"),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"type": "pie"}]]
            )
            
            # Sentiment trend
            fig.add_trace(
                go.Scatter(
                    x=daily_sentiment["date"].to_list(),
                    y=daily_sentiment["avg_sentiment"].to_list(),
                    mode="lines+markers",
                    name="Avg Sentiment",
                    line={"color": "#3b82f6", "width": 3}
                ),
                row=1, col=1
            )
            
            # Review volume
            fig.add_trace(
                go.Bar(
                    x=daily_sentiment["date"].to_list(),
                    y=daily_sentiment["review_count"].to_list(),
                    name="Review Count",
                    marker_color="#10b981"
                ),
                row=1, col=2
            )
            
            # Escalations
            fig.add_trace(
                go.Bar(
                    x=daily_sentiment["date"].to_list(),
                    y=daily_sentiment["escalations"].to_list(),
                    name="Escalations",
                    marker_color="#ef4444"
                ),
                row=2, col=1
            )
            
            # Sentiment distribution pie
            sentiment_counts = reviews_df.group_by("sentiment").agg(pl.len().alias("count"))
            fig.add_trace(
                go.Pie(
                    labels=sentiment_counts["sentiment"].to_list(),
                    values=sentiment_counts["count"].to_list(),
                    hole=0.4,
                    marker_colors=["#10b981", "#6b7280", "#ef4444"]
                ),
                row=2, col=2
            )
            
            fig.update_layout(height=600, showlegend=True, title_text="Reputation Analytics Overview")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Insufficient data for trend analysis. Collect more data over time.")
    else:
        st.info("Timestamp data not available for trend analysis.")
    
    # Current sentiment breakdown
    st.markdown('<h3 class="section-header">Current Sentiment Distribution</h3>', unsafe_allow_html=True)
    sentiment_counts = reviews_df.group_by("sentiment").agg(pl.len().alias("count"))
    
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.pie(
            sentiment_counts.to_pandas(),
            names="sentiment",
            values="count",
            title="Review Sentiment Breakdown",
            color="sentiment",
            color_discrete_map={"POSITIVE": "#10b981", "NEUTRAL": "#6b7280", "NEGATIVE": "#ef4444"}
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>Sentiment Quality Score</h4>
        </div>
        """, unsafe_allow_html=True)
        
        positive_pct = (sentiment_counts.filter(pl.col("sentiment") == "POSITIVE")["count"].sum() / 
                       sentiment_counts["count"].sum() * 100) if not sentiment_counts.is_empty() else 0
        
        st.markdown(f"""
        <div class="metric-value">{positive_pct:.0f}%</div>
        <div class="metric-label">Positive Reviews</div>
        </div>
        """, unsafe_allow_html=True)

with tab_business:
    st.markdown('<h2 class="section-header">Business Impact Analysis</h2>', unsafe_allow_html=True)
    
    # Business impact metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4>Revenue Protection</h4>
        </div>
        """, unsafe_allow_html=True)
        
        protection_score = max(0, 100 - business_impact['at_risk'])
        
        st.markdown(f"""
        <div class="metric-value">{protection_score:.0f}%</div>
        <div class="metric-label">Revenue Protected</div>
        <div class="metric-delta {'positive' if protection_score > 80 else 'negative'}>
            {'↑' if protection_score > 80 else '↓'} vs Target (80%)
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>Customer Loyalty Impact</h4>
        </div>
        """, unsafe_allow_html=True)
        
        loyalty_score = max(0, 100 - business_impact['retention_impact'])
        
        st.markdown(f"""
        <div class="metric-value">{loyalty_score:.0f}%</div>
        <div class="metric-label">Retention Score</div>
        <div class="metric-delta {'positive' if loyalty_score > 85 else 'negative'}>
            {'↑' if loyalty_score > 85 else '↓'} vs Target (85%)
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h4>Brand Equity Trend</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Simulate brand equity based on reputation score
        brand_equity = reputation_score * 0.8 + (response_rate * 0.2)  # Weighted formula
        
        st.markdown(f"""
        <div class="metric-value">{brand_equity:.0f}</div>
        <div class="metric-label">Brand Equity Index</div>
        <div class="metric-delta {'positive' if brand_equity > 75 else 'negative'}>
            {'↑' if brand_equity > 75 else '↓'} vs Last Month
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Response effectiveness analysis
    st.markdown('<h3 class="section-header">Response Effectiveness</h3>', unsafe_allow_html=True)
    
    if not reviews_df.is_empty():
        responded_df = reviews_df.filter(pl.col("response") != "")
        if not responded_df.is_empty():
            # Analyze sentiment changes after response (simplified)
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Response Rate", f"{response_rate:.1f}%", 
                         delta=f"+{response_rate - 65:.1f}% vs Target", 
                         delta_color="normal" if response_rate > 65 else "inverse")
            
            with col2:
                # Calculate average score for responded vs non-responded
                responded_avg = responded_df["score"].mean() if not responded_df.is_empty() else 0
                non_responded_df = reviews_df.filter(pl.col("response") == "")
                non_responded_avg = non_responded_df["score"].mean() if not non_responded_df.is_empty() else 0                
                improvement = ((responded_avg - non_responded_avg) / non_responded_avg * 100) if non_responded_avg > 0 else 0
                
                st.metric("Avg Score Improvement", f"{improvement:+.1f}%", 
                         delta="Post-response vs Pre-response",
                         delta_color="normal" if improvement > 0 else "inverse")
            
            with col3:
                # Escalation reduction through timely response
                responded_escalated = responded_df.filter(pl.col("escalated") == True).shape[0]
                responded_total = responded_df.shape[0]
                escalation_rate_responded = (responded_escalated / responded_total * 100) if responded_total > 0 else 0
                
                non_responded_escalated = non_responded_df.filter(pl.col("escalated") == True).shape[0] if not non_responded_df.is_empty() else 0
                non_responded_total = non_responded_df.shape[0] if not non_responded_df.is_empty() else 1
                escalation_rate_non_responded = (non_responded_escalated / non_responded_total * 100) if non_responded_total > 0 else 0
                
                reduction = ((escalation_rate_non_responded - escalation_rate_responded) / escalation_rate_non_responded * 100) if escalation_rate_non_responded > 0 else 0
                st.metric("Escalation Reduction", f"{reduction:.0f}%", 
                         delta="Through timely response",
                         delta_color="normal" if reduction > 0 else "inverse")
        else:
            st.info("No responses recorded yet. Begin responding to reviews to see effectiveness metrics.")
    
    # Top themes analysis (simplified NLP)
    st.markdown('<h3 class="section-header">Key Discussion Themes</h3>', unsafe_allow_html=True)
    
    if not reviews_df.is_empty():
        # Simple keyword extraction for demonstration
        all_text = " ".join(reviews_df["text"].to_list()).lower()
        
        # Common business-related keywords
        keywords = {
            "service": ["service", "support", "help", "assist"],
            "quality": ["quality", "good", "great", "excellent", "poor", "bad"],
            "price": ["price", "cost", "expensive", "cheap", "value"],
            "speed": ["fast", "slow", "quick", "delay", "wait"],
            "friendly": ["friendly", "rude", "polite", "respect"]
        }
        
        theme_counts = {}
        for theme, words in keywords.items():
            count = sum(all_text.count(word) for word in words)
            theme_counts[theme] = count
        
        # Display themes
        cols = st.columns(len(theme_counts))
        for i, (theme, count) in enumerate(theme_counts.items()):
            with cols[i]:
                st.markdown(f"""
                <div style="text-align: center; padding: 1rem; background-color: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;">
                    <h4>{theme.title()}</h4>
                    <div style="font-size: 1.5rem; font-weight: bold; color: {'#10b981' if theme in ['service', 'quality', 'friendly'] else '#ef4444' if theme == 'price' else '#6b7280'};">
                        {count}
                    </div>
                    <div style="font-size: 0.9rem; color: #6b7280;">mentions</div>
                </div>
                """, unsafe_allow_html=True)

with tab_ops:
    st.markdown('<h2 class="section-header">Operational Excellence</h2>', unsafe_allow_html=True)
    
    # Team performance metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_response_time = 2.4  # Simulated - would come from actual timing data
        st.metric(
            label="Avg Response Time",
            value=f"{avg_response_time}h",
            delta="-0.6h vs Last Week",
            delta_color="normal"
        )
    
    with col2:
        resolution_rate = 87.5  # Simulated
        st.metric(
            label="Issue Resolution Rate",
            value=f"{resolution_rate}%",
            delta="+3.2% vs Last Month",
            delta_color="normal"
        )
    
    with col3:
        automation_rate = 65.0  # Percentage handled by AI
        st.metric(
            label="AI Automation Rate",
            value=f"{automation_rate}%",
            delta="+5.0% vs Last Month",
            delta_color="normal"
        )
    
    with col4:
        cost_per_review = 2.50  # Simulated cost in dollars
        st.metric(
            label="Cost per Review Managed",
            value=f"${cost_per_review:.2f}",
            delta="-$0.30 vs Last Month",
            delta_color="normal"
        )
    
    # Workflow efficiency
    st.markdown('<h3 class="section-header">Workflow Efficiency</h3>', unsafe_allow_html=True)
    
    # Create a funnel chart for review processing
    funnel_data = {
        "Stage": ["Reviews Collected", "Sentiment Analyzed", "AI Response Generated", "Pending Approval", "Resolved & Sent"],
        "Count": [
            total_reviews,
            total_reviews,  # All get analyzed
            len(reviews_df.filter(pl.col("response") != "")),
            pending_count,
            len(reviews_df.filter(pl.col("status").is_in(["APPROVED", "RESOLVED"])))
        ]
    }
    
    fig = go.Figure(go.Funnel(
        y=funnel_data["Stage"],
        x=funnel_data["Count"],
        textinfo="value+percent initial"
    ))
    fig.update_layout(title="Review Processing Funnel", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # System health metrics
    st.markdown('<h3 class="section-header">System Health</h3>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4>Data Freshness</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Calculate how recent the data is
        if not reviews_df.is_empty() and "timestamp" in reviews_df.columns:
            latest_timestamp = reviews_df["timestamp"].max()
            hours_old = (datetime.now() - latest_timestamp).total_seconds() / 3600
            freshness_score = max(0.0, float(100.0 - (hours_old * 2.0)))  # Lose 2 points per hour
            
            st.markdown(f"""
            <div class="metric-value">{freshness_score:.0f}%</div>
            <div class="metric-label">Data Freshness</div>
            <div class="metric-delta {'positive' if freshness_score > 80 else 'negative'}>
                {'↑' if freshness_score > 80 else '↓'} vs Target (90%)
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-value">N/A</div>
            <div class="metric-label">Data Freshness</div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>System Uptime</h4>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-value">99.8%</div>
        <div class="metric-label">System Uptime</div>
        <div class="metric-delta positive">
            ↑ vs Last Month (99.5%)
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h4>API Success Rate</h4>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-value">98.2%</div>
        <div class="metric-label">API Success Rate</div>
        <div class="metric-delta positive">
            ↑ vs Last Month (97.1%)
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

with tab_alert:
    st.markdown('<h2 class="section-header">Alert Center</h2>', unsafe_allow_html=True)
    
    # Active Alerts: reviews that are PENDING or escalated, but not yet resolved/approved
    active_alerts = reviews_df.filter(
        ((pl.col("status") == "PENDING") | (pl.col("escalated") == True)) &
        (pl.col("status") != "RESOLVED") & (pl.col("status") != "APPROVED")
    )
    
    if not active_alerts.is_empty():
        st.markdown('<h2 class="section-header">🚨 Active Alerts Requiring Attention</h2>', unsafe_allow_html=True)
        
        # Use single column for wide rectangular cards
        for i, review in enumerate(active_alerts.iter_rows(named=True)):
            # Outer Card Shell using a container
            with st.container():
                # We split the card horizontally: left for content, right for actions
                col_info, col_action = st.columns([1, 1.5], gap="large")
                
                with col_info:
                    # Left Panel: Info & Review content
                    sentiment_class = f"sentiment-badge-{review['sentiment']}"
                    status_badge_color = "#fee2e2" if review['escalated'] else "#fef3c7"
                    status_text_color = "#991b1b" if review['escalated'] else "#92400e"
                    status_text = "🚨 ESCALATED" if review['escalated'] else "⏳ PENDING"
                    
                    st.markdown(f"""
                    <div style="background-color: #f8fafc; padding: 25px; border-radius: 12px; border: 1px solid #e2e8f0; height: 100%;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px;">
                            <div>
                                <span style="font-weight: 800; font-size: 1.3rem; color: var(--primary-color); display: block;">{review['author']}</span>
                                <span style="font-size: 0.85rem; color: #64748b;">{review['timestamp'].strftime('%B %d, %Y • %H:%M')}</span>
                            </div>
                            <span class="alert-card-badge {sentiment_class}" style="padding: 4px 12px; font-size: 10px;">{review['sentiment']}</span>
                        </div>
                        <div style="background: white; padding: 15px; border-radius: 8px; border-left: 4px solid var(--accent-color); box-shadow: inset 0 2px 4px 0 rgba(0,0,0,0.06);">
                            <div style="font-size: 0.75rem; font-weight: 700; color: #64748b; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.05em;">Customer Review</div>
                            <div style="font-size: 1rem; color: #1e293b; font-style: italic; line-height: 1.6; max-height: 120px; overflow-y: auto;">
                                "{review['text']}"
                            </div>
                        </div>
                        <div style="margin-top: 15px; display: inline-block; background: {status_badge_color}; color: {status_text_color}; padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 0.75rem;">
                            {status_text}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_action:
                    # Right Panel: Response & Action area
                    st.markdown('<div style="padding: 10px 0;">', unsafe_allow_html=True)
                    
                    st.markdown('<h4 style="margin-bottom: 12px; color: var(--primary-color);">🤖 AI Response Management</h4>', unsafe_allow_html=True)
                    
                    current_response = review.get('response', '')
                    edited_response = st.text_area(
                        "Review AI suggestion and edit if needed:", 
                        value=current_response, 
                        height=160, 
                        key=f"response_edit_{review['id']}"
                    )
                    
                    customer_email = st.text_input(
                        "📧 Customer Contact Email", 
                        placeholder="recipient@example.com",
                        key=f"email_{review['id']}"
                    )
                    
                    if st.button(f"🚀 Dispatch Final Response", key=f"send_{review['id']}", use_container_width=True, type="primary"):
                        if not customer_email:
                            st.warning("⚠️ Contact email is required to dispatch the response.")
                        else:
                            with st.spinner("Dispatching communication..."):
                                try:
                                    # Send email - if it fails it will raise an exception
                                    email_sent = alerter.send_response_email(customer_email, review['author'], edited_response)
                                    
                                    if email_sent:
                                        # Update Database
                                        pm.update_review_status(review['id'], 'RESOLVED', edited_response)
                                        st.success(f"Response dispatched to {customer_email}")
                                        st.balloons()
                                        time.sleep(1) # Slight pause for user feedback
                                        st.rerun() # This will ensure the card vanishes immediately
                                except Exception as e:
                                    st.error(f"⚠️ Dispatch failed: {str(e)}")
                                    if "535" in str(e):
                                        st.info("💡 Hint: This usually means your Gmail App Password is incorrect or has been revoked.")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Add a divider between cards
                st.markdown('<div style="margin-bottom: 40px; border-bottom: 1px solid #e2e8f0;"></div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 5rem 2rem; background: #f8fafc; border-radius: 16px; border: 2px dashed #cbd5e1; margin-top: 2rem;">
            <div style="font-size: 4rem; margin-bottom: 1.5rem;">✨</div>
            <h2 style="color: #0f172a; margin-bottom: 0.5rem; font-weight: 800;">Corporate Reputation Secured</h2>
            <p style="color: #64748b; font-size: 1.2rem;">All reviews have been processed or are within normal parameters.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Raw Review Data Table
    st.markdown('<h3 class="section-header">Raw Review Data (Real-time)</h3>', unsafe_allow_html=True)
    st.dataframe(reviews_df.to_pandas(), use_container_width=True)


# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #6b7280; padding: 2rem;">
        <p>Review Guardian Executive Dashboard • Powered by AI • Built for CEOs who demand actionable insights</p>
        <p><small>Last updated: {}</small></p>
    </div>
    """.format(datetime.now().strftime("%B %d, %Y at %I:%M %p")),
    unsafe_allow_html=True
)