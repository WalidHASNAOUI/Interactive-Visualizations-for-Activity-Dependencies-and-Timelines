# Project Management Dashboard

## Overview

The **Project Management Dashboard** is an interactive web-based application designed to help project managers efficiently monitor and manage tasks, dependencies, and workload. It provides visual insights into project progress, unresolved issues, dependency networks, and workload distribution using intuitive graphs and tables. The dashboard is built using Python, Dash, and Plotly, with a focus on usability and customization.

---

## Features

### 1. **General Overview**
- **Dynamic Summary Cards:** Real-time metrics on project time, tasks, workload, progress, and cost savings.
- **Dependency Insights:** Bar and pie charts illustrating dependencies by type and status.
- **Unresolved Issues Table:** A detailed table highlighting unresolved issues, their comments, and issue target dates.

### 2. **Workload Section**
- **Workload Distribution:** Bar chart showing tasks categorized by dependency status (e.g., No Problem, Slowing, Blocking).
- **Overdue Activities:** Donut chart highlighting overdue activities by dependency status.
- **Workload Over Time:** Line chart representing workload trends over time.
- **High Dependency Activities:** A table displaying activities with a high number of dependencies.

### 3. **Network Graph**
- **Dependency Network Visualization:** Spectral clustering to identify clusters in dependency networks.
- **Filters:** Filter the network graph by dependency type and status.
- **Customizable Nodes and Edges:** Node size and color indicate activity type and connections, while edge colors represent dependency status.

---

## Installation

### Prerequisites
- Python 3.9+
- `pip` package manager

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/project-management-dashboard.git
   cd project-management-dashboard
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Place your CSV data file (`Updated_Dependencies_Data.csv`) in the root directory.

4. Run the application:
   ```bash
   python dashboard.py
   ```

5. Open your browser and navigate to:
   ```
   http://127.0.0.1:8050/
   ```

---

## File Structure
```plaintext
project-management-dashboard/
├── dashboard.py        # Main script for the dashboard
├── Updated_Dependencies_Data.csv  # Data file
├── README.md           # Project documentation
├── ...
```

---

## Usage

1. **General Section**
   - Monitor high-level project metrics using the dynamic summary cards.
   - Visualize dependencies and delayed activities through interactive charts.

2. **Workload Section**
   - Analyze task distribution and trends over time.
   - Identify critical tasks with the highest dependencies.

3. **Network Graph Section**
   - Navigate and filter the dependency network to gain insights into task relationships and bottlenecks.

---

## Technologies Used

- **Dash**: For building the interactive dashboard.
- **Plotly**: For creating charts and network graphs.
- **NetworkX**: For dependency graph construction and manipulation.
- **Spectral Clustering**: For clustering tasks in the dependency network.
- **CSS**: For enhancing the dashboard’s UI/UX.

---

## Future Enhancements

- Add authentication and role-based access control.
- Integrate with live project management tools (e.g., Jira, Trello).
- Add advanced analytics, such as critical path calculation and risk assessment.

---

## Authors

- **Walid Hasnaoui**
- **Ayoub Zohri**
- **Ibtissam Dahmane**

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---



