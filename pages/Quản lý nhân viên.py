import streamlit as st
from pymongo import MongoClient
import pandas as pd

client = MongoClient("mongodb://localhost:27017")
db = client["emp"]
col_nv = db["nhan_vien"]

pipeline = [
    {
        "$lookup": {
            "from": "phong_ban",
            "localField": "id_phong_ban",
            "foreignField": "_id",
            "as": "phong_ban_info"
        }
    },
    {
        "$unwind": "$phong_ban_info"
    },
    {
        "$project": {
            "_id": 1,
            "ten": 1,
            "nam_sinh": 1,
            "gioi_tinh": 1,
            "dia_chi": 1,
            "sdt": 1,
            "ten_phong_ban": "$phong_ban_info.ten_phong_ban"
        }
    }
]

data = list(col_nv.aggregate(pipeline))

# Đổi _id sang chuỗi (nếu muốn)
for item in data:
    item["_id"] = str(item["_id"])

df = pd.DataFrame(data)

# Đổi tên cột
column_map = {
    "_id": "Mã nhân viên",
    "ten": "Tên",
    "nam_sinh": "Năm sinh",
    "gioi_tinh": "Giới tính",
    "dia_chi": "Địa chỉ",
    "sdt": "Số điện thoại",
    "ten_phong_ban": "Phòng ban"
}
df = df.rename(columns=column_map)

st.title("Danh sách Nhân viên kèm tên Phòng ban")
st.dataframe(df)
