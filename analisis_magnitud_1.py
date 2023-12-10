import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import folium
from folium import plugins
from streamlit_folium import folium_static
from branca.colormap import linear
import geopandas as gpd
from shapely.geometry import Point

def mostrar_dashboard(archivo_excel):
    df = pd.read_excel(archivo_excel)

    # Resto del código...
    # Extraer Año, Mes y Día de la columna Fecha_UTC
    df['Año'] = df['FECHA_UTC'].astype(str).str[:4]
    df['Mes'] = df['FECHA_UTC'].astype(str).str[4:6]
    df['Día'] = df['FECHA_UTC'].astype(str).str[6:]


    # Crear slider para seleccionar un rango de años de 'Fecha_UTC'
    min_year = df['Año'].astype(int).min()
    max_year = df['Año'].astype(int).max()
    #----------------------------------------------------------------------------
    st.subheader(' MAGNITUD DE LOS SISMOS TOMANDO EN CUENTA LOS AÑOS')
    st.text("SELECCIONE EL RANGO DE AÑOS EN EL QUE DESEA VER EL GRAFICO DE MAGNITUD")
    selected_year = st.slider('Seleccione:',
                                    min_value=min_year,
                                    max_value=max_year,
                                    value=(min_year, max_year),
                                    key="select_slider_year")
    # Rangos para Magnitud
    rangos_magnitud= pd.cut(df['MAGNITUD'], bins=5)
    df['Rango_Magnitud'] = rangos_magnitud.astype(str)
    df_filtrado_ = df[(df['Año'].astype(int) >= selected_year[0]) & (df['Año'].astype(int) <= selected_year[1])]
    # Actualizar el DataFrame de frecuencia por rango de Profundidad
    conteo_rangos_magnitud = pd.cut(df['MAGNITUD'], bins=5).value_counts().sort_index()
    df_conteo_rangos_magnitud = pd.DataFrame({'RANGO_MAGNITUD': [str(rango) for rango in conteo_rangos_magnitud.index],
                                                'FRECUENCIA_MAGNITUD': conteo_rangos_magnitud.values})

    # Actualizar el DataFrame de frecuencia por rango de Profundidad de acuerdo al año seleccionado
    conteo_rangos_magnitud_filtrado = pd.cut(df_filtrado_['MAGNITUD'], bins=5).value_counts().sort_index()
    df_conteo_rangos_magnitud_filtrado = pd.DataFrame({'RANGO_MAGNITUD': [str(rango) for rango in conteo_rangos_magnitud_filtrado.index],
                                                        'FRECUENCIA_MAGNITUD': conteo_rangos_magnitud_filtrado.values})

    # Mostrar los DataFrames en Streamlit
    
    # Crear gráfico Plotly Express con el Dataframe de Rangos actualizado
    fig_ = px.bar(df_conteo_rangos_magnitud_filtrado, x='RANGO_MAGNITUD', y='FRECUENCIA_MAGNITUD', color='RANGO_MAGNITUD', labels={'FRECUENCIA_MAGNITUD': 'Frecuencia'})
    fig_.update_layout(title=f'Frecuencia de Sismos en Rangos de Magnitud ({selected_year[0]} - {selected_year[1]})', xaxis_title='Rango de Magnitud', yaxis_title='Frecuencia')


    # Mostrar el gráfico en Streamlit


    #-------------------------------------------------
    # Crear un DataFrame para la frecuencia de rangos de magnitudes a lo largo de los años
    df_frecuencia_rangos_magnitudes = df.groupby(['Año', pd.cut(df['MAGNITUD'], bins=10)]).size().reset_index(name='FRECUENCIA')

    # Renombrar la columna de rangos de magnitudes para mejorar la presentación en el gráfico
    df_frecuencia_rangos_magnitudes['Rango_Magnitud'] = df_frecuencia_rangos_magnitudes['MAGNITUD'].astype(str)
    df_frecuencia_rangos_magnitudes['Rango_Magnitud'] = df_frecuencia_rangos_magnitudes['Rango_Magnitud'].str.replace('(', '[')  # Cambiar el paréntesis para incluir el límite inferior

    # Filtrar el DataFrame de frecuencia por el rango de años seleccionado
    df_frecuencia_rangos_magnitudes_filtrado = df_frecuencia_rangos_magnitudes[
        (df_frecuencia_rangos_magnitudes['Año'].astype(int) >= selected_year[0]) &
        (df_frecuencia_rangos_magnitudes['Año'].astype(int) <= selected_year[1])
    ]

    # Crear gráfico de líneas con la frecuencia de rangos de magnitudes a lo largo de los años
    fig_lineas_rangos_magnitudes = px.line(df_frecuencia_rangos_magnitudes_filtrado, x='Rango_Magnitud', y='FRECUENCIA', color='Año',
                                        title='Frecuencia de Rangos de Magnitudes a lo largo de los Años')

    # Configurar diseño del gráfico de líneas
    fig_lineas_rangos_magnitudes.update_layout(xaxis_title='Rango de Magnitud', yaxis_title='Frecuencia', legend_title='Año')


    #-----------------------------------------------------------------
    #Seleccionar el tipo de grafico: 

    tipo_grafico = st.radio("Seleccione el tipo de gráfico:", ["Gráfico de Barras", "Gráfico de Líneas"])

    # Gráfico de barras
    if tipo_grafico == "Gráfico de Barras":
        st.text("GRAFICO DE BARRAS DE LOS RANGOS DE MAGNITUD PRESENTES EN LOS SISMOS RESPECTO A LOS AÑOS SELECCIONADOS")
        st.plotly_chart(fig_)

    # Gráfico de líneas
    elif tipo_grafico == "Gráfico de Líneas":
        st.text("GRÁFICO DE LÍNEAS: Frecuencia de Rangos de Magnitudes a lo largo de los Años")
        st.plotly_chart(fig_lineas_rangos_magnitudes)
    #----------------------------------------------

    # Mapa con opción de selección
    st.subheader('MAPA DE MAGNITUD TOMANDO EN CUENTA LA SELECCION DE LOS AÑOS')

    # Crear slider para la magnitud de los sismos
    min_value_7_5 = df['MAGNITUD'].min()
    max_value_7_5 = df['MAGNITUD'].max()

    min_selected_value_7_5, max_selected_value_7_5 = st.slider(
        'Selecciona un rango de valores de Magnitud',
        min_value_7_5, max_value_7_5, (min_value_7_5, max_value_7_5),
        key="slider_7_5"
    )

    # Crear opciones de selección para año y mes mínimo
    min_year_option = st.selectbox('Selecciona el año mínimo', options=list(range(min_year, max_year + 1)))

    min_month_option = st.selectbox('Selecciona el mes mínimo', options=['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'])

    # Crear opciones de selección para año y mes máximo
    max_year_option = st.selectbox('Selecciona el año máximo', options=list(range(min_year, max_year + 1)))

    max_month_option = st.selectbox('Selecciona el mes máximo', options=['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'])

    # Mapear los nombres de los meses a números
    meses_a_numeros = {'Enero': '01', 'Febrero': '02', 'Marzo': '03', 'Abril': '04', 'Mayo': '05', 'Junio': '06', 'Julio': '07', 'Agosto': '08', 'Septiembre': '09', 'Octubre': '10', 'Noviembre': '11', 'Diciembre': '12'}

    # Obtener los números de los meses
    min_month_option_num = meses_a_numeros[min_month_option]
    max_month_option_num = meses_a_numeros[max_month_option]

    # Filtrar el DataFrame por los rangos seleccionados
    df_filtrado_opcion = df[
        (df['Año'].astype(int) >= min_year_option) & (df['Mes'].astype(int) >= int(min_month_option_num)) &
        (df['Año'].astype(int) <= max_year_option) & (df['Mes'].astype(int) <= int(max_month_option_num)) &
        (df['MAGNITUD'] >= min_selected_value_7_5) & (df['MAGNITUD'] <= max_selected_value_7_5)
    ]

    # Actualizar el mapa con los filtros de opción de selección
    if not df_filtrado_opcion.empty:
        mapa_filtrado_opcion = folium.Map(location=[df_filtrado_opcion['LATITUD'].iloc[0], df_filtrado_opcion['LONGITUD'].iloc[0]],
                                        zoom_start=10, control_scale=True, prefer_canvas=True)  # Nuevos parámetros

        for i, row in df_filtrado_opcion.iterrows():
            # Personalizar el icono del marcador
            folium.Marker([row['LATITUD'], row['LONGITUD']],
                        popup=f"MAGNITUD: {row['MAGNITUD']}",
                        icon=folium.Icon(color='blue', icon='info-sign')).add_to(mapa_filtrado_opcion)  # Cambiar el color y el icono

        # Agregar capa adicional de Stamen Watercolor
        folium.TileLayer('Stamen Watercolor', attr='OpenStreetMap contributors').add_to(mapa_filtrado_opcion) 
        folium_static(mapa_filtrado_opcion)
    else:
        st.warning("No hay datos disponibles para los filtros seleccionados.")

    st.text("TABLA DE FRECUENCIA PARA UN RANGO DE MAGNITUD")
    st.dataframe(df_conteo_rangos_magnitud_filtrado)

    # Agregar botón de descarga para el gráfico de barras
    dataframe_download_button = st.download_button(
        label="Descargar Dataframe Seleccionado",
        data=df_conteo_rangos_magnitud_filtrado.to_html(),
        file_name="data_frame.html",
        key="download_frame_chart"
    )

    bar_chart_download_button = st.download_button(
        label="Descargar Gráfico de Barras",
        data=fig_.to_html(),
        file_name="grafico_barras.html",
        key="download_bar_chart"
    )

    line_chart_download_button = st.download_button(
        label="Descargar Gráfico de Líneas",
        data=fig_lineas_rangos_magnitudes.to_html(),
        file_name="grafico_lineas.html",
        key="download_line_chart"
    )


