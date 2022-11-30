import pandas as pd
import numpy as np
import streamlit as st
import folium
import seaborn as sns
import matplotlib.pyplot as plt
from streamlit_folium import st_folium
import geopandas as gpd
import plotly.graph_objects as go

APP_TITLE = 'Visualisasi Data'

def display_map(df_jkt):
    map = folium.Map(location=[-6.2, 106.90], zoom_start=11, scrollWhileZoom=False, tiles='cartodbdark_matter')

    choropleth = folium.Choropleth(
        geo_data='demografi_jakarta_utara.geojson',
        data=df_jkt,
        columns=('nama_desa', 'JUMLAH_PEN'),
        key_on='feature.properties.nama_desa',
        fill_color='YlOrRd',
        line_opacity=0.8,
        legend_name='nama_desa',
        highlight=True
    )
    choropleth.geojson.add_to(map)
    df_indexed = df_jkt.set_index('nama_desa')
    for feature in choropleth.geojson.data['features']:
        state_name = feature['properties']['nama_desa']
        feature['properties']['JUMLAH_PEN'] = 'Population: ' + '{:,}'.format(int(df_indexed.loc[state_name, 'JUMLAH_PEN'])) if state_name in list(df_indexed.index) else ''



    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(['nama_desa', 'JUMLAH_PEN'], labels=False)
    )
    st_map=st_folium(map, width=700, height=450)
    return st_map

def display_filter_desa(join_right_df):
    desa_list = ['ALL']+list(join_right_df['nama_desa'].unique())
    desa_list.sort()
    desa = st.sidebar.selectbox('Nama Desa', desa_list)
    return desa

def ratio(df_desa):
    agg_tips=df_desa[['nama_desa', 'PRIA', 'WANITA', 'JUMLAH_PEN']]
    agg_tips=agg_tips.sort_values('JUMLAH_PEN')
    agg_tips=agg_tips[['nama_desa', 'PRIA', 'WANITA']]
    agg_tips=agg_tips.set_index('nama_desa')

    fig, ax = plt.subplots()

    # Initialize the bottom at zero for the first set of bars.
    colors = ['#24b1d1', '#ae24d1']
    bottom = np.zeros(len(agg_tips))

    # Plot each layer of the bar, adding each bar to the "bottom" so
    # the next bar starts higher.
    for i, col in enumerate(agg_tips.columns):
        ax.bar(agg_tips.index, agg_tips[col], bottom=bottom, width=0.35, label=col
            ,color=colors[i])
        bottom += np.array(agg_tips[col])
    
    # # Sum up the rows of our data to get the total value of each bar.
    # totals = agg_tips.sum(axis=1)
    # # Set an offset that is used to bump the label up a bit above the bar.
    # y_offset = 4
    # # Add labels to each bar.
    # for i, total in enumerate(totals):
    #     ax.text(totals.index[i], total + y_offset, round(total), ha='center', weight='bold')
    
    ax.set_xlabel('Nama Desa')
    ax.set_ylabel('Jumlah Populasi')
    ax.set_xticks(df_desa['nama_desa'])
    ax.set_xticklabels(df_desa['nama_desa'], rotation=80)
    ax.set_title('Rasio Pria dan Wanita')
    ax.legend()

    st.pyplot(fig)

