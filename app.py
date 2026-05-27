import streamlit as st
import pandas as pd
import datetime
import os

# 設定網頁標題與風格
st.set_page_config(page_title="Gym & Shop System", layout="wide")

# 定義數據儲存的檔案名稱
DATA_FILE = "financial_records.csv"

# 載入現有數據
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    df['日期'] = pd.to_datetime(df['日期']).dt.date
else:
    df = pd.DataFrame(columns=["日期", "類型", "項目", "金額", "支付方式", "卡片細分", "備註"])

# --- 語言字典設定 (中英文對照) ---
lang = st.sidebar.radio("🌐 Language / 語言", ["繁體中文", "English"])

texts = {
    "繁體中文": {
        "title": "📊 每日收支記帳與統計系統",
        "sidebar_header": "✍️ 新增收支紀錄",
        "date": "選擇日期",
        "trans_type": "交易類型",
        "income": "收入",
        "expense": "支出",
        "item_income": "收入項目",
        "item_expense": "支出項目",
        "membership": "會員費 (Membership)",
        "drinks": "飲料銷售 (Drinks)",
        "other_inc": "其他收入 (Other Income)",
        "rent": "店租/水電 (Rent/Utilities)",
        "stock": "進貨成本 (Inventory)",
        "salary": "員工薪資 (Salary)",
        "other_exp": "其他支出 (Other Expense)",
        "amount": "金額 (RM)",
        "pay_method": "支付方式",
        "card_sub": "卡片細分類型",
        "note": "備註 (選填)",
        "save_btn": "💾 儲存此筆紀錄",
        "err_amount": "請輸入大於 0 的金額！",
        "success_save": "紀錄已成功儲存！",
        "tab1": "📋 當月明細與管理",
        "tab2": "📈 每月財務統計報告",
        "history_title": "📅 所有歷史記帳明細",
        "del_btn": "🗑️ 刪除最後一筆紀錄",
        "del_success": "已刪除最後一筆紀錄！",
        "no_data": "目前尚無任何記帳數據，請從左側開始輸入。",
        "report_title": "📊 月度財務分析簡報",
        "select_month": "選擇要查看的月份",
        "m_income": "總收入 (Total Income)",
        "m_expense": "總支出 (Total Expense)",
        "m_profit": "淨利潤 (Net Profit)",
        "recon_title": "💳 支付管道對帳統計",
        "download_btn": "📥 下載此月月報 (CSV 格式)",
        "cash": "現金 (Cash)",
        "qr": "QR Pay",
        "transfer": "銀行轉帳 (Bank Transfer)",
        "card": "信用卡/Debit卡",
        "detail_col": "詳細分類",
        "amount_col": "收款總額 (RM)"
    },
    "English": {
        "title": "📊 Daily Income & Expense Tracker",
        "sidebar_header": "✍️ Add New Record",
        "date": "Select Date",
        "trans_type": "Transaction Type",
        "income": "Income",
        "expense": "Expense",
        "item_income": "Income Item",
        "item_expense": "Expense Item",
        "membership": "Membership Fee",
        "drinks": "Drinks Sales",
        "other_inc": "Other Income",
        "rent": "Rent/Utilities",
        "stock": "Inventory/Stock",
        "salary": "Staff Salary",
        "other_exp": "Other Expense",
        "amount": "Amount (RM)",
        "pay_method": "Payment Method",
        "card_sub": "Card Subtype",
        "note": "Notes (Optional)",
        "save_btn": "💾 Save Record",
        "err_amount": "Please enter an amount greater than 0!",
        "success_save": "Record saved successfully!",
        "tab1": "📋 Monthly Details",
        "tab2": "📈 Monthly Financial Report",
        "history_title": "📅 Historical Records Table",
        "del_btn": "🗑️ Delete Last Record",
        "del_success": "Last record deleted!",
        "no_data": "No data found. Please add records from the sidebar.",
        "report_title": "📊 Monthly Financial Analysis",
        "select_month": "Select Month",
        "m_income": "Total Income",
        "m_expense": "Total Expense",
        "m_profit": "Net Profit",
        "recon_title": "💳 Payment Channel Reconciliation",
        "download_btn": "📥 Download Monthly Report (CSV)",
        "cash": "Cash",
        "qr": "QR Pay",
        "transfer": "Bank Transfer",
        "card": "Credit/Debit Card",
        "detail_col": "Category Detail",
        "amount_col": "Total Collected (RM)"
    }
}

t = texts[lang]
st.title(t["title"])

# --- 側邊欄：輸入介面 ---
st.sidebar.header(t["sidebar_header"])
date = st.sidebar.date_input(t["date"], datetime.date.today())
trans_type = st.sidebar.selectbox(t["trans_type"], [t["income"], t["expense"]])

# 對照中英文項目
if trans_type in ["收入", "Income"]:
    item_options = [t["membership"], t["drinks"], t["other_inc"]]
    item = st.sidebar.selectbox(t["item_income"], item_options)
else:
    item_options = [t["rent"], t["stock"], t["salary"], t["other_exp"]]
    item = st.sidebar.selectbox(t["item_expense"], item_options)

amount = st.sidebar.number_input(t["amount"], min_value=0.0, step=1.0, format="%.2f")

pay_options = [t["cash"], t["qr"], t["transfer"], t["card"]]
payment_method = st.sidebar.selectbox(t["pay_method"], pay_options)

