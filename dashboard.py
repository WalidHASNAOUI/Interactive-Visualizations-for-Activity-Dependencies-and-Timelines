from dash import Dash, html, dcc, Input, Output, State
import plotly.express as px
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from sklearn.cluster import SpectralClustering  # For Spectral Clustering

# Initialize the Dash app
app = Dash(__name__)

# Load the cleaned data from the CSV file
updated_dependencies_data = pd.read_csv('Updated_Dependencies_Data.csv')

# Create bar chart
dependency_counts = updated_dependencies_data.groupby(['Type of dependency', 'Dependency status']).size().reset_index(name='Count')
bar_chart = px.bar(
    dependency_counts,
    x='Type of dependency',
    y='Count',
    color='Dependency status',
    barmode='group',
    title="Dependencies per Type and Status"
)
bar_chart.update_layout(
    plot_bgcolor="#1e1e2f",
    paper_bgcolor="#1e1e2f",
    font=dict(color="#cfd4da")
)

# Create pie chart
delayed_activities = updated_dependencies_data[updated_dependencies_data['Dependency status'].isin(['Slowing', 'Blocking'])]
delayed_counts = delayed_activities['Dependency status'].value_counts().reset_index()
delayed_counts.columns = ['Status', 'Count']
pie_chart = px.pie(
    delayed_counts,
    names='Status',
    values='Count',
    title="Activities Delayed Due to Dependencies",
    hole=0.4
)
pie_chart.update_layout(
    plot_bgcolor="#1e1e2f",
    paper_bgcolor="#1e1e2f",
    font=dict(color="#cfd4da")
)

# Prepare table for unresolved issues
unresolved_issues = updated_dependencies_data[updated_dependencies_data['Dependency status'].isin(['Slowing', 'Blocking'])][['Activity A', 'Comment', 'Issue target date']]
unresolved_issues_table = html.Table([
    html.Thead(
        html.Tr([html.Th(col, style={"borderBottom": "2px solid white", "padding": "10px", "textAlign": "left"}) for col in unresolved_issues.columns])
    ),
    html.Tbody([
        html.Tr([
            html.Td(row[col], style={"borderBottom": "1px solid gray", "padding": "10px", "textAlign": "left"}) for col in unresolved_issues.columns
        ]) for _, row in unresolved_issues.iterrows()
    ])
], style={"width": "100%", "borderCollapse": "collapse", "backgroundColor": "#2a2a40", "color": "#cfd4da", "borderRadius": "8px", "overflow": "hidden"})

# Create network graph
G = nx.DiGraph()
for _, row in updated_dependencies_data.iterrows():
    G.add_edge(row['Activity A'], row['Activity B'], type=row['Type of dependency'], status=row['Dependency status'])

# Perform Spectral Clustering
nodes = list(G.nodes)
adjacency_matrix = nx.to_numpy_array(G, nodelist=nodes)
spectral = SpectralClustering(n_clusters=4, affinity='precomputed', random_state=42)
clusters = spectral.fit_predict(adjacency_matrix)

# Assign positions and colors based on clusters
pos = nx.spring_layout(G, seed=42)
cluster_colors = px.colors.qualitative.Set3
node_cluster_map = dict(zip(nodes, clusters))

# Extract edge attributes
types = nx.get_edge_attributes(G, 'type')
statuses = nx.get_edge_attributes(G, 'status')

# Create node trace
x_nodes = []
y_nodes = []
node_sizes = []
node_colors = []
node_hover_text = []

max_degree = max(dict(G.degree()).values())

for node in G.nodes:
    x_nodes.append(pos[node][0])
    y_nodes.append(pos[node][1])
    degree = G.degree(node)
    normalized_size = 10 + (degree / max_degree) * 20  # Normalize node sizes
    node_sizes.append(normalized_size)
    node_colors.append(cluster_colors[node_cluster_map[node] % len(cluster_colors)])
    node_hover_text.append(f"Node: {node}\nConnections: {degree}\nCluster: {node_cluster_map[node]}")

# Create edge traces for each status
edge_traces = []

for edge_status, color in [('No problem', 'green'), ('Slowing', 'orange'), ('Blocking', 'red')]:
    x_edges = []
    y_edges = []

    for edge in G.edges:
        if statuses.get(edge, 'No problem') == edge_status:
            x_edges.extend([pos[edge[0]][0], pos[edge[1]][0], None])
            y_edges.extend([pos[edge[0]][1], pos[edge[1]][1], None])

    edge_traces.append(go.Scatter(
        x=x_edges,
        y=y_edges,
        mode='lines',
        line=dict(width=1.5, color=color),
        hoverinfo='none'
    ))

network_graph = go.Figure()

# Add edge traces to the network graph
for trace in edge_traces:
    network_graph.add_trace(trace)

# Add nodes
network_graph.add_trace(go.Scatter(
    x=x_nodes,
    y=y_nodes,
    mode='markers+text',
    text=list(G.nodes),
    textposition="top center",
    marker=dict(size=node_sizes, color=node_colors, line=dict(width=2, color='black')),
    hoverinfo='text',
    textfont=dict(size=10),
    hovertext=node_hover_text
))

network_graph.update_layout(
    title="Dependency Network Graph with Spectral Clustering",
    showlegend=False,
    margin=dict(l=40, r=40, t=40, b=40),
    height=700,
    plot_bgcolor="#1e1e2f",
    paper_bgcolor="#1e1e2f",
    font=dict(color="#cfd4da"),
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=False)
)

