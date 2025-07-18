import streamlit as st
from pymongo import MongoClient
import pandas as pd
import numpy as np

client = MongoClient("mongodb://localhost:27017")
db = client["emp"]
col_nv = db["nhan_vien"]

st.title("Quản lý Nhân viên")

st.subheader("Danh sách nhân viên")
nhanVien = pd.DataFrame(list(col_nv.find()))
if not nhanVien.empty:
    st.dataframe(nhanVien)
else:
    st.info("Chưa có nhân viên nào trong cơ sở dữ liệu.")

st.subheader("Thêm nhân viên mới")
new_ten = st.text_input("Tên" )
new_ns = st.number_input("Năm sinh", min_value=1900, max_value=2100, step=1)
new_gt = st.selectbox("Giới tính", ["Nam", "Nữ"])
new_dc = st.text_input("Địa chỉ")
new_sdt = st.text_input("SĐT")
new_pb = st.number_input("ID phòng ban", min_value=1, step=1)
if st.button("Thêm nhân viên"):
    if new_ten and new_dc and new_sdt:
        max_doc = col_nv.find_one(sort=[("_id", -1)])
        next_id = (max_doc["_id"] + 1) if max_doc else 1
        col_nv.insert_one({
            "_id": next_id,
            "ten": new_ten,
            "nam_sinh": new_ns,
            "gioi_tinh": new_gt,
            "dia_chi": new_dc,
            "sdt": new_sdt,
            "id_phong_ban": new_pb
        })
        st.success(f"Đã thêm nhân viên _id={next_id}")
    else:
        st.error("Vui lòng nhập đủ thông tin")

st.subheader("Cập nhật nhân viên")
upd_id = st.number_input("Chọn _id nhân viên", min_value=1, step=1)
upd_ten = st.text_input("Tên mới")
upd_ns = st.number_input("Năm sinh mới", min_value=1900, max_value=2100, step=1)
upd_gt = st.selectbox("Giới tính mới", ["Nam", "Nữ"])
upd_dc = st.text_input("Địa chỉ mới")
upd_sdt = st.text_input("SĐT mới")
upd_pb = st.number_input("ID phòng ban mới", min_value=1, step=1)
if st.button("Cập nhật nhân viên"):
    update_fields = {
        "ten": upd_ten,
        "nam_sinh": upd_ns,
        "gioi_tinh": upd_gt,
        "dia_chi": upd_dc,
        "sdt": upd_sdt,
        "id_phong_ban": upd_pb
    }
    result = col_nv.update_one({"_id": upd_id}, {"$set": update_fields})
    if result.matched_count:
        st.success(f"Đã cập nhật nhân viên _id={upd_id}")
    else:
        st.error(f"Không tìm thấy nhân viên _id={upd_id}")

st.subheader("Xóa nhân viên")
del_id = st.number_input("Chọn _id nhân viên để xóa", min_value=1, step=1)
if st.button("Xóa nhân viên"):
    result = col_nv.delete_one({"_id": del_id})
    if result.deleted_count:
        st.success(f"Đã xóa nhân viên _id={del_id}")
    else:
        st.error(f"Không tìm thấy nhân viên _id={del_id}")
