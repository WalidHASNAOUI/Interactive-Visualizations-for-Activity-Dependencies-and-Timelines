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

# Calculate dynamic metrics for summary cards
total_tasks = updated_dependencies_data['Activity A'].nunique()
total_dependencies = len(updated_dependencies_data)
overdue_dependencies = len(updated_dependencies_data[updated_dependencies_data['Dependency status'] == 'Blocking'])
progress_percentage = round((total_tasks - overdue_dependencies) / total_tasks * 100, 2) if total_tasks > 0 else 0
cost_saving_percentage = 42  # Placeholder value for demonstration

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

# Create workload section
# Workload bar chart
activity_status = updated_dependencies_data['Dependency status'].value_counts().reset_index()
activity_status.columns = ['Status', 'Count']
workload_status_chart = px.bar(
    activity_status,
    x='Status',
    y='Count',
    title="Workload Distribution by Status",
    color='Status',
    color_discrete_map={
        'No problem': 'green',
        'Slowing': 'orange',
        'Blocking': 'red'
    }
)
workload_status_chart.update_layout(
    plot_bgcolor="#1e1e2f",
    paper_bgcolor="#1e1e2f",
    font=dict(color="#cfd4da")
)

# Workload pie chart
overdue_activities = updated_dependencies_data[
    updated_dependencies_data['Dependency status'].isin(['Slowing', 'Blocking'])
]
overdue_pie_chart = px.pie(
    overdue_activities,
    names='Dependency status',
    title="Overdue Activities by Dependency Status",
    hole=0.4
)
overdue_pie_chart.update_layout(
    plot_bgcolor="#1e1e2f",
    paper_bgcolor="#1e1e2f",
    font=dict(color="#cfd4da")
)

# Workload over time
workload_over_time = updated_dependencies_data.groupby('Start').size().reset_index(name='Count')
workload_time_chart = px.line(
    workload_over_time,
    x='Start',
    y='Count',
    title="Workload Over Time"
)
workload_time_chart.update_layout(
    plot_bgcolor="#1e1e2f",
    paper_bgcolor="#1e1e2f",
    font=dict(color="#cfd4da")
)

# High dependency activities
dependency_counts = updated_dependencies_data.groupby('Activity A').size().reset_index(name='Dependency Count')
high_dependency_activities = dependency_counts[dependency_counts['Dependency Count'] > 3]
high_dependency_table = html.Table([
    html.Thead(html.Tr([html.Th(col) for col in high_dependency_activities.columns])),
    html.Tbody([
        html.Tr([html.Td(row[col]) for col in high_dependency_activities.columns])
        for _, row in high_dependency_activities.iterrows()
    ])
])

workload_content = html.Div([
    html.H2("Workload Overview", style={"textAlign": "center", "color": "#ffffff"}),
    html.Div([
        html.Div([
            dcc.Graph(figure=workload_status_chart)
        ], className="chart-item-half"),
        html.Div([
            dcc.Graph(figure=overdue_pie_chart)
        ], className="chart-item-half"),
    ], className="chart-row"),
    html.Div([
        html.Div([
            dcc.Graph(figure=workload_time_chart)
        ], className="chart-item-half"),
        html.Div([
            html.H2("High Dependency Activities", style={"textAlign": "center", "color": "#ffffff"}),
            html.Div(high_dependency_table, className="dependency-table-container")
        ], className="chart-item-half"),
    ], className="chart-row")
], className="workload-section")

# Create network graph
G = nx.DiGraph()
for _, row in updated_dependencies_data.iterrows():
    G.add_edge(row['Activity A'], row['Activity B'], type=row['Type of dependency'], status=row['Dependency status'])

# Convert directed graph to undirected
undirected_G = G.to_undirected()

# Extract the largest connected component
largest_cc = max(nx.connected_components(undirected_G), key=len)
subgraph = undirected_G.subgraph(largest_cc)

# Create the adjacency matrix
adjacency_matrix = nx.to_numpy_array(subgraph, nodelist=list(subgraph.nodes))

# Perform spectral clustering
spectral = SpectralClustering(n_clusters=4, affinity='precomputed', random_state=42)
clusters = spectral.fit_predict(adjacency_matrix)

# Map clusters back to the original nodes
node_cluster_map = {node: clusters[i] for i, node in enumerate(subgraph.nodes)}

