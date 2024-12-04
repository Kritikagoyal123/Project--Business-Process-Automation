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
author_url = "https://sheets.googleapis.com/v4/spreadsheets/1d974FnqiPtsTgekWMJBuD8mkeN0v7xo2MpBUhd_CNKw/values/Author!A1:F42?key=AIzaSyA2tl9b-0I65tDVOmMMwnax45raYyk4Q0s"

# Fetch data
df_books = fetch_google_sheet_data(book_url)
df_sales_q1 = fetch_google_sheet_data(sales_q1_url)
df_sales_q2 = fetch_google_sheet_data(sales_q2_url)
df_sales_q3 = fetch_google_sheet_data(sales_q3_url)
df_sales_q4 = fetch_google_sheet_data(sales_q4_url)
df_edition = fetch_google_sheet_data(edition_url)
df_authors = fetch_google_sheet_data(author_url)

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

# Merge Author information with Books (on AuthID)
df_merged = pd.merge(df_merged, df_authors, on='AuthID', how='left')

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

# Get top 10 selling books
top_10_books = book_sales.sort_values(by='Total Sales', ascending=False).head(10)

# Create a Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout of the app
app.layout = html.Div([
    # Header Section with Titles
    dbc.Row([
        dbc.Col([
            html.H1("Bookshop Dashboard", style={
                'textAlign': 'center',
                'marginBottom': '20px',
                'fontSize': '48px',
                'fontWeight': 'bold',
                'color': '#FFFFFF',  # White text for contrast
                'fontFamily': 'Arial, sans-serif'  # Modern font
            })
        ], width=12)
    ], style={'marginBottom': '20px'}),  # Space between header and content

    # Book Selection and Author Name Section
    dbc.Row([
        # Select Book Dropdown
        dbc.Col([
            html.H3("Book Name", style={
                'textAlign': 'center',
                'marginBottom': '15px',
                'fontSize': '20px',
                'color': 'white',  # Blue
                'fontWeight': 'bold',
                'fontFamily': 'Arial, sans-serif'
            }),
            dcc.Dropdown(
                id='book-dropdown',
                options=books_options,
                placeholder="Please select a book",
                style={
                    'width': '100%',
                    'fontSize': '15px',
                    'padding': '15px',
                    'borderRadius': '8px',
                    'border': '1px solid #BDC3C7',  # Border
                    'backgroundColor': '#ECF0F1',  # Light gray background
                    'color': 'black',
                    'textAlign': 'center',



                }
            ),
        ], width=6, style={'paddingLeft': '30px'}),

        # Author Name Box
        dbc.Col([
            html.H3("Author Name", style={
                'textAlign': 'center',
                'marginBottom': '15px',
                'fontSize': '20px',
                'color': 'white',

                'fontFamily': 'Arial, sans-serif'

}),
            dbc.Card(
                dbc.CardBody([
                    html.Div(id='author-name', style={
                        'fontSize': '24px',
                        'fontWeight': 'bold',
                        'padding': '15px',
                        'border': '1px solid #BDC3C7',  # Border
                        'borderRadius': '8px',  # Rounded corners
                        'backgroundColor': '#ECF0F1',  # Light background
                        'textAlign': 'center',
                        'color': 'black'  # Blue color for the count
                    })
                ]),
                style={
                    'boxShadow': '0 4px 8px rgba(0,0,0,0.2)',
                    'borderRadius': '8px',
                    'backgroundColor': '#fff'
                }
            )
        ], width=5, style={'paddingLeft': '30px'}),  # Adjust the width of the column
    ], style={'marginBottom': '20px'}),  # Add space between rows

    # Book Output Row
    dbc.Row([
        dbc.Col(html.Div(id='book-output'), width=6, style={'padding': '10px'})
    ], style={'marginBottom': '20px'}),

    # Sales and Review Charts Row
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='sales-bar-chart',
                config={'displayModeBar': False},
                style={
                    'height': '800px',  # Set the same height for all charts
                    'padding': '20px'  # Uniform padding for the chart
                }
            )
        ], width=6, style={'padding': '10px'}),
        dbc.Col([
            dcc.Graph(
                id='review-bar-chart',
                config={'displayModeBar': False},
                style={
                    'height': '800px',  # Set the same height for all charts
                    'padding': '20px'  # Uniform padding for the chart
                }
            )
        ], width=6, style={'padding': '10px'})
    ], style={'marginBottom': '20px'}),  # Add space between charts

    # Sales Trend Line Chart Row
    # Sales Trend and Top 10 Books side by side
    dbc.Row([
        # Sales Trend Line Chart
        dbc.Col([
            dcc.Graph(
                id='sales-trend-line-chart',
                config={'displayModeBar': False},
                style={
                    'height': '800px',  # Set the same height for all charts
                    'padding': '20px'  # Uniform padding for the chart
                }
            )
        ], width=6, style={'padding': '20px'}),  # Width set to 6 (half of the row)

        # Top 10 Selling Books Chart
        dbc.Col([
            html.H3(style={
                'textAlign': 'center',
                'marginBottom': '20px',
                'fontSize': '24px',
                'fontWeight': 'bold',
                'color': '#2980B9',  # Blue color
                'fontFamily': 'Arial, sans-serif'
            }),
            dcc.Graph(
                id='top-10-books-bar-chart',
                config={'displayModeBar': False},
                style={
                    'height': '800px',  # Set the same height for all charts
                    'padding': '20px'  # Uniform padding for the chart
                }
            )
        ], width=6, style={'padding': '10px'})  # Width set to 6 (half of the row)
    ], style={'marginBottom': '20px'})  # Add space between the charts

], style={'backgroundColor': '#2C3E50', 'color': '#fff'})  # Overall background color and white text



# Callback to update the sales chart
@app.callback(Output('sales-bar-chart', 'figure'),Input('book-dropdown', 'value')     )
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
@app.callback( Output('review-bar-chart', 'figure'),Input('book-dropdown', 'value')
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
@app.callback(Output('sales-trend-line-chart', 'figure'), Input('book-dropdown', 'value')
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

# Callback to display Top 10 Selling Books
@app.callback(
    Output('top-10-books-bar-chart', 'figure'),
    Input('book-dropdown', 'value')
)
def update_top_10_books_chart(selected_book):
    # Sort the books by Total Sales in descending order and get the top 10
    top_10_books = book_sales.sort_values(by='Total Sales', ascending=False).head(10)

    # Add a 'Rank' column to display ranking
    top_10_books['Rank'] = range(1, len(top_10_books) + 1)

    # Create a bar chart showing the rank of books by their total sales
    fig = px.bar(
        top_10_books,
        x='Title',  # Book Title on x-axis
        y='Rank',  # Rank on y-axis
        title="Top 10 Selling Books",
        labels={'Title': 'Book Title', 'Rank': 'Rank'},
        color='Rank',  # Color by rank to differentiate the bars
        height=500
    )

    # Add ranking as text labels on the bars
    fig.update_traces(text=top_10_books['Rank'], textposition='outside')

    # Rotate x-axis labels for better readability
    fig.update_layout(xaxis_tickangle=45)

    return fig

# Callback to update the Author Name
@app.callback(
    Output('author-name', 'children'),
    Input('book-dropdown', 'value')
)
def update_author_name(selected_book):
    if selected_book:
        # Get the Author Name for the selected book
        author_first_name = df_merged.loc[df_merged['Title'] == selected_book, 'First Name'].values[0]
        author_last_name = df_merged.loc[df_merged['Title'] == selected_book, 'Last Name'].values[0]
        return f'{author_first_name} {author_last_name}'
    return "No book selected."

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8054)