import streamlit as st
import firebase_admin 
from firebase_admin import credentials, firestore
import pandas as pd
from io import BytesIO
#-- ket noi firebase (chi khoi tao 1 lan duy nhat)
@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate("scalp-trade-5m-firebase-adminsdk-fbsvc-382ef870b4.json");
        firebase_admin.initialize_app(cred)
    return firestore.client()
    
db = init_firebase()

#--- giao dien ---
st.title("Streamlit + Firebase Demo")

#--- form nhap du lieu ---
name = st.text_input("Tên: ")
age = st.number_input("Tuổi: ", 0, 120)

if st.button("Lưu vào firebase"):
    if name.strip():
        doc_ref = db.collection("users").document()
        doc_ref.set({
            "name" : name,
            "age" : age
        })
        st.success("Đã lưu thành công!")
        st.rerun()
    else:
        st.warning("Vui lòng nhập tên trước khi lưu")
#--- lấy dữ liệu từ firestore ---
users_ref = db.collection("users").stream()
data = [doc.to_dict() for doc in users_ref]
if data:
    df = pd.DataFrame(data)
    st.subheader("Dữ liệu đã lưu: ")
    #-- căn giữ bảng
    st.markdown("""
        <style>
            table {
                text-align: center !important;
                border-collapse: collapse !important;
            }
            th, td {
                text-align: center !important;
                padding: 8px !important;
            }
            thead tr {
                background-color: #f0f2f6 !important;
            }
        </style>
    """, unsafe_allow_html=True)

    st.dataframe(df, use_container_width=True)
    
    # tùy chọn xuất file csv
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label = "Tải dữ liệu CSV",
        data = csv,
        file_name = "users.csv",
        mime = "text/csv",
    )
    #-- xuất file excel    
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine = 'xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Users', startrow=1, header=False)
        
        workbook = writer.book
        worksheet = writer.sheets['Users']
        #-- lấy kích thước bảng
        (max_row, max_col) = df.shape
        #-- tạo style: căn giữa + kẻ ô
        border_fmt = workbook.add_format({
            'border' : 1,
            'align' : 'center',
            'valign' : 'vcenter'
        })
        #-- Ghi header có border và tô nền nhẹ
        header_fmt = workbook.add_format({
            'bold' : True,
            'border' : 1,
            'bg_color' : '#DCE6F1',
            'align' : 'center',
            'valign' : 'vcenter'            
        })
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_fmt)
            # auto fit cột theo độ dài dữ liệu
            column_len = max(df[value].astype(str).map(len).max(), len(value)) + 2
            worksheet.set_column(col_num, col_num, column_len)
        # Áp dụng border cho toàn bộ vùng dữ liệu
        worksheet.conditional_format(1, 0, max_row, max_col - 1, {
            'type': 'no_blanks',
            'format': border_fmt
        })    
    output.seek(0)
    excel_data = output.read()
    
    st.download_button(
        label = "Tải file excel",
        data = excel_data,
        file_name = "users.xlsx",
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )    
else:
    st.info("Chưa có dữ liệu nào trong firestore")