# Importing required libraries
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
    response = requests.get(url)  # Make an HTTP GET request to the provided URL
    if response.status_code == 200:
        data = response.json()  # Parse the response as JSON
        values = data.get('values', [])  # Extract values from the JSON response
        if values:
            header = values[0]  # First row is treated as column headers
            rows = values[1:]  # Remaining rows contain data
            df = pd.DataFrame(rows, columns=header)  # Create a DataFrame
            return df
        else:
            print("No data found in the sheet")
            return pd.DataFrame()  # Return empty DataFrame if no data
    else:
        print(f"Failed to fetch data. HTTP Status Code: {response.status_code}")
        return pd.DataFrame()  # Return empty DataFrame if request fails


# Google Sheets URLs
# URL for book details
book_url = "https://sheets.googleapis.com/v4/spreadsheets/1d974FnqiPtsTgekWMJBuD8mkeN0v7xo2MpBUhd_CNKw/values/Book!A1:C59?key=AIzaSyA2tl9b-0I65tDVOmMMwnax45raYyk4Q0s"
# URL for edition details
edition_url = "https://sheets.googleapis.com/v4/spreadsheets/1d974FnqiPtsTgekWMJBuD8mkeN0v7xo2MpBUhd_CNKw/values/Edition!A1:H96?key=AIzaSyA2tl9b-0I65tDVOmMMwnax45raYyk4Q0s"
# URL for Q1 sales data
sales_q1_url = "https://sheets.googleapis.com/v4/spreadsheets/1d974FnqiPtsTgekWMJBuD8mkeN0v7xo2MpBUhd_CNKw/values/Sales Q1!A1:E7786?key=AIzaSyA2tl9b-0I65tDVOmMMwnax45raYyk4Q0s"
# URL for Q2 sales data
sales_q2_url = "https://sheets.googleapis.com/v4/spreadsheets/1d974FnqiPtsTgekWMJBuD8mkeN0v7xo2MpBUhd_CNKw/values/Sales Q2!A1:E13355?key=AIzaSyA2tl9b-0I65tDVOmMMwnax45raYyk4Q0s"
# URL for Q3 sales data
sales_q3_url = "https://sheets.googleapis.com/v4/spreadsheets/1d974FnqiPtsTgekWMJBuD8mkeN0v7xo2MpBUhd_CNKw/values/Sales Q3!A1:E22119?key=AIzaSyA2tl9b-0I65tDVOmMMwnax45raYyk4Q0s"
# URL for Q4 sales data
sales_q4_url = "https://sheets.googleapis.com/v4/spreadsheets/1d974FnqiPtsTgekWMJBuD8mkeN0v7xo2MpBUhd_CNKw/values/Sales Q4!A1:E13094?key=AIzaSyA2tl9b-0I65tDVOmMMwnax45raYyk4Q0s"
# URL for author details
author_url = "https://sheets.googleapis.com/v4/spreadsheets/1d974FnqiPtsTgekWMJBuD8mkeN0v7xo2MpBUhd_CNKw/values/Author!A1:F42?key=AIzaSyA2tl9b-0I65tDVOmMMwnax45raYyk4Q0s"

# Load data from Google Sheets into DataFrames
df_books = fetch_google_sheet_data(book_url)
df_sales_q1 = fetch_google_sheet_data(sales_q1_url)
df_sales_q2 = fetch_google_sheet_data(sales_q2_url)
df_sales_q3 = fetch_google_sheet_data(sales_q3_url)
df_sales_q4 = fetch_google_sheet_data(sales_q4_url)
df_edition = fetch_google_sheet_data(edition_url)
df_authors = fetch_google_sheet_data(author_url)

# Add a 'Quarter' column to distinguish data by quarter
df_sales_q1['Quarter'] = 'Q1'
df_sales_q2['Quarter'] = 'Q2'
df_sales_q3['Quarter'] = 'Q3'
df_sales_q4['Quarter'] = 'Q4'

# Combine all quarterly sales data into one DataFrame
df_sales = pd.concat([df_sales_q1, df_sales_q2, df_sales_q3, df_sales_q4])

# Merge sales data with edition and book details
df_merged = pd.merge(df_sales, df_edition, on='ISBN', how='inner')
df_merged = pd.merge(df_merged, df_books, on='BookID', how='inner')

# Merge author details with the combined data
df_merged = pd.merge(df_merged, df_authors, on='AuthID', how='left')

# Generate random ratings if the 'Rating' column is missing
if 'Rating' not in df_merged.columns:
    df_merged['Rating'] = np.random.randint(1, 5, size=len(df_merged))

# Calculate total sales for each book
df_merged['Total Sales'] = df_merged.groupby('Title')['OrderID'].transform('count')

# Summarize total sales and average ratings for each book
book_sales = df_merged.groupby('Title')['Total Sales'].sum().reset_index()
book_ratings = df_merged.groupby('Title')['Rating'].mean().reset_index()

# Prepare options for dropdown
books_options = []
for index, row in book_sales.iterrows():
    book_option = {'label': row['Title'], 'value': row['Title']}
    books_options.append(book_option)

# Get top 10 selling books
top_10_books = book_sales.sort_values(by='Total Sales', ascending=False).head(10)