def ratio_Pria_dan_Wanita(df, desa):
    df_filter = df[(df['nama_desa'] == desa)]
    df_filter = df_filter[['PRIA', 'WANITA']].drop_duplicates().T
    df_filter = df_filter.reset_index().rename(columns={'index': 'gender'})
    df_filter = df_filter.rename(columns={ df_filter.columns[1]: "jumlah" })
    title= str("Rasio Pria dan Wanita di "+desa)


    pie_colors = ['rgba(38, 24, 74, 0.8)', 'rgba(71, 58, 131, 0.8)',  
          'rgba(122, 120, 168, 0.8)', 'rgba(164, 163, 204, 0.85)',
          'rgba(190, 192, 213, 1)', 'RGB(186,85,211)', 'RGB(224,102,255)',
          'RGB(209,95,238)', 'RGB(180,82,205)', 'RGB(122,55,139)']
    
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=df_filter['gender'].to_list(),
        values=df_filter.jumlah.to_list(),
        name='gender',
        hoverinfo="label+percent+value",
        marker_colors=pie_colors
    ))

    fig.update_layout(
        title=title,
        height= 600,
        width= 700,
        paper_bgcolor='rgb(248, 248, 255)',
        plot_bgcolor='rgb(248, 248, 255)'
    )
    st.plotly_chart(fig)

def bar_chart_filter(df, desa):
    df_filter=df[(df['nama_desa'] == desa)]
    df_sort=df_filter.groupby('nama_kategori')['gid'].count().sort_values(ascending=True)
    df_sort_to_frame=df_sort.to_frame()
    data=df_sort_to_frame.reset_index()
    
    kategori = data['nama_kategori']
    jumlah_data = data['gid']

    x = np.arange(len(kategori)) # the label locations
    width = 0.5 # the width of the bars

    fig, ax = plt.subplots()

    #bar_labels = ['red', 'yellow', 'green', 'blue', 'navy', 'black', 'purple', 'orange', 'brown', 'grey', 'pink', 'gold']
    bar_colors = ['red', 'yellow', 'green', 'blue', 'navy', 'black', 'purple', 'orange', 'brown', 'grey', 'pink', 'gold']
    ax.set_xlabel('Nama Kategori')
    ax.set_ylabel('Jumlah Kategori')
    ax.set_title('Visualisasi Data POI')
    ax.set_xticks(x)
    ax.set_xticklabels(kategori, rotation=80)

    pps = ax.bar(x - width/2, jumlah_data, width, color=bar_colors)
    for p in pps:
        height = p.get_height()
        ax.annotate('{}'.format(height),
                    xy=(p.get_x() + p.get_width() / 2, height),
                    xytext=(0, 3), # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

    st.pyplot(fig)




def bar_chart(data):
    kategori = data['nama_kategori']
    jumlah_data = data['gid']

    x = np.arange(len(kategori)) # the label locations
    width = 0.70 # the width of the bars

    fig, ax = plt.subplots()

    bar_colors = ['red', 'yellow', 'green', 'blue', 'navy', 'black', 'purple', 'orange', 'brown', 'grey', 'pink', 'gold']
    ax.set_xlabel('Nama Kategori')
    ax.set_ylabel('Jumlah Kategori')
    ax.set_title('Visualisasi Data POI')
    ax.set_xticks(x)
    ax.set_xticklabels(kategori, rotation=80)

    pps = ax.bar(x - width/2, jumlah_data, width, color=bar_colors)
    for p in pps:
        height = p.get_height()
        ax.annotate('{}'.format(height),
        xy=(p.get_x() + p.get_width() / 2, height),
        xytext=(0, 3), # 3 points vertical offset
        textcoords="offset points",
        ha='center', va='bottom')

    st.pyplot(fig)

#func Rasio Agama

def distribusi_agama_all(df_desa):
    agg_tips=df_desa[['nama_desa','ISLAM','BUDHA','KATHOLIK', 'HINDU', 'KONGHUCU', 'KRISTEN', 'JUMLAH_PEN']]
    agg_tips=agg_tips.sort_values('JUMLAH_PEN')
    agg_tips=agg_tips[['nama_desa','ISLAM','BUDHA','KATHOLIK', 'HINDU', 'KONGHUCU', 'KRISTEN']]
    agg_tips=agg_tips.set_index('nama_desa')

    fig, ax = plt.subplots()

    # Initialize the bottom at zero for the first set of bars.
    colors = ['red', 'yellow', 'green', 'blue', 'navy', 'black']
    bottom = np.zeros(len(agg_tips))

    # Plot each layer of the bar, adding each bar to the "bottom" so
    # the next bar starts higher.
    for i, col in enumerate(agg_tips.columns):
        ax.bar(agg_tips.index, agg_tips[col], bottom=bottom, width=0.35, label=col
            ,color=colors[i])
        bottom += np.array(agg_tips[col])
    
    # # Sum up the rows of our data to get the total value of each bar.
    # totals = agg_tips.sum(axis=1)
    # # Set an offset that is used to bump the label up a bit above the bar.
    # y_offset = 4
    # # Add labels to each bar.
    # for i, total in enumerate(totals):
    #     ax.text(totals.index[i], total + y_offset, round(total), ha='center', weight='bold')
    
    ax.set_xlabel('Nama Desa')
    ax.set_ylabel('Jumlah Populasi')
    ax.set_xticks(df_desa['nama_desa'])
    ax.set_xticklabels(df_desa['nama_desa'], rotation=80)
    ax.set_title('Rasio Agama')
    ax.legend()
    st.pyplot(fig)

def distribusi_agama_tiap_desa(df, desa):
    df_filter = df[(df['nama_desa'] == desa)]
    df_filter = df_filter[['ISLAM','BUDHA','KATHOLIK', 'HINDU', 'KONGHUCU', 'KRISTEN']].drop_duplicates().T
    df_filter = df_filter.reset_index().rename(columns={'index': 'agama'})
    df_filter = df_filter.rename(columns={ df_filter.columns[1]: "jumlah" })
    title= str("Rasio Agama di "+desa)


    pie_colors = ['rgba(38, 24, 74, 0.8)', 'rgba(71, 58, 131, 0.8)',  
          'rgba(122, 120, 168, 0.8)', 'rgba(164, 163, 204, 0.85)',
          'rgba(190, 192, 213, 1)', 'RGB(186,85,211)', 'RGB(224,102,255)',
          'RGB(209,95,238)', 'RGB(180,82,205)', 'RGB(122,55,139)']
    
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=df_filter['agama'].to_list(),
        values=df_filter.jumlah.to_list(),
        name='agama',
        hoverinfo="label+percent",
        marker_colors=pie_colors,
    ))

    fig.update_layout(
        title=title,
        height= 600,
        width= 700,
        paper_bgcolor='rgb(248, 248, 255)',
        plot_bgcolor='rgb(248, 248, 255)',
    )
    st.plotly_chart(fig)

