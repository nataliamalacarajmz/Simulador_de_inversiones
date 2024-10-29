import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# Título y descripción
st.markdown("<h1 style='text-align: center; color: #003366;'>Simulador de Inversión Allianz</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #336699;'>Selecciona uno, dos o tres ETFs para comparar su rendimiento y simular la inversión:</h3>", unsafe_allow_html=True)

# Instrucciones para el usuario
st.info("1. Selecciona los ETFs que quieres analizar.\n"
        "2. Define el monto inicial de inversión.\n"
        "3. Selecciona el rango de fechas o periodo de tiempo.\n"
        "4. Haz clic en 'Simular Inversión' para ver los resultados.")

# Lista de ETFs disponibles con sus símbolos de Yahoo Finance
etfs = {
    "AZ China": "ASHR",
    "AZ MSCI TAIWAN INDEX FD": "EWT",
    "AZ RUSSELL 2000": "IWM",
    "AZ Brasil": "EWZ",
    "AZ MSCI UNITED KINGDOM": "EWU",
    "AZ DJ US FINANCIAL SECT": "IYF",
    "AZ BRIC": "BKF",
    "AZ MSCI SOUTH KOREA IND": "EWY",
    "AZ BARCLAYS AGGREGATE": "AGG",
    "AZ Mercados Emergentes": "EEM",
    "AZ MSCI EMU": "EZU",
    "AZ FTSE/XINHUA CHINA 25": "FXI",
    "AZ Oro": "GLD",
    "AZ LATIXX MEX CETETRAC": "MXX",
    "AZ QQQ NASDAQ 100": "QQQ",
    "AZ MSCI ASIA EX-JAPAN": "AAXJ",
    "AZ SPDR S&P 500 ETF TRUST": "SPY",
    "AZ DJ US OIL & GAS EXPL": "IEO"
}

# Descripciones de los ETFs
descripciones_etfs = {
    "AZ China": "ASHR sigue el índice CSI 300 de acciones de grandes capitalizaciones en China.",
    "AZ MSCI TAIWAN INDEX FD": "EWT sigue el índice MSCI Taiwan, que representa a empresas de gran capitalización de Taiwán.",
    "AZ RUSSELL 2000": "IWM sigue el índice Russell 2000, que representa las pequeñas capitalizaciones del mercado estadounidense.",
    "AZ Brasil": "EWZ sigue el índice MSCI Brazil, que cubre a grandes empresas del mercado brasileño.",
    "AZ DJ US FINANCIAL SECT": "IYF sigue el índice DJ US Financials, que incluye acciones de grandes empresas financieras estadounidenses.",
    "AZ SPDR S&P 500 ETF TRUST": "SPY sigue el índice S&P 500, que es uno de los principales indicadores del mercado bursátil de EE.UU.",
    # Puedes agregar más descripciones aquí
}

# Selector de ETF
etf_nombres = list(etfs.keys())
seleccion_etfs = st.multiselect('Selecciona uno, dos o tres ETFs para comparar', etf_nombres, default=[etf_nombres[0]])

# Mostrar descripciones de los ETFs seleccionados
for etf in seleccion_etfs:
    st.write(f"**{etf}:** {descripciones_etfs.get(etf, 'Descripción no disponible.')}")
    st.write("---")  # Línea divisoria para mayor claridad

# Parámetros de entrada
monto_inicial = st.number_input("Introduce el monto inicial de inversión ($)", min_value=100.0, value=1000.0)

# Opción para seleccionar un rango de fechas personalizado o periodo predefinido
tipo_fecha = st.radio("¿Quieres seleccionar un rango de fechas o un periodo de tiempo predefinido?", ("Rango de fechas", "Periodo predefinido"))

if tipo_fecha == "Rango de fechas":
    fecha_inicio = st.date_input("Fecha de inicio", value=datetime(2020, 1, 1))
    fecha_fin = st.date_input("Fecha de fin", value=datetime.today())
else:
    periodo = st.selectbox('Selecciona el periodo de tiempo', ['1mo', '3mo', '6mo', '1y', 'ytd', '5y', '10y'])

