# du_an.py
import streamlit as st
from pymongo import MongoClient
import pandas as pd

# Kết nối MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["emp"]
collection_du_an = db["du_an"]

st.title("Quản lý Dự án")

# --- Hiển thị danh sách dự án ---
st.subheader("\U0001F4C4 Danh sách dự án")
docs = list(collection_du_an.find({}, {"_id": 0}))
if docs:
    df = pd.DataFrame(docs)
    st.dataframe(df)
else:
    st.info("Chưa có dự án nào trong cơ sở dữ liệu.")

# --- Thêm hoặc Sửa dự án ---
st.subheader("✍️ Thêm / Sửa dự án")
che_do = st.radio("Chọn chế độ", ["Thêm", "Sửa"], horizontal=True)

if che_do == "Sửa":
    ds_ma = [doc["ma"] for doc in docs]
    chon_ma = st.selectbox("Chọn mã dự án để sửa", ds_ma)
    doc = collection_du_an.find_one({"ma": chon_ma}, {"_id": 0})
    ten = st.text_input("Tên mới", value=doc.get("ten", ""))
else:
    chon_ma = st.number_input("Mã dự án", min_value=1, step=1)
    ten = st.text_input("Tên dự án")

if st.button("\U0001F4BE Lưu"):
    if not ten:
        st.warning("⚠️ Vui lòng nhập tên dự án.")
    else:
        if che_do == "Thêm":
            if collection_du_an.find_one({"ma": chon_ma}):
                st.warning("Mã đã tồn tại.")
            else:
                collection_du_an.insert_one({"ma": chon_ma, "ten": ten})
                st.success("Đã thêm dự án mới.")
        else:
            result = collection_du_an.update_one({"ma": chon_ma}, {"$set": {"ten": ten}})
            if result.matched_count:
                st.success("Đã cập nhật tên dự án.")
            else:
                st.error("Không tìm thấy mã dự án.")

# --- Xóa dự án ---
st.subheader("\U0001F5D1️ Xóa dự án")
ma_can_xoa = st.selectbox("Chọn mã dự án để xóa", [doc["ma"] for doc in docs])
if st.button("Xóa"):
    result = collection_du_an.delete_one({"ma": ma_can_xoa})
    if result.deleted_count:
        st.success("Đã xóa dự án.")
    else:
        st.error("Không tìm thấy mã dự án.")