# Distribution Umur

def distribution_umur(df_desa):
    agg_tips=df_desa[['nama_desa','U0','U5', 'U10', 'U15', 'U20','U25','U30', 'U35', 'U40', 'U45', 'U50', 'U55', 'U60', 'U70', 'U75', 'JUMLAH_PEN']]
    agg_tips=agg_tips.sort_values('JUMLAH_PEN')
    agg_tips=agg_tips[['nama_desa','U0','U5', 'U10', 'U15', 'U20','U25','U30', 'U35', 'U40', 'U45', 'U50', 'U55', 'U60', 'U70', 'U75']]
    agg_tips=agg_tips.set_index('nama_desa')

    fig, ax = plt.subplots(figsize=(8,10))

    # Initialize the bottom at zero for the first set of bars.
    colors = ['red', 'yellow', 'green', 'blue', 'navy', 'black', 'purple', 'orange', 'brown', 'grey', 'pink', 'gold', 'dodgerblue', 'olive', 'darkcyan']
    bottom = np.zeros(len(agg_tips))

    # Plot each layer of the bar, adding each bar to the "bottom" so
    # the next bar starts higher.
    for i, col in enumerate(agg_tips.columns):
        ax.bar(agg_tips.index, agg_tips[col], bottom=bottom, width=0.35, label=col
            ,color=colors[i])
        bottom += np.array(agg_tips[col])
    
    # # Sum up the rows of our data to get the total value of each bar.
    # totals = agg_tips.sum(axis=1)
    # # Set an offset that is used to bump the label up a bit above the bar.
    # y_offset = 4
    # # Add labels to each bar.
    # for i, total in enumerate(totals):
    #     ax.text(totals.index[i], total + y_offset, round(total), ha='center', weight='bold')
    
    ax.set_xlabel('Nama Desa')
    ax.set_ylabel('Jumlah Populasi')
    ax.set_xticks(df_desa['nama_desa'])
    ax.set_xticklabels(df_desa['nama_desa'], rotation=80)
    ax.set_title('Rasio Umur')
    ax.legend()
    st.pyplot(fig)

