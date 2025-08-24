import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import get_db_manager, initialize_database

# Configure page
st.set_page_config(
    page_title="Database Administration",
    page_icon="🗄️",
    layout="wide"
)

st.title("🗄️ Database Administration")
st.markdown("---")

# Initialize database manager
db_manager = get_db_manager()

# Sidebar controls
st.sidebar.title("🔧 Database Controls")

# Initialize database
if st.sidebar.button("🚀 Initialize Database"):
    with st.spinner("Initializing database..."):
        success = initialize_database()
        if success:
            st.sidebar.success("✅ Database initialized successfully!")
        else:
            st.sidebar.error("❌ Failed to initialize database")

# Cleanup cache
if st.sidebar.button("🧹 Cleanup Cache"):
    if db_manager.initialized:
        with st.spinner("Cleaning up expired cache entries..."):
            success = db_manager.cleanup_expired_cache()
            if success:
                st.sidebar.success("✅ Cache cleanup completed!")
            else:
                st.sidebar.error("❌ Failed to cleanup cache")
    else:
        st.sidebar.warning("Database not initialized")

# Main content
if not db_manager.initialized:
    st.error("🚫 Database not initialized or connection failed")
    st.info("""
    **To enable database features:**
    1. Ensure PostgreSQL is running
    2. Set the DATABASE_URL environment variable
    3. Click "Initialize Database" in the sidebar
    """)
    st.stop()

# Database statistics
st.subheader("📊 Database Statistics")

# Get database stats
stats = db_manager.get_database_stats()

if stats['status'] == 'active':
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Analyses", stats.get('total_analyses', 0))
    
    with col2:
        st.metric("Portfolio Snapshots", stats.get('total_portfolios', 0))
    
    with col3:
        st.metric("Active Cache Entries", stats.get('active_cache', 0))
    
    with col4:
        st.metric("Recent Analyses (7d)", stats.get('recent_analyses_7d', 0))

# Analysis history
st.subheader("📈 Analysis History")

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["Recent Analyses", "Portfolio Snapshots", "Cache Status"])

