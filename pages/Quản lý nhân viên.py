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

def XoaNhanVien(ma_nhan_vien_muon_xoa):
    collection_nhan_vien.delete_one({"ma": ma_nhan_vien_muon_xoa})
    collection_nv_va_du_an.delete_many({"ma_nhan_vien": ma_nhan_vien_muon_xoa})
    st.success("Đã xóa nhân viên.")
    # st.rerun()

def ThemNhanVienVaDuAnThamGia(du_lieu_nhan_vien, du_lieu_cac_ma_du_an_tham_gia):
    if collection_nhan_vien.find_one({"ma": du_lieu_nhan_vien["ma"]}):
        st.warning("⚠️ Mã nhân viên đã tồn tại. Vui lòng nhập mã khác.")
        return
    st.write(du_lieu_cac_ma_du_an_tham_gia)
    collection_nhan_vien.insert_one(du_lieu_nhan_vien)
    du_lieu_nhan_vien_va_du_an = [{"ma_nhan_vien": du_lieu_nhan_vien["ma"], "ma_du_an": ma_du_an} for ma_du_an in du_lieu_cac_ma_du_an_tham_gia]

    if du_lieu_nhan_vien_va_du_an:
        collection_nv_va_du_an.insert_many(du_lieu_nhan_vien_va_du_an)
       
    # st.write(du_lieu_nhan_vien_va_du_an)
    st.success("✅ Đã thêm nhân viên.")

def SuaNhanVien(du_lieu_nhan_vien, du_lieu_cac_ma_du_an_tham_gia):
    collection_nhan_vien.update_one({"ma": du_lieu_nhan_vien["ma"]}, {"$set": du_lieu_nhan_vien})
    collection_nv_va_du_an.delete_many({"ma_nhan_vien": du_lieu_nhan_vien["ma"]})
    du_lieu_du_an = [{"ma_nhan_vien": du_lieu_nhan_vien["ma"], "ma_du_an": ma_du_an} for ma_du_an in du_lieu_cac_ma_du_an_tham_gia]
    if du_lieu_du_an:
        collection_nv_va_du_an.insert_many(du_lieu_du_an)
    st.success("✅ Đã cập nhật nhân viên.")

      
# Truy vấn dữ liệu nhân viên
def LayNhanVienDF():
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
                "as": "danh_sach_nhan_vien_va_du_an_tham_gia",
            }
        },
        # Nối với bảng du_an để lấy tên
        {
            "$lookup": {
                "from": "du_an",
                "localField": "danh_sach_nhan_vien_va_du_an_tham_gia.ma_du_an",
                "foreignField": "ma",
                "as": "du_annh_sach_du_an_tham_gia",
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
                "hop_chon_phong_ban": "$phong_ban_truc_thuoc.ten",
                "du_annh_sach_du_an_tham_gia": "$du_annh_sach_du_an_tham_gia.ten",
            }
        },
    ]
    danh_sach_thong_tin_nhan_vien = list(collection_nhan_vien.aggregate(cau_truy_van))
    return pd.DataFrame(danh_sach_thong_tin_nhan_vien)


st.title("Quản lý Nhân viên")

# Danh sách nhân viên
st.subheader("📋 Danh sách thông tin nhân viên")

df = LayNhanVienDF()
st.dataframe(df)

# du_annh sách phòng ban để chọn
ds_phong_ban = list(collection_phong_ban.find({}, {"_id": 0}))
cac_lua_chon_phong_ban = {phong_ban["ten"]: phong_ban["ma"] for phong_ban in ds_phong_ban}

# du_annh sách dự án để chọn
ds_du_an = list(collection_du_an.find({}, {"_id": 0}))
cac_lua_chon_du_an = {du_an["ten"]: du_an["ma"] for du_an in ds_du_an}

st.subheader("✍️ Thêm / Sửa nhân viên")
che_do_chon = st.radio("Chọn chế độ:", ["Thêm", "Sửa"], horizontal=True)

# Nếu Sửa thì lấy dữ liệu nhân viên và các dự án đang tham gia
if che_do_chon == "Sửa":
    ds_ma_nv = df["ma"].tolist()
    selected_ma = st.selectbox("Chọn mã nhân viên để sửa", ds_ma_nv)
    thong_tin_nhan_vien = collection_nhan_vien.find_one({"ma": selected_ma}, {"_id": 0})

    # Lấy du_annh sách mã dự án nhân viên đang tham gia
    du_annh_sach_du_an_du_an_tham_gia = list(
        collection_nv_va_du_an.find(
            {"ma_nhan_vien": selected_ma}, {"_id": 0, "ma_du_an": 1}
        )
    )
    # Chuyển mã dự án thành tên dự án
    cac_du_lieu_du_an_chon = [
        ten for ten, ma in cac_lua_chon_du_an.items()
        if any(ma == d["ma_du_an"] for d in du_annh_sach_du_an_du_an_tham_gia)
    ]
else:
    thong_tin_nhan_vien = {}
    cac_du_lieu_du_an_chon = []

with st.form("form_nhan_vien"):
    if che_do_chon == "Sửa":
        ma = thong_tin_nhan_vien.get("ma", "")
        st.text_input("Mã nhân viên", ma, disabled=True)
    else:
        ma = st.text_input("Mã nhân viên", "")
    ten = st.text_input("Tên", thong_tin_nhan_vien.get("ten", ""))
    nam_sinh = st.number_input("Năm sinh", value=int(thong_tin_nhan_vien.get("nam_sinh", 1990)))
    gioi_tinh = st.selectbox(
        "Giới tính",
        ["Nam", "Nữ"],
        index=0 if thong_tin_nhan_vien.get("gioi_tinh", "Nam") == "Nam" else 1,
    )
    dia_chi = st.text_input("Địa chỉ", thong_tin_nhan_vien.get("dia_chi", ""))
    sdt = st.text_input("SĐT", thong_tin_nhan_vien.get("sdt", ""))
    hop_chon_phong_ban = st.selectbox("Phòng ban", list(cac_lua_chon_phong_ban.keys()))
    hop_nhieu_lua_chon_du_an = st.multiselect("Các dự án tham gia", list(cac_lua_chon_du_an.keys()), default=cac_du_lieu_du_an_chon)

    submitted = st.form_submit_button("💾 Lưu")

    if submitted:
        du_lieu_nv = {
            "ma": ma,
            "ten": ten,
            "nam_sinh": nam_sinh,
            "gioi_tinh": gioi_tinh,
            "dia_chi": dia_chi,
            "sdt": sdt,
            "ma_phong_ban": cac_lua_chon_phong_ban[hop_chon_phong_ban],
        }
        ma_du_an_da_chon = [cac_lua_chon_du_an[ten] for ten in hop_nhieu_lua_chon_du_an]
        st.write(ma_du_an_da_chon)
        if che_do_chon == "Thêm":
            ThemNhanVienVaDuAnThamGia(du_lieu_nv, ma_du_an_da_chon)
        else:
            SuaNhanVien(du_lieu_nv, ma_du_an_da_chon)
            

# Xóa nhân viên
st.subheader("🗑️ Xóa nhân viên")
ma_can_xoa = st.selectbox("Chọn mã nhân viên để xóa", df["ma"].tolist())
if st.button("Xóa"):
    XoaNhanVien(ma_can_xoa)

