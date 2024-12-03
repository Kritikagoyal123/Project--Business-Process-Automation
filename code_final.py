import requests
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import numpy as np


# Function to fetch Google Sheets data
def fetch_google_sheet_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        values = data.get('values', [])
        if values:
            header = values[0]  # The first row is considered the header
            rows = values[1:]
            df = pd.DataFrame(rows, columns=header)  # Create DataFrame
            return df
        else:
            print("No data found in the sheet")
            return pd.DataFrame()
    else:
        print(f"Failed to fetch data. HTTP Status Code: {response.status_code}")
        return pd.DataFrame()


# Google Sheets URLs
book_url = "https://sheets.googleapis.com/v4/spreadsheets/1d974FnqiPtsTgekWMJBuD8mkeN0v7xo2MpBUhd_CNKw/values/Book!A1:C59?key=AIzaSyA2tl9b-0I65tDVOmMMwnax45raYyk4Q0s"
edition_url = "https://sheets.googleapis.com/v4/spreadsheets/1d974FnqiPtsTgekWMJBuD8mkeN0v7xo2MpBUhd_CNKw/values/Edition!A1:H96?key=AIzaSyA2tl9b-0I65tDVOmMMwnax45raYyk4Q0s"
sales_q1_url = "https://sheets.googleapis.com/v4/spreadsheets/1d974FnqiPtsTgekWMJBuD8mkeN0v7xo2MpBUhd_CNKw/values/Sales Q1!A1:E7786?key=AIzaSyA2tl9b-0I65tDVOmMMwnax45raYyk4Q0s"
sales_q2_url = "https://sheets.googleapis.com/v4/spreadsheets/1d974FnqiPtsTgekWMJBuD8mkeN0v7xo2MpBUhd_CNKw/values/Sales Q2!A1:E13355?key=AIzaSyA2tl9b-0I65tDVOmMMwnax45raYyk4Q0s"
sales_q3_url = "https://sheets.googleapis.com/v4/spreadsheets/1d974FnqiPtsTgekWMJBuD8mkeN0v7xo2MpBUhd_CNKw/values/Sales Q3!A1:E22119?key=AIzaSyA2tl9b-0I65tDVOmMMwnax45raYyk4Q0s"
sales_q4_url = "https://sheets.googleapis.com/v4/spreadsheets/1d974FnqiPtsTgekWMJBuD8mkeN0v7xo2MpBUhd_CNKw/values/Sales Q4!A1:E13094?key=AIzaSyA2tl9b-0I65tDVOmMMwnax45raYyk4Q0s"

# Fetch data
df_books = fetch_google_sheet_data(book_url)
df_sales_q1 = fetch_google_sheet_data(sales_q1_url)
df_sales_q2 = fetch_google_sheet_data(sales_q2_url)
df_sales_q3 = fetch_google_sheet_data(sales_q3_url)
df_sales_q4 = fetch_google_sheet_data(sales_q4_url)
df_edition = fetch_google_sheet_data(edition_url)

# Add Quarter column to each sales dataframe
df_sales_q1['Quarter'] = 'Q1'
df_sales_q2['Quarter'] = 'Q2'
df_sales_q3['Quarter'] = 'Q3'
df_sales_q4['Quarter'] = 'Q4'

# Merge all sales data
df_sales = pd.concat([df_sales_q1, df_sales_q2, df_sales_q3, df_sales_q4])

# Merge with Edition and Books DataFrames
df_merged = pd.merge(df_sales, df_edition, on='ISBN', how='inner')
df_merged = pd.merge(df_merged, df_books, on='BookID', how='inner')

# Generate random ratings if missing
if 'Rating' not in df_merged.columns:
    df_merged['Rating'] = np.random.randint(1, 6, size=len(df_merged))

# Calculate Total Sales (Order ID count)
df_merged['Total Sales'] = df_merged.groupby('Title')['OrderID'].transform('count')

# Aggregate sales and average rating by book title
book_sales = df_merged.groupby('Title')['Total Sales'].sum().reset_index()
book_ratings = df_merged.groupby('Title')['Rating'].mean().reset_index()

# Prepare dropdown options for books
books_options = [{'label': row['Title'], 'value': row['Title']} for index, row in book_sales.iterrows()]

