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

/* Old big summary box - remove */
.summary-box {
    display: none;
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

# Main header - left aligned with candlestick icon
st.markdown("""
<div class="header-container">
    <div class="header-icon">📊</div>
    <div class="header-text">My Stock Market</div>
</div>
""", unsafe_allow_html=True)

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
    
    # Convert to DataFrame for calculations
    df = pd.DataFrame(st.session_state['rows'])
    df['net'] = df['amount'] - df['fee']
    df['cumulative'] = df['net'].cumsum()
    
    # Editable data section
    st.markdown("## 📝 Edit Trade History")
    st.info("💡 Double-click any cell to edit it. You can also add or delete rows using the controls at the bottom of the table.")
    
    # Prepare data for editing
    edit_df = df.copy()
    edit_df['date'] = edit_df['timestamp'].dt.strftime('%Y-%m-%d')
    edit_df['time'] = edit_df['timestamp'].dt.strftime('%H:%M:%S')
    
    # Create editable dataframe
    edited_df = st.data_editor(
        edit_df[['id', 'date', 'time', 'amount', 'fee', 'note']],
        column_config={
            "id": st.column_config.NumberColumn("ID", disabled=True),
            "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
            "time": st.column_config.TimeColumn("Time", format="HH:mm:ss"),
            "amount": st.column_config.NumberColumn("Amount", format="%.2f"),
            "fee": st.column_config.NumberColumn("Fee", format="%.2f"),
            "note": st.column_config.TextColumn("Notes", max_chars=100)
        },
        num_rows="dynamic",
        use_container_width=True,
        key="trade_editor"
    )
    
    # Update session state if data changed
    if len(edited_df) != len(df) or not edited_df[['amount', 'fee', 'note']].equals(edit_df[['amount', 'fee', 'note']]):
        
        # Convert edited data back to session state format
        new_rows = []
        max_id = max([row['id'] for row in st.session_state['rows']], default=0)
        
        for idx, row in edited_df.iterrows():
            try:
                # Combine date and time
                date_str = str(row['date']) if pd.notna(row['date']) else datetime.now().strftime('%Y-%m-%d')
                time_str = str(row['time']) if pd.notna(row['time']) else "00:00:00"
                
                timestamp = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M:%S')
                
                # Handle new rows (no ID or ID is NaN)
                trade_id = row['id'] if pd.notna(row['id']) and row['id'] > 0 else max_id + 1
                if pd.isna(row['id']) or row['id'] <= 0:
                    max_id += 1
                    trade_id = max_id
                
                new_rows.append({
                    "id": int(trade_id),
                    "timestamp": timestamp,
                    "amount": float(row['amount']) if pd.notna(row['amount']) else 0.0,
                    "fee": float(row['fee']) if pd.notna(row['fee']) else 13.0,
                    "note": str(row['note']) if pd.notna(row['note']) else "No notes"
                })
            except (ValueError, TypeError) as e:
                st.error(f"Error processing row {idx}: {str(e)}")
                continue
        
        # Update session state and next_id
        st.session_state['rows'] = new_rows
        st.session_state['next_id'] = max([row['id'] for row in new_rows], default=0) + 1
        
        st.success("✅ Changes saved successfully!")
        st.rerun()
    
    # Recalculate with updated data
    df = pd.DataFrame(st.session_state['rows'])
    if not df.empty:
        df['net'] = df['amount'] - df['fee']
        df['cumulative'] = df['net'].cumsum()
        
        # Calculate overall summary
        final_result = df['net'].sum()
        total_trades = len(df)
        
        # Display compact summary - NEW DESIGN
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
    <div class="compact-summary">
        <h2>👋 Welcome!</h2>
        <p>Track your stock market profits and losses with ease</p>
        <p><strong>How it works:</strong></p>
        <p>🔹 Made a profit? Enter a positive number (e.g., 1200)</p>
        <p>🔹 Had a loss? Enter a negative number (e.g., -800)</p>
        <p>🔹 The chart will show how your total balance changes over time</p>
        <p>🔹 Edit any trade by double-clicking in the edit table</p>
    </div>
    """, unsafe_allow_html=True)
