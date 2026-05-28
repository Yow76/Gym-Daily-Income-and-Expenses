import streamlit as st
import pandas as pd
import datetime
import os
import base64

# 設定網頁標題與風格
st.set_page_config(page_title="TheOneGym Financial System", layout="wide")

# --- 核心檔案與資料夾路徑設定 ---
# 💡【終極修正】改成全新檔名 v6，逼迫雲端伺服器徹底拋棄所有舊語法快取！
DATA_FILE = "gym_records_v6.csv" 
UPLOAD_DIR = "uploaded_receipts"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# 標準 10 大必備欄位
standard_cols = ["日期", "類型", "大類項目", "細分項目", "金額", "支付方式", "卡片細分", "收據號", "證明文件", "備註"]

# 核心記憶庫初始化
if "gym_df" not in st.session_state:
    if os.path.exists(DATA_FILE):
        try:
            loaded_df = pd.read_csv(DATA_FILE)
            loaded_df.columns = [str(c).strip() for c in loaded_df.columns]
            for col in standard_cols:
                if col not in loaded_df.columns:
                    loaded_df[col] = "-"
            st.session_state.gym_df = loaded_df[standard_cols]
        except:
            st.session_state.gym_df = pd.DataFrame(columns=standard_cols)
    else:
        st.session_state.gym_df = pd.DataFrame(columns=standard_cols)

# 表單版本計數器
if "form_version" not in st.session_state:
    st.session_state.form_version = 0

# 🌟 回呼函式機制（安全無 rerun）
def save_record_on_click(date_val, type_val, cat_val, sub_val, amt_val, pay_val, card_val, receipt_val, uploaded_file_obj, note_val):
    if amt_val <= 0:
        st.session_state.form_error = True
        return
    
    st.session_state.form_error = False
    saved_file_path = "-"
    
    if uploaded_file_obj is not None:
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            saved_file_name = f"{timestamp}_{uploaded_file_obj.name}"
            saved_file_path = os.path.join(UPLOAD_DIR, saved_file_name)
            with open(saved_file_path, "wb") as f:
                f.write(uploaded_file_obj.getbuffer())
        except:
            saved_file_path = "-"

    final_receipt = receipt_val.strip() if receipt_val.strip() else "-"
    
    new_row = {
        "日期": str(date_val), "類型": "收入" if type_val in ["收入", "Income"] else "支出", 
        "大類項目": cat_val, "細分項目": sub_val, "金額": float(amt_val), "支付方式": pay_val, 
        "卡片細分": card_val, "收據號": final_receipt, "證明文件": saved_file_path, "備註": note_val
    }
    new_df = pd.DataFrame([new_row])
    st.session_state.gym_df = pd.concat([st.session_state.gym_df, new_df], ignore_index=True)
    st.session_state.gym_df.to_csv(DATA_FILE, index=False)
    
    st.session_state.form_version += 1
    st.session_state.form_success = True

def delete_last_on_click():
    if not st.session_state.gym_df.empty:
        st.session_state.gym_df = st.session_state.gym_df.drop(st.session_state.gym_df.index[-1])
        st.session_state.gym_df.to_csv(DATA_FILE, index=False)
        st.session_state.del_success = True

# --- 圖片與文件下載小工具 ---
def get_image_download_link(file_path, text):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.png', '.jpg', '.jpeg']:
            return f'<a href="data:image/{ext[1:]};base64,{b64}" target="_blank">{text}</a>'
        else:
            return f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(file_path)}">{text}</a>'
    return "-"

# --- 側邊欄 ---
st.sidebar.markdown("### 🌐 System Settings / 系統設定")
lang = st.sidebar.radio("Language / 語言", ["繁體中文", "English"])

st.sidebar.markdown("---")
admin_password = st.sidebar.text_input("🔑 Admin Password / 管理員密碼", type="password")
is_admin = (admin_password == "8888") 