def ratio_umur_tiap_desa(df, desa):
    df_filter = df[(df['nama_desa'] == desa)]
    df_filter = df_filter[['U0','U5', 'U10', 'U15', 'U20','U25','U30', 'U35', 'U40', 'U45', 'U50', 'U55', 'U60', 'U70', 'U75']].drop_duplicates().T
    df_filter = df_filter.reset_index().rename(columns={'index': 'umur'})
    df_filter = df_filter.rename(columns={ df_filter.columns[1]: "jumlah" })
    title= str("Rasio Agama di "+desa)


    pie_colors = ['rgba(38, 24, 74, 0.8)', 'rgba(71, 58, 131, 0.8)',  
          'rgba(122, 120, 168, 0.8)', 'rgba(164, 163, 204, 0.85)',
          'rgba(190, 192, 213, 1)', 'RGB(186,85,211)', 'RGB(224,102,255)',
          'RGB(209,95,238)', 'RGB(180,82,205)', 'RGB(122,55,139)']
    
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=df_filter['umur'].to_list(),
        values=df_filter.jumlah.to_list(),
        name='umur',
        hoverinfo="label+percent",
        marker_colors=pie_colors,
    ))

    fig.update_layout(
        title=title,
        height= 600,
        width= 700,
        paper_bgcolor='rgb(248, 248, 255)',
        plot_bgcolor='rgb(248, 248, 255)',
    )
    st.plotly_chart(fig)


def main():
    st.set_page_config(APP_TITLE)
    st.title(APP_TITLE)

    #load_data
    df_poi = pd.read_csv('poi.csv')
    df_desa= pd.read_csv('demografi_jakarta_utara.csv')

    df_jkt = gpd.read_file('demografi_jakarta_utara.geojson')
    geoPOI=gpd.read_file('poi.geojson')

    #Join
    geoPOI.crs = df_jkt.crs

    join_right_df = geoPOI.sjoin(df_jkt, how="right")

    # Display Visual and maps
    #maps
    display_map(df_jkt)


    # sidebar
    desa=display_filter_desa(join_right_df)


    #visualisasi
    
    if desa=='ALL':
        jumlah_kategori=df_poi.groupby('nama_kategori')['gid'].count().sort_values(ascending=True)
        data=jumlah_kategori.to_frame()
        data=data.reset_index()
        st.markdown('Visualisasi Jumlah Kategori POI.')
        bar_chart(data)
        st.markdown('Visualisasi Ratio Pria dan Wanita.')
        ratio(df_desa)
        st.markdown('Visualisasi Ratio Agama')
        distribusi_agama_all(df_desa)
        st.markdown('Visualisasi Umur')
        distribution_umur(df_desa)
    else:
        st.markdown('Visualisasi Jumlah Kategori POI.')
        bar_chart_filter(df=join_right_df, desa=desa)
        st.markdown('Visualisasi Ratio Pria dan Wanita.')
        ratio_Pria_dan_Wanita(df=join_right_df, desa=desa)
        st.markdown('Visualisasi Ratio Agama')
        distribusi_agama_tiap_desa(df=join_right_df, desa=desa)
        st.markdown('Visualisasi Ratio Umur')
        ratio_umur_tiap_desa(df=join_right_df, desa=desa)

if __name__ == "__main__":
    main()