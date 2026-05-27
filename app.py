import streamlit as st
import pandas as pd
import datetime
import os

# 設定網頁標題與風格
st.set_page_config(page_title="Gym & Shop 財務管理系統", layout="wide")
st.title("📊 每日收支記帳與統計系統")

# 定義數據儲存的檔案名稱
DATA_FILE = "financial_records.csv"

# 載入現有數據，如果沒有就建立新的
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    df['日期'] = pd.to_datetime(df['日期']).dt.date
else:
    df = pd.DataFrame(columns=["日期", "類型", "項目", "金額", "支付方式", "卡片細分", "備註"])

# --- 側邊欄：記帳輸入介面 ---
st.sidebar.header("✍️ 新增收支紀錄")

date = st.sidebar.date_input("選擇日期", datetime.date.today())
trans_type = st.sidebar.selectbox("交易類型", ["收入", "支出"])

# 根據類型動態調整項目
if trans_type == "收入":
    item = st.sidebar.selectbox("收入項目", ["會員費 (Membership)", "飲料銷售 (Drinks)", "其他收入"])
else:
    item = st.sidebar.selectbox("支出項目", ["店租/水電", "進貨成本", "員工薪資", "其他支出"])

amount = st.sidebar.number_input("金額 (RM)", min_value=0.0, step=1.0, format="%.2f")
payment_method = st.sidebar.selectbox("支付方式", ["現金 (Cash)", "QR Pay", "銀行轉帳 (Bank Transfer)", "信用卡/Debit卡"])

# 如果選擇信用卡，顯示細分選單
card_type = "-"
if payment_method == "信用卡/Debit卡":
    card_type = st.sidebar.selectbox("卡片細分類型", [
        "Visa (Maybank)", "Mastercard (Public Bank)", 
        "Visa (CIMB)", "Debit Card (儲蓄卡)", "其他信用卡"
    ])

note = st.sidebar.text_input("備註 (選填)")

# 新增按鈕邏輯
if st.sidebar.button("💾 儲存此筆紀錄"):
    if amount <= 0:
        st.sidebar.error("請輸入大於 0 的金額！")
    else:
        new_data = pd.DataFrame([{
            "日期": date, "類型": trans_type, "項目": item, 
            "金額": amount, "支付方式": payment_method, "卡片細分": card_type, "備註": note
        }])
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.sidebar.success("紀錄已成功儲存！")
        st.rerun()

# --- 主畫面：數據顯示與統計報告 ---
tab1, tab2 = st.tabs(["📋 當月明細與管理", "📈 每月財務統計報告"])

with tab1:
    st.subheader("📅 所有歷史記帳明細")
    if not df.empty:
        # 顯示表格
        st.dataframe(df.sort_values(by="日期", ascending=False), use_container_width=True)
        
        # 刪除最後一筆的功能（防呆）
        if st.button("🗑️ 刪除最後一筆紀錄"):
            df = df.drop(df.index[-1])
            df.to_csv(DATA_FILE, index=False)
            st.success("已刪除最後一筆紀錄！")
            st.rerun()
    else:
        st.info("目前尚無任何記帳數據，請從左側開始輸入。")

with tab2:
    st.subheader("📊 月度財務分析簡報")
    if not df.empty:
        # 將日期轉為字串方便按月分組
        df['月份'] = df['日期'].apply(lambda x: x.strftime('%Y-%m'))
        all_months = sorted(list(df['月份'].unique()), reverse=True)
        selected_month = st.selectbox("選擇要查看的月份", all_months)
        
        # 篩選該月份數據
        month_df = df[df['月份'] == selected_month]
        
        # 計算核心指標
        total_income = month_df[month_df['類型'] == "收入"]['金額'].sum()
        total_expense = month_df[month_df['類型'] == "支出"]['金額'].sum()
        net_profit = total_income - total_expense
        
        # 顯示數據方塊
        col1, col2, col3 = st.columns(3)
        col1.metric("總收入 (Total Income)", f"RM {total_income:,.2f}")
        col2.metric("總支出 (Total Expense)", f"RM {total_expense:,.2f}")
        col3.metric("淨利潤 (Net Profit)", f"RM {net_profit:,.2f}", delta=f"{net_profit:,.2f}")
        
        st.markdown("---")
        
        # 支付管道細分統計
        st.write(f"### 💳 {selected_month} 支付管道對帳統計")
        pay_summary = month_df[month_df['類型'] == "收入"].groupby(["支付方式", "卡片細分"])["金額"].sum().reset_index()
        pay_summary.columns = ["支付方式", "詳細分類", "收款總額 (RM)"]
        st.table(pay_summary)
        
        # 提供下載 Excel/CSV 功能
        csv = month_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 下載此月月報 (CSV 格式)",
            data=csv,
            file_name=f"Financial_Report_{selected_month}.csv",
            mime='text/csv',
        )
    else:
        st.info("暫無數據可生成報告。")