# --- 雙語字典 ---
texts = {
    "繁體中文": {
        "title": "🏋️ TheOneGym 智能財務管理系統",
        "sidebar_header": "✍️ 新增收支紀錄",
        "date": "選擇日期",
        "trans_type": "交易類型",
        "income": "收入",
        "expense": "支出",
        "cat_income": "收入大類項目",
        "cat_expense": "支出項目",
        "sub_item": "項目細分選擇",
        "pt_type": "教練類型 (Trainer Type)",
        "manual_sessions": "手動填寫堂數/課時 (Sessions)",
        "receipt_no": "收據號 (Receipt No.) [選填]",
        "upload_doc": "上傳支出證明文件/照片",
        "amount": "金額 (RM)",
        "pay_method": "支付方式",
        "card_sub": "卡片細分類型",
        "note": "備註 (選填)",
        "save_btn": "💾 儲存此筆紀錄",
        "err_amount": "請輸入大於 0 的金額！",
        "success_save": "紀錄已成功儲存！",
        "tab1": "📋 當日 Closing 與明細",
        "tab2": "📈 月度財務統計與分析",
        "history_title": "📅 所有記帳歷史明細",
        "del_btn": "🗑️ 刪除最後一筆紀錄",
        "del_success": "已成功刪除最後一筆紀錄！",
        "no_data": "目前尚無數據，請從左側開始輸入。",
        "m_income": "總收入 (Total Income)",
        "m_expense": "總支出 (Total Expense)",
        "m_profit": "淨利潤 (Net Profit)",
        "recon_title": "💳 支付管道對帳統計",
        "download_csv": "📥 導出成 Excel/CSV 報表",
        "cash": "現金 (Cash)",
        "qr": "QR Pay",
        "transfer": "銀行轉帳 (Bank Transfer)",
        "card": "信用卡/Debit卡",
        "detail_col": "詳細分類",
        "amount_col": "收款總額 (RM)",
        "day_report": "🌅 今日營運結帳看板 (Closing Dashboard)",
        "select_day": "選擇查看日期",
        "report_title": "📊 月度財務分析簡報"
    },
    "English": {
        "title": "🏋️ TheOneGym Intelligent Financial System",
        "sidebar_header": "✍️ Add New Record",
        "date": "Select Date",
        "trans_type": "Transaction Type",
        "income": "Income",
        "expense": "Expense",
        "cat_income": "Income Category",
        "cat_expense": "Expense Item",
        "sub_item": "Sub-item Category",
        "pt_type": "Trainer Type",
        "manual_sessions": "Enter Number of Sessions",
        "receipt_no": "Receipt No. [Optional]",
        "upload_doc": "Upload Receipt Photo/Document",
        "amount": "Amount (RM)",
        "pay_method": "Payment Method",
        "card_sub": "Card Subtype",
        "note": "Notes (Optional)",
        "save_btn": "💾 Save Record",
        "err_amount": "Please enter an amount greater than 0!",
        "success_save": "Record saved successfully!",
        "tab1": "📋 Daily Closing & Details",
        "tab2": "📈 Monthly Report & Analysis",
        "history_title": "📅 Transaction History Table",
        "del_btn": "🗑️ Delete Last Record",
        "del_success": "Last record deleted!",
        "no_data": "No data found.",
        "m_income": "Total Income",
        "m_expense": "Total Expense",
        "m_profit": "Net Profit",
        "recon_title": "💳 Payment Channel Reconciliation",
        "download_csv": "📥 Export to Excel/CSV Report",
        "cash": "Cash",
        "qr": "QR Pay",
        "transfer": "Bank Transfer",
        "card": "Credit/Debit Card",
        "detail_col": "Category Detail",
        "amount_col": "Total Collected (RM)",
        "day_report": "🌅 Daily Closing Dashboard",
        "select_day": "Select Date to Check",
        "report_title": "📊 Monthly Financial Analysis"
    }
}

t = texts[lang]

if "form_error" in st.session_state and st.session_state.form_error:
    st.sidebar.error(t["err_amount"])
    st.session_state.form_error = False

if "form_success" in st.session_state and st.session_state.form_success:
    st.sidebar.success(t["success_save"])
    st.session_state.form_success = False

# --- 輸入表單 ---
v = st.session_state.form_version

date_input = st.sidebar.date_input(t["date"], datetime.date.today(), key=f"date_{v}")
trans_type = st.sidebar.selectbox(t["trans_type"], [t["income"], t["expense"]], key=f"type_{v}")

form_cat, form_sub, form_receipt, uploaded_file = "", "", "-", None

