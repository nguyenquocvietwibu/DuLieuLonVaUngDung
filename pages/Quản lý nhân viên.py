import streamlit as st
from pymongo import MongoClient
import pandas as pd

# Kết nối MongoDB
client = MongoClient("mongodb://localhost:27017")
emp_db = client["emp"]
collection_nhan_vien = emp_db["nhan_vien"]
collection_phong_ban = emp_db["phong_ban"]
collection_du_an = emp_db["du_an"]
collection_nv_va_du_an = emp_db["nhan_vien_va_du_an"]


# Truy vấn dữ liệu nhân viên
def get_nhan_vien_df():
    cau_truy_van = [
        # Nối với phòng ban
        {
            "$lookup": {
                "from": "phong_ban",
                "localField": "ma_phong_ban",
                "foreignField": "ma",
                "as": "phong_ban_truc_thuoc",
            }
        },
        # Nối với bảng trung gian nhan_vien_va_du_an
        {
            "$lookup": {
                "from": "nhan_vien_va_du_an",
                "localField": "ma",
                "foreignField": "ma_nhan_vien",
                "as": "nhan_vien_va_cac_du_an_tham_gia",
            }
        },
        # Nối với bảng du_an để lấy tên
        {
            "$lookup": {
                "from": "du_an",
                "localField": "nhan_vien_va_cac_du_an_tham_gia.ma_du_an",
                "foreignField": "ma",
                "as": "danh_sach_du_an_tham_gia",
            }
        },
        # Project ra dữ liệu mong muốn
        {
            "$project": {
                "_id": 0,
                "ma": 1,
                "ten": 1,
                "nam_sinh": 1,
                "gioi_tinh": 1,
                "dia_chi": 1,
                "sdt": 1,
                "ten_phong_ban": "$phong_ban_truc_thuoc.ten",
                "danh_sach_du_an_tham_gia": "$danh_sach_du_an_tham_gia.ten",
            }
        },
    ]
    data = list(collection_nhan_vien.aggregate(cau_truy_van))
    return pd.DataFrame(data)


st.title("Quản lý Nhân viên")

# Danh sách nhân viên
st.subheader("📋 Danh sách nhân viên")

df = get_nhan_vien_df()
st.dataframe(df)

# Danh sách phòng ban để chọn
ds_phong_ban = list(collection_phong_ban.find({}, {"_id": 0}))
phong_ban_options = {pb["ten"]: pb["ma"] for pb in ds_phong_ban}

# Danh sách dự án để chọn
ds_du_an = list(collection_du_an.find({}, {"_id": 0}))
du_an_options = {da["ten"]: da["ma"] for da in ds_du_an}

st.subheader("✍️ Thêm / Sửa nhân viên")
form_mode = st.radio("Chọn chế độ:", ["Thêm", "Sửa"], horizontal=True)

# Nếu Sửa thì lấy dữ liệu nhân viên và các dự án đang tham gia
if form_mode == "Sửa":
    ds_ma_nv = df["ma"].tolist()
    selected_ma = st.selectbox("Chọn mã nhân viên để sửa", ds_ma_nv)
    nv_info = collection_nhan_vien.find_one({"ma": selected_ma}, {"_id": 0})

    # Lấy danh sách mã dự án nhân viên đang tham gia
    du_an_da_tham_gia = list(
        collection_nv_va_du_an.find(
            {"ma_nhan_vien": selected_ma}, {"_id": 0, "ma_du_an": 1}
        )
    )
    # Chuyển mã dự án thành tên dự án
    selected_projects = [
        ten for ten, ma in du_an_options.items()
        if any(ma == d["ma_du_an"] for d in du_an_da_tham_gia)
    ]
else:
    nv_info = {}
    selected_projects = []

with st.form("form_nhan_vien"):
    if form_mode == "Sửa":
        ma = nv_info.get("ma", "")
        st.text_input("Mã nhân viên", ma, disabled=True)
    else:
        ma = st.text_input("Mã nhân viên", "")
    ten = st.text_input("Tên", nv_info.get("ten", ""))
    nam_sinh = st.number_input("Năm sinh", value=int(nv_info.get("nam_sinh", 1990)))
    gioi_tinh = st.selectbox(
        "Giới tính",
        ["Nam", "Nữ"],
        index=0 if nv_info.get("gioi_tinh", "Nam") == "Nam" else 1,
    )
    dia_chi = st.text_input("Địa chỉ", nv_info.get("dia_chi", ""))
    sdt = st.text_input("SĐT", nv_info.get("sdt", ""))
    phong_ban_ten = st.selectbox("Phòng ban", list(phong_ban_options.keys()))
    cac_du_an = st.multiselect("Các dự án tham gia", list(du_an_options.keys()), default=selected_projects)

    submitted = st.form_submit_button("💾 Lưu")

    if submitted:

        du_lieu_nv = {
            "ma": ma,
            "ten": ten,
            "nam_sinh": nam_sinh,
            "gioi_tinh": gioi_tinh,
            "dia_chi": dia_chi,
            "sdt": sdt,
            "ma_phong_ban": phong_ban_options[phong_ban_ten],
        }
        st.write("Đã submit với mode:", form_mode)
        st.write("Thông tin lưu:", du_lieu_nv)
        st.write("các dự án tham gia:", cac_du_an)
        if form_mode == "Thêm":
            # Kiểm tra trùng mã
            if collection_nhan_vien.find_one({"ma": ma}):
                st.warning("⚠️ Mã nhân viên đã tồn tại. Vui lòng nhập mã khác.")
            else:
                collection_nhan_vien.insert_one(du_lieu_nv)
                for ten_du_an in cac_du_an:
                    collection_nv_va_du_an.insert_one(
                        {"ma_nhan_vien": ma, "ma_du_an": du_an_options[ten_du_an]}
                    )
                st.success("✅ Đã thêm nhân viên.")
                # st.rerun()

        else:  # sửa
            collection_nhan_vien.update_one({"ma": ma}, {"$set": du_lieu_nv})
            collection_nv_va_du_an.delete_many({"ma_nhan_vien": ma})
            for ten_du_an in cac_du_an:
                collection_nv_va_du_an.insert_one(
                    {"ma_nhan_vien": ma, "ma_du_an": du_an_options[ten_du_an]}
                )
            st.success("✅ Đã cập nhật nhân viên.")
            # st.rerun()

# Xóa nhân viên
st.subheader("🗑️ Xóa nhân viên")
ma_can_xoa = st.selectbox("Chọn mã nhân viên để xóa", df["ma"].tolist())
if st.button("Xóa"):
    collection_nhan_vien.delete_one({"ma": ma_can_xoa})
    collection_nv_va_du_an.delete_many({"ma_nhan_vien": ma_can_xoa})
    st.success("Đã xóa nhân viên.")
    st.rerun()