# Botón de simulación de inversión
if st.button("Simular Inversión 🚀"):
    # Descargar datos históricos de los ETFs seleccionados
    datos_etfs = {}
    for etf in seleccion_etfs:
        simbolo = etfs[etf]
        try:
            if tipo_fecha == "Rango de fechas":
                datos = yf.download(simbolo, start=fecha_inicio, end=fecha_fin)['Adj Close']
            else:
                datos = yf.download(simbolo, period=periodo)['Adj Close']

            if not datos.empty:
                datos_etfs[etf] = datos
        except Exception as e:
            st.error(f"Error al descargar datos para {etf}: {e}")

    # Verificar si se descargaron datos correctamente
    if datos_etfs:
        st.success("Datos descargados correctamente.")

        # Crear un DataFrame combinando las series de tiempo por columna, alineadas por fecha
        df_combined = pd.concat(datos_etfs.values(), axis=1, join='inner')  # Combina solo las fechas comunes
        df_combined.columns = datos_etfs.keys()  # Asigna los nombres de los ETFs como columnas

        # Asegurarse de que el índice del DataFrame tenga un nombre de fecha
        df_combined.index.name = "Fecha"

        # **CORRECCIÓN: Crear rendimiento_acumulado_df**
        rendimiento_acumulado_df = df_combined / df_combined.iloc[0] * monto_inicial

        # Comparación de rendimiento acumulado
        st.write("### Evolución del rendimiento acumulado")
        fig_rendimiento = px.line(
            rendimiento_acumulado_df,
            labels={'value': 'Rendimiento Acumulado (USD)', 'variable': 'ETF'},
            title="Evolución del Rendimiento Acumulado"
        )
        fig_rendimiento.update_layout(title_font_size=20, xaxis_title="Fecha", yaxis_title="Valor (USD)")
        st.plotly_chart(fig_rendimiento)

        # Descargar datos del índice S&P 500 (SPY)
        if tipo_fecha == "Rango de fechas":
            spy_data = yf.download("SPY", start=fecha_inicio, end=fecha_fin)['Adj Close']
        else:
            spy_data = yf.download("SPY", period=periodo)['Adj Close']
        
        rendimiento_spy = spy_data / spy_data.iloc[0] * monto_inicial
        rendimiento_acumulado_df['SPY'] = rendimiento_spy

        # Gráfica de comparación contra el S&P 500
        st.write("### Comparación contra el índice S&P 500 (SPY)")
        fig_comparacion_spy = px.line(
            rendimiento_acumulado_df,
            labels={'value': 'Rendimiento Acumulado (USD)', 'variable': 'Instrumento'},
            title="Comparación del Rendimiento contra el S&P 500"
        )
        fig_comparacion_spy.update_layout(title_font_size=20, xaxis_title="Fecha", yaxis_title="Valor (USD)")
        st.plotly_chart(fig_comparacion_spy)

        # Simulación de inversión
        st.write("### Resultados de la simulación de inversión:")

        # Definir una tasa libre de riesgo
        tasa_libre_riesgo = 2.0  # Tasa libre de riesgo en %

        for etf in seleccion_etfs:
            datos = datos_etfs[etf]
            rendimiento_acumulado = (datos / datos.iloc[0]) * monto_inicial  # Rendimiento relativo al monto inicial
            valor_final = rendimiento_acumulado.iloc[-1]
            valor_final = float(valor_final)  # Convertimos el valor final a número flotante

            # Cálculo de rendimiento y riesgo (volatilidad)
            rendimientos_diarios = datos.pct_change().dropna()

            # Convertir el rendimiento diario promedio y la volatilidad a flotante
            rendimiento_promedio_diario = float(rendimientos_diarios.mean())  # Rendimiento promedio diario en decimal

            # Cálculo del rendimiento anualizado
            rendimiento_anualizado = (1 + rendimiento_promedio_diario)**252 - 1  # 252 días de mercado por año
            rendimiento_anualizado *= 100  # Convertir a porcentaje

            volatilidad_anualizada = float(rendimientos_diarios.std() * np.sqrt(252) * 100)  # Volatilidad anualizada

            # Cálculo del Sharpe Ratio
            rendimiento_exceso = rendimiento_anualizado - tasa_libre_riesgo  # Rendimiento ajustado por la tasa libre de riesgo
            if volatilidad_anualizada != 0:
                sharpe_ratio = rendimiento_exceso / volatilidad_anualizada
            else:
                sharpe_ratio = 0

            # Mostrar los resultados con el periodo en la leyenda
            st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 10px; border-radius: 10px;">
            <h4 style="color: #003366;">Resultados para <strong>{etf}</strong> (Plazo: {periodo if tipo_fecha == "Periodo predefinido" else "Rango de fechas"})</h4>
            <p>Si hubieras invertido <strong>${monto_inicial:,.2f}</strong> en <strong>{etf}</strong> durante el periodo seleccionado, ahora tendrías <strong style="color: #2E8B57;">${valor_final:,.2f}</strong>.</p>
            <ul>
                <li><strong>Rendimiento anualizado:</strong> {rendimiento_anualizado:.2f}%</li>
                <li><strong>Volatilidad anualizada:</strong> {volatilidad_anualizada:.2f}%</li>
                <li><strong>Sharpe Ratio:</strong> {sharpe_ratio:.2f}</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)

        # Descarga del informe en PDF (solo placeholder, necesitarías integrarlo con una librería como FPDF)
        st.download_button("Descargar informe en PDF", data="Aquí va tu informe PDF", file_name="informe_inversion.pdf")
    else:
        st.error("No se pudieron obtener datos para los ETFs seleccionados.")
else:
    st.warning("Selecciona al menos un ETF para comparar.")







