import streamlit as st
import pandas as pd
import datetime
import os
import base64

# 設定網頁標題與風格
st.set_page_config(page_title="TheOneGym Financial System", layout="wide")

# --- 核心檔案與資料夾路徑設定 ---
DATA_FILE = "financial_records.csv"
UPLOAD_DIR = "uploaded_receipts" # 建立資料夾存儲支出收據照片
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# 載入現有數據（加入強大自動修復與對齊欄位功能）
if os.path.exists(DATA_FILE):
    try:
        df = pd.read_csv(DATA_FILE)
        
        # 💡 自動對齊舊數據格式：如果發現是舊版欄位名，自動強制更名為標準版
        rename_dict = {
            "Card 細分": "卡片細分",
            "CardSubType": "卡片細分",
            "項目": "細分項目",
            "Category": "大類項目",
            "Item": "細分項目",
            "ReceiptNo": "收據號"
        }
        df = df.rename(columns=rename_dict)
        
        # 檢查必備欄位，如果缺少就自動補齊空欄位，防止報錯
        required_cols = ["日期", "類型", "大類項目", "細分項目", "金額", "支付方式", "卡片細分", "收據號", "證明文件", "備註"]
        for col in required_cols:
            if col not in df.columns:
                df[col] = "-"
        
        # 如果大類項目全是空的（比如剛導入舊數據時），把舊的“項目”內容安全搬移過去
        df.loc[df["大類項目"] == "-", "大類項目"] = "Membership"
                
        df['日期'] = pd.to_datetime(df['日期']).dt.date
    except Exception as e:
        df = pd.DataFrame(columns=["日期", "類型", "大類項目", "細分項目", "金額", "支付方式", "卡片細分", "收據號", "證明文件", "備註"])
else:
    df = pd.DataFrame(columns=["日期", "類型", "大類項目", "細分項目", "金額", "支付方式", "卡片細分", "收據號", "證明文件", "備註"])

# --- 圖片顯示小工具 ---
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

# --- 側邊欄：全局設定 (語言與密碼) ---
st.sidebar.markdown("### 🌐 System Settings / 系統設定")
lang = st.sidebar.radio("Language / 語言", ["繁體中文", "English"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔒 Admin Auth / 管理員認證")
admin_password = st.sidebar.text_input("Enter Admin Password / 輸入密碼", type="password", help="輸入密碼解鎖員工薪資數據")
is_admin = (admin_password == "8888") # 預設管理員密碼

if is_admin:
    st.sidebar.success("🔑 Admin Mode Active / 已解鎖管理員權限")
else:
    st.sidebar.info("👤 Staff Mode (Salary Hidden) / 員工模式（薪資已隱藏）")

# --- 語言字典設定 ---
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
        "sub_item": "細分說明 (如：飲料名稱/會員卡種/PT教練)",
        "receipt_no": "收據號 (Receipt No.) *必填",
        "upload_doc": "上傳支出證明文件/照片",
        "amount": "金額 (RM)",
        "pay_method": "支付方式",
        "card_sub": "卡片細分類型",
        "note": "備註 (選填)",
        "save_btn": "💾 儲存此筆紀錄",
        "err_amount": "請輸入大於 0 的金額！",
        "err_receipt": "請填寫收據號！",
        "success_save": "紀錄已成功儲存！",
        "tab1": "📋 當日 Closing 與明細",
        "tab2": "📈 月度財務統計與分析",
        "history_title": "📅 記帳明細歷史",
        "del_btn": "🗑️ 刪除最後一筆紀錄",
        "del_success": "已刪除最後一筆紀錄！",
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
        "select_day": "選擇查看日期"
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
        "sub_item": "Sub-item Detail (e.g. Card Type / Coach Name)",
        "receipt_no": "Receipt No. *Required",
        "upload_doc": "Upload Receipt Photo/Document",
        "amount": "Amount (RM)",
        "pay_method": "Payment Method",
        "card_sub": "Card Subtype",
        "note": "Notes (Optional)",
        "save_btn": "💾 Save Record",
        "err_amount": "Please enter an amount greater than 0!",
        "err_receipt": "Receipt No. is required!",
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
        "select_day": "Select Date to Check"
    }
}

