import dash
from dash import dcc
from dash import html
import plotly.express as px
from dash.dependencies import Output, Input
import preparing_data

app = dash.Dash(__name__)

df = preparing_data.df
russia_reg = preparing_data.russia_reg

options_for_dropdown = {
    'LOG_PREM' : 'PREM_SUM_REG',
    'LOG_POL_COUNT' : 'POL_COUNT'
}

app.layout = html.Div(
        children =[

        # Header block
        html.Div([
        html.H1(children='Распределение полисов страхования', className='title'),
        # html.P(children='Данные на 08/2023', className='status-description')
            ], className="header"),
        # End of header block

        # Filters block
        html.Div(
            children = [
                # Dropdown block
                html.Div(
                    children = [
                        html.H3('Параметр', className="filter-title"),
                        dcc.Dropdown(
                                options=[
                               {'label': 'Сумма премии', 'value': 'LOG_PREM'},
                               # {'label': 'Средняя сумма премии по полису', 'value': 'LOG_AVG_SUM_PREM_REG'},
                               {'label': 'Количество полисов', 'value': 'POL_COUNT'}
                               ],
                               value='LOG_PREM',
                               id='chosen_filter',

                                )
                    ], className="dropdown"),

                # Slider block
                html.Div(
                    children=[
                        html.H3('Год заключения договора', className="filter-title"),

                        dcc.Slider(2018, 2023, step=None,
                                       marks={
                                           2018: '2018 г.',
                                           2019: '2019 г.',
                                           2020: '2020 г.',
                                           2021: '2021 г.',
                                           2022: '2022 г.',
                                           2023: '2023 г.'
                                       },
                                       value=2023,
                                       id='year_slider',
                                       className='slider'
                                     )
                            ], className='slider_block')
                ], className='filters'),

        # Graphs block
        html.Div([
            html.Div([dcc.Graph(id='choroplet_map')], className= 'map_container'),
            html.Div([
                html.Div([dcc.Graph(id='barplot_months')], className= 'box_bar1'),
                html.Div([dcc.Graph(id='barplot_salech')], className= 'box_bar2'),
                # html.Div([dcc.Graph(id='barplot_lob')], className= 'map_container')
                ], className= 'bar_container')

            ], className= 'container'),

        ])


@app.callback(
    Output('choroplet_map', 'figure'),
    [Input(component_id = 'year_slider', component_property= 'value'),
     Input(component_id = 'chosen_filter', component_property = 'value')]
)
def build_map(year, chosen_option):

    df_cur = df.copy()
    df_cur = df_cur[df_cur['YEAR_CONC'] == year]

    fig = px.choropleth_mapbox(df_cur,
                               locations=df_cur.id,
                               geojson=russia_reg,
                               color=chosen_option,
                               mapbox_style="carto-positron",
                               color_continuous_scale="Blues",
                               hover_name='state',
                               # title='Распределение по регионам России',
                               hover_data=[options_for_dropdown[chosen_option], ],
                               labels={
                                       'id': 'ID регионa',
                                       'PREM_SUM_REG': 'Сумма премии, руб.',
                                       'LOG_PREM': ' Премия',
                                       'POL_COUNT': 'Количество полисов'
                                       },
                               zoom=3,
                               opacity=0.8,
                               center={'lat': 65, 'lon': 78})

    fig.update_layout(margin={"r":20,"t":5,"l":5,"b":5},
                      clickmode='event + select'
                      )

    return fig

@app.callback(
    Output('barplot_months', 'figure'),
    [Input(component_id='year_slider', component_property='value'),
     Input('choroplet_map', 'clickData')]
)

