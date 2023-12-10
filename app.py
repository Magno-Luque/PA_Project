import streamlit as st
from PIL import Image
from analisis_nacional import visualizacion_a_nivel_nacional
from analisis_departamental import load_department_boundaries, load_data, assign_departments, show_departments_count
from analisis_magnitud_1 import mostrar_dashboard
st.set_page_config(
    page_title="Sismos en el Perú",
    page_icon="volcano",
    initial_sidebar_state="expanded",
)

page_bg_img = """
    <style>
    [data-testid="stAppViewContainer"] > .main {
        background-image: url("https://raw.githubusercontent.com/gcdavidq/Project_PA/main/imagenes/image1.png");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    </style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)
image1 = Image.open('/imagenes/image1.png')

# Añadimos un panel de control
tab1, tab2, tab3 = st.tabs([":blue[**INICIO**]", ":blue[_**ANÁLISIS A NIVEL NACIONAL**_]", ":blue[_**ANÁLISIS A NIVEL DEPARTAMENTAL**_]"])

with tab1:
    font_style_cooper_black = 'font-family: "Cooper Black", sans-serif;';
    color = '#ba55d3'  
    st.markdown(f'<h1 style="color:{color}; font-family: Cooper Black, sans-serif;">ANÁLISIS SÍSMICO REGISTRADOS EN EL PERÚ (1960_2022)</h1>', unsafe_allow_html=True)

    st.image(image1)

# Análisis a nivel nacional
with tab2:
    visualizacion_a_nivel_nacional("Catalogo1960_2022.csv")
    mostrar_dashboard("Catalogo1960_2022.csv")




# Análisis a nivel departamental
with tab3:
    st.header("Análisis Departamental")
    department_boundaries = load_department_boundaries()
    file_path = 'Proyecto_final.csv'
    data = load_data(file_path)
    merged_data = assign_departments(data, department_boundaries)
    show_departments_count(merged_data)