if trans_type in ["收入", "Income"]:
    income_categories = ["Walk in", "Membership", "Personal Training", "Group Class", "Drinks / Merchandise", "Others"]
    form_cat = st.sidebar.selectbox(t["cat_income"], income_categories, key=f"cat_inc_{v}")
    
    if form_cat == "Walk in":
        walk_in_options = ["Walk in Gym", "Walk in Group Class", "Seven Day Pass"]
        form_sub = st.sidebar.selectbox(t["sub_item"], walk_in_options, key=f"sub_walk_{v}")
    elif form_cat == "Membership":
        membership_options = [
            "Fitness Renew (NEW)", "Fitness Renew (OLD)", "Fitness Renew 3M", "Fitness Renew 6M",
            "Fitness(Renew)(AB)", "1M NEWJOIN PROMO", "Fitness Student (New)", "Fitness Student (Renew)", 
            "Fitness Renew 12M (Promo)", "2M PROMO", "Fitness Unlimited Group Class 168", 
            "Fitness Unlimited Group Class Promo 138", "Unlimited Group Class Package 110", "Others/Other Promo"
        ]
        form_sub = st.sidebar.selectbox(t["sub_item"], membership_options, key=f"sub_mem_{v}")
    elif form_cat == "Personal Training":
        pt_type = st.sidebar.selectbox(t["pt_type"], ["Inhouse Trainer", "Freelance Trainer"], key=f"pt_type_{v}")
        sessions = st.sidebar.text_input(t["manual_sessions"], placeholder="例如: 10堂課 / 15堂課", key=f"pt_sess_{v}")
        form_sub = f"{pt_type} ({sessions})"
    elif form_cat == "Group Class":
        gc_sessions = st.sidebar.text_input(t["manual_sessions"], placeholder="例如: Zumba 5堂課 / Yoga 12堂課", key=f"gc_sess_{v}")
        form_sub = gc_sessions if gc_sessions.strip() else "Group Class"
    elif form_cat == "Drinks / Merchandise":
        drinks_options = ["Mineral water 1.5L", "Mineral water 500ml", "100 號 (100 Plus)", "Vida", "Protein (乳清蛋白)", "Others"]
        form_sub = st.sidebar.selectbox(t["sub_item"], drinks_options, key=f"drinks_{v}")
    elif form_cat == "Others":
        form_sub = "-"
        
    form_receipt = st.sidebar.text_input(t["receipt_no"], value="-", key=f"receipt_{v}")

else:
    expense_categories = ["店租/水電 (Rent/Utilities)", "進貨成本 (Inventory)", "員工薪資 (Salary)", "其他支出 (Others)"]
    form_cat = st.sidebar.selectbox(t["cat_expense"], expense_categories, key=f"cat_exp_{v}")
    form_sub = st.sidebar.text_input(t["sub_item"], placeholder="例如：水電費 / 飲料進貨補貨", key=f"exp_sub_{v}")
    uploaded_file = st.sidebar.file_uploader(t["upload_doc"], type=["png", "jpg", "jpeg", "pdf"], key=f"upload_{v}")

amount = st.sidebar.number_input(t["amount"], min_value=0.0, step=1.0, format="%.2f", key=f"amt_{v}")
pay_options = [t["cash"], t["qr"], t["transfer"], t["card"]]
payment_method = st.sidebar.selectbox(t["pay_method"], pay_options, key=f"pay_{v}")

card_type = "-"
if payment_method in ["信用卡/Debit卡", "Credit/Debit Card"]:
    card_type = st.sidebar.selectbox(t["card_sub"], [
        "Autodebit (Credit Card)", "Visa (Maybank)", "Mastercard (Public Bank)", 
        "Visa (CIMB)", "Debit Card", "Others"
    ], key=f"card_sub_{v}")

note = st.sidebar.text_input(t["note"], key=f"note_{v}")

st.sidebar.button(
    t["save_btn"], 
    key="save_record_btn", 
    on_click=save_record_on_click, 
    args=(date_input, trans_type, form_cat, form_sub, amount, payment_method, card_type, form_receipt, uploaded_file, note)
)

# --- 資料清洗與過濾 ---
df_active = st.session_state.gym_df.copy()
df_active['日期'] = df_active['日期'].astype(str)

try:
    df_active['金額'] = pd.to_numeric(df_active['金額'], errors='coerce').fillna(0.0)
    df_active = df_active[df_active['大類項目'].notnull() & (df_active['大類項目'] != "") & (df_active['大類項目'] != "-")]
except:
    pass

if is_admin:
    display_df = df_active.copy()
else:
    display_df = df_active[df_active["大類項目"] != "員工薪資 (Salary)"].copy()

# --- 主畫面分頁 ---
tab1, tab2 = st.tabs([t["tab1"], t["tab2"]])