# Create a Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout of the app
app.layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.H3("Select a Book"),
            dcc.Dropdown(
                id='book-dropdown',
                options=books_options,
                placeholder="Select a Book"
            ),
        ], width=6)
    ]),
    dbc.Row([
        dbc.Col(html.Div(id='book-output'), width=6),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='sales-bar-chart',
                config={'displayModeBar': False}
            )
        ], width=6),
        dbc.Col([
            dcc.Graph(
                id='review-bar-chart',
                config={'displayModeBar': False}
            )
        ], width=6)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='sales-trend-line-chart',
                config={'displayModeBar': False}
            )
        ], width=12)
    ])
])


# Callback to update book selection output
@app.callback(
    Output('book-output', 'children'),
    Input('book-dropdown', 'value')
)
def update_output(selected_book):
    if selected_book:
        total_sales = book_sales.loc[book_sales['Title'] == selected_book, 'Total Sales'].values[0]
        return f'Total Sales for "{selected_book}": {total_sales}'
    return "No book selected."


# Callback to update the sales chart
@app.callback(
    Output('sales-bar-chart', 'figure'),
    Input('book-dropdown', 'value')
)
def update_sales_chart(selected_book):
    if selected_book:
        filtered_sales = book_sales[book_sales['Title'] == selected_book]
        fig = px.bar(
            filtered_sales,
            x='Title',
            y='Total Sales',
            title=f"Sales for {selected_book}",
            labels={'Title': 'Book Title', 'Total Sales': 'Total Sales'},
            color='Total Sales',
            height=500
        )
    else:
        fig = px.bar(
            book_sales,
            x='Title',
            y='Total Sales',
            title="Total Sales by Book",
            labels={'Title': 'Book Title', 'Total Sales': 'Total Sales'},
            color='Total Sales',
            height=500
        )
    if selected_book:
        fig.update_layout(xaxis_tickangle=0)
    else:
        fig.update_layout(xaxis_tickangle=45)
    return fig


# Callback to update the review chart
@app.callback(
    Output('review-bar-chart', 'figure'),
    Input('book-dropdown', 'value')
)
def update_review_chart(selected_book):
    if selected_book:
        filtered_reviews = book_ratings[book_ratings['Title'] == selected_book]
        fig = px.bar(
            filtered_reviews,
            x='Title',
            y='Rating',
            title=f"Average Rating for {selected_book}",
            labels={'Title': 'Book Title', 'Rating': 'Average Rating'},
            color='Rating',
            height=500
        )
    else:
        fig = px.bar(
            book_ratings,
            x='Title',
            y='Rating',
            title="Average Ratings by Book",
            labels={'Title': 'Book Title', 'Rating': 'Average Rating'},
            color='Rating',
            height=500
        )
    if selected_book:
        fig.update_layout(xaxis_tickangle=0)
    else:
        fig.update_layout(xaxis_tickangle=45)

    return fig


# Callback to update the sales trend line chart
@app.callback(
    Output('sales-trend-line-chart', 'figure'),
    Input('book-dropdown', 'value')
)
def update_sales_trend_chart(selected_book):
    if selected_book:
        # Filter the sales data for the selected book
        filtered_sales = df_merged[df_merged['Title'] == selected_book]
        # Group by quarter to get total sales per quarter
        filtered_sales = filtered_sales.groupby(['Quarter']).agg({'Total Sales': 'sum'}).reset_index()

        # Create a line chart showing the sales trend across the quarters
        fig = px.line(
            filtered_sales,
            x='Quarter',  # Quarter on x-axis
            y='Total Sales',  # Total Sales on y-axis
            title=f"Sales Trend for {selected_book}",  # Title of the chart
            labels={'Quarter': 'Quarter', 'Total Sales': 'Total Sales'},  # Axis labels
            markers=True  # Display markers for each data point
        )
    else:
        # If no book is selected, show the sales trend across all books for each quarter
        sales_by_quarter = df_merged.groupby(['Quarter']).agg({'Total Sales': 'sum'}).reset_index()

        # Create a line chart showing total sales per quarter across all books
        fig = px.line(
            sales_by_quarter,
            x='Quarter',  # Quarter on x-axis
            y='Total Sales',  # Total Sales on y-axis
            title="Sales Trend by Quarter for All Books",  # Title of the chart
            labels={'Quarter': 'Quarter', 'Total Sales': 'Total Sales'},  # Axis labels
            markers=True  # Display markers for each data point
        )

    # Rotate x-axis labels for better readability
    if selected_book:
        fig.update_layout(xaxis_tickangle=0)
    else:
        fig.update_layout(xaxis_tickangle=45)
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8054)

