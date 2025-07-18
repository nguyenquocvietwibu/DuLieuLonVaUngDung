import streamlit as st
from pymongo import MongoClient
import pandas as pd

# Chạy: python -m streamlit run du_an.py

# Kết nối tới MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["emp"]
du_an = db["du_an"]

st.title("Quản lý Dự Án")

# --- Hiển thị danh sách dự án ---
st.subheader("Danh sách dự án")
duAn = pd.DataFrame(list(du_an.find()))
if not duAn.empty:
    st.dataframe(duAn)
else:
    st.info("Chưa có dự án nào trong cơ sở dữ liệu.")

# --- Thêm dự án ---
st.subheader("Thêm dự án mới")
new_name = st.text_input("Tên dự án")
if st.button("Thêm dự án"):
    if new_name:
        max_id_doc = du_an.find_one(sort=[("_id", -1)])
        next_id = (max_id_doc["_id"] + 1) if max_id_doc else 1
        du_an.insert_one({"_id": next_id, "ten": new_name})
        st.success(f"Đã thêm dự án với _id={next_id}")
    else:
        st.error("Vui lòng nhập tên dự án")

# --- Cập nhật tên dự án ---
st.subheader("Sửa tên dự án")
update_id = st.number_input("Chọn _id", min_value=1, step=1)
updated_name = st.text_input("Tên mới")
if st.button("Cập nhật dự án"):
    result = du_an.update_one({"_id": update_id}, {"$set": {"ten": updated_name}})
    if result.matched_count:
        st.success(f"Đã cập nhật dự án _id={update_id}")
    else:
        st.error(f"Không tìm thấy dự án với _id={update_id}")

# --- Xóa dự án ---
st.subheader("Xóa dự án")
delete_id = st.number_input("Chọn _id để xóa", min_value=1, step=1)
if st.button("Xóa dự án"):
    result = du_an.delete_one({"_id": delete_id})
    if result.deleted_count:
        st.success(f"Đã xóa dự án _id={delete_id}")
    else:
        st.error(f"Không tìm thấy dự án với _id={delete_id}")