t = texts[lang]
st.title(t["title"])
st.markdown("---")

# --- 側邊欄：數據輸入介面 ---
st.sidebar.header(t["sidebar_header"])
date_input = st.sidebar.date_input(t["date"], datetime.date.today())
trans_type = st.sidebar.selectbox(t["trans_type"], [t["income"], t["expense"]])

# 初始化變數
form_cat = ""
form_sub = ""
form_receipt = "-"
saved_file_path = "-"

if trans_type in ["收入", "Income"]:
    income_categories = ["Walk in", "Membership", "Personal Training", "Group Class", "Drinks / Merchandise", "Others"]
    form_cat = st.sidebar.selectbox(t["cat_income"], income_categories)
    form_sub = st.sidebar.text_input(t["sub_item"], placeholder="例如：Fitness Renew / Coach Ernest")
    form_receipt = st.sidebar.text_input(t["receipt_no"])
else:
    expense_categories = ["店租/水電 (Rent/Utilities)", "進貨成本 (Inventory)", "員工薪資 (Salary)", "其他支出 (Others)"]
    form_cat = st.sidebar.selectbox(t["cat_expense"], expense_categories)
    form_sub = st.sidebar.text_input(t["sub_item"], placeholder="例如：May 水電費 / 買水進貨")
    
    uploaded_file = st.sidebar.file_uploader(t["upload_doc"], type=["png", "jpg", "jpeg", "pdf"])
    if uploaded_file is not None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_file_name = f"{timestamp}_{uploaded_file.name}"
        saved_file_path = os.path.join(UPLOAD_DIR, saved_file_name)
        with open(saved_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

amount = st.sidebar.number_input(t["amount"], min_value=0.0, step=1.0, format="%.2f")
pay_options = [t["cash"], t["qr"], t["transfer"], t["card"]]
payment_method = st.sidebar.selectbox(t["pay_method"], pay_options)

card_type = "-"
if payment_method in ["信用卡/Debit卡", "Credit/Debit Card"]:
    card_type = st.sidebar.selectbox(t["card_sub"], [
        "Autodebit (Credit Card)", "Visa (Maybank)", "Mastercard (Public Bank)", 
        "Visa (CIMB)", "Debit Card", "Others"
    ])

note = st.sidebar.text_input(t["note"])

if st.sidebar.button(t["save_btn"]):
    if amount <= 0:
        st.sidebar.error(t["err_amount"])
    elif trans_type in ["收入", "Income"] and not form_receipt.strip():
        st.sidebar.error(t["err_receipt"])
    else:
        new_data = pd.DataFrame([{
            "日期": date_input, "類型": "收入" if trans_type in ["收入", "Income"] else "支出", 
            "大類項目": form_cat, "細分項目": form_sub, "金額": amount, "支付方式": payment_method, 
            "卡片細分": card_type, "收據號": form_receipt, "證明文件": saved_file_path, "備註": note
        }])
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.sidebar.success(t["success_save"])
        st.rerun()

# --- 權限鎖過濾 ---
if is_admin:
    display_df = df.copy()
else:
    display_df = df[df["大類項目"] != "員工薪資 (Salary)"].copy()

# --- 主畫面分頁 ---
tab1, tab2 = st.tabs([t["tab1"], t["tab2"]])

with tab1:
    st.subheader(t["day_report"])
    if not display_df.empty:
        all_days = sorted(list(df['日期'].unique()), reverse=True)
        selected_day = st.selectbox(t["select_day"], all_days, key="day_select")
        day_df = display_df[display_df['日期'] == selected_day]
        
        day_income = day_df[day_df['類型'] == "收入"]['金額'].sum()
        day_expense = day_df[day_df['類型'] == "支出"]['金額'].sum()
        day_net = day_income - day_expense
        
        c1, c2, c3 = st.columns(3)
        c1.metric("今日總收入 / Today Income", f"RM {day_income:,.2f}")
        c2.metric("今日總支出 / Today Expense" + ("" if is_admin else " (薪資除外)"), f"RM {day_expense:,.2f}")
        c3.metric("今日結餘結算 / Today Balance", f"RM {day_net:,.2f}")
        
        st.write("#### 💳 今日支付方式細分 (Today Payments Breakdown)")
        day_inc_df = day_df[day_df['類型'] == "收入"]
        if not day_inc_df.empty:
            # 增加安全檢查防範缺失欄位
            try:
                day_summary = day_inc_df.groupby(["支付方式", "卡片細分"])["金額"].sum().reset_index()
                day_summary.columns = [t["pay_method"], t["detail_col"], t["amount_col"]]
                st.table(day_summary)
            except:
                st.dataframe(day_inc_df[["日期", "大類項目", "細分項目", "金額", "支付方式"]])
        else:
            st.info("今日暫無收入款項。")
            
        day_csv = day_df.to_csv(index=False).encode('utf-8')
        st.download_button(label=f"📥 {t['download_csv']} ({selected_day})", data=day_csv, file_name=f"Daily_Report_{selected_day}.csv", mime='text/csv')
    else:
        st.info(t["no_data"])
        
    st.markdown("---")
    
    st.subheader(t["history_title"])
    if not display_df.empty:
        grid_df = display_df.sort_values(by="日期", ascending=False).copy()
        links = []
        for path in grid_df["證明文件"]:
            if path != "-" and os.path.exists(str(path)):
                links.append(get_image_download_link(path, "📄 查看證明 (View)"))
            else:
                links.append("-")
        grid_df["證明文件連結"] = links
        
        st.write("💡 *小提示：可於最右側直欄直接點擊查看或下載上傳的支出證明。*")
        st.write(grid_df[["日期", "類型", "大類項目", "細分項目", "金額", "支付方式", "卡片細分", "收據號", "備註", "證明文件連結"]].to_html(escape=False, index=False), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(t["del_btn"]):
            df = df.drop(df.index[-1])
            df.to_csv(DATA_FILE, index=False)
            st.success(t["del_success"])
            st.rerun()
    else:
        st.info(t["no_data"])

with tab2:
    st.subheader(t["report_title"])
    if not display_df.empty:
        display_df['月份'] = display_df['日期'].apply(lambda x: x.strftime('%Y-%m') if hasattr(x, 'strftime') else str(x)[:7])
        all_months = sorted(list(display_df['月份'].unique()), reverse=True)
        selected_month = st.selectbox(t["select_month"], all_months, key="month_select")
        
        month_df = display_df[display_df['月份'] == selected_month]
        
        m_inc = month_df[month_df['類型'] == "收入"]['金額'].sum()
        m_exp = month_df[month_df['類型'] == "支出"]['金額'].sum()
        m_prof = m_inc - m_exp
        
        col1, col2, col3 = st.columns(3)
        col1.metric(t["m_income"], f"RM {m_inc:,.2f}")
        col2.metric(t["m_expense"] + ("" if is_admin else " (薪資除外)"), f"RM {m_exp:,.2f}")
        col3.metric(t["m_profit"], f"RM {m_prof:,.2f}")
        
        st.markdown("---")
        
        st.write(f"### 📈 {selected_month} 各大核心業務收入佔比分析")
        inc_df = month_df[month_df['類型'] == "收入"]
        if not inc_df.empty:
            cat_summary = inc_df.groupby("大類項目")["金額"].sum().reset_index()
            cat_summary['百分比 (Percentage)'] = (cat_summary['金額'] / cat_summary['金額'].sum() * 100).map("{:.1f}%".format)
            cat_summary.columns = ["業務核心項目 (Business Item)", "總收入 (RM)", "收入貢獻佔比"]
            st.table(cat_summary)
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
                st.dataframe(inc_df[["日期", "大類項目", "細分項目", "金額", "支付方式"]])
            
        month_csv = month_df.to_csv(index=False).encode('utf-8')
        st.download_button(label=f"📥 {t['download_csv']} ({selected_month}月報)", data=month_csv, file_name=f"Monthly_Report_{selected_month}.csv", mime='text/csv')
    else:
        st.info(t["no_data"])
