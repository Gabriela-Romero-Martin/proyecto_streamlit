'''
app.py

Visualización de Datos - IMAT
ICAI, Universidad Pontificia Comillas

Autor: 
    - Gabriela Romero Martín

Descripción:
Aplicación desarrollada en Streamlit para el análisis y la visualización de datos de ventas de una empresa del sector de alimentación. 
los datos proceden de los archivos CSV (parte_1 y parte_2) que se integran en un único dataset. 
El dashboardresultante se organiza en varias pestañas para analizar la información a nivel global, por tienda y estado, mostrando 
indicadores clave, rankings por ventas y patrones de estacionalidad. Además se incluye una pestaña con análisis adicionales como el 
impacto de promociones, festivos y la relación con dcoilwtico.  
'''

# Importamos las librerías necesarias. 
import numpy as np
import pandas as pd
import plotly.express as px 
import streamlit as st


# Creamos las variables globales, almacenamos el path de los datasets. 
PATH_1 = 'data/parte_1_bis.csv.gz'
PATH_2 = 'data/parte_2_bis.csv.gz'

# # Se han creado dos nuevos ficheros csv para almacenar los datos más pequeños para poder subirlos a github con el siguiente código. 
# # Paths de salida
# OUT_1 = "data/parte_1_bis.csv.gz"
# OUT_2 = "data/parte_2_bis.csv.gz"

# # Columnas necesarias según tu app.py
# NEEDED_COLS = [
#     "id",
#     "date",
#     "store_nbr",
#     "family",
#     "sales",
#     "onpromotion",
#     "holiday_type",
#     "dcoilwtico",
#     "state",
#     "transactions",
#     "year",
#     "month",
#     "week",
#     "day_of_week",
# ]

# def make_bis(in_path: str, out_path: str) -> None:
#     df = pd.read_csv(in_path)

#     missing = [c for c in NEEDED_COLS if c not in df.columns]
#     if missing:
#         raise ValueError(f"Faltan columnas en {in_path}: {missing}")

#     df_bis = df[NEEDED_COLS].copy()
#     df_bis.to_csv(out_path, index=False, compression="gzip")


# make_bis(PATH_1, OUT_1)
# make_bis(PATH_2, OUT_2)
# print("Generados:", OUT_1, "y", OUT_2)


# Definimos las funciones auxiliares. 
def month_name(m:int) -> str: 
    '''
    Función que pasa el mes en formato numérico recibido por argumentos a su nombre. 
    '''
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    if pd.isna(m): 
        return 'NA'
    m_int = int(m)
    return meses[m_int - 1] if 1 <= m_int <= 12 else str(m_int)

@st.cache_data(show_spinner=False)
def load_dataset(path1: str, path2: str) -> pd.DataFrame: 
    '''
    Función que carga y prepara los datos para que puedan ser analizados correctamente sin errores. Los carga y concatena ambos datasets 
    para trabajar con un solo DataFrame con todos los datos. 
    
    Args: 
        path1, path2 (str): los paths de ambos datasets con los que se va a trabajar. 
    Returns: 
        df (DataFrame): el dataframe limpio con todos los datos. 
    Decorador: 
        @st.cache_data(show_spinner=False): guarda el df resultante para que cuándo Streamlit re-ejecute el scripts no tenga que volver a 
        leer y procesar los CSV si no se ha producido ningún cambio. 
    '''
    dtype = {
    "store_nbr": "int16",
    "onpromotion": "int16",
    "cluster": "int16",
    "sales": "float32",
    "transactions": "float32",
}
    df1 = pd.read_csv(path1,dtype=dtype, low_memory=False)
    df2 = pd.read_csv(path2,dtype=dtype, low_memory=False)

    # Concatenamos todos los datos en un único DataFrame.  
    df = pd.concat([df1, df2], ignore_index=True)

    # Limpiamos el DataFrame obtenido. 
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date']).copy()

    # Pasamos los datos relevantes a formato numérico. 
    df['sales'] = pd.to_numeric(df['sales'], errors='coerce').fillna(0.0)
    df['transactions'] = pd.to_numeric(df['transactions'], errors='coerce').fillna(0.0)
    df['onpromotion'] = pd.to_numeric(df['onpromotion'], errors='coerce').fillna(0).astype(int)

    # Quitamos los duplicados.
    df = df.drop_duplicates(subset=['id'], keep='first').copy()
    return df

