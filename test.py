import justpy as jp
import pandas as pd
import datetime

poch = datetime.datetime(1970, 1, 1)


def convert_date(date_string):
    date = datetime.datetime.strptime(date_string, '%Y-%m-%d')
    return (date - epoch).total_seconds()*1000


def stock_test(request):
    wp = jp.WebPage()
    ticker = request.query_params.get('ticker', 'MSFT')
    if ticker not in ['AAPL', 'IBM', 'INTC', 'MSFT']:
        ticker = 'MSFT'
    data = pd.read_csv(f'https://elimintz.github.io/stocks/{ticker.upper()}.csv')
    chart = jp.HighStock(a=wp, classes='m-1 p-2 border w-10/12')
    o = chart.options
    o.title.text = 'Historical Stock Price'
    o.legend = {'enabled': True, 'align': 'right', 'layout': 'proximate'}
    o.rangeSelector.selected = 4  # Set default range to 1 year
    x = list(data['Date'].map(convert_date))
    y = data['Adj Close'].to_list()
    s = jp.Dict({'name': ticker.upper(), 'data': jp.make_pairs_list(x, y)})
    o.series = [s]
    s.tooltip.valueDecimals = 2  # Price displayed by tooltip will have 2 decimal values
    return wp

grid_options = """
{
    defaultColDef: {
        filter: true,
        sortable: true,
        resizable: true,
        cellStyle: {textAlign: 'center'},
        headerClass: 'font-bold'
    }, 
      columnDefs: [
      {headerName: "Make", field: "make"},
      {headerName: "Model", field: "model"},
      {headerName: "Price", field: "price"}
    ],
      rowData: [
      {make: "Toyota", model: "Celica", price: 35000},
      {make: "Ford", model: "Mondeo", price: 32000},
      {make: "Porsche", model: "Boxter", price: 72000}
    ]
}
"""
def grid_test():
    wp = jp.WebPage()
    grid = jp.AgGrid(a=wp, options=grid_options, style='height: 200px; width: 300px; margin: 0.25em')
    grid.options.rowData.append({'make': 'Autocars', 'model': 'Sussita', 'price': 3})
    return wp
    
def pandas_grid_test():
    wm_df = pd.read_csv('https://elimintz.github.io/women_majors.csv').round(2)
    wp = jp.WebPage()
    grid = jp.AgGrid(a=wp)
    grid.load_pandas_frame(wm_df)
    return wp    

wm = pd.read_csv('https://elimintz.github.io/women_majors.csv').round(2)
# Create list of majors which start under 20% women students
wm_under_20 = list(wm.loc[0, wm.loc[0] < 20].index)

def women_majors():
    wp = jp.WebPage()
    wm.jp.plot(0, wm_under_20, kind='spline', a=wp, title='The gender gap is transitory - even for extreme cases',
               subtitle='Percentage of Bachelors conferred to women form 1970 to 2011 in the US for extreme cases where the percentage was less than 20% in 1970',
                classes='m-2 p-2 w-3/4')
    return wp


import random

async def my_click(self, msg):
    self.color = random.choice(['primary', 'secondary', 'accent', 'dark', 'positive',
                                'negative','info', 'warning'])
    self.label = self.color
    msg.page.dark = not msg.page.dark
    await msg.page.set_dark_mode(msg.page.dark)

def quasar_example():
    wp = jp.QuasarPage(dark=True)  # Load page in dark mode
    d = jp.Div(classes='q-pa-md q-gutter-sm', a=wp)
    jp.QBtn(color='primary', icon='mail', label='On Left', a=d, click=my_click)
    jp.QBtn(color='secondary', icon_right='mail', label='On Right', a=d, click=my_click)
    jp.QBtn(color='red', icon='mail', icon_right='send', label='On Left and Right', a=d, click=my_click)
    jp.Br(a=d)
    jp.QBtn(icon='phone', label='Stacked', stack=True, glossy=True, color='purple', a=d, click=my_click)
    return wp


async def dog_pic(request):
    symbols = ['COMEX:GC', 'NYMEX:CL', 'COMEX:SI', 'NYMEX:NG', 'CBOT:ZW', 'COMEX:HG', 'KS:KSU7', 'HK:HCEIc1', 'OSE:JP225',
     'Eurex:DE30', 'CME:US500', 'CME:USTEC']
    wp = jp.WebPage()
    breed = request.query_params.get('breed', 'papillon' )
    host = 'https://tvc4.forexpros.com/bf9b0cf35ce6ca91b1bba8dd1d70c0c2/1601606035/18/18/88/'
    symbols_text = ','.join(symbols)
    uri = f'quotes?symbols={symbols_text}'
    r = await jp.get(host+uri)
    print(r)
    d = [row['v'] for row in r['d']]
    df = pd.DataFrame(d)
    grid = jp.AgGrid(a=wp)
    grid.load_pandas_frame(df)

    return wp

jp.justpy(dog_pic)