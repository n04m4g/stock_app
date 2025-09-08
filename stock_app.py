import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="My Stock Market",
    page_icon="📈",
    layout="wide"
)

# Simple CSS styling
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    padding: 1rem;
    margin-bottom: 2rem;
    background: linear-gradient(90deg, #f0f0f0, #ffffff);
    border-radius: 10px;
}
.summary-box {
    background: #f8f9fa;
    padding: 2rem;
    border-radius: 10px;
    border: 2px solid #e9ecef;
    text-align: center;
    margin: 1rem 0;
}
.big-number-positive {
    font-size: 3rem;
    font-weight: bold;
    color: #28a745;
    margin: 1rem 0;
}
.big-number-negative {
    font-size: 3rem;
    font-weight: bold;
    color: #dc3545;
    margin: 1rem 0;
}
.trades-count {
    font-size: 1.2rem;
    color: #6c757d;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# Function to parse numbers
def parse_num(raw):
    if not raw or raw.strip() == "":
        return None
    
    raw = raw.replace('\u2212', '-')
    filtered = ''.join(ch for ch in raw if ch.isdigit() or ch in ['.', ',', '-', '+'])
    
    try:
        cleaned = filtered.replace(',', '')
        value = float(cleaned)
        return value
    except:
        return None

# Initialize session state
if 'rows' not in st.session_state:
    st.session_state['rows'] = []
if 'next_id' not in st.session_state:
    st.session_state['next_id'] = 1
if 'show_success' not in st.session_state:
    st.session_state['show_success'] = False

# Main header
st.markdown('<h1 class="main-header">📈 My Stock Market</h1>', unsafe_allow_html=True)

# Show success message
if st.session_state['show_success']:
    st.success("✅ Trade added successfully!")
    st.session_state['show_success'] = False

# Add trade form
st.markdown("## ➕ Add New Trade")

with st.form(key="trade_form", clear_on_submit=True):
    col1, col2, col3 = st.columns([3, 2, 4])
    
    with col1:
        amount_input = st.text_input(
            "Trade Amount", 
            placeholder="Profit: 1200, Loss: -800",
            help="Profit = positive number, Loss = negative number with minus sign"
        )
    
    with col2:
        fee_input = st.text_input("Commission", value="13")
    
    with col3:
        note_input = st.text_input("Notes", placeholder="e.g., Bought Apple, Sold Google...")
    
    submitted = st.form_submit_button("💾 Save Trade", use_container_width=True)
    
    if submitted:
        amount = parse_num(amount_input)
        fee = parse_num(fee_input) or 13
        
        if amount is None:
            st.error("❌ Please enter a valid amount")
        else:
            new_entry = {
                "id": st.session_state['next_id'],
                "timestamp": datetime.now(),
                "amount": amount,
                "fee": fee,
                "note": note_input or "No notes"
            }
            st.session_state['rows'].append(new_entry)
            st.session_state['next_id'] += 1
            st.session_state['show_success'] = True
            st.rerun()

# Display data if trades exist
if st.session_state['rows']:
    df = pd.DataFrame(st.session_state['rows'])
    df['net'] = df['amount'] - df['fee']
    df['cumulative'] = df['net'].cumsum()
    
    # Calculate overall summary
    final_result = df['net'].sum()
    total_trades = len(df)
    
    # Display main summary
    st.markdown("## 📊 My Summary")
    
    result_class = "big-number-positive" if final_result >= 0 else "big-number-negative"
    profit_loss_text = "Profit" if final_result >= 0 else "Loss"
    
    st.markdown(f"""
    <div class="summary-box">
        <h2>💰 Total {profit_loss_text}</h2>
        <div class="{result_class}">${abs(final_result):,.2f}</div>
        <div class="trades-count">From {total_trades} trades</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Cumulative results chart
    st.markdown("## 📈 Cumulative Performance Chart")
    
    fig = go.Figure()
    
    colors = ['green' if x >= 0 else 'red' for x in df['cumulative']]
    
    fig.add_trace(go.Scatter(
        x=list(range(1, len(df) + 1)),
        y=df['cumulative'],
        mode='lines+markers',
        name='Cumulative Amount',
        line=dict(color='blue', width=3),
        marker=dict(size=10, color=colors),
        hovertemplate='<b>Trade %{x}</b><br>' +
                     'Cumulative: $%{y:,.2f}<extra></extra>'
    ))
    
    # Zero line
    fig.add_hline(y=0, line_dash="dash", line_color="black", line_width=2)
    
    fig.update_layout(
        title="Your Cumulative Performance Over Time",
        xaxis_title="Trade Number",
        yaxis_title="Cumulative Amount ($)",
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("💡 This chart shows your cumulative balance after each trade. Green dots = overall profit, Red dots = overall loss.")
    
    # Table with cumulative amounts
    st.markdown("## 📋 All My Trades")
    
    display_df = df.copy()
    display_df['date'] = display_df['timestamp'].dt.strftime('%d/%m/%Y %H:%M')
    display_df = display_df.sort_values('timestamp', ascending=False)
    
    st.dataframe(
        display_df[['date', 'amount', 'fee', 'net', 'cumulative', 'note']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "date": "When",
            "amount": st.column_config.NumberColumn("Trade Amount", format="$%.2f"),
            "fee": st.column_config.NumberColumn("Commission", format="$%.2f"),
            "net": st.column_config.NumberColumn("Net P&L", format="$%.2f"),
            "cumulative": st.column_config.NumberColumn("Cumulative", format="$%.2f"),
            "note": "What Happened"
        }
    )
    
    # Actions with clean CSV export
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        # Create clean CSV export
        csv_data = []
        
        for _, row in df.iterrows():
            csv_data.append([
                int(row['id']),
                row['timestamp'].strftime('%d/%m/%Y %H:%M:%S'),
                float(row['amount']),
                float(row['fee']),
                float(row['net']),
                float(row['cumulative']),
                str(row['note'])
            ])
        
        # Create clean DataFrame for export
        export_df = pd.DataFrame(csv_data, columns=[
            'ID',
            'DATE_TIME', 
            'AMOUNT',
            'FEE',
            'NET',
            'CUMULATIVE',
            'NOTE'
        ])
        
        csv_string = export_df.to_csv(index=False)
        
        st.download_button(
            label="📥 Download Data",
            data=csv_string,
            file_name=f"stock_trades_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        if st.button("🗑️ Delete All", use_container_width=True):
            st.warning("⚠️ This will delete all your data!")
            if st.button("✅ Yes, Delete Everything"):
                st.session_state['rows'] = []
                st.session_state['next_id'] = 1
                st.rerun()

else:
    # Welcome screen
    st.markdown("""
    <div class="summary-box">
        <h2>👋 Welcome!</h2>
        <p>Track your stock market profits and losses with ease</p>
        <p><strong>How it works:</strong></p>
        <p>🔹 Made a profit? Enter a positive number (e.g., 1200)</p>
        <p>🔹 Had a loss? Enter a negative number (e.g., -800)</p>
        <p>🔹 The chart will show how your total balance changes over time</p>
    </div>
    """, unsafe_allow_html=True)
