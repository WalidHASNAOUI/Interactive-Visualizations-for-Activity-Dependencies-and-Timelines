import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash.dependencies import Input, Output

# Load data
dependencies_df = pd.read_csv("./data/dependencies.csv")  # Load your CSV file

# activities_df['Start'] = pd.to_datetime(activities_df['Start'], format='%d/%m/%y' , errors='coerce')
# activities_df['End'] = pd.to_datetime(activities_df['End'], format='%d/%m/%y' , errors='coerce')
dependencies_df['Start'] = pd.to_datetime(dependencies_df['Start'],format='%d/%m/%y', errors='coerce')
dependencies_df['End'] = pd.to_datetime(dependencies_df['End'], format='%d/%m/%y', errors='coerce')

# Process the data for various components
# 1. Number of dependencies per type and status
dependency_counts = dependencies_df.groupby(['Type of dependency', 'Dependency status']).size().reset_index(name='Count')

# 2. Activities delayed due to dependencies
delayed_activities = dependencies_df[dependencies_df['Dependency status'] == 'Slowing']
delayed_activities_count = delayed_activities['Activity A'].nunique()

# 3. Unresolved issues and target dates
unresolved_issues = dependencies_df[dependencies_df['Issue target date'].notna()]

# Initialize the Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Project Management Dashboard", style={'textAlign': 'center'}),

    # Bar Chart: Number of dependencies per type and status
    dcc.Graph(
        id="dependency-chart",
        figure={
            "data": [
                go.Bar(
                    x=dependency_counts['Type of dependency'] + " - " + dependency_counts['Dependency status'],
                    y=dependency_counts['Count'],
                    name="Dependencies",
                )
            ],
            "layout": go.Layout(
                title="Number of Dependencies per Type and Status",
                xaxis={"title": "Dependency Type and Status"},
                yaxis={"title": "Count"},
                barmode='stack'
            ),
        },
    ),

    # Pie Chart: Activities delayed due to dependencies
    dcc.Graph(
        id="delayed-activities-chart",
        figure={
            "data": [
                go.Pie(
                    labels=["Delayed", "On time"],
                    values=[delayed_activities_count, len(dependencies_df) - delayed_activities_count],
                    name="Delayed Activities",
                    hole=0.3,
                ),
            ],
            "layout": go.Layout(
                title="Total Activities Delayed Due to Dependencies",
                showlegend=True
            ),
        },
    ),

    # Table: Overview of unresolved issues and their target dates
    html.Div([
        html.H3("Unresolved Issues and Target Dates", style={'textAlign': 'center'}),
        html.Table(
            # Header
            [html.Tr([html.Th(col) for col in unresolved_issues.columns])] +
            # Body
            [html.Tr([html.Td(unresolved_issues.iloc[i][col]) for col in unresolved_issues.columns]) for i in range(len(unresolved_issues))]
        ),
    ], style={'padding': '20px'}),

    # Gantt Chart: Visualizing project activities
    html.Div([
        html.H3("Gantt Chart", style={'textAlign': 'center'}),
        dcc.Graph(
            id="gantt-chart",
            figure=px.timeline(dependencies_df, x_start="Start", x_end="End", y="Activity A", title="Project Activities Gantt Chart").update_layout(
                xaxis=dict(type="date"),
            ),
        ),
    ], style={'padding': '20px'}),

    # Dependency Network Graph (Interactive Plotly Network)
    html.Div([
        html.H3("Dependency Network Graph", style={'textAlign': 'center'}),
        dcc.Graph(
            id="dependency-network",
            figure={  # Replace this with the code for the Dependency Network Graph
                "data": [  # Example plot, replace with actual network data
                    go.Scatter(x=[0, 1], y=[0, 1], mode="lines", line=dict(color='gray'))
                ],
                "layout": go.Layout(
                    title="Dependency Network Graph",
                    hovermode="closest",
                    showlegend=False,
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=False),
                ),
            },
        ),
    ], style={'padding': '20px'}),
])

if __name__ == "__main__":
    app.run_server(debug=True)