card_type = "-"
if payment_method in ["信用卡/Debit卡", "Credit/Debit Card"]:
    card_type = st.sidebar.selectbox(t["card_sub"], [
        "Visa (Maybank)", "Mastercard (Public Bank)", 
        "Visa (CIMB)", "Debit Card", "Others"
    ])

note = st.sidebar.text_input(t["note"])

if st.sidebar.button(t["save_btn"]):
    if amount <= 0:
        st.sidebar.error(t["err_amount"])
    else:
        new_data = pd.DataFrame([{
            "日期": date, "類型": "收入" if trans_type in ["收入", "Income"] else "支出", 
            "項目": item, "金額": amount, "支付方式": payment_method, "卡片細分": card_type, "備註": note
        }])
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.sidebar.success(t["success_save"])
        st.rerun()

# --- 主畫面 ---
tab1, tab2 = st.tabs([t["tab1"], t["tab2"]])

with tab1:
    st.subheader(t["history_title"])
    if not df.empty:
        st.dataframe(df.sort_values(by="日期", ascending=False), use_container_width=True)
        if st.button(t["del_btn"]):
            df = df.drop(df.index[-1])
            df.to_csv(DATA_FILE, index=False)
            st.success(t["del_success"])
            st.rerun()
    else:
        st.info(t["no_data"])

with tab2:
    st.subheader(t["report_title"])
    if not df.empty:
        df['月份'] = df['日期'].apply(lambda x: x.strftime('%Y-%m'))
        all_months = sorted(list(df['月份'].unique()), reverse=True)
        selected_month = st.selectbox(t["select_month"], all_months)
        
        month_df = df[df['月份'] == selected_month]
        
        total_income = month_df[month_df['類型'] == "收入"]['金額'].sum()
        total_expense = month_df[month_df['類型'] == "支出"]['金額'].sum()
        net_profit = total_income - total_expense
        
        col1, col2, col3 = st.columns(3)
        col1.metric(t["m_income"], f"RM {total_income:,.2f}")
        col2.metric(t["m_expense"], f"RM {total_expense:,.2f}")
        col3.metric(t["m_profit"], f"RM {net_profit:,.2f}")
        
        st.markdown("---")
        
        st.write(f"### {t['recon_title']} ({selected_month})")
        pay_summary = month_df[month_df['類型'] == "收入"].groupby(["支付方式", "卡片細分"])["金額"].sum().reset_index()
        pay_summary.columns = [t["pay_method"], t["detail_col"], t["amount_col"]]
        st.table(pay_summary)
        
        csv = month_df.to_csv(index=False).encode('utf-8')
        st.download_button(label=t["download_btn"], data=csv, file_name=f"Report_{selected_month}.csv", mime='text/csv')
    else:
        st.info(t["no_data"])
import pandas as pd

file_may26 = "05.MAY 2026.xlsx - MAY 26.csv"
file_list = "05.MAY 2026.xlsx - List.csv"

df_may26 = pd.read_csv(file_may26)
df_list = pd.read_csv(file_list)

print("--- MAY 26 Head ---")
print(df_may26.head(10))
print("\n--- MAY 26 Info ---")
print(df_may26.info())

print("\n--- List Head ---")
print(df_list.head(10))
print("\n--- List Info ---")
print(df_list.info())
print(df_may26[df_may26['Unnamed: 0'].notnull()][['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2']].head(20))
print(df_may26.iloc[30:65])
# Let's inspect rows where Unnamed: 8 (Card) has a non-zero value and look at the context.
# We need to trace the date for each row.

current_date = None
card_records = []

for idx, row in df_may26.iterrows():
    # Detect date change
    val_0 = str(row['Unnamed: 0']).strip() if pd.notnull(row['Unnamed: 0']) else ""
    if val_0.startswith("2026-"):
        current_date = val_0
    
    # Check if there is a card payment
    card_val = row['Unnamed: 8']
    if pd.notnull(card_val):
        try:
            # try to convert to float
            card_amount = float(str(card_val).replace(',', '').strip())
            if card_amount > 0:
                # Get details
                receipt = row['Unnamed: 1']
                item = row['Unnamed: 2']
                qty = row['Unnamed: 3']
                name = row['Unnamed: 4']
                
                card_records.append({
                    "Index": idx,
                    "Date": current_date,
                    "Receipt": receipt,
                    "Item": item,
                    "Qty": qty,
                    "Name": name,
                    "Card Amount": card_amount
                })
        except ValueError:
            # Not a number (could be header or string like "Card")
            pass

df_card = pd.DataFrame(card_records)
print(df_card)
# Let's clean up and filter only rows that represent real transactions (where Receipt is not null)
individual_cards = df_card[df_card['Receipt'].notnull()].copy()
print(individual_cards[['Date', 'Receipt', 'Item', 'Name', 'Card Amount']])
print(f"Total individual card transactions count: {len(individual_cards)}")
print(f"Sum of individual card amounts: {individual_cards['Card Amount'].sum()}")
# Let's see if columns Unnamed: 12, Unnamed: 13 onwards contain any card breakdown info for these specific indices
card_indices = individual_cards['Index'].tolist()
print(df_may26.loc[card_indices, ['Unnamed: 0', 'Unnamed: 4', 'Unnamed: 8', 'Unnamed: 12', 'Unnamed: 13']].dropna(subset=['Unnamed: 12', 'Unnamed: 13'], how='all'))
card_summary = individual_cards.groupby('Item').agg(
    Count=('Card Amount', 'count'),
    Total_Amount=('Card Amount', 'sum')
).reset_index()
print(card_summary)
