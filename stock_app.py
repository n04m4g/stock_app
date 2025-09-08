import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go

# הגדרות עמוד
st.set_page_config(
    page_title="My Stock Market",
    page_icon="📈",
    layout="wide"
)

# CSS פשוט יותר
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

# פונקציה לפענוח מספרים
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

# אתחול נתוני הסשן
if 'rows' not in st.session_state:
    st.session_state['rows'] = []
if 'next_id' not in st.session_state:
    st.session_state['next_id'] = 1
if 'show_success' not in st.session_state:
    st.session_state['show_success'] = False

# כותרת ראשית
st.markdown('<h1 class="main-header">📈 my stock market</h1>', unsafe_allow_html=True)

# הצגת הודעת הצלחה
if st.session_state['show_success']:
    st.success("✅ העסקה התווספה!")
    st.session_state['show_success'] = False

# טופס הוספת עסקה - רק הבסיס
st.markdown("## ➕ הוספת עסקה")

with st.form(key="trade_form", clear_on_submit=True):
    col1, col2, col3 = st.columns([3, 2, 4])
    
    with col1:
        amount_input = st.text_input(
            "סכום העסקה", 
            placeholder="רווח: 1200, הפסד: -800",
            help="רווח = מספר חיובי,```סד = מספר שלילי ע```ינוס"
        )
    
    with col2:
        fee_input = st.text_input("עמלה", value="13")
    
    with col3:
        note_input = st.text_input("הערה", placeholder="למשל: קנית אפל, מכרת```גל...")
    
    submitted = st.form_submit_button("💾 שמור עסקה", use_container_width=True)
    
    if submitted:
        amount = parse_num(amount_input)
        fee = parse_num(fee_input) or 13
        
        if amount is None:
            st.error("❌ אנא הזינו סכום תקין")
        else:
            new_entry = {
                "id": st.session_state['next_id'],
                "stamp": datetime.now(),
                "amount": amount,
                "fee": fee,
                "note": note_input or "לל```ערות"
            }
            st.session_state['rows'].append(new_entry)
            st.session_state['next_id'] += 1
            st.session_state['show_success'] = True
            st.rerun()

# תצוגת הנתונים אם יש עסקאות
if st.session_state['rows']:
    df = pd.DataFrame(st.session_state['rows'])
    df['net'] = df['amount'] - df['fee']  # סכום נקי אחרי עמלה
    df['cumulative'] = df['net'].cumsum()  # סכום מצטבר - זה מה שהשתנה!
    
    # חישוב הסיכום הכולל
    final_result = df['net'].sum()  # כמה כסף עשיתי/הפסדתי בסך הכל
    total_trades = len(df)
    
    # תצוגת הסיכום הראשי - פשוט ובהיר
    st.markdown("## 📊 הסיכום שלי")
    
    # תיבה אחת גדולה עם התוצאה העיקר```    result_class = "big-number-positive" if final_result >= 0 else "big-number-negative"
    profit_loss_text = "רווח" if final_```ult >= 0 else "הפסד"
    
    st.markdown(f"""
    <div class="summary-box">
        <h2>💰 סה"כ {profit_loss_text}</h2>
        <div class="{result_class}">₪{abs(final_result):,.2f}</div>
        <div class="trades-count">מתוך {total_trades} עסקאות</div>
    </div>
    """, unsafe_allow_html=True)
    
    # גרף הסכום המצטבר - זה השינוי העיקרי!
    st.markdown("## 📈 גרף התוצאות המצטברות")
    
    fig = go.Figure()
    
    # קו שמראה את הסכום המצטבר לאורך הזמן
    colors = ['green' if x >= 0 else 'red' for x in df['cumulative']]
    
    fig.add_trace(go.Scatter(
        x=list(range(1, len(df) + 1)),
        y=df['cumulative'],
        mode='lines+markers',
        name='סכום מצטבר',
        line=dict(color='blue', width=3),
        marker=dict(size=10, color=colors),
        hovertemplate='<b>עסקה %{x}</b><br>' +
                     'סכום מצטבר: ₪%{y:,.2f}<extra></extra>'
    ))
    
    # קו אפס
    fig.add_hline(y=0, line_dash="dash", line_color="black",```ne_width=2)
    
    fig.update_layout(
        title="הסכום המצטבר שלך לאורך הזמן",```      xaxis_title="מספר עסקה",
        yaxis_title="סכום מצטבר (₪)",
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # הוספת הסבר לגרף
    st.info("💡 הגרף מראה את הסכום המצטבר שלכם לאח```ל עסקה. נקודה ירוקה```רווח כולל, נקודה א```ה = הפסד כול```)
    
    # טבלה עם הסכום המצטבר
    st.markdown("## 📋 כל העסקאות שלי")
    
    display_df = df.copy()
    display_df['תאריך'] = display_df['stamp'].dt.strftime('%d/%m/%Y %H:%M')
    display_df = display_df.sort_values('stamp', ascending=False)
    
    st.dataframe(
        display_df[['תאריך', 'amount', 'fee', 'net', 'cumulative', 'note']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "תאריך": "מתי",
            "amount": st.column_config.NumberColumn("סכום עסקה", format="₪%.2f"),
            "fee": st.column_config.NumberColumn("עמלה", format="₪%.2f"),
            "net": st.column_config.NumberColumn("רווח/הפסד נקי", format="₪%.2f"),
            "cumulative": st.column_config.NumberColumn("סכום מצטבר", format="₪%.2f"),
            "note": "מה קרה"
        }
    )
    
    # פעולות
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 הורד את הנתונים",
            data=csv,
            file_name=f"my_trades_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        if st.button("🗑️ מחק הכל", use_container_width=True):
            st.warning("⚠️ פעולה זו תמחק את כל הנתונים!")
            if st.button("✅ כן, מחק הכל"):
                st.session_state['rows'] = []
                st.session_state['next_id'] = 1
                st.rerun()

else:
    # מסך פתיחה
    st.markdown("""
    <div class="summary-box">
        <h2>👋 ברוכים הבאים!</h2>
        <p>כאן תוכלו לעקוב אחר הרווחים ו```סדים המצטברים שלכם בבורס```p>
        <p><strong>איך זה עובד?</strong></p>```      <p>🔹 עשיתם רווח? הזינו מספר חיובי (למשל: 1200)</p>
        <p>🔹 הפסדתם? הזינו מספר שלילי (למשל: -800)</p>
        <p>🔹 הגרף יראה לכם איך הסכום ה```ל משתנה לאורך זמן</p>
    </div>
    """, unsafe_allow_html=True)