def render_sidebar() -> str: 
    '''
    Función para proporcionar una navegación sencilla. Dibuja un sidebar con un título y un select box para escoger entre 'Dashboard' 'Datos'
    y 'Acerca de' quedandose con la elección del usuario.  

    Returns: 
        selection (str): el valor de página seleccionado. 
    '''
    with st.sidebar: 
        st.title('Menú: ')
        selection = st.selectbox('Selección', ['Dashboard', 'Datos', 'Acerca de'])
        return selection
    
def set_data_section(df: pd.DataFrame): 
    '''
    Muestra en pantalla la sección de 'Datos'. 
    
    Args: 
        df (DataFrame): El dataset ya cargado y consolidado. 
    '''
    st.header('Datos')
    st.write('Vista previa del dataset completo ya consolidado. ')
    st.dataframe(df.head(50), use_container_width=True)

    # Mostramos datos básicos del dataset. 
    c1, c2, c3 = st.columns(3)
    c1.metric('Filas', f'{df.shape[0]:,}'.replace(',', '.'))
    c2.metric('Columnas', f'{df.shape[1]:,}'.replace(',', '.'))
    c3.metric('Tiendas únicas', f'{df['store_nbr'].nunique():,}'.replace(',', '.'))

    # Mostramos una lista de columnas en formato desplegable. 
    with st.expander('Columnas'): 
        st.write(list(df.columns))

def set_abuout_section(): 
    '''
    Muestra la sección de 'Acerca de', sección que muestra un breve texto descriptivo acerca de la aplicación. 
    '''
    st.header('Acerca de')
    st.write(
        'Dashboard creado en Streamlit para analizar ventas. '
        'Datos obtenidos de dos archivos tipo csv con el mismo esquema (parte_1 y parte_2)'
        'unificados mediante una concatenación de filas patra crear una única base de datos. '
    )

