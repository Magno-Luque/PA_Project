import streamlit as st
from PIL import Image
from analisis_nacional import visualizacion_a_nivel_nacional
from analisis_departamental import load_department_boundaries, load_data, assign_departments, show_departments_count
from analisis_magnitud_1 import mostrar_dashboard

page_bg_img = f"""
    <style>
    [data-testid="stAppViewContainer"] > .main {{
        background-image: url("https://raw.githubusercontent.com/Magno-Luque/PA_Project/main/imagenes/image2.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: local;
    }}
    </style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

image = Image.open('imagenes/image.png')


# Añadimos un panel de control
tab1, tab2, tab3 = st.tabs([":blue[**INICIO**] :derelict_house_building:", ":blue[_Análisis a nivel nacional_]", ":blue[_Análisis a nivel departamental_]"])

with tab1:
    st.image(image1)

# Análisis a nivel nacional
with tab2:
    visualizacion_a_nivel_nacional("Catalogo1960_2022.csv")


# Análisis a nivel departamental
with tab3:
    st.header("Análisis Departamental")
    department_boundaries = load_department_boundaries()
    file_path = 'Proyecto_final.csv'
    data = load_data(file_path)
    merged_data = assign_departments(data, department_boundaries)
    show_departments_count(merged_data)
