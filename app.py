import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import pandas as pd

# Create a Dash application
app = dash.Dash(__name__)

train_df = pd.read_csv("data/raw/train.csv")
train_df[["Deck", "Cabin_num", "Side"]] = (
    train_df["Cabin"].str.split("/", expand=True).values
)

# Concatenate Deck and Side names
train_df["Deck_Side"] = "Deck " + train_df["Deck"] + " Side " + train_df["Side"]
train_df = train_df.sort_values(by=["Deck_Side"], ascending=True)
train_df[['VIP', 'Transported', 'CryoSleep']] = train_df[['VIP', 'Transported', 'CryoSleep']].astype(str)

# Define the layout of the application
app.layout = html.Div(
    children=[
        html.H1("Spaceship Titanic Passenger Location"),
        html.Div(
            className="container",
            children=[
                html.Div(
                    className="graph-container",
                    style={"width": "70%", "display": "inline-block", "vertical-align": "top"},
                    children=[
                        dcc.Graph(
                            id="passenger-location",
                            figure={
                                "data": [
                                    {
                                        "x": train_df["Cabin_num"],
                                        "y": train_df["Deck_Side"],
                                        "mode": "markers",
                                        "marker": {
                                            "size": 10,
                                            "color": train_df["Transported"].map({'False': "lightgray", 'True': "red"}),
                                            "opacity": 0.7,
                                        },
                                        "text": train_df["PassengerId"],
                                        "hovertemplate": "Passenger: %{text}<br>"
                                        + "Deck and Side: %{y}<br>"
                                        + "Cabin number: %{x}<br>"
                                        + "Transported: %{marker.color}",
                                    }
                                ],
                                "layout": {
                                    "title": "Passenger Location During Transportation Anomaly",
                                    "yaxis": {
                                        "autorange": "reversed",
                                        "ticktext": ["A", "B", "C", "D", "E", "F"],
                                    },
                                    "xaxis": {"title": "Cabin Number"},
                                    "hovermode": "closest",
                                    "height": 600,  # Adjust the height as per your requirement
                                },
                            },
                        ),
                    ],
                ),
                html.Div(
                    className="widget-container",
                    style={"width": "30%", "display": "inline-block", "vertical-align": "top"},
                    children=[
                        html.H2("Passenger Information"),
                        html.Label("Deck:"),
                        dcc.Dropdown(
                            id="deck-dropdown",
                            options=[
                                {"label": str(deck), "value": str(deck)} for deck in train_df["Deck"].unique()
                            ],
                            value=None,
                            multi=False,
                        ),
                        html.Label("Cabin Number:"),
                        dcc.Dropdown(
                            id="cabin-dropdown",
                            options=[
                                {"label": str(cabin), "value": str(cabin)} for cabin in sorted(train_df["Cabin_num"].unique(), key=lambda x: float(x))
                            ],
                            value=None,
                            multi=False,
                        ),
                        html.Label("Side:"),
                        dcc.Dropdown(
                            id="side-dropdown",
                            options=[
                                {"label": str(side), "value": str(side)} for side in train_df["Side"].unique()
                            ],
                            value=None,
                            multi=False,
                        ),
                        html.Div(
                            className="search-field",
                            children=[
                                dcc.Input(
                                    id="search-input",
                                    type="text",
                                    placeholder="Enter Passenger ID or Name",
                                    debounce=True,
                                ),
                                html.Button("Search", id="search-button"),
                            ],
                        ),
                        html.Div(id="passenger-info"),
                    ],
                ),
            ],
        ),
    ],
)


@app.callback(
    Output("passenger-info", "children"),
    [
        Input("deck-dropdown", "value"),
        Input("cabin-dropdown", "value"),
        Input("side-dropdown", "value"),
        Input("search-button", "n_clicks"),
        State("search-input", "value"),
    ],
)
def update_passenger_info(deck_value, cabin_value, side_value, n_clicks, search_value):
    filtered_df = None
    if deck_value is not None and cabin_value is not None and side_value is not None:
        filtered_df = train_df[
            (train_df["Deck"] == deck_value)
            & (train_df["Cabin_num"] == cabin_value)
            & (train_df["Side"] == side_value)
        ]
    elif n_clicks is not None and n_clicks == 0 and search_value is not None and search_value == "":
        # Perform the search based on Passenger ID or Name
        filtered_df = train_df[train_df["PassengerId"] == search_value]
        if filtered_df.empty:
            filtered_df = train_df[train_df["Name"].str.contains(search_value, case=False, regex=False)]
    else:
        return html.P("No matching passenger found.")

    passenger_info = filtered_df.iloc[0].to_frame().reset_index()
    passenger_info.columns = ["Feature", "Value"]
    passenger_info_table = html.Table(
        [
            html.Tr([html.Th("Feature"), html.Th("Value")]),
            *[
                html.Tr([html.Td(row["Feature"]), html.Td(row["Value"])])
                for _, row in passenger_info.iterrows()
            ],
        ]
    )

    return passenger_info_table

# Run the Dash application
if __name__ == "__main__":
    app.run_server(debug=True)
