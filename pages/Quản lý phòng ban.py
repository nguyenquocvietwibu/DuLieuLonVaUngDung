import streamlit as st
from pymongo import MongoClient
import pandas as pd

# Kết nối tới MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["emp"]
col_phong_ban = db["phong_ban"]

st.title("Quản lý Phòng ban")

st.subheader("Danh sách phòng ban")
phong_ban = pd.DataFrame(list(col_phong_ban.find()))
if not phong_ban.empty:
    st.dataframe(phong_ban)
else:
    st.info("Chưa có phòng ban nào trong cơ sở dữ liệu.")

st.subheader("Thêm phòng ban mới")
new_name = st.text_input("Tên phòng ban")
if st.button("Thêm phòng ban"):
    if new_name:
        max_id_doc = col_phong_ban.find_one(sort=[("_id", -1)])
        next_id = (max_id_doc["_id"] + 1) if max_id_doc else 1
        col_phong_ban.insert_one({"_id": next_id, "ten": new_name})
        st.success(f"Đã thêm phòng ban _id={next_id}")
    else:
        st.error("Vui lòng nhập tên phòng ban")

st.subheader("Cập nhật phòng ban")
upd_id = st.number_input("Chọn _id phòng ban", min_value=1, step=1  )
upd_name = st.text_input("Tên phòng ban mới"    )
if st.button("Cập nhật phòng ban"   ):
    result = col_phong_ban.update_one({"_id": upd_id}, {"$set": {"ten": upd_name}})
    if result.matched_count:
        st.success(f"Đã cập nhật phòng ban _id={upd_id}")
    else:
        st.error(f"Không tìm thấy phòng ban _id={upd_id}")

st.subheader("Xóa phòng ban")
del_id = st.number_input("Chọn _id phòng ban để xóa", min_value=1, step=1   )
if st.button("Xóa phòng ban" ):
    result = col_phong_ban.delete_one({"_id": del_id})
    if result.deleted_count:
        st.success(f"Đã xóa phòng ban _id={del_id}")
    else:
        st.error(f"Không tìm thấy phòng ban _id={del_id}")