# Create a Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([  # The root layout for the dashboard

    # Header Section with Titles
    dbc.Row([  # A Bootstrap row for the header
        dbc.Col([  # A single column that spans the entire row
            html.H1("Bookshop Dashboard", style={  # The main dashboard title
                'textAlign': 'center',  # Center-aligned text
                'marginBottom': '20px',  # Space below the title
                'fontSize': '48px',  # Font size
                'fontWeight': 'bold',  # Bold font
                'color': '#FFFFFF',  # White text color for contrast
                'fontFamily': 'Arial, sans-serif'  # Modern font style
            })
        ], width=12)  # Column spans all 12 grid spaces (full width)
    ], style={'marginBottom': '20px'}),  # Space below the header row

    # Book Selection and Author Name Section
    dbc.Row([  # A Bootstrap row containing the dropdown and author name
        # Select Book Dropdown
        dbc.Col([  # First column for the dropdown
            html.H3("Book Name", style={  # Label for the dropdown
                'textAlign': 'center',  # Center-aligned text
                'marginBottom': '15px',  # Space below the label
                'fontSize': '20px',  # Font size
                'color': 'white',  # White text for visibility
                'fontWeight': 'bold',  # Bold font
                'fontFamily': 'Arial, sans-serif'  # Font style
            }),
            dcc.Dropdown(  # Dropdown for selecting a book
                id='book-dropdown',  # Unique ID for callback functionality
                options=books_options,  # Options for the dropdown
                placeholder="Please select a book",  # Placeholder text
                style={  # Styling for the dropdown
                    'width': '100%',  # Full width
                    'fontSize': '15px',  # Font size
                    'padding': '15px',  # Padding inside the dropdown
                    'borderRadius': '8px',  # Rounded corners
                    'border': '1px solid #BDC3C7',  # Light border
                    'backgroundColor': '#ECF0F1',  # Light gray background
                    'color': 'black',  # Black text color
                    'textAlign': 'center',  # Center-aligned placeholder
                }
            ),
        ], width=6, style={'paddingLeft': '30px'}),  # Column width and left padding

        # Author Name Box
        dbc.Col([  # Second column for the author name card
            html.H3("Author Name", style={  # Label for the author name
                'textAlign': 'center',  # Center-aligned text
                'marginBottom': '15px',  # Space below the label
                'fontSize': '20px',  # Font size
                'color': 'white',  # White text for visibility
                'fontFamily': 'Arial, sans-serif'  # Font style
            }),
            dbc.Card(  # Card to display the author name
                dbc.CardBody([
                    html.Div(id='author-name', style={  # Placeholder for dynamic author name
                        'fontSize': '24px',  # Font size
                        'fontWeight': 'bold',  # Bold font
                        'padding': '15px',  # Padding inside the card
                        'border': '1px solid #BDC3C7',  # Border around the text
                        'borderRadius': '8px',  # Rounded corners
                        'backgroundColor': '#ECF0F1',  # Light background color
                        'textAlign': 'center',  # Center-aligned text
                        'color': 'black'  # Black text color
                    })
                ]),
                style={  # Styling for the card
                    'borderRadius': '8px',  # Rounded corners for the card
                    'backgroundColor': '#fff'  # White background for contrast
                }
            )
        ], width=5, style={'paddingLeft': '30px'}),  # Column width and left padding
    ], style={'marginBottom': '20px'}),  # Space between this row and the next

    # Book Output Row
    dbc.Row([  # Row to display additional book-related information
        dbc.Col(html.Div(id='book-output'), width=6, style={'padding': '10px'})
    ], style={'marginBottom': '20px'}),

    # Sales and Review Charts Row
    dbc.Row([  # Row for sales and review charts
        dbc.Col([  # First column for the sales bar chart
            dcc.Graph(
                id='sales-bar-chart',  # Unique ID for callback functionality
                config={'displayModeBar': False},  # Hide extra toolbar
                style={  # Styling for the chart
                    'height': '800px',  # Height for larger charts
                    'padding': '20px'  # Uniform padding
                }
            )
        ], width=6, style={'padding': '10px'}),  # Column width and padding
        dbc.Col([  # Second column for the review bar chart
            dcc.Graph(
                id='review-bar-chart',  # Unique ID for callback functionality
                config={'displayModeBar': False},  # Hide extra toolbar
                style={  # Styling for the chart
                    'height': '800px',  # Height for larger charts
                    'padding': '20px'  # Uniform padding
                }
            )
        ], width=6, style={'padding': '10px'})  # Column width and padding
    ], style={'marginBottom': '20px'}),

    # Sales Trend Line Chart Row
    dbc.Row([  # Row for the sales trend and top 10 books charts
        dbc.Col([  # First column for the sales trend line chart
            dcc.Graph(
                id='sales-trend-line-chart',  # Unique ID for callback functionality
                config={'displayModeBar': False},  # Hide extra toolbar
                style={  # Styling for the chart
                    'height': '800px',  # Height for larger charts
                    'padding': '20px'  # Uniform padding
                }
            )
        ], width=6, style={'padding': '20px'}),  # Column width and padding

        # Top 10 Selling Books Chart
        dbc.Col([  # Second column for the top 10 selling books bar chart
            html.H3(style={  # Placeholder for any additional heading
                'textAlign': 'center',  # Center-aligned text
                'marginBottom': '20px',  # Space below the heading
                'fontSize': '24px',  # Font size
                'fontWeight': 'bold',  # Bold font
                'color': '#2980B9',  # Blue text color
                'fontFamily': 'Arial, sans-serif'  # Font style
            }),
            dcc.Graph(
                id='top-10-books-bar-chart',  # Unique ID for callback functionality
                config={'displayModeBar': False},  # Hide extra toolbar
                style={  # Styling for the chart
                    'height': '800px',  # Height for larger charts
                    'padding': '20px'  # Uniform padding
                }
            )
        ], width=6, style={'padding': '10px'})  # Column width and padding
    ], style={'marginBottom': '20px'})

], style={'backgroundColor': '#2C3E50', 'color': '#fff'})  # Overall dashboard background and text color

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

    fig.update_layout(xaxis_tickangle=0)
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

# Run the dashboard
if __name__ == '__main__':
    app.run_server(debug=True, port=8054)