import requests
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd

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

# Google Sheets URL for Book data (Ensure this URL is correct)
book_url = "https://sheets.googleapis.com/v4/spreadsheets/1d974FnqiPtsTgekWMJBuD8mkeN0v7xo2MpBUhd_CNKw/values/Book!A1:C59?key=AIzaSyA2tl9b-0I65tDVOmMMwnax45raYyk4Q0s"
author_url = "https://sheets.googleapis.com/v4/spreadsheets/1d974FnqiPtsTgekWMJBuD8mkeN0v7xo2MpBUhd_CNKw/values/Author!A1:F42?key=AIzaSyA2tl9b-0I65tDVOmMMwnax45raYyk4Q0s"

# Fetch the data
df_books = fetch_google_sheet_data(book_url)
df_author = fetch_google_sheet_data(author_url)

# Extract BookID and Book Name (assuming columns in your sheet are "BookID" and "Book Name")
# Ensure the columns exist in your sheet
# Initialize an empty list to store book options
books_options = []

# Iterate through each row in the dataframe
for index, row in df_books.iterrows():
    # Create a dictionary for each book with 'label' and 'value'
    book_option = {
        'label': row['Title'],  # Book title as the label
        'value': row['BookID']  # BookID as the value
    }

    # Append the book option to the books_options list
    books_options.append(book_option)

# Create a Dash app
app = dash.Dash(__name__)

# Layout of the app
app.layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.H3("Select a Book"),
            dcc.Dropdown(
                id='book-dropdown',
                options=books_options,
                value=books_options[0]['value'],  # Default value
                placeholder="Select a Book"
            ),
        ], width=6)
    ]),
    # Add the Output component for displaying the selected book
    html.Div(id='book-output')
])

# Callback to update the content based on the selected book
@app.callback(
    Output('book-output', 'children'),
    Input('book-dropdown', 'value')
)
def update_output(value):
    return f'You have selected Book ID: {value}'



if __name__ == '__main__':
