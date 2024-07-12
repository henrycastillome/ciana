from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
from folium.plugins import MarkerCluster
import folium
from io import BytesIO
import plotly.express as px
import pandas as pd
import pycountry
import plotly.express as px

app = Flask(__name__)
CORS(app) 

@app.route('/upload', methods=['POST'])
def upload_file():
    print(request.form)
    file=request.files['file']
    sheet_name=request.form['sheet_name']

    print(f"Sheet name: {sheet_name}")
    df=pd.read_excel(file, sheet_name=sheet_name)
    print("Dataframe head after loading Excel:")
    print(df.head())

    filtered_df = df[df['State'] == 'NY']
    print("Dataframe head after filtering for NY state:")
    print(filtered_df.head())

    df_zip= filtered_df.groupby('Zip').size().reset_index(name='Client count')
    df_zip.rename(columns={'Zip':'ZIP'}, inplace=True)
    df_zip['ZIP'] = df_zip['ZIP'].astype(int).astype(str)
    df_zip['ZIP'] = df_zip['ZIP'].apply(lambda x: x.zfill(5))
    print("Dataframe after grouping by ZIP:")
    print(df_zip.head())

    us_zipcodes = pd.read_csv('uszipcodes_geodata.txt', delimiter=',', dtype = str)
    us_zipcodes['ZIP'] = us_zipcodes['ZIP'].astype(str)
    print("US ZIP codes geodata head:")
    print(us_zipcodes.head())

    df_merged = pd.merge(us_zipcodes, df_zip, on='ZIP', how='inner')
    print("Merged dataframe head:")
    print(df_merged.head())

    map = folium.Map(location=[df_merged['LAT'].median(), df_merged['LNG'].median()], zoom_start=18)

    map.choropleth(geo_data='nyc-zip-code-tabulation-areas-polygons.geojson',
               data=df_merged, columns=['ZIP', 'Client count'], key_on='feature.properties.postalCode', fill_color='YlGnBu', fill_opacity=0.7, line_opacity=0.2, legend_name='Client count')
    
    marker_cluster = MarkerCluster().add_to(map)

    for i in range(df_merged.shape[0]):
        location = [float(df_merged['LAT'][i]), float(df_merged['LNG'][i])]  # Convert latitude and longitude to float
        folium.Marker(location, 
                    popup=""" <i>ZIP: </i> """ + df_merged['ZIP'][i] + """ <br> <i>Client count: </i> """ + str(df_merged['Client count'][i])).add_to(marker_cluster)
        
    map.fit_bounds([[40.54, -74], [40.81, -73.9]])

    map_html=BytesIO()
    map.save(map_html, close_file=False)
    map_html.seek(0)

    return send_file(map_html, mimetype='text/html')


@app.route('/wwmap', methods=['POST'])
def ww_map():
    file=request.files['file']
    sheet_name=request.form['sheet_name']

    df=pd.read_excel(file, sheet_name=sheet_name)

    countries = df['Country of Origin'].value_counts().reset_index()
    countries.columns = ['Country', 'Total']

    def get_country_code(country):
        try:
            return pycountry.countries.lookup(country).alpha_3
        except:
            return None
        
    countries['iso_alpha'] = countries['Country'].apply(get_country_code)

    print(countries.head())

    fig = px.choropleth(countries, locations="iso_alpha", color="Total", hover_name="Country", color_continuous_scale=px.colors.sequential.YlOrBr)

    html_str = fig.to_html(full_html=False)

    map_html = BytesIO()
    map_html.write(html_str.encode('utf-8'))


    map_html.seek(0)

    return send_file(map_html, mimetype='text/html')



if __name__ == '__main__':
    app.run(debug=True)



