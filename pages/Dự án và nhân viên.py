import streamlit as st
from pymongo import MongoClient
import pandas as pd

# Kết nối tới MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["emp"]
col_da_nv = db["du_an_va_nhan_vien"]

st.title("Quản lý Dự án & Nhân viên")

st.subheader("Danh sách mapping dự án & nhân viên")
danhsach_mapping = pd.DataFrame(list(col_da_nv.find()))
if not danhsach_mapping.empty:
    st.dataframe(danhsach_mapping)
else:
    st.info("Chưa có mapping nào trong cơ sở dữ liệu.")

st.subheader("Thêm mapping dự án – nhân viên")
new_da = st.number_input("ID dự án", min_value=1, step=1)
new_list = st.text_input("Danh sách nhân viên (vd: 1,2,3)")
if st.button("Thêm mapping"):
    if new_list:
        ids = [int(x.strip()) for x in new_list.split(",") if x.strip().isdigit()]
        max_id_doc = col_da_nv.find_one(sort=[("_id", -1)])
        next_id = (max_id_doc["_id"] + 1) if max_id_doc else 1
        col_da_nv.insert_one({"_id": next_id, "id_du_an": new_da, "id_nhan_vien": ids})
        st.success(f"Đã thêm mapping _id={next_id}")
    else:
        st.error("Vui lòng nhập danh sách nhân viên")

st.subheader("Cập nhật mapping")
upd_id = st.number_input("Chọn _id mapping", min_value=1, step=1)
upd_da = st.number_input("ID dự án mới", min_value=1, step=1)
upd_list = st.text_input("Danh sách nhân viên mới (vd: 1,2,3)")
if st.button("Cập nhật mapping"):
    if upd_list:
        ids = [int(x.strip()) for x in upd_list.split(",") if x.strip().isdigit()]
        result = col_da_nv.update_one({"_id": upd_id}, {"$set": {"id_du_an": upd_da, "id_nhan_vien": ids}})
        if result.matched_count:
            st.success(f"Đã cập nhật mapping _id={upd_id}")
        else:
            st.error(f"Không tìm thấy mapping _id={upd_id}")
    else:
        st.error("Vui lòng nhập danh sách nhân viên mới")

st.subheader("Xóa mapping")
del_id = st.number_input("Chọn _id mapping để xóa", min_value=1, step=1)
if st.button("Xóa mapping"):
    result = col_da_nv.delete_one({"_id": del_id})
    if result.deleted_count:
        st.success(f"Đã xóa mapping _id={del_id}")
    else:
        st.error(f"Không tìm thấy mapping _id={del_id}")
