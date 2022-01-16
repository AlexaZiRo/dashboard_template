# -*- coding: utf-8 -*-
import pandas as pd

import dash
import dash_core_components as dcc
from dash import html
import plotly.express as px
from ast import literal_eval

from dash.dependencies import Input, Output

smd = pd.read_csv("data/data_for_dash.csv")

################################################################################
# APP INITIALIZATION
################################################################################

app = dash.Dash(__name__)

# this is needed by gunicorn command in procfile
server = app.server

################################################################################
# HELPER FUNCTIONS
################################################################################

# this function converts lists within the strings in the specified columns into real lists
columns = ['actors', "genre", "production_country"]
for i in columns:
    smd[i] = smd[i].apply(literal_eval)



#this function coverts the series data into an 1D array
def to_1D(series):
 return pd.Series([x for _list in series for x in _list])


# get year values for dropdown-menu
years = smd.year.unique()
smd_year = smd[smd["year"] == years[0]]


# dat subsets for plots
smd_ya = pd.DataFrame(to_1D(smd_year["actors"]).value_counts())
smd_yg = pd.DataFrame(to_1D(smd_year["genre"]).value_counts())
smd_yp = pd.DataFrame(to_1D(smd_year["production_country"]).value_counts())
rel = pd.DataFrame(smd_year.month.value_counts().reindex(['January', 'February', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December']))

################################################################################
# PLOTS
################################################################################


fig1 = px.bar(x=smd_year.sort_values("budget")["original_title"][:10], y=smd_year.sort_values("budget").index[:10])
fig1.update_layout(title_text='Most expensive movies', title_x=0.5)

fig2 = px.bar(x=smd_year.sort_values("popularity")["original_title"][:10], y=smd_year.sort_values("popularity").index[:10])
fig2.update_layout(title_text='Most popular movies', title_x=0.5)

fig3 = px.pie(values=smd_ya[0][:10], names=smd_yg.index[:10])
fig3.update_layout(title_text='Movie genres', title_x=0.5)

fig4 = px.choropleth(locations=smd_yp.index,
                    locationmode="country names",
                    color = smd_yp[0])
fig4.update_layout(title_text='Movies produced by Country', title_x=0.5)

fig5 = px.line(x=rel.index, y=rel["month"])
fig5.update_layout(title_text='Releases over the year', title_x=0.5)

################################################################################
# LAYOUT
################################################################################

app =dash.Dash()
app.title = 'Mokey Dash'

app.layout = html.Div(style = {"background-color": "white"},children=[html.Div([
                                                                    html.H2("Please choose a year you want to have information about",style = {"padding-top": "10px","padding-bottom": "10px","background-color": "#FFF1AF"}),
                                                                    dcc.Dropdown(
                                                                                id="dropdown",
                                                                                options=sorted([{'label': i, 'value': i} for i in years], key = lambda x: x['label']),
                                                                                value=years[0],
                                                                                clearable=False, 
                                                                                style= {"width": "50%",'margin':'auto'}),
                                                                    dcc.Graph(id="exp-movies", figure = fig1,style = {"width":"30%", "margin-left": "20px","position": "relative", "display":"inline-block"}),
                                                                    dcc.Graph(id="pop-movies", figure = fig2,style = {"width":"30%", "margin-left": "20px","position": "relative","display":"inline-block"}),
                                                                    dcc.Graph(id="pieplot", figure = fig3,style = {"width":"30%", "margin-left": "20px","position": "relative","display":"inline-block"}),
                                                                    dcc.Graph(id="mapplot", figure = fig4,style = {"width":"65%", "margin-left":"20px","position": "relative","display":"inline-block"}),
                                                                    dcc.Graph(id="lineplot", figure = fig5,style = {"width":"30%", "margin-left": "20px","position": "relative", "display":"inline-block"}),

                                                                    ])
                                                                ])



################################################################################
# INTERACTION CALLBACKS
################################################################################


@app.callback(
    [Output("exp-movies", "figure"), Output("pop-movies", "figure"),Output("pieplot", "figure"), Output("mapplot", "figure"), Output("lineplot", "figure")], 
    [Input("dropdown", "value")])
def update_plots(year):
    smd_year = smd[smd["year"] == year]
    smd_ya = pd.DataFrame(to_1D(smd_year["actors"]).value_counts())
    smd_yg = pd.DataFrame(to_1D(smd_year["genre"]).value_counts())
    smd_yp = pd.DataFrame(to_1D(smd_year["production_country"]).value_counts())
    rel = pd.DataFrame(smd_year.month.value_counts().reindex(['January', 'February', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December']))
    fig1 = px.bar(x=smd_year.sort_values("budget",ascending =False).budget[:10], y=smd_year.sort_values("budget", ascending =False)["original_title"][:10]).update_layout(title_text='Most expensive movies', title_x=0.5).update_xaxes(title="US $")
    fig1.update_yaxes(title=None, autorange="reversed")
    fig2 = px.bar(x=smd_year.sort_values("popularity",ascending =False).popularity[:10], y=smd_year.sort_values("popularity",ascending =False)["original_title"][:10]).update_layout(title_text='Most popular movies', title_x=0.5).update_xaxes(title="TMDB popularity score")
    fig2.update_yaxes(title=None, autorange="reversed")
    fig3 = px.pie(values=smd_ya[0][:10], names=smd_yg.index[:10]).update_layout(title_text='Movie genres', title_x=0.5)       
    fig4 = px.choropleth(locations=smd_yp.index,
                    locationmode="country names",
                    color = smd_yp[0]).update_layout(title_text='Movies produced by Country', title_x=0.5)
    fig5 = px.line(x=rel.index, y=rel["month"], markers = True).update_layout(title_text='Releases over the year', title_x=0.5).update_xaxes(title=None)
    fig5.update_yaxes(title=None)


    return fig1, fig2, fig3, fig4, fig5
                   
                   
# Add the server clause:
if __name__ == "__main__":
    app.run_server()