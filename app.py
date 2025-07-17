import streamlit as st
from pymongo import MongoClient

# Hello World
# Kết nối tới MongoDB local (thông qua Compass)
# làm bài tập với MongoDB và Streamlit
st.title("Hello World! 🌍")
MONGO_URI = "mongodb://localhost:27017"  # Nếu dùng Compass local
client = MongoClient(MONGO_URI)

# Chọn database và collection
db = client["emp"]
collection = db["restaurants"]  # ✅ Đã sửa lại tên collection

# Truy vấn tất cả restaurants
restaurants = list(collection.find())

# Hiển thị với Streamlit
st.title("📋 Danh sách tất cả các Restaurants")

if not restaurants:
    st.warning("⚠️ Không có dữ liệu nào trong collection 'restaurants'.")
else:
    for idx, r in enumerate(restaurants, 1):
        st.subheader(f"🍽️ Restaurant {idx}")
        st.json(r)