# For nodes not in the largest connected component, assign a default cluster
for node in G.nodes:
    if node not in node_cluster_map:
        node_cluster_map[node] = -1  # Use -1 to indicate disconnected nodes

# Assign positions and colors based on clusters
pos = nx.spring_layout(G, seed=42)
cluster_colors = px.colors.qualitative.Set3

# Extract edge attributes
types = nx.get_edge_attributes(G, 'type')
statuses = nx.get_edge_attributes(G, 'status')

# Define color mappings for node types and edge statuses
type_color_map = {
    'Finish-to-Start': 'blue',
    'Start-to-Start': 'orange',
    'Finish-to-Finish': 'purple'
}
status_color_map = {
    'No problem': 'green',
    'Slowing': 'orange',
    'Blocking': 'red'
}

# Truncate long labels
def truncate_label(label, max_length=20):
    if isinstance(label, str):
        return label if len(label) <= max_length else label[:max_length] + "..."
    return str(label)  # Convert non-string labels to strings

# Create node trace
x_nodes = []
y_nodes = []
node_sizes = []
node_colors = []
node_hover_text = []
node_text_labels = []

max_degree = max(dict(G.degree()).values())

for node in G.nodes:
    x_nodes.append(pos[node][0])
    y_nodes.append(pos[node][1])
    degree = G.degree(node)
    normalized_size = 10 + (degree / max_degree) * 20  # Normalize node sizes
    node_sizes.append(normalized_size)

    # Determine the type of the node
    outgoing_edges = list(G.out_edges(node, data=True))
    if outgoing_edges:
        node_type = outgoing_edges[0][2].get('type', 'Other')
    else:
        node_type = 'Other'  # Default type for nodes without outgoing edges

    # Map the type to the color
    node_colors.append(type_color_map.get(node_type, 'gray'))
    node_hover_text.append(f"Node: {node}\nConnections: {degree}\nType: {node_type}")
    node_text_labels.append(truncate_label(node))

# Create edge traces for each status
edge_traces = []

for edge_status, color in status_color_map.items():
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
        hoverinfo='none',
        showlegend=False
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
    text=node_text_labels,
    textposition="top center",
    marker=dict(size=node_sizes, color=node_colors, line=dict(width=2, color='black')),
    hoverinfo='text',
    textfont=dict(size=10),
    hovertext=node_hover_text
))

# Add a legend for node types and edge statuses
legend_items = [
    go.Scatter(
        x=[None], y=[None], mode='markers',
        marker=dict(size=10, color=color),
        name=f'Node Type: {node_type}'
    )
    for node_type, color in type_color_map.items()
] + [
    go.Scatter(
        x=[None], y=[None], mode='lines',
        line=dict(color=color, width=2),
        name=f'Edge Status: {status}'
    )
    for status, color in status_color_map.items()
]

for item in legend_items:
    network_graph.add_trace(item)

network_graph.update_layout(
    title="Dependency Network Graph with Spectral Clustering",
    showlegend=True,
    legend=dict(title="Legend", orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
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
            dcc.Link("General", href="/general", className="sidebar-link"),
            dcc.Link("Workload", href="/workload", className="sidebar-link"),
            dcc.Link("Network Graph", href="/dependency-network", className="sidebar-link")
        ])
    ], className="sidebar"),

    # Main content
    html.Div(id='page-content', className="main-content")
])

# Callback to render content based on URL
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/workload':
        return workload_content
    elif pathname == '/dependency-network':
        return html.Div([
            html.H2("Dependency Network Graph"),
            dcc.Graph(id='network-graph', figure=network_graph)
        ], className="network-section")
    else:
        return html.Div([
            html.Div([
                html.Div([html.H3("Time"), html.P(f"{progress_percentage}% ahead of schedule.")], className="card"),
                html.Div([html.H3("Tasks"), html.P(f"{total_tasks} tasks to be completed.")], className="card"),
                html.Div([html.H3("Workload"), html.P(f"{overdue_dependencies} tasks overdue.")], className="card"),
                html.Div([html.H3("Progress"), html.P(f"{progress_percentage}% complete.")], className="card"),
                html.Div([html.H3("Cost"), html.P(f"{cost_saving_percentage}% under budget.")], className="card")
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
    <link rel="stylesheet" type="text/css" href="/assets/styles.css">
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
