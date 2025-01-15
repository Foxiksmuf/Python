import pyodbc
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# Połączenie z bazą danych
polaczenie = pyodbc.connect("""DRIVER={ODBC Driver 17 for SQL Server};
Server=****;
DATABASE=synop;
uid=****;
pwd=****""")

# Zapytanie SQL do pobrania danych
query = """
SELECT 
    DATENAME(MONTH, Data) AS NazwaM, 
    MONTH(Data) AS MiesiacNum,
    YEAR(Data) AS Rok,
    AVG(TemperaturaPunktuRosy) AS SredTemp
FROM dbo.depesze
WHERE TemperaturaPunktuRosy IS NOT NULL
GROUP BY DATENAME(MONTH, Data), MONTH(Data), YEAR(Data)
ORDER BY Rok, MiesiacNum;
"""

# Wykonanie zapytania i załadowanie danych do DataFrame
df = pd.read_sql(query, polaczenie)

# Zamknięcie połączenia z bazą danych
polaczenie.close()

# Kolory przypisane do przedziałów lat, od jasnego do ciemnego
color_mapping = {
    1999: 'rgb(144, 238, 144)',  # Jasny zielony
    2000: 'rgb(124, 208, 124)',
    2001: 'rgb(104, 178, 104)',
    2002: 'rgb(84, 148, 84)',
    2003: 'rgb(64, 118, 64)',  # Ciemny zielony
    2004: 'rgb(255, 255, 153)',  # Jasny żółty
    2005: 'rgb(255, 255, 102)',
    2006: 'rgb(255, 255, 51)',
    2007: 'rgb(255, 255, 0)',
    2008: 'rgb(204, 204, 0)',  # Ciemny żółty
    2009: 'rgb(173, 216, 230)',  # Jasny niebieski
    2010: 'rgb(135, 206, 250)',
    2011: 'rgb(100, 149, 237)',
    2012: 'rgb(65, 105, 225)',
    2013: 'rgb(0, 0, 255)',  # Ciemny niebieski
    2014: 'rgb(216, 191, 216)',  # Jasny fioletowy
    2015: 'rgb(186, 85, 211)',
    2016: 'rgb(138, 43, 226)',
    2017: 'rgb(75, 0, 130)',
    2018: 'rgb(148, 0, 211)',  # Ciemny fioletowy
    2019: 'rgb(255, 182, 193)',  # Jasny czerwony
    2020: 'rgb(255, 105, 180)',
    2021: 'rgb(255, 20, 147)',
    2022: 'rgb(219, 50, 55)',
    2023: 'rgb(255, 0, 0)',  # Ciemny czerwony
    2024: 'rgb(200, 0, 0)',
    2025: 'rgb(139, 0, 0)'  # Bardzo ciemny czerwony
}

# Zaokrąglamy wartości do 1 miejsca po przecinku
df['SredTemp'] = df['SredTemp'].round(1)

# Tworzenie wykresu interaktywnego
fig = make_subplots(rows=1, cols=1)

# Iterujemy po latach, aby dodać wykres słupkowy dla każdego roku
for i, rok in enumerate(df['Rok'].unique()):
    df_rok = df[df['Rok'] == rok]
    color = color_mapping.get(rok, 'rgb(0, 0, 0)')  # Domyślny kolor czarny, jeśli rok nie ma przypisanego koloru
    fig.add_trace(
        go.Bar(
            x=df_rok['NazwaM'],
            y=df_rok['SredTemp'],
            name=str(rok),
            marker=dict(color=color),  # Użycie przypisanego koloru
            hovertemplate="<b>%{x}</b><br>Średnia temperatura: %{y}°C",
            text=[f"{temp}°C ({rok})" for temp in df_rok['SredTemp']],  # Dodanie roku do tekstu na słupkach
            textposition='outside',  # Ustawienie pozycji tekstu na zewnątrz słupków
            showlegend=True  # Domyślnie pokazujemy legendę
        )
    )

# Dodajemy tło z gradientem
fig.update_layout(
    plot_bgcolor='rgba(240, 240, 240, 0.9)',
    paper_bgcolor='rgba(255, 255, 255, 0.7)',
    title={
        'text': "Średnia temperatura w każdym miesiącu",
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'size': 24, 'family': 'Arial, sans-serif', 'color': 'rgb(30, 30, 30)'}
    },
    xaxis=dict(
        title='Miesiąc',
        titlefont=dict(size=18, family='Arial, sans-serif', color='rgb(80, 80, 80)'),
        tickfont=dict(size=14, family='Arial, sans-serif', color='rgb(80, 80, 80)'),
        showgrid=True,
        gridcolor='rgba(200, 200, 200, 0.5)',
        zeroline=True,
        zerolinecolor='rgba(200, 200, 200, 0.5)',
    ),
    yaxis=dict(
        title='Średnia temperatura (°C)',
        titlefont=dict(size=18, family='Arial, sans-serif', color='rgb(80, 80, 80)'),
        tickfont=dict(size=14, family='Arial, sans-serif', color='rgb(80, 80, 80)'),
        showgrid=True,
        gridcolor='rgba(200, 200, 200, 0.5)',
        zeroline=True,
        zerolinecolor='rgba(200, 200, 200, 0.5)',
    ),
    showlegend=True,
    updatemenus=[dict(
        type="dropdown",
        x=0.1,
        y=1.15,
        showactive=True,
        buttons=[dict(
            label="Wszystkie lata",
            method="update",
            args=[{"visible": [True] * len(df['Rok'].unique())},
                  {"title": "Średnia temperatura w każdym miesiącu"}]
        )] + [
            dict(
                label=f"{rok}",
                method="update",
                args=[{"visible": [r == rok for r in df['Rok'].unique()]},
                      {"title": f"Średnia temperatura w {rok} roku"}]
            )
            for rok in df['Rok'].unique()
        ]
    )],
    margin=dict(t=50, b=50, l=50, r=50),
    dragmode='zoom',  # Włączenie trybu zoomowania za pomocą myszy
)

# Wyświetlenie wykresu
fig.show()