def update_bar_prem(year, custom_data):
    df_cur = df.copy()

    if custom_data is not None:
        state = custom_data['points'][0]['location']
        df_cur = df_cur[(df_cur['YEAR_CONC'] == year)&(df_cur['id'] == state)][['MONTH','PREM', 'MONTH_CONC']].groupby(['MONTH', 'MONTH_CONC']).agg('sum').reset_index().sort_values('MONTH_CONC')
    else:
        df_cur = df_cur[df_cur['YEAR_CONC'] == year][['MONTH', 'PREM', 'MONTH_CONC']].groupby(['MONTH', 'MONTH_CONC']).agg('sum').reset_index().sort_values('MONTH_CONC')

    # df_cur = df_cur[df_cur['YEAR_CONC'] == year][['MONTH', 'PREM']].groupby('MONTH').agg('sum').reset_index()

    fig = px.bar( df_cur,
                  x = 'MONTH',
                  y = 'PREM',
                  title='Распределение премии по месяцам',
                  hover_data=['PREM'],
                  color='PREM',
                  text_auto='.2s',
                  orientation='v',
                  color_continuous_scale = 'Blues',
                  labels={
                      'MONTH': 'Месяц',
                      'PREM': 'Сумма премии, руб.'
                  },
                 ).add_traces(
            px.line(df_cur, x="MONTH", y="PREM").update_traces(showlegend=False).data)

    # for idx in range(len(fig.data)):
    #     fig.data[idx].x = months

    fig.update_layout(yaxis={'visible': False, 'showticklabels': False},xaxis_title=None, title_x=0.5,
                      coloraxis_showscale=False,
                      legend = {"title": "Сумма премии, руб."}
                    )
    fig.update_xaxes(tickangle=45)

    return fig


@app.callback(
    Output('barplot_salech', 'figure'),
    [Input(component_id='year_slider', component_property='value'),
     Input('choroplet_map', 'clickData')]
)

def update_bar_salech(year, custom_data):
    df_cur = df.copy()

    if custom_data is not None:
        state = custom_data['points'][0]['location']
        df_cur = df_cur[(df_cur['YEAR_CONC'] == year)&(df_cur['id'] == state)][['MONTH', 'SALE_CHANNEL','ID']].groupby(['MONTH', 'SALE_CHANNEL']).agg('count').reset_index()
    else:
        df_cur = df_cur[df_cur['YEAR_CONC'] == year][['MONTH', 'SALE_CHANNEL', 'ID']].groupby(['MONTH', 'SALE_CHANNEL']).agg('count').reset_index()

    # fig = px.pie(df_cur,
    #              names = 'SALE_CHANNEL',
    #              values= 'ID',
    #              color='SALE_CHANNEL',
    #              hover_data=['ID'],
    #              color_discrete_sequence=px.colors.qualitative.Set2,
    #              labels={'MONTH': 'Месяц',
    #                     'SALE_CHANNEL': 'Канал продаж',
    #                     'ID':'Количество полисов'
    #                     }
    #              )

    fig = px.sunburst(
        df_cur,
        path=['MONTH', 'SALE_CHANNEL'],
        names = 'SALE_CHANNEL',
        # parents='MONTH',
        title='Распределение по каналам продаж в каждом месяце',
        values='ID',
        color='SALE_CHANNEL',
        hover_data=['ID'],
        color_continuous_scale='RdBu',
        # color_discrete_sequence=px.colors.qualitative.Set2,
        labels={'MONTH': 'Месяц',
        'SALE_CHANNEL': 'Канал продаж',
        'ID':'Количество полисов'
        }
    )


    # for idx in range(len(fig.data)):
    #     fig.data[idx].x = months
    # fig.update_xaxes(tickangle=45)
    fig.update_layout(title_x=0.5)

    return fig


# @app.callback(
#     Output('barplot_lob', 'figure'),
#     Input(component_id='year_slider', component_property='value')
# )

# def update_bar_lob(year):
#     df_cur = df.copy()
#     df_cur = df_cur[df_cur['YEAR_CONC'] == year][['MONTH', 'LOB']].groupby(['MONTH', 'LOB']).agg('count').reset_index()
#
#     fig = px.bar(   df_cur,
#                     x = 'MONTH',
#                     y = 'LOB',
#                     title='Линии бизнеса',
#                     # hover_data=['PREM_SUM_REG'],
#                     color='LOB',
#                     orientation='v',
#                     # text_auto='.2s',
#                     labels={None}
#                  )
#     return fig


if __name__ == '__main__':
   app.run_server(debug=True)

