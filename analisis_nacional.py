import streamlit as st
import folium as fl
from streamlit_folium import folium_static
from folium.plugins import HeatMap
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
from folium import plugins
from branca.colormap import linear
import geopandas as gpd
from shapely.geometry import Point

# Análisis a nivel nacional
def visualizacion_a_nivel_nacional(archivo):
    # Leemos nuestro data set
    df = pd.read_excel(archivo)

    # Extraemos Año, Mes y Día de la columna Fecha_UTC del data set
    df["Anio"] = df["FECHA_UTC"].astype(str).str[:4]
    df["Mes"] = df["FECHA_UTC"].astype(str).str[4:6]
    df["Dia"] = df["FECHA_UTC"].astype(str).str[6:]

    # Encontramos el mínimo y el máximo de años comprendidos
    min_anio = df["Anio"].astype(int).min()
    max_anio = df["Anio"].astype(int).max()
    min_prof = df["PROFUNDIDAD"].astype(int).min()
    max_prof = df["PROFUNDIDAD"].astype(int).max()

    selected_min_anio = min_anio
    selected_max_anio = max_anio

    anios_comprendidos = []
    for i in range(min_anio, max_anio + 1):
        anios_comprendidos.append(i)
    st.subheader("MAPA DE CALOR DE EVENTOS SÍSMICOS POR CONCURRENCIA EN ZONAS GEOGRÁFICAS Y DISTRIBUCIÓN POR PROFUNDIDAD")
    st.markdown(
        '<div style="background-color: white; padding: 10px; border-radius: 10px;">'
        '<h>En esta sección, se presenta el análisis de la concurrencia de eventos sísmicos mediante un mapa de calor, '
        'junto con la distribución de estos por profundidad. Esta última, ya sea superficial, intermedia'
        ' o profunda, influye en la forma en que el sismo afecta a la superficie, por ende, el potencial destructivo.'
        ' A continuación, se ofrece la opción de búsqueda de eventos por fechas, ya sea de manera puntual o en rangos,'
        ' acompañada de una gráfica estadística para facilitar su comprensión.</h>'
        '</div>',
        unsafe_allow_html=True
    )
    st.divider()
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    with col1:
        # Selección del tipo de búsqueda
        st.write("Seleccione la forma de búsqueda:")
        opcion = st.radio( 
            "Mostrar los eventos por",
            [ "**Mapa de calor**","**Distribución por porfundidad**"],
            captions = ["*con opción de búsqueda por fechas.*", "*con opción de búsqueda por fechas.*"],
            index=None)
        
    with col2:   
        # Mostraremos la información correspondiente a la opción seleccionada
        st.markdown(f"*Filtro de información de: {opcion}*")

    if opcion == None:
        # Inicializamos la previsualización con el mapa centrado 
        mapa = fl.Map(location=[-9.189967, -75.015152], zoom_start=5)
        folium_static(mapa) 

    if opcion == "**Mapa de calor**":
        with col2:
            op_fecha1 = st.selectbox(
                "Por",
                ("años puntuales","ninguno"),
                index=None, placeholder="Seleccione . . .")
            
            if op_fecha1 == "años puntuales":
                fe_punt = st.multiselect(
                    "El año puntual de búsqueda es:",
                    anios_comprendidos, placeholder="elija")
                
                if fe_punt:
                    # Almacenamos los años puntuales seleccionados para después usarlos como filtro
                    fe_punt = list(map(int, fe_punt))

                    # Filtrarmos el DataFrame para incluir solo los años seleccionados
                    df_filtrado_opcion = df[df['Anio'].astype(int).isin(fe_punt)]

                    mapa = fl.Map(location=[df_filtrado_opcion['LATITUD'].mean(), df_filtrado_opcion['LONGITUD'].mean()], 
                                zoom_start=5.5, max_zoom=10, control_scale=True, width="100%", height="100%")

                    for index, row in df_filtrado_opcion.iterrows():
                        fl.Marker([row['LATITUD'], row['LONGITUD']],
                                    popup=f"Profundidad: {row['PROFUNDIDAD']} km\nMagnitud: {row['MAGNITUD']}").add_to(mapa)

                    heat_data = [[row['LATITUD'], row['LONGITUD']] for index, row in df_filtrado_opcion.iterrows()]
                    HeatMap(heat_data, name='Mapa de Calor', radius=50, max_zoom=15).add_to(mapa)
                    
                    # Construir la leyenda en HTML
                    legend_html = """
                        <div style="position: fixed; 
                                    bottom: 35px; left: 5px; width: 220px; height: 130px; 
                                    border:3px solid grey; z-index:9999; font-size:14px;
                                    background-color:white;text-align: center;
                                    border-radius: 6px;">
                            &nbsp; <span style="text-decoration: underline;", class="font-monospace">Leyenda</span> <br>
                            &nbsp; <span class="font-monospace">Baja concurrencia</span> &nbsp; 
                            <div style="width: 20px; height: 20px; background-color: green; display: inline-block;"></div>
                            &nbsp; <span class="font-monospace">Concurrencia moderada</span> &nbsp; 
                            <div style="width: 20px; height: 20px; background-color: orange; display: inline-block;"></div>
                            &nbsp; <span class="font-monospace">Alta concurrencia</span> &nbsp; 
                            <div style="width: 20px; height: 20px; background-color: red; display: inline-block;"></div>
                        </div>
                    """


                    # Convertir la leyenda HTML a un objeto de Folium
                    legend = fl.Element(legend_html)

                    # Agregar la leyenda al mapa
                    mapa.get_root().html.add_child(legend)
                
                    with col3:
                        st.components.v1.html(mapa._repr_html_(), width=710, height=470)
                else: 
                    with col3: 
                        mapa = fl.Map(location=[-9.189967, -75.015152], zoom_start=5)
                        folium_static(mapa)
            else: 
                with col3: 
                    mapa = fl.Map(location=[-9.189967, -75.015152], zoom_start=5)
                    folium_static(mapa) 

    if opcion == "**Distribución por porfundidad**":
        with col2:
            op_fecha2 = st.selectbox(
                "Por",
                ("rango de años", "ninguno"),
                index=None, placeholder="Seleccione . . .")
            

        if op_fecha2 == "rango de años":
            with col2:
                min_anio_option = st.selectbox('Selecciona el año mínimo', options=list(range(min_anio, max_anio + 1)), 
                                            index=None, placeholder="elija")
            if min_anio_option is not None:
                with col2:
                    if min_anio_option >= min_anio: 
                        max_anio_option = st.selectbox('Selecciona el año máximo', 
                                                    options=list(range(min_anio_option, max_anio + 1)))
                        max_anio = max_anio_option  
                        min_anio = min_anio_option      
                            
                        df_filtrado_opcion = df[
                            (df['Anio'].astype(int) >= min_anio) & (df['Anio'].astype(int) <= max_anio)
                        ]

                color_ub = ""                                   
                mapa = fl.Map(location=[df_filtrado_opcion['LATITUD'].mean(), df_filtrado_opcion['LONGITUD'].mean()], 
                            zoom_start=4.6, max_zoom=12, control_scale=True)

                for index, row in df_filtrado_opcion.iterrows():
                    if row['PROFUNDIDAD'] < 70:
                        color_ub = "red"
                    elif (row['PROFUNDIDAD'] >= 70) and (row['PROFUNDIDAD'] < 300):
                        color_ub = "orange"
                    elif row['PROFUNDIDAD'] >= 300:
                        color_ub = "green"

                    fl.Marker([row['LATITUD'], row['LONGITUD']], icon=fl.Icon(color=color_ub, icon="circle", prefix="fa"),
                            popup=f"Profundidad: {row['PROFUNDIDAD']} km\nMagnitud: {row['MAGNITUD']}").add_to(mapa)

                # Construir la leyenda en HTML
                legend_html = """
                    <div style="position: fixed; 
                                bottom: 50px; left: 50px; width: 150px; height: 100px; 
                                border:3px solid grey; z-index:9999; font-size:14px;
                                background-color:white;text-align: center;
                                border-radius: 6px;">
                        &nbsp; <span style="text-decoration: underline;", class="font-monospace">Leyenda</span> <br>
                        &nbsp; <span class="font-monospace">Superficiales</span> &nbsp; 
                        <i class="fa fa-map-marker" style="color:red"></i><br>
                        &nbsp; <span class="font-monospace">Intermedios</span> &nbsp; 
                        <i class="fa fa-map-marker" style="color:orange"></i><br>
                        &nbsp; <span class="font-monospace">Profundos</span> &nbsp; 
                        <i class="fa fa-map-marker" style="color:green"></i><br>
                    </div>
                """

                # Convertir la leyenda HTML a un objeto de Folium
                legend = fl.Element(legend_html)

                # Agregar la leyenda al mapa
                mapa.get_root().html.add_child(legend)
                st.markdown(
                    """
                    <div style="background-color: white; padding: 10px; border-radius: 10px;">
                        <p>
                            Una vez seleccionada la fecha, podrás observar dos gráficos. El primero es un mapa con ubicaciones marcadas,
                            mientras que el segundo es un gráfico de barras. La información sobre la frecuencia de eventos se presenta en
                            el segundo gráfico, donde cada barra indica el nivel de profundidad.
                        </p>
                        <p>
                            Cada nivel está representado por rangos de colores característicos:
                        </p>
                        <ul>
                            <li>Rojo: Sismos superficiales (0-70 km de profundidad)</li>
                            <li>Naranja: Sismos intermedios (70-300 km de profundidad)</li>
                            <li>Verde: Sismos profundos (más de 300 km de profundidad)</li>
                        </ul>
                        <p>
                            En el mapa, también puedes ubicar estos niveles mediante la lectura de la leyenda.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.components.v1.html(mapa._repr_html_(), width=710, height=470)
                    
                # Asignamos los colores para identificarlo en el gráfico de barras
                colores_barras = ['red', 'orange', 'green']
                # Actualizamos el DataFrame de frecuencia por rango de Profundidad de acuerdo al año seleccionado
                conteo_rangos_profundidad_filtrado = pd.cut(df_filtrado_opcion['PROFUNDIDAD'],bins=[0,70,300,max_prof]).value_counts().sort_index()
                df_conteo_rangos_profundidad_filtrado = pd.DataFrame({'RANGO_PROFUNDIDAD': [str(rango) for rango in conteo_rangos_profundidad_filtrado.index],
                                                                            'FRECUENCIA_PROFUNDIDAD': conteo_rangos_profundidad_filtrado.values})
    
                cero, uno, dos = df_conteo_rangos_profundidad_filtrado['FRECUENCIA_PROFUNDIDAD']
                nivel_mostrar = "superficial"
                numero_mostrar = cero
                informac = "al ser muy recurrentes, porque sucedieron cerca de la superficie, \
                            tuvieron un impacto directo y más fuerte en las estructuras\
                            que generó movimientos repentinos y rápidos, lo que contribuyó a un mayor riesgo de daños."
                if cero < uno:
                    if uno < dos:
                        nivel_mostrar = "profundo"
                        numero_mostrar = dos
                        informac = "tuvieron menos impacto en la superficie debido a su mayor profundidad.\
                                    La energía liberada en la superficie fue menor en comparación con los sismos superficiales\
                                    porque fueron percibidos con menos intensidad en la superficie."
                    
                    nivel_mostrar = "intermedio"
                    numero_mostrar = uno
                    informac = ", aunque tubieron menos impacto directo en la superficie que los sismos superficiales, fueron significativos \
                                el cual generó movimientos sísmicos que afectaron áreas más extensas."
                                                
                
                # Creamos gráfico Plotly Express con el Dataframe de Rangos actualizado
                fig = px.bar(df_conteo_rangos_profundidad_filtrado, x='RANGO_PROFUNDIDAD', y='FRECUENCIA_PROFUNDIDAD', color='RANGO_PROFUNDIDAD', color_discrete_sequence=colores_barras, labels={'FRECUENCIA_PROFUNDIDAD': 'Frecuencia '})
                if min_anio == max_anio:
                    tex = ""
                    texto_max = " para el año "
                    texto_max2 = f"{min_anio}"
                else: 
                    tex = f"-{max_anio}"
                    texto_max =  " entre los años "
                    texto_max2 = f"{min_anio} - {max_anio}"
                fig.update_layout(title={'text': f'Frecuencia de Sismos en Rangos de Profundidad ({min_anio}{tex})','x': 0.2,},xaxis_title='Rango de Profundidad (Km)',yaxis_title='Frecuencia',height=500,width=712)
                fig.update_traces(marker=dict(line=dict(color='black', width=1)), selector=dict(type='bar'))
                st.plotly_chart(fig)
                st.subheader("Después de visualizar el mapa y el gráfico de barras, se detalla lo siguiente: ") 
                st.write(
                    f'<div style="background-color: white; padding: 10px; border-radius: 10px;">'
                    f'<h> De este modo se observa que {texto_max} <span style="color: red;">{texto_max2}</span>, resalta la presencia de eventos sísmicos a un nivel de profundidad'
                    f' <span style="color: red;">{nivel_mostrar}</span>, calculados desde el hipocentro hasta la capa superficial de la tierra, en comparación con las demás.'
                    f' Y esta, contabiliza un total de <span style="color: red;">{numero_mostrar}</span> puntos de evento. De manera tal, se puede inferir'
                    f' que {informac}</h>'
                    '</div>',
                    unsafe_allow_html=True
                )             
            else:  
                mapa = fl.Map(location=[-9.189967, -75.015152], zoom_start=5)
                folium_static(mapa) 
        else:  
            mapa = fl.Map(location=[-9.189967, -75.015152], zoom_start=5)
            folium_static(mapa)

def mostrar_dashboard(archivo_excel):
    df = pd.read_excel(archivo_excel)
    
    # Extraer Año, Mes y Día de la columna Fecha_UTC
    df['Año'] = df['FECHA_UTC'].astype(str).str[:4]
    df['Mes'] = df['FECHA_UTC'].astype(str).str[4:6]
    df['Día'] = df['FECHA_UTC'].astype(str).str[6:]


    # Crear slider para seleccionar un rango de años de 'Fecha_UTC'
    min_year = df['Año'].astype(int).min()
    max_year = df['Año'].astype(int).max()
    #----------------------------------------------------------------------------
    st.subheader("MAGNITUD DE LOS SISMOS TOMANDO EN CUENTA LOS AÑOS")
    st.text("SELECCIONE EL RANGO DE AÑOS EN EL QUE DESEA VER EL GRÁFICO DE MAGNITUD")
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
    
    # Crear gráfico Plotly Express con el Dataframe de Rangos actualizado
    fig_ = px.bar(df_conteo_rangos_magnitud_filtrado, x='RANGO_MAGNITUD', y='FRECUENCIA_MAGNITUD', color='RANGO_MAGNITUD', labels={'FRECUENCIA_MAGNITUD': 'Frecuencia'})
    fig_.update_layout(title=f'Frecuencia de Sismos en Rangos de Magnitud ({selected_year[0]} - {selected_year[1]})', xaxis_title='Rango de Magnitud', yaxis_title='Frecuencia',height=500,width=712)

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
        st.text("GRÁFICO DE BARRAS DE LOS RANGOS DE MAGNITUD PRESENTES EN LOS SISMOS RESPECTO\n"
        "A LOS AÑOS SELECCIONADOS")
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
        mapa_filtrado_opcion = fl.Map(location=[df_filtrado_opcion['LATITUD'].iloc[0], df_filtrado_opcion['LONGITUD'].iloc[0]],
                                        zoom_start=10, control_scale=True, prefer_canvas=True)  # Nuevos parámetros

        for i, row in df_filtrado_opcion.iterrows():
            # Personalizar el icono del marcador
            fl.Marker([row['LATITUD'], row['LONGITUD']],
                        popup=f"MAGNITUD: {row['MAGNITUD']}",
                        icon=fl.Icon(color='blue', icon='info-sign')).add_to(mapa_filtrado_opcion)  # Cambiar el color y el icono

        # Agregar capa adicional de Stamen Watercolor
        fl.TileLayer('Stamen Watercolor', attr='OpenStreetMap contributors').add_to(mapa_filtrado_opcion) 
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
