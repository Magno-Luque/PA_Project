import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from shapely.geometry import Point
from streamlit_folium import folium_static
import plotly.express as px

@st.cache_data
def load_department_boundaries():
    peru_departments = gpd.read_file('departamentos_perú.geojson')
    return peru_departments
    
@st.cache_data
def load_data(file):
    data = pd.read_csv(file)
    # Rename 'FECHA_UTC' to 'Año'
    data['Año'] = data['FECHA_UTC'].astype(str).str[:4]
    data['Mes'] = data['FECHA_UTC'].astype(str).str[4:6]
    data['Día'] = data['FECHA_UTC'].astype(str).str[6:]
    return data

def assign_departments(data, department_boundaries):
    geometry = [Point(xy) for xy in zip(data['LONGITUD'], data['LATITUD'])]
    geo_df = gpd.GeoDataFrame(data, geometry=geometry, crs='EPSG:4326')
    merged = gpd.sjoin(geo_df, department_boundaries, op='within')
    return merged

def create_map(data):
    if not data.empty:
        st.subheader('Mapa de Puntos')
        m = folium.Map(location=[-9.1900, -75.0152], zoom_start=6)

        for index, row in data.iterrows():
            folium.Marker([row['LATITUD'], row['LONGITUD']]).add_to(m)

        folium_static(m)
    else:
        st.info("No hay datos disponibles para mostrar en el mapa.")

def show_departments_count(data):
    st.subheader('Mapa Sísmico del Perú periodo 1960-2022 (IGP) ')

    data = data.rename(columns={'NOMBDEP': 'DEPARTAMENTOS'})
    options = ['DEPARTAMENTOS','GRÁFICOS DE LINEA']

    selected_column = st.selectbox('Selecciona una columna:', options)
    default_department = data[selected_column].unique()[0]
    selected_values = st.multiselect(f'Selecciona valor(es) de {selected_column}:', data[selected_column].unique(),
                                     default=default_department)

    # Filter data based on the selected column and value(s)
    filtered_data = data[data[selected_column].isin(selected_values)]

    # Filter data based on the selected years using the slider
    min_year = filtered_data['Año'].astype(int).min()
    max_year = filtered_data['Año'].astype(int).max()

    st.text("SELECCIONE EL RANGO DE AÑOS EN EL QUE DESEA VER LAS TABLAS Y EL GRAFICO DE PROFUNDIDAD")
    selected_years = st.slider('Seleccione:',
                               min_value=min_year,
                               max_value=max_year,
                               value=(min_year, max_year),
                               key="select_slider_years")

    # Apply the year filter
    filtered_data = filtered_data[(filtered_data['Año'].astype(int) >= selected_years[0]) &
                                  (filtered_data['Año'].astype(int) <= selected_years[1])]

    department_count = filtered_data.shape[0]
    st.write(f'En {selected_column} hay {department_count} puntos para los años {selected_years[0]} - {selected_years[1]}.')
    create_map(filtered_data)

    # Gráfico de barras con intervalo dinámico en el eje y
    st.subheader(f'Cantidad de Sismos por {selected_column}')
    fig = px.bar(filtered_data[selected_column].value_counts(),
                 x=filtered_data[selected_column].value_counts().index,
                 y=filtered_data[selected_column].value_counts().values)

    # Ajustar dinámicamente el dtick basado en la cantidad de datos
    dtick_value = max(1, int(department_count / 10))  # Puedes ajustar el divisor según tus preferencias
    fig.update_layout(xaxis_title=selected_column, yaxis_title=f'Cantidad de Sismos en {selected_column}', yaxis=dict(dtick=dtick_value))
    st.plotly_chart(fig)