def set_dashboard_section(df: pd.DataFrame): 
    '''
    Muestra la sección del 'Dashboard', sección en la que encontramos las 4 pestañas pedidas. La pestaña 1 mostrando un análisi global, 
    la pestaña 2 un análisis de tienda, la pestaña 3 centrada en el estado y por último la pestaña 4 que analiza las promociones, los festivos 
    y la relación entre las ventas y el dcoilwtico. 
     
    Args: 
        df (DataFrame): el dataset ya cargado y consolidado. 
    '''
    st.title('Dashboard de Ventas')
    st.caption('Dataset unificado: parte_1 + parte_2')
    st.divider()

    # Creamos las 4 pestañas. 
    tab1, tab2, tab3, tab4 = st.tabs(['Pestaña 1: Global', 'Pestaña 2: Tienda', 'Pestaña 3: Estado', 'Pestaña 4: Insights'])

    # Rellenamos la pestaña 1. 
    with tab1: 
        st.subheader('Análisi global')

        # Conteo general. 
        c1, c2, c3, c4 = st.columns(4)
        c1.metric('Tiendas', f'{df['store_nbr'].nunique():,}'.replace(',', '.'))
        c2.metric('Familias producto', f'{df['family'].nunique():,}'.replace(',', '.'))
        c3.metric('Estados', f'{df['state'].nunique():,}'.replace(',', '.'))
        n_months = df[['year', 'month']].drop_duplicates().shape[0]
        c4.metric('Meses con dtaos', f'{n_months:,}'.replace(',', '.'))

        st.divider()
        izda, dcha = st.columns([1.2, 0.8])

        # Análisis en términos medios. 
        with izda: 
            # Ranking de productos más vendidos (top 10). 
            st.markdown('Top 10 productos más vendidos')
            prod_ventas = df.groupby('family', as_index=False)['sales'].sum().sort_values('sales', ascending=False).head(10)
            fig = px.bar(prod_ventas, x='sales', y='family', orientation='h')
            fig.update_layout(height=420, xaxis_title="Ventas (suma)", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
        with dcha: 
            # Distribución de las ventas por tiendas. 
            st.markdown('Distribución de ventas por tienda')
            ventas_tienda = df.groupby('store_nbr', as_index=False)['sales'].sum()
            fig2 = px.box(ventas_tienda, y='sales', points='outliers')
            fig2.update_layout(height=420, yaxis_title="Ventas por tienda (suma)")
            st.plotly_chart(fig2, use_container_width=True)
        
        # Ranking de tiendas con ventas en productos de promoción (top 10). 
        st.markdown('Top 10 tiendas con ventas en promoción')
        promo_tiendas = df[df['onpromotion'] > 0].groupby('store_nbr', as_index=False)['sales'].sum().sort_values('sales', ascending=False).head(10)
        fig3 = px.bar(promo_tiendas, x='store_nbr', y='sales')
        fig3.update_layout(height=380, xaxis_title="Tienda", yaxis_title="Ventas en promoción (suma)")
        st.plotly_chart(fig3, use_container_width=True)

        st.divider()

        # Análisis de la estacionalidad de ventas. 
        st.markdown('Estacionalidad')
        a, b, c, = st.columns(3)
        with a: 
            # Días de la semana con más media de ventas. 
            st.markdown('Ventas promedio por día de la semana')
            dia_sem = df.groupby('day_of_week', as_index=False)['sales'].mean().sort_values('sales', ascending=True)
            fig4 = px.bar(dia_sem, x="day_of_week", y="sales")
            fig4.update_layout(height=320, xaxis_title="", yaxis_title="Ventas promedio")
            st.plotly_chart(fig4, use_container_width=True)

        with b: 
            # Volumen de ventas medio por semana del año. 
            st.markdown('Ventas por semana')
            sem_avg = df.groupby('week', as_index=False)['sales'].mean().sort_values('week')
            fig5 = px.line(sem_avg, x='week', y='sales')
            fig5.update_layout(height=320, xaxis_title="Semana", yaxis_title="Ventas promedio")
            st.plotly_chart(fig5, use_container_width=True)

        with c: 
            # Volumen de ventas medio por mes. 
            st.markdown('Ventas promedio por mes')
            month_avg = df.groupby('month', as_index=False)['sales'].mean().sort_values('month')
            month_avg['month_name'] = month_avg['month'].apply(month_name)
            fig6 = px.line(month_avg, x="month_name", y="sales", markers=True)
            fig6.update_layout(height=320, xaxis_title="", yaxis_title="Ventas promedio")
            st.plotly_chart(fig6, use_container_width=True)

    # Rellenamos la pestaña 2. 
    with tab2: 
        st.subheader('Información por tienda')
        # Escogemos la tienda que vamos a añalizar con un desplegable en pantalla. 
        tiendas = sorted(df['store_nbr'].dropna().unique().tolist())
        tienda_selec = st.selectbox('Selecciona store_nbr', options=tiendas)
        df_t = df[df['store_nbr'] == tienda_selec].copy() 

        c1, c2, c3 = st.columns([1.2, 0.9, 0.9])

        # Número total de ventas por año. 
        with c1: 
            st.markdown('Ventas totales por año')
            ventas_year = df_t.groupby('year', as_index=False)['sales'].sum().sort_values('year')
            fig = px.bar(ventas_year, x="year", y="sales")
            fig.update_layout(height=380, xaxis_title="Año", yaxis_title="Ventas (suma)")
            st.plotly_chart(fig, use_container_width=True)

        # Número total de productos vendidos. 
        with c2: 
            st.markdown("Productos totales vendidos")
            st.metric("Ventas (suma)", f"{df_t['sales'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            st.metric("Transacciones (suma)", f"{df_t['transactions'].sum():,.0f}".replace(",", "."))

        # Número total de productos vendidos en promoción. 
        with c3: 
            st.markdown('Productos totales vendidos en promoción')
            promo_ventas = df_t.loc[df_t["onpromotion"] > 0, "sales"].sum()
            total_ventas = df_t["sales"].sum()
            ratio = promo_ventas / total_ventas if total_ventas > 0 else 0.0
            st.metric("Ventas en promoción", f"{promo_ventas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            st.metric("% ventas en promoción", f"{ratio*100:,.1f}%".replace(",", "X").replace(".", ",").replace("X", "."))

    # Rellenamos la pestaña 3. 
    with tab3: 
        st.subheader('Información por estado')
        # Escogemos el estado que vamos a añalizar con un desplegable en pantalla. 
        estado_selec = st.selectbox('Selecciona estado', options=sorted(df['state'].unique()))
        df_estado = df[df['state'] == estado_selec].copy()

        izda, dcha = st.columns([1.1, 0.9])
        with izda: 
            # Número total de transacciones por año. 
            st.markdown('Transacciones totales por año')
            t_year = df_estado.groupby('year', as_index=False)['transactions'].sum().sort_values('year')
            fig = px.line(t_year, x="year", y="transactions", markers=True)
            fig.update_layout(height=380, xaxis_title="Año", yaxis_title="Transacciones (suma)")
            st.plotly_chart(fig, use_container_width=True)

        with dcha: 
            # Ranking de tiendas con más ventas (top 10). 
            st.markdown(f'Top 10 tiendas por ventas en {estado_selec}')
            top_ventas = df_estado.groupby('store_nbr', as_index=False)['sales'].sum().sort_values('sales', ascending=False).head(10)
            fig2 = px.bar(top_ventas, x="sales", y="store_nbr", orientation="h")
            fig2.update_layout(height=380, xaxis_title="Ventas (suma)", yaxis_title="Tienda")
            st.plotly_chart(fig2, use_container_width=True)

        # Producto más vendido. 
        st.markdown(f'Familia de producto más vendida en el estado {estado_selec}')
        top_prod = df_estado.groupby('family', as_index=False)['sales'].sum().sort_values('sales', ascending=False).head(1)
        st.success(f'En {estado_selec}, la familia más vendida es {top_prod.iloc[0]['family']} con vemtas {top_prod.iloc[0]['sales']:,.2f}. '.replace(",", "X").replace(".", ",").replace("X", "."))

    # Rellenamos la página 4. 
    with tab4: 
        st.markdown('Insights adicionales. ')

        c1, c2 = st.columns(2)
        with c1: 
            # Analizamos si las promociones realmente aumentan las ventas promedio. 
            st.markdown('Lift de promoción por mes. ')
            tmp = df.copy()
            tmp['promo_flag'] = np.where(tmp["onpromotion"] > 0, "Promo", "No promo")
            # Calculamos el impacto de las promociones. 
            lift = tmp.groupby(['month', 'promo_flag'], as_index=False)['sales'].mean().sort_values('month')
            lift['month_name'] = lift['month'].apply(month_name)
            # Comparamos ventas con y sin promoción a lo largo del año. 
            fig = px.line(lift, x="month_name", y="sales", color="promo_flag", markers=True)
            fig.update_layout(height=380, xaxis_title="", yaxis_title="Ventas promedio")
            st.plotly_chart(fig, use_container_width=True)

        with c2: 
            # Analizamos las ventas en los días fetivos y no festivos. 
            st.markdown('Ventas promedio en festivos VS no festivos')
            tmp = df.copy()
            ht = tmp['holiday_type'].astype(str).str.strip().str.lower()
            tmp['event_flag'] = np.where((ht == 'nan') | (ht == ''), 'Sin evento', 'Con evento')
            hol = tmp.groupby('event_flag', as_index=False)['sales'].mean()
            fig2 = px.bar(hol, x="event_flag", y="sales")
            fig2.update_layout(height=380, xaxis_title="", yaxis_title="Ventas promedio")
            st.plotly_chart(fig2, use_container_width=True)

        # Analizamos la relación entra las ventas y el petroleo con un scatter plot. 
        st.markdown('Ventas VS dcoilwtico')
        scatter = df[['dcoilwtico', 'sales']].copy()
        scatter['dcoilwtico'] = pd.to_numeric(scatter['dcoilwtico'], errors='coerce')
        scatter = scatter.dropna()
        fig3 = px.scatter(scatter, x="dcoilwtico", y="sales", trendline="ols")
        fig3.update_layout(height=420, xaxis_title="dcoilwtico", yaxis_title="Ventas")
        st.plotly_chart(fig3, use_container_width=True)




if __name__ == '__main__': 

    # Configuramos la página. 
    st.set_page_config(page_title='Dashboard de Ventas', layout='wide', initial_sidebar_state='expanded')

    # Cargamos los datos. 
    df = load_dataset(PATH_1, PATH_2)
    pag = render_sidebar()
    if pag == 'Dashboard': 
        set_dashboard_section(df)
    elif pag == 'Datos':
        set_data_section(df)
    elif pag == 'Acerca de':
        set_abuout_section()

    st.divider()
    st.caption('Proyecto desarrollado con Streamlit')