# App layout with navigation
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),

    # Sidebar with collapsible sections using Dash callbacks
    html.Div([
        html.H2("Project Dashboard", className="sidebar-title"),

        html.Div([
            html.Button("General", id="general-toggle", n_clicks=0, className="collapsible"),
            html.Div([
                dcc.Link("Health", href="/health", className="sidebar-link"),
                dcc.Link("Tasks", href="/tasks", className="sidebar-link"),
                dcc.Link("Progress", href="/progress", className="sidebar-link")
            ], id="general-content", style={"display": "none"})
        ]),

        html.Div([
            html.Button("Time & Cost", id="time-cost-toggle", n_clicks=0, className="collapsible"),
            html.Div([
                dcc.Link("Time", href="/time", className="sidebar-link"),
                dcc.Link("Cost", href="/cost", className="sidebar-link")
            ], id="time-cost-content", style={"display": "none"})
        ]),

        html.Div([
            html.Button("Workload & Network", id="workload-network-toggle", n_clicks=0, className="collapsible"),
            html.Div([
                dcc.Link("Workload", href="/workload", className="sidebar-link"),
                dcc.Link("Dependency Network Graph", href="/dependency-network", className="sidebar-link")
            ], id="workload-network-content", style={"display": "none"})
        ])
    ], className="sidebar"),

    # Main content
    html.Div(id='page-content', className="main-content")
])

# Callback to toggle collapsible sections
@app.callback(
    [Output("general-content", "style"),
     Output("time-cost-content", "style"),
     Output("workload-network-content", "style")],
    [Input("general-toggle", "n_clicks"),
     Input("time-cost-toggle", "n_clicks"),
     Input("workload-network-toggle", "n_clicks")]
)
def toggle_sections(general_clicks, time_cost_clicks, workload_network_clicks):
    general_style = {"display": "block"} if general_clicks % 2 == 1 else {"display": "none"}
    time_cost_style = {"display": "block"} if time_cost_clicks % 2 == 1 else {"display": "none"}
    workload_network_style = {"display": "block"} if workload_network_clicks % 2 == 1 else {"display": "none"}
    return general_style, time_cost_style, workload_network_style

# Callback to render content based on URL
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/dependency-network':
        return html.Div([
            html.H2("Dependency Network Graph"),
            dcc.Graph(id='network-graph', figure=network_graph)
        ], className="network-section")
    else:
        return html.Div([
            html.Div([
                html.Div([html.H3("Time"), html.P("14% ahead of schedule.")], className="card"),
                html.Div([html.H3("Tasks"), html.P("12 tasks to be completed.")], className="card"),
                html.Div([html.H3("Workload"), html.P("0 tasks overdue.")], className="card"),
                html.Div([html.H3("Progress"), html.P("14% complete.")], className="card"),
                html.Div([html.H3("Cost"), html.P("42% under budget.")], className="card")
            ], className="summary-cards-redesigned"),

            html.Div([
                html.Div([
                    html.H2("Dependencies per Type and Status"),
                    dcc.Graph(id='bar-chart', figure=bar_chart)
                ], className="chart"),
                html.Div([
                    html.H2("Activities Delayed Due to Dependencies"),
                    dcc.Graph(id='pie-chart', figure=pie_chart)
                ], className="chart"),
            ], className="charts"),

            html.Div([
                html.Div([
                    html.H2("Unresolved Issues Overview"),
                    unresolved_issues_table
                ], className="table")
            ], className="details")
        ])

# Add CSS styles
app.index_string = '''
<!DOCTYPE html>
<html>
<head>
    <title>Project Management Dashboard</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background-color: #1e1e2f;
            color: #cfd4da;
            height: 100vh;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        .dashboard {
            display: flex;
            height: 100vh;
        }
        .sidebar {
            width: 15%;
            background-color: #2a2a40;
            padding: 20px;
            height: 100vh;
            position: fixed;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            align-items: flex-start;
        }
        .sidebar-title {
            color: #ffffff;
            margin-bottom: 20px;
        }
        .collapsible {
            background-color: #2a2a40;
            color: #cfd4da;
            cursor: pointer;
            padding: 10px 15px;
            text-align: left;
            width: 100%;
            border: none;
            outline: none;
            font-size: 15px;
            margin-bottom: 5px;
            border-radius: 5px;
        }
        .collapsible:hover {
            background-color: #4caf50;
            color: #ffffff;
        }
        .sidebar-link {
            display: block;
            width: 100%;
            padding: 10px 15px;
            color: #cfd4da;
            text-decoration: none;
            border-radius: 5px;
            margin-bottom: 5px;
            text-align: left;
        }
        .sidebar-link.active {
            background-color: #4caf50;
            color: #ffffff;
        }
        .sidebar-link:hover {
            background-color: #4caf50;
            color: #ffffff;
        }
        .main-content {
            margin-left: 15%;
            padding: 20px;
            width: 85%;
            height: 100vh;
            overflow-y: auto;
        }
        .summary-cards-redesigned {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background-color: #2a2a40;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            transition: transform 0.3s ease;
        }
        .card:hover {
            transform: translateY(-10px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
        }
        .card h3 {
            color: #ffffff;
            margin-bottom: 10px;
            font-size: 1.5em;
        }
        .card p {
            color: #a0a3ab;
            font-size: 1em;
        }
        .charts {
            display: flex;
            justify-content: space-around;
            margin-bottom: 20px;
        }
        .chart, .table, .network-section {
            background-color: #2a2a40;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .details {
            display: flex;
            justify-content: space-around;
        }
    </style>
</head>
<body>
    {%app_entry%}
    <footer>
        {%config%}
        {%scripts%}
        {%renderer%}
    </footer>
</body>
</html>
'''

if __name__ == '__main__':
    app.run_server(debug=True)
