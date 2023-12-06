import streamlit as st
from PIL import Image
from analisis_nacional import visualizacion_a_nivel_nacional
from analisis_departamental import load_department_boundaries, load_data, assign_departments, show_departments_count

page_bg_img = f"""
    <style>
    [data-testid="stAppViewContainer"] > .main {{
        background-image: url("C:\Users\Magno Ricardo\Proyecto_PA_2023_2\imagen2.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: local;
    }}
    </style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

image1 = Image.open('image1.png')


# Añadimos un panel de control
tab1, tab2, tab3 = st.tabs(["Inicio", "Análisis a nivel nacional", "Anális a nivel departamental"])

with tab1:
    st.image(image1)

# Análisis a nivel nacional
with tab2:
    visualizacion_a_nivel_nacional("Catalogo1960_2022.xlsx")


# Análisis a nivel departamental
with tab3:
    st.header("Análisis a nivel departamental")
    department_boundaries = load_department_boundaries()
    file_path = 'Proyecto_final.csv'
    data = load_data(file_path)
    merged_data = assign_departments(data, department_boundaries)
    show_departments_count(merged_data)
