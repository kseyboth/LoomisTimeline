import numpy as np
import pandas as pd
import plotly_express as px
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
#from Init.py import *


#Define Class

class Event:
    grid = [[0 for x in range(10)] for y in range(200)]

    def __init__(self, list):
        self.desc = list[1]
        year = list[0]
        if year.find("-") != -1: #Case 1: range of years
            x= year.split("-")
            self.startyear = x[0]
            self.endyear = str(int(x[1]) + 1)
            self.month = 'N/A'
        elif len(year) == 5: #Case 2: Decade of years
            self.startyear = year[0:4]
            self.endyear = str(int(year[0:4]) + 9)
            self.month = 'N/A'
        elif len(year) == 4: # Case 3: a singular year
            self.startyear = year
            self.endyear = str(int(year) + 1)
            self.month = 'N/A'
        else: #Case 4: month and year
            x = year.split(" ")
            self.month = x[0]
            self.startyear = x[1]
            self.endyear = str(int(x[1]) + 1)


        self.theme = list[2]
        self.loc = list[3]
        self.display_y = self.find_y() #this assigns the y value the events should display on

    def y_works(self, y):
        for i in range(int(self.startyear) - 1700, (int(self.endyear))- 1700):
            if Event.grid[i][y] != 0:
                return False
        return True

    def find_y(self):
        for i in range(0, 10):
            if self.y_works(i):
                self.mark_grid(i)
                return i

    def mark_grid(self, y):
        for i in range(int(self.startyear) - 1700, (int(self.endyear)) -1700):
            Event.grid[i][y] = 1

    def __str__(self):
        return f'Event( Description = {self.desc}, Start Year = {self.startyear}, ' \
               f'End Year = {self.endyear}, Theme = {self.theme}, Location = {self.loc}'



timedat = pd.read_csv("Timeline Data - Sheet1.csv")
listtimedat = timedat.to_numpy().tolist()





#runs through all of the events

startyear_list = []
endyear_list = []
startyear_list2 = []
endyear_list2 = []
month_list = []
desc_list = []
location_list = []
theme_list = []
display_list = []

for i in range(0, len(listtimedat)):
    obj = Event(listtimedat[i])
    startyear_list.append(obj.startyear)
    endyear_list.append(obj.endyear)
    startyear_list2.append(int(obj.startyear))
    endyear_list2.append(int(obj.endyear))
    month_list.append(obj.month)
    desc_list.append(obj.desc)
    location_list.append(obj.loc)
    theme_list.append(obj.theme)
    display_list.append(obj.display_y)

dict_allevents = {"Start Year": startyear_list, "End Year": endyear_list,
                  "Start Year2": startyear_list2, "End Year2": endyear_list2,
                  "Month": month_list,
                  "Event Description": desc_list,
                  "Event Location": location_list,
                  'Event Theme': theme_list,
                  'Display Y': display_list}

df_allevents = pd.DataFrame(dict_allevents)



#Dash App
app = dash.Dash()
app.layout = html.Div([
    html.Div(style = {
  'backgroundColor': '#98252B', 'height': '20vh'}
,
        children=[html.Div([
        html.H1(children = 'Chronology of Contextual Events',
                style= {'text-align': 'center',
                        #'vertical-align': 'top',
                        'line-height': 150,
                        'font': 'TimesNewRoman', 'fontSize': 50, 'color': '#FFFFFF'})])]), #try sans serif font, chronology

html.Div([
html.Div(
    [ html.H4("Select Starting and Ending Year [must be within 1700 to 1861]"),
        #html.Br(),
        dcc.Input(id="input1", type="number", placeholder="", style={'marginRight':'10px'}, value = 1699 ),
        dcc.Input(id="input2", type="number", placeholder="", value = 1861, debounce=True),
        #html.Div(id="output"),
        ],
className = 'six columns'
),

html.Div([
    html.H4("Select Themes Displayed"),
dcc.Checklist(id = 'themechecklist',
             options = [
                 {'label': 'Political Events', 'value': 'Political'},
                 {'label': 'Economic Events', 'value': 'Economic'},
                 {'label': 'Legal Events', 'value': 'Legal'},
                 {'label': 'Social Events', 'value': 'Social'}
                 ],
             #searchable= False,
             #multi = True,
             value = ['Political', 'Economic', 'Legal', 'Social'],
             className = 'six columns'

),]),

    html.Div([
        html.H4("Select Regions Displayed"),
        dcc.Checklist(id='locationchecklist',
                     options=[
                         {'label': 'United States', 'value': 'USA'},
                         {'label': 'Connecticut', 'value': 'CT'},
                         {'label': 'South Carolina', 'value': 'SC'},
                     ],
                     #searchable=False,
                     #multi=True,
                     value=['USA', 'CT', 'SC'],
                     className='six columns'

                     ), ]),

]),
    dcc.Graph( id="timelinegraph")
])

color_dict = {'Political': 'red', "Social": 'green', "Economic": 'orange', "Legal": 'blue'}
hover_dict = {"Event Theme": False, "Start Year": False, "End Year": False, "Display Y": False, "Event Description": True}


#Write Call back for input
@app.callback(
    Output('timelinegraph', 'figure'),
    [Input('input1', 'value'), Input('input2', 'value'), Input('themechecklist', 'value'), Input('locationchecklist', 'value')])

def update_timelinegraph(start_year_selected, end_year_selected, themes_selected, locations_selected):
    start_year = start_year_selected
    end_year_selected = end_year_selected
    theme_list = themes_selected
    loc_list = locations_selected
    df_new = df_allevents.query('`Start Year2` > @start_year_selected and `End Year2` < @end_year_selected')
    #df_theme_empty = pd.DataFrame()
    df_theme_filtered = df_new[df_new['Event Theme'].isin(theme_list)]
    df_loc_filtered = df_theme_filtered[df_theme_filtered['Event Location'].isin(loc_list)]
    #pd.concat([df_theme_empty, x])

    #df_new_dict = {'Start Year': str(df_new['Start Year'][:]), 'End Year': str(df_new['End Year'][:]),
                  #'Event Description': df_new['Event Description'][:]}
    #df_new_dict = pd.DataFrame.to_dict(df_theme_empty)
    fig = px.timeline(data_frame=df_loc_filtered,
                      x_start="Start Year",
                      x_end="End Year",
                      y='Display Y',
                      color=  'Event Theme', #'Start Year',  # ['rgba(96, 98, 251, 1)', 'rgba(251, 96, 160, 1)'],
                      color_discrete_map= color_dict,
                      hover_name='Start Year2',
                      hover_data= hover_dict,#,
                     #hovertemplate=
                     # '<i>Event Year</i>: $%{x_start}' +
                     # '<br><b>Event</b>: %{y}<br>',
                      # labels = {"Event": "Event Description", "Year": "Start Year2"},
                      range_y=[0, 15]
                      )

    #fig.update_traces(hovertemplate=
                     # f"<b>Event Year: </b> {df_loc_filtered['Start Year2']} <br>" + #'<i>Event Year</i>: %{x_start}<br>'
                     # f'<br><b>Event</b>: {df_loc_filtered["Event Description"]}<br>')
    fig.update_layout(showlegend= True, uirevision='constant', hoverlabel_align='right',
                      #hovermode = 'Event Description',
                      font=dict(
        family="Times New Roman",
        size=18
    ))
    fig.update_yaxes(showticklabels=False, title = 'Historical Event', range = [-1, 5])
    fig.update_xaxes(title = 'Year', )


    return fig




app.run_server(debug=True, use_reloader=False)
