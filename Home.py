import streamlit as st
from pymongo import MongoClient
import pandas as pd

st.set_page_config(page_title="Trang chủ", layout="wide")
st.title("Trang chủ – Tổng quan dữ liệu MongoDB")

# Kết nối MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["emp"]

# Danh sách các collection cần hiển thị
collections = {
    "Nhân viên": "nhan_vien",
    "Dự án": "du_an",
    "Phòng ban": "phong_ban",
    "Dự án và Nhân viên": "du_an_va_nhan_vien"
}

# Hiển thị từng collection trong expander
for title, collection_name in collections.items():
    collection = db[collection_name]
    data = list(collection.find({}))
    
    # # Loại bỏ _id nếu cần
    # for item in data:
    #     item.pop("_id", None)

    df = pd.DataFrame(data)

    with st.expander(f"📂 {title} ({len(df)} dòng)", expanded=False):
        if df.empty:
            st.info("Không có dữ liệu.")
        else:
            st.dataframe(df, use_container_width=True)
