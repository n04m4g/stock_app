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

# Enhanced CSS styling
st.markdown("""
<style>
/* Header styling - left aligned with candlestick icon */
.header-container {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 15px;
    margin-bottom: 30px;
}
.header-text {
    font-size: 2.8rem;
    font-weight: bold;
    color: #1f77b4;
    margin: 0;
}
.header-icon {
    width: 50px;
    height: 50px;
    font-size: 3rem;
}

/* Compact summary styling */
.compact-summary {
    background: #f8f9fa;
    padding: 1.2rem;
    border-radius: 10px;
    border: 2px solid #e9ecef;
    margin: 1rem 0;
}
.summary-header {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 0.3rem;
    color: #333333;
}
.summary-value {
    font-size: 2.2rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
}
.summary-value.positive {
    color: #28a745;
}
.summary-value.negative {
    color: #dc3545;
}
.summary-info {
    font-size: 1rem;
    color: #666666;
    margin: 0;
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

# Main header - left aligned with candlestick icon
st.markdown("""
<div class="header-container">
    <div class="header-icon">📊</div>
    <div class="header-text">My Stock Market</div>
</div>
""", unsafe_allow_html=True)

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
            st.success("✅ Trade added successfully!")

# Display data if trades exist
if st.session_state['rows']:
    
    # Convert to DataFrame for calculations
    df = pd.DataFrame(st.session_state['rows'])
    df['net'] = df['amount'] - df['fee']
    df['cumulative'] = df['net'].cumsum()
    
    # Calculate overall summary
    final_result = df['net'].sum()
    total_trades = len(df)
    
    # Display compact summary
    st.markdown("## 📊 My Summary")
    
    result_class = "positive" if final_result >= 0 else "negative"
    profit_loss_text = "Total Profit" if final_result >= 0 else "Total Loss"
    sign = "" if final_result >= 0 else "-"
    
    st.markdown(f"""
    <div class="compact-summary">
        <div class="summary-header">{profit_loss_text}</div>
        <div class="summary-value {result_class}">{sign}${abs(final_result):,.2f}</div>
        <div class="summary-info">from {total_trades} trades</div>
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
    
    # Editable data section - SIMPLIFIED VERSION
    st.markdown("## 📝 Edit Trade History")
    st.info("💡 You can edit the values directly in the table below. Changes will be applied when you click outside the cell.")
    
    # Prepare data for editing - simpler approach
    edit_df = df.copy()
    edit_df['Date'] = edit_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
    
    # Create editable dataframe without dynamic rows to avoid the error
    edited_data = st.data_editor(
        edit_df[['id', 'Date', 'amount', 'fee', 'note']],
        column_config={
            "id": st.column_config.NumberColumn("ID", disabled=True),
            "Date": st.column_config.TextColumn("Date & Time"),
            "amount": st.column_config.NumberColumn("Amount ($)", format="%.2f"),
            "fee": st.column_config.NumberColumn("Fee ($)", format="%.2f"),
            "note": st.column_config.TextColumn("Notes", max_chars=100)
        },
        use_container_width=True,
        hide_index=True,
        disabled=['id']
    )
    
    # Simple update mechanism
    if st.button("💾 Save Changes", type="primary"):
        try:
            # Update the session state with edited data
            updated_rows = []
            for idx, row in edited_data.iterrows():
                # Parse the date back
                try:
                    parsed_date = datetime.strptime(row['Date'], '%Y-%m-%d %H:%M')
                except:
                    parsed_date = datetime.now()
                
                updated_rows.append({
                    "id": int(row['id']),
                    "timestamp": parsed_date,
                    "amount": float(row['amount']),
                    "fee": float(row['fee']),
                    "note": str(row['note'])
                })
            
            st.session_state['rows'] = updated_rows
            st.success("✅ Changes saved successfully!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error saving changes: {str(e)}")
    
    # Display current data table (read-only)
    st.markdown("## 📋 Current Trade History")
    
    display_df = df.copy()
    display_df['Date'] = display_df['timestamp'].dt.strftime('%d/%m/%Y %H:%M')
    display_df = display_df.sort_values('timestamp', ascending=False)
    
    st.dataframe(
        display_df[['Date', 'amount', 'fee', 'net', 'cumulative', 'note']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Date": "When",
            "amount": st.column_config.NumberColumn("Trade Amount", format="$%.2f"),
            "fee": st.column_config.NumberColumn("Commission", format="$%.2f"),
            "net": st.column_config.NumberColumn("Net P&L", format="$%.2f"),
            "cumulative": st.column_config.NumberColumn("Cumulative", format="$%.2f"),
            "note": "What Happened"
        }
    )
    
    # Actions with clean CSV export
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
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
        # Add individual trade button
        if st.button("➕ Add Individual Trade", use_container_width=True):
            # Show a simple form to add individual trade
            with st.expander("Add Trade Manually", expanded=True):
                with st.form("manual_trade_form"):
                    st.markdown("### Add Trade Details")
                    manual_amount = st.number_input("Amount ($)", value=0.0, format="%.2f")
                    manual_fee = st.number_input("Fee ($)", value=13.0, format="%.2f")
                    manual_note = st.text_input("Note", value="Manual entry")
                    manual_date = st.date_input("Date", value=datetime.now().date())
                    manual_time = st.time_input("Time", value=datetime.now().time())
                    
                    if st.form_submit_button("Add Trade"):
                        manual_datetime = datetime.combine(manual_date, manual_time)
                        new_manual_entry = {
                            "id": st.session_state['next_id'],
                            "timestamp": manual_datetime,
                            "amount": manual_amount,
                            "fee": manual_fee,
                            "note": manual_note
                        }
                        st.session_state['rows'].append(new_manual_entry)
                        st.session_state['next_id'] += 1
                        st.success("✅ Manual trade added!")
                        st.rerun()
    
    with col3:
        if st.button("🗑️ Delete All", use_container_width=True):
            if st.checkbox("✅ Confirm delete all data"):
                if st.button("🗑️ Yes, Delete Everything", type="secondary"):
                    st.session_state['rows'] = []
                    st.session_state['next_id'] = 1
                    st.success("All data deleted!")
                    st.rerun()

else:
    # Welcome screen
    st.markdown("""
    <div class="compact-summary">
        <h2>👋 Welcome!</h2>
        <p>Track your stock market profits and losses with ease</p>
        <p><strong>How it works:</strong></p>
        <p>🔹 Made a profit? Enter a positive number (e.g., 1200)</p>
        <p>🔹 Had a loss? Enter a negative number (e.g., -800)</p>
        <p>🔹 The chart will show how your total balance changes over time</p>
        <p>🔹 You can edit trades in the editing section below</p>
    </div>
    """, unsafe_allow_html=True)
        