with tab1:
    st.subheader(t["day_report"])
    if not display_df.empty:
        all_days = sorted(list(display_df['日期'].unique()), reverse=True)
        selected_day = st.selectbox(t["select_day"], all_days, key="day_select")
        day_df = display_df[display_df['日期'] == selected_day]
        
        day_income = day_df[day_df['類型'] == "收入"]['金額'].sum()
        day_expense = day_df[day_df['類型'] == "支出"]['金額'].sum()
        day_net = day_income - day_expense
        
        c1, c2, c3 = st.columns(3)
        c1.metric("今日總收入 / Today Income", f"RM {day_income:,.2f}")
        c2.metric("今日總支出 / Today Expense", f"RM {day_expense:,.2f}")
        c3.metric("今日結餘結算 / Today Balance", f"RM {day_net:,.2f}")
        
        st.write("#### 記錄細分項目明細")
        day_inc_df = day_df[day_df['類型'] == "收入"]
        if not day_inc_df.empty:
            try:
                day_summary = day_inc_df.groupby(["支付方式", "卡片細分"])["金額"].sum().reset_index()
                day_summary.columns = [t["pay_method"], t["detail_col"], t["amount_col"]]
                st.table(day_summary)
            except:
                st.dataframe(day_inc_df)
        else:
            st.info("今日暫無收入款項。")
            
        day_csv = day_df.to_csv(index=False).encode('utf-8')
        st.download_button(label=f"📥 {t['download_csv']} ({selected_day})", data=day_csv, file_name=f"Daily_Report_{selected_day}.csv", mime='text/csv')
    else:
        st.info(t["no_data"])
        
    st.markdown("---")
    
    st.subheader(t["history_title"])
    if "del_success" in st.session_state and st.session_state.del_success:
        st.success(t["del_success"])
        st.session_state.del_success = False

    st.button(t["del_btn"], key="delete_last_btn", on_click=delete_last_on_click)
                
    if not display_df.empty:
        grid_df = display_df.sort_values(by="日期", ascending=False).copy()
        links = []
        for path in grid_df["證明文件"]:
            if path != "-" and os.path.exists(str(path)):
                links.append(get_image_download_link(path, "📄 查看證明 (View)"))
            else:
                links.append("-")
        grid_df["證明文件連結"] = links
        st.write(grid_df[["日期", "類型", "大類項目", "細分項目", "金額", "支付方式", "卡片細分", "收據號", "備註", "證明文件連結"]].to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.info(t["no_data"])

with tab2:
    st.subheader(t["report_title"])
    if not display_df.empty:
        display_df['月份'] = display_df['日期'].apply(lambda x: str(x)[:7])
        all_months = sorted(list(display_df['月份'].unique()), reverse=True)
        selected_month = st.selectbox(t["select_month"], all_months, key="month_select")
        
        month_df = display_df[display_df['月份'] == selected_month]
        
        m_inc = month_df[month_df['類型'] == "收入"]['金額'].sum()
        m_exp = month_df[month_df['類型'] == "支出"]['金額'].sum()
        m_prof = m_inc - m_exp
        
        col1, col2, col3 = st.columns(3)
        col1.metric(t["m_income"], f"RM {m_inc:,.2f}")
        col2.metric(t["m_expense"], f"RM {m_exp:,.2f}")
        col3.metric(t["m_profit"], f"RM {m_prof:,.2f}")
        
        st.markdown("---")
        
        st.write(f"### 📈 {selected_month} 各大核心業務收入佔比分析")
        inc_df = month_df[month_df['類型'] == "收入"]
        if not inc_df.empty:
            try:
                cat_summary = inc_df.groupby("大類項目")["金額"].sum().reset_index()
                total_inc_sum = cat_summary["金額"].sum()
                if total_inc_sum > 0:
                    cat_summary['百分比 (Percentage)'] = cat_summary['金額'].apply(lambda x: f"{(x / total_inc_sum * 100):.1f}%")
                else:
                    cat_summary['百分比 (Percentage)'] = "0.0%"
                cat_summary.columns = ["業務核心項目 (Business Item)", "總收入 (RM)", "收入貢獻佔比"]
                st.table(cat_summary)
            except:
                st.dataframe(inc_df)
        else:
            st.info("本月暫無收入分析數據。")
            
        st.markdown("---")
        
        st.write(f"### 💳 {t['recon_title']} ({selected_month})")
        if not inc_df.empty:
            try:
                pay_summary = inc_df.groupby(["支付方式", "卡片細分"])["金額"].sum().reset_index()
                pay_summary.columns = [t["pay_method"], t["detail_col"], t["amount_col"]]
                st.table(pay_summary)
            except:
                st.dataframe(inc_df)
            
        month_csv = month_df.to_csv(index=False).encode('utf-8')
        st.download_button(label=f"📥 {t['download_csv']} ({selected_month}月報)", data=month_csv, file_name=f"Monthly_Report_{selected_month}.csv", mime='text/csv')
    else:
        st.info(t["no_data"])
