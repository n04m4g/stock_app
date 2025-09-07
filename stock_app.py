import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# הגדרות עמוד
st.set_page_config(
    page_title="My Stock Market",
    page_icon="📈",
    layout="wide"
)

# CSS מותאם לעיצוב
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
.kpi-card {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 10px;
    border-left: 4px solid #1f77b4;
    margin: 0.5rem 0;
}
.positive {
    color: #28a745;
    font-weight: bold;
}
.negative {
    color: #dc3545;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# פונקציה לפענוח מספרים כולל ניקוי תווים
def parse_num(raw):
    """
    פונקציה לפענוח מספרים התומכת בפורמטים שונים:
    - מינוס יוניקוד (−) → מינוס רגיל (-)
    - פסיקים כמפרידי אלפים
    - נקודות עשרוניות
    - מספרים שליליים
    """
    if not raw or raw.strip() == "":
        return None
    
    # החלפת מינוס יוניקוד במינוס רגיל
    raw = raw.replace('\u2212', '-')
    
    # השארת תווים רלוונטיים בלבד
    filtered = ''.join(ch for ch in raw if ch.isdigit() or ch in ['.', ',', '-', '+'])
    
    try:
        # הסרת פסיקים והמרה לנקודות עשרוניות
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

# כותרת ראשית
st.markdown('<h1 class="main-header">📈 my stock market</h1>', unsafe_allow_html=True)

# טופס הוספת עסקה
st.markdown("## הוספת עסקה חדשה")

col1, col2, col3, col4 = st.columns([3, 2, 3, 2])

with col1:
    amount_input = st.text_input("סכום עסקה", placeholder="למשל: 1,200 או -850", key="amount_field")

with col2:
    fee_input = st.text_input("עמלה", value="13", key="fee_field")

with col3:
    note_input = st.text_input("הערה", placeholder="תיאור העסקה...", key="note_field")

with col4:
    st.markdown("<br>", unsafe_allow_html=True)
    add_btn = st.button("➕ הוסף עסקה", use_container_width=True)

# כפתורי עזר מתמטיים
st.markdown("### כפתורי עזר")
col_btn1, col_btn2, col_btn3 = st.columns(3)

with col_btn1:
    minus_btn = st.button("➖ מינוס", use_container_width=True)

with col_btn2:
    plus_btn = st.button("➕ פלוס", use_container_width=True)

with col_btn3:
    flip_btn = st.button("± הפוך סימן", use_container_width=True)

# טיפול בכפתורי עזר
if minus_btn:
    current_amount = st.session_state.get('amount_field', '')
    st.session_state['amount_field'] = current_amount + '-'
    st.rerun()

if plus_btn:
    current_amount = st.session_state.get('amount_field', '')
    st.session_state['amount_field'] = current_amount + '+'
    st.rerun()

if flip_btn:
    current_amount = st.session_state.get('amount_field', '')
    if current_amount:
        num = parse_num(current_amount)
        if num is not None:
            st.session_state['amount_field'] = str(-num)
            st.rerun()

# טיפול בהוספת עסקה
if add_btn:
    amount = parse_num(amount_input)
    fee = parse_num(fee_input)
    
    if fee is None:
        fee = 13
    
    if amount is None:
        st.error("❌ סכום עסקה לא תקין. יש להזין מספר חוקי.")
    else:
        new_entry = {
            "id": st.session_state['next_id'],
            "stamp": datetime.now(),
            "amount": amount,
            "fee": fee,
            "note": note_input or "אין הערות"
        }
        st.session_state['rows'].append(new_entry)
        st.session_state['next_id'] += 1
        st.success("✅ העסקה התווספה בהצלחה!")
        
        # ניקוי השדות
        st.session_state['amount_field'] = ''
        st.session_state['fee_field'] = '13'
        st.session_state['note_field'] = ''
        st.rerun()

# עיבוד הנתונים ותצוגה
if st.session_state['rows']:
    df = pd.DataFrame(st.session_state['rows'])
    df['net'] = df['amount'] - df['fee']
    df['total'] = df['net'].cumsum()
    
    # חישובי KPI
    total_net = df['net'].sum()
    total_trades = len(df)
    total_fees = df['fee'].sum()
    
    wins = (df['net'] > 0).sum()
    losses = (df['net'] < 0).sum()
    wins_amount = df.loc[df['net'] > 0, 'net'].sum() if wins > 0 else 0
    losses_amount = df.loc[df['net'] < 0, 'net'].sum() if losses > 0 else 0
    
    best_trade = df['net'].max()
    worst_trade = df['net'].min()
    
    # הצגת כרטיסי KPI
    st.markdown("## 📊 מדדי ביצועים")
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        color_class = "positive" if total_net >= 0 else "negative"
        st.markdown(f"""
        <div class="kpi-card">
            <h4>סה"כ נטו</h4>
            <h2 class="{color_class}">₪{total_net:,.2f}</h2>
            <p>{total_trades} עסקאות</p>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col2:
        st.markdown(f"""
        <div class="kpi-card">
            <h4>ניצחונות / הפסדים</h4>
            <h2>{wins} / {losses}</h2>
            <p class="positive">+₪{wins_amount:,.2f}</p>
            <p class="negative">-₪{abs(losses_amount):,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col3:
        st.markdown(f"""
        <div class="kpi-card">
            <h4>עסקה טובה / גרועה</h4>
            <p class="positive">₪{best_trade:,.2f}</p>
            <p class="negative">₪{worst_trade:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col4:
        st.markdown(f"""
        <div class="kpi-card">
            <h4>סך עמלות</h4>
            <h2 class="negative">₪{total_fees:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # גרף מגמות
    st.markdown("## 📈 גרף מגמות עסקאות")
    
    fig = go.Figure()
    
    # קו העסקאות
    fig.add_trace(go.Scatter(
        y=df['net'],
        mode='lines+markers',
        name='סכום נטו',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=6)
    ))
    
    # קו אפס
    fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="קו אפס")
    
    fig.update_layout(
        title="גרף סכומי עסקאות לאורך זמן",
        xaxis_title="מספר עסקה",
        yaxis_title="סכום נטו (₪)",
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # טבלת היסטוריה
    st.markdown("## 📋 היסטוריית עסקאות")
    
    # הכנת הטבלה לתצוגה
    display_df = df.copy()
    display_df['תאריך'] = display_df['stamp'].dt.strftime('%Y-%m-%d %H:%M')
    display_df['סכום'] = display_df['amount'].apply(lambda x: f"₪{x:,.2f}")
    display_df['עמלה'] = display_df['fee'].apply(lambda x: f"₪{x:.2f}")
    display_df['נטו'] = display_df['net'].apply(lambda x: f"₪{x:,.2f}")
    display_df['מצטבר'] = display_df['total'].apply(lambda x: f"₪{x:,.2f}")
    
    # בחירת עמודות לתצוגה
    columns_to_show = ['תאריך', 'סכום', 'עמלה', 'נטו', 'מצטבר', 'note']
    column_names = ['תאריך', 'סכום', 'עמלה', 'נטו', 'מצטבר', 'הערות']
    
    final_display_df = display_df[columns_to_show].copy()
    final_display_df.columns = column_names
    
    st.dataframe(
        final_display_df,
        use_container_width=True,
        hide_index=True
    )
    
    # כפתורי פעולות נוספות
    st.markdown("## ⚙️ פעולות נוספות")
    
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        if st.button("📊 יצא ל-CSV"):
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="הורד קובץ CSV",
                data=csv,
                file_name=f"stock_trades_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with action_col2:
        if st.button("🗑️ נקה הכל", type="secondary"):
            confirm = st.checkbox("אני בטוח שאני רוצה למחוק את כל הנתונים")
            if confirm and st.button("אישור מחיקה"):
                st.session_state['rows'] = []
                st.session_state['next_id'] = 1
                st.rerun()
    
    with action_col3:
        success_rate = (wins/(wins+losses)*100) if (wins+losses) > 0 else 0
        st.metric("שיעור הצלחה", f"{success_rate:.1f}%")

else:
    st.info("👋 ברוכים הבאים! הוסיפו את העסקה הראשונה שלכם למעלה כדי להתחיל.")
    st.markdown("""
    ### איך להשתמש באפליקציה:
    1. **הזינו סכום עסקה** - חיובי לרווח, שלילי להפסד
    2. **הזינו עמלה** - ברירת מחדל 13 ש"ח  
    3. **הוסיפו הערה** (אופציונלי)
    4. **לחצו על הוסף עסקה**
    
    האפליקציה תציג אוטומטית את מדדי הביצועים, גרף המגמות וטבלת ההיסטוריה.
    """)
