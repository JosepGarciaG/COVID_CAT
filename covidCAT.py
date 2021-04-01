from bs4 import BeautifulSoup
import requests
import pandas as pd
import matplotlib.pyplot as plt

html = requests.get('https://dadescovid.cat/diari')
soup = BeautifulSoup(html.text, 'html.parser')

table = soup.find('table', class_='table center')
body = soup.find('tbody')


# Extracció dels títols i dades de la web (web scraping)
def web_scraping_covid(table):
    """
    Crear una llista dels títols de la web
    Crear varies llistes amb les dades
    Obtenim un dataframe amb els títols i les dades

    Args:
        table: (:obj: `html`) : html
    Returns:
        df_covid (:obj: `df`) : dataframe
    """
    titles = []
    for i in table.find_all('th'):
        title = i.text.strip()
        titles.append(title)

    # Creem un df i posem nom a les columnes
    df_covid = pd.DataFrame(columns=titles)

    for idx, row in enumerate(body.find_all('tr')):  # genera una llista per cada fila
        fila = []
        for element in row.find_all('td'):  # genera els elements de cada fila
            elem = element.text.strip()
            fila.append(elem)
        df_covid.loc[idx] = fila  # afegim files al dataframe

    return df_covid


df_covid = web_scraping_covid(table)


def calc_df_covid(df_covid):
    """
    Fer les modificacions necessàries per netejar i deixar
    operatiu el dataframe definitiu.
    Creació d'un fitxer csv amb les dades.

    Args:
        df_covid: (:obj: `df`) : dataframe
    Returns:
        df_cl (:obj: `df`) : dataframe
    """
    # Ordenem d'antic a més nou perquè faci els càlculs correctes
    df_covid=df_covid.loc[::-1].reset_index(drop=True)
    
    # Eliminem asterisc a Data, convertim la resta de variables a enters (eliminant el punt),
    # excepte % PCR/TA Positives que la passem a real (substituim coma per punt).
    df_covid['Data'] = df_covid['Data'].str.replace('\*', '')
    df_covid['Casos confirmats per PCR/TA'] = df_covid['Casos confirmats per PCR/TA'].str.replace('\.', '').astype(int)
    df_covid['PCR Fetes'] = df_covid['PCR Fetes'].str.replace('\.', '').astype(int)
    df_covid['TA Fets'] = df_covid['TA Fets'].str.replace('\.', '').astype(int)
    df_covid['% PCR/TA Positives'] = df_covid['% PCR/TA Positives'].str.replace('\,', '.').astype(float)
    df_covid['Vacunats 1a dosi'] = df_covid['Vacunats 1a dosi'].str.replace('\.', '').astype(int)
    df_covid['Vacunats 2a dosi'] = df_covid['Vacunats 2a dosi'].str.replace('\.', '').astype(int)
    df_covid['Ingressats'] = df_covid['Ingressats'].str.replace('\.', '').astype(int)
    df_covid['Defuncions'] = df_covid['Defuncions'].str.replace('\.', '').astype(int)

    for index, row in df_covid.iterrows():
        # Calculem la diferència
        df_covid['Canvi_diari'] = df_covid['Casos confirmats per PCR/TA'].diff()  # diferència diària
        df_covid['Canvi_7D'] = df_covid['Casos confirmats per PCR/TA'].diff(7)  # diferència 7 dies
        # Calculem el % d'increment o disminució
        df_covid['Canvi_%'] = df_covid['Casos confirmats per PCR/TA'].pct_change()
        df_covid['Canvi_7D_%'] = df_covid['Casos confirmats per PCR/TA'].pct_change(7)
        # Mitjana aritmètica mòbil
        df_covid['MA_7'] = df_covid['Casos confirmats per PCR/TA'].rolling(window=7).mean()  # Dels 7 últims dies
        df_covid['MA_30'] = df_covid['Casos confirmats per PCR/TA'].rolling(window=30).mean()  # Dels 30

    # Substituïm N/A per 0 (així podem canviar el type)
    df_covid = df_covid.fillna(0)
    # Canviem el type
    df_covid['Canvi_diari'] = df_covid['Canvi_diari'].astype('int64')
    df_covid['Canvi_7D'] = df_covid['Canvi_7D'].astype('int64')
    df_covid['Canvi_%'] = df_covid['Canvi_%'].astype('float64')
    df_covid['Canvi_7D_%'] = df_covid['Canvi_7D_%'].astype('float64')
    df_covid['MA_7'] = df_covid['MA_7'].astype('float64')
    df_covid['MA_30'] = df_covid['MA_30'].astype('float64')
    # Arrodonim a dos decimals
    df_covid['MA_7'] = round(df_covid['MA_7'].astype('float64'), 2)
    df_covid['MA_30'] = round(df_covid['MA_30'].astype('float64'), 2)
    df_covid['Canvi_%'] = round(df_covid['Canvi_%'].astype('float64'), 2)
    df_covid['Canvi_7D_%'] = round(df_covid['Canvi_7D_%'].astype('float64'), 2)
    # Creació fitxer csv
    df_covid.to_csv("evolucio_covid_a_catalunya.csv", index=False)

    return df_covid


df_covid = calc_df_covid(df_covid)


# fem un gràfic de barres
def plot_covid_casos(df_covid):
    """
    Gràfic de barres en funció de X y Y que triem d'un dataframe.
    Guardem el resultat en png.

    Args:
        df_covid (:obj:`dataframe`): Dades del COVID a Catalunya
    """
    df_covid['MA_30'].plot(kind="bar", color=['blue'])  # Mitja últims 30 dies
    df_covid['MA_7'].plot(kind="bar", color=['green'])  # Mitja últims 7 dies
    df_covid['Casos confirmats per PCR/TA'].plot(kind="bar", color=['red'])  # Casos diaris
    plt.rcParams["figure.figsize"] = [40, 24]
    plt.xlabel('Dies')
    plt.ylabel('Nombre de casos confirmats per PCR/TA')
    plt.title('Evolució COVID a Catalunya')
    plt.legend(loc='upper left')
    plt.savefig('Evolucio_COVID_CAT_PCR.png')
    plt.show()


plot_covid_casos(df_covid)