with tab1:
    # Get analysis history
    analysis_history = db_manager.get_analysis_history(limit=100)
    
    if analysis_history:
        # Convert to DataFrame
        history_df = pd.DataFrame(analysis_history)
        history_df['created_at'] = pd.to_datetime(history_df['created_at'])
        
        # Analysis type distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Analysis Type Distribution**")
            type_counts = history_df['analysis_type'].value_counts()
            fig_pie = px.pie(
                values=type_counts.values,
                names=type_counts.index,
                title="Analysis Types"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.markdown("**Success Rate**")
            success_counts = history_df['success'].value_counts()
            fig_success = px.bar(
                x=['Success', 'Failed'],
                y=[success_counts.get(True, 0), success_counts.get(False, 0)],
                title="Analysis Success Rate",
                color=['Success', 'Failed'],
                color_discrete_map={'Success': 'green', 'Failed': 'red'}
            )
            st.plotly_chart(fig_success, use_container_width=True)
        
        # Timeline of analyses
        st.markdown("**Analysis Timeline**")
        history_df['date'] = history_df['created_at'].dt.date
        daily_counts = history_df.groupby(['date', 'analysis_type']).size().reset_index(name='count')
        
        fig_timeline = px.bar(
            daily_counts,
            x='date',
            y='count',
            color='analysis_type',
            title="Daily Analysis Activity"
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Recent analysis details
        st.markdown("**Recent Analysis Details**")
        
        # Display recent analyses in a table
        display_columns = ['created_at', 'analysis_type', 'success', 'symbols']
        recent_display = history_df[display_columns].head(20).copy()
        recent_display['symbols'] = recent_display['symbols'].apply(lambda x: ', '.join(x) if isinstance(x, list) else str(x))
        recent_display['created_at'] = recent_display['created_at'].dt.strftime('%Y-%m-%d %H:%M')
        
        st.dataframe(recent_display, use_container_width=True)
        
    else:
        st.info("No analysis history found. Run some analyses to see data here.")

with tab2:
    # Portfolio snapshots
    portfolio_snapshots = db_manager.get_portfolio_snapshots(limit=50)
    
    if portfolio_snapshots:
        snapshots_df = pd.DataFrame(portfolio_snapshots)
        snapshots_df['created_at'] = pd.to_datetime(snapshots_df['created_at'])
        
        # Portfolio metrics overview
        st.markdown("**Portfolio Snapshots Overview**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Portfolio count by period
            if 'period' in snapshots_df.columns:
                period_counts = snapshots_df['period'].value_counts()
                fig_periods = px.bar(
                    x=period_counts.index,
                    y=period_counts.values,
                    title="Portfolios by Analysis Period"
                )
                st.plotly_chart(fig_periods, use_container_width=True)
        
        with col2:
            # Portfolio count by benchmark
            if 'benchmark' in snapshots_df.columns:
                benchmark_counts = snapshots_df['benchmark'].value_counts()
                fig_benchmarks = px.pie(
                    values=benchmark_counts.values,
                    names=benchmark_counts.index,
                    title="Benchmark Usage"
                )
                st.plotly_chart(fig_benchmarks, use_container_width=True)
        
        # Portfolio details table
        st.markdown("**Portfolio Details**")
        display_cols = ['created_at', 'portfolio_name', 'symbols', 'benchmark', 'period']
        portfolio_display = snapshots_df[display_cols].copy()
        portfolio_display['symbols'] = portfolio_display['symbols'].apply(lambda x: ', '.join(x) if isinstance(x, list) else str(x))
        portfolio_display['created_at'] = portfolio_display['created_at'].dt.strftime('%Y-%m-%d %H:%M')
        
        st.dataframe(portfolio_display, use_container_width=True)
        
    else:
        st.info("No portfolio snapshots found. Save some portfolio analyses to see data here.")

with tab3:
    # Cache status
    st.markdown("**Market Data Cache Status**")
    
    if db_manager.initialized:
        # Get cache statistics from database stats
        cache_stats = {
            'Total Entries': stats.get('cache_entries', 0),
            'Active Entries': stats.get('active_cache', 0),
            'Expired Entries': stats.get('cache_entries', 0) - stats.get('active_cache', 0)
        }
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Cache Entries", cache_stats['Total Entries'])
        
        with col2:
            st.metric("Active Entries", cache_stats['Active Entries'])
        
        with col3:
            st.metric("Expired Entries", cache_stats['Expired Entries'])
        
        # Cache efficiency visualization
        if cache_stats['Total Entries'] > 0:
            labels = ['Active', 'Expired']
            values = [cache_stats['Active Entries'], cache_stats['Expired Entries']]
            
            fig_cache = px.pie(
                values=values,
                names=labels,
                title="Cache Entry Status",
                color_discrete_map={'Active': 'green', 'Expired': 'red'}
            )
            st.plotly_chart(fig_cache, use_container_width=True)
    
    else:
        st.error("Database connection not available")

# Database configuration info
st.subheader("⚙️ Database Configuration")

config_info = {
    "Database Status": "✅ Connected" if db_manager.initialized else "❌ Not Connected",
    "Engine": "PostgreSQL" if db_manager.initialized else "N/A",
    "Connection Pool": "Active" if db_manager.initialized else "N/A",
    "Tables Created": "Yes" if db_manager.initialized else "No"
}

for key, value in config_info.items():
    st.text(f"{key}: {value}")

# Export functionality
st.subheader("📤 Data Export")

col1, col2 = st.columns(2)

with col1:
    if st.button("📊 Export Analysis History"):
        if analysis_history:
            history_df = pd.DataFrame(analysis_history)
            csv = history_df.to_csv(index=False)
            st.download_button(
                label="⬇️ Download Analysis History CSV",
                data=csv,
                file_name=f"analysis_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

with col2:
    if st.button("💼 Export Portfolio Snapshots"):
        if portfolio_snapshots:
            portfolios_df = pd.DataFrame(portfolio_snapshots)
            csv = portfolios_df.to_csv(index=False)
            st.download_button(
                label="⬇️ Download Portfolio Snapshots CSV",
                data=csv,
                file_name=f"portfolio_snapshots_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )