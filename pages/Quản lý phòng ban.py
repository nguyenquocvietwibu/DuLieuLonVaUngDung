import streamlit as st
from pymongo import MongoClient
import pandas as pd

# Kết nối MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["emp"]
col_phong_ban = db["phong_ban"]
col_nhan_vien = db["nhan_vien"]

st.title("📁 Quản lý Phòng ban")

# Hàm load phòng ban
def get_phong_ban():
    data = list(col_phong_ban.find({}, {"_id": 0, "ma": 1, "ten": 1}))
    return pd.DataFrame(data)

# -----------------------
# 👉 THÊM PHÒNG BAN
# -----------------------
st.subheader("➕ Thêm phòng ban")
with st.form("form_them"):
    ma = st.number_input("Mã phòng ban", min_value=1, step=1, format="%d")
    ten = st.text_input("Tên phòng ban")
    submitted = st.form_submit_button("Thêm")
    if submitted:
        if ten:
            if col_phong_ban.find_one({"ma": ma}):
                st.warning("⚠️ Mã phòng ban đã tồn tại.")
            else:
                col_phong_ban.insert_one({"ma": int(ma), "ten": ten})
                st.success("✅ Đã thêm phòng ban.")

# -----------------------
# 👉 SỬA PHÒNG BAN
# -----------------------
st.subheader("✏️ Sửa phòng ban")
phong_ban_list = list(col_phong_ban.find({}, {"_id": 0, "ma": 1, "ten": 1}))
if phong_ban_list:
    chon_pb = st.selectbox(
        "Chọn phòng ban cần sửa",
        phong_ban_list,
        format_func=lambda x: f"{x['ma']} - {x['ten']}"
    )
    new_ten = st.text_input("Tên phòng ban mới", chon_pb["ten"], key="sua")
    if st.button("Cập nhật"):
        col_phong_ban.update_one({"ma": chon_pb["ma"]}, {"$set": {"ten": new_ten}})
        st.success("✅ Đã cập nhật phòng ban.")
else:
    st.info("Không có phòng ban để sửa.")

# -----------------------
# 👉 XÓA PHÒNG BAN
# -----------------------
st.subheader("🗑️ Xóa phòng ban")
if phong_ban_list:
    chon_xoa = st.selectbox(
        "Chọn phòng ban cần xóa",
        phong_ban_list,
        key="xoa",
        format_func=lambda x: f"{x['ma']} - {x['ten']}"
    )
    if st.button("Xóa"):
        col_phong_ban.delete_one({"ma": chon_xoa["ma"]})
        st.success("🗑️ Đã xóa phòng ban.")
else:
    st.info("Không có phòng ban để xóa.")

# -----------------------
# 👉 HIỂN THỊ DANH SÁCH VÀ NHÂN VIÊN THEO PHÒNG BAN
# -----------------------
st.markdown("---")
with st.expander("📋 Danh sách phòng ban", expanded=True):
    df = get_phong_ban()
    df = df.rename(columns={"ma": "Mã phòng ban", "ten": "Tên phòng ban"})
    if df.empty:
        st.info("Chưa có phòng ban nào.")
    else:
        st.dataframe(df, hide_index=True)

        # 👉 Cho chọn phòng ban để xem danh sách nhân viên
        ten_pb_chon = st.selectbox("Chọn phòng ban để xem nhân viên", df["Tên phòng ban"].tolist())

        # 👉 Lấy mã phòng ban tương ứng
        ma_pb = df[df["Tên phòng ban"] == ten_pb_chon]["Mã phòng ban"].values[0]

        # 👉 Truy vấn nhân viên thuộc phòng ban (sửa lỗi np.int64)
        nhan_vien_list = list(col_nhan_vien.find({"ma_phong_ban": int(ma_pb)}, {"_id": 0, "ten": 1}))

        # 👉 Hiển thị danh sách nhân viên
        if nhan_vien_list:
            df_nv = pd.DataFrame(nhan_vien_list).rename(columns={"ten": "Tên nhân viên"})
            st.markdown(f"### 👥 Nhân viên thuộc **{ten_pb_chon}**:")
            st.dataframe(df_nv, hide_index=True)
        else:
            st.warning("Phòng ban này chưa có nhân viên nào.")
