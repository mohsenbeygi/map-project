// This program consists of these main parts:
// 1. read graph from file (parsed data from osm files)
// 2. read source and destination nodes from file
// 3. find shortest path between the nodes
// (dijkstra with STL set)
// 4. write path to file
#include <iostream>
#include <string>
#include <vector>
#include <array>
#include <list>
#include <set>
#include <iterator> 
#include <cmath>
#include <fstream>
#include <sstream>
#include <iomanip>

using namespace std;
# define INF 0x3f3f3f3f

const double EARTH_RADIUS = 6378.137;

// This class represents a directed graph using
// adjacency list representation
class Graph
{

    // In a weighted graph, we need to store vertex
    // and weight pair for every edge
    list< pair<int, int> > *adj;

public:
    // Graph(int node_count); // Constructor

    void create(int node_count);

    // function to add an edge to graph
    void addEdge(int u, int v, int w);

    // prints shortest path from s
    void shortestPath(int s, int sink, vector <int> &parents);

    // creates vector with a path from source to destination
    bool get_path(int src, int dest, vector <int> &path, vector <int> &parents);

    int node_count; // No. of vertices
};

// Allocates memory for adjacency list
void Graph::create(int node_count)
{
    this->node_count = node_count;
    adj = new list< pair<int, int> >[node_count];
}

void Graph::addEdge(int u, int v, int w)
{
    // only one way
    adj[u].push_back(make_pair(v, w));
    // adj[v].push_back(make_pair(u, w));
}

// Prints shortest paths from src to all other vertices
void Graph::shortestPath(int src, int sink, vector<int> &parents)
{
    // Create a set to store vertices that are being
    // prerocessed
    set< pair<int, int> > setds;

    // Create a vector for distances and initialize all
    // distances as infinite (INF)
    vector<int> dist(node_count, INF);

    // Insert source itself in Set and initialize its
    // distance as 0.
    setds.insert(make_pair(0, src));
    dist[src] = 0;

    /* Looping till all shortest distance are finalized
    then setds will become empty */
    while (!setds.empty())
    {
        // The first vertex in Set is the minimum distance
        // vertex, extract it from set.
        pair<int, int> tmp = *(setds.begin());
        setds.erase(setds.begin());

        // vertex label is stored in second of pair (it
        // has to be done this way to keep the vertices
        // sorted distance (distance must be first item
        // in pair)
        int u = tmp.second;

        if (u == sink){
            // cout << "\nreached destination!\n\n";
            break;
        }

        // 'i' is used to get all adjacent vertices of a vertex
        list< pair<int, int> >::iterator i;
        for (i = adj[u].begin(); i != adj[u].end(); ++i)
        {
            // Get vertex label and weight of current adjacent
            // of u.
            int v = (*i).first;
            int weight = (*i).second;

            // If there is shorter path to v through u.
            if (dist[v] > dist[u] + weight)
            {
                /*
                If distance of v is not INF then it must be in
                our set, so removing it and inserting again
                with updated less distance.
                Note : We extract only those vertices from Set
                for which distance is finalized. So for them,
                we would never reach here.
                */
                if (dist[v] != INF)
                    setds.erase(setds.find(make_pair(dist[v], v)));

                // Updating distance of v
                dist[v] = dist[u] + weight + 5;
                //number for influencing node count in path
                parents[v] = u;
                setds.insert(make_pair(dist[v], v));
            }
        }
    }
}

bool Graph::get_path(int src, int dest, vector<int> &path, vector<int> &parents){
    int last = dest;
    while (last != src) {
        path.push_back(last);
        if (parents.size() <= last)
        {
            // path between start and dest node doesn't exist
            return false;
        }
        last = parents[last];
    }
    path.push_back(src);
    return true;
}

// Utility function for converting degrees to radians
double to_radians(double degree)
{
    // cmath library in C++
    // defines the constant
    // M_PI as the value of
    // pi accurate to 1e-30
    return (((M_PI) / 180) * degree);
}

double geo_to_meter(double lat1, double long1,
                    double lat2, double long2)
{
    // Convert the latitudes
    // and longitudes
    // from degree to radians.
    lat1 = to_radians(lat1);
    long1 = to_radians(long1);
    lat2 = to_radians(lat2);
    long2 = to_radians(long2);

    // Haversine Formula
    double dlong = long2 - long1;
    double dlat = lat2 - lat1;

    double ans = pow(sin(dlat / 2), 2) +
                 cos(lat1) * cos(lat2) *
                 pow(sin(dlong / 2), 2);

    ans = 2 * asin(sqrt(ans));

    // Radius of Earth in
    // Kilometers, R = 6371
    // Use R = 3956 for miles.
    // Calculate the result:
    ans = ans * EARTH_RADIUS;

    return ans;
}

int find_closest_node(
    array <double, 2> &node_cords,
    vector < array <double, 2> > &nodes)
{
    // cout << "\n\ninside\n\n";
    double max_dis = INF;
    
    int nearest_node;

    double dis;

    for (int i = 0; i < nodes.size(); i++)
    {
        dis = geo_to_meter(node_cords[0], node_cords[1], nodes[i][0], nodes[i][1]);
        if (dis < max_dis)
        {
            max_dis = dis;
            nearest_node = i;
            // cout << "new nearest node!  " << nearest_node << "  dis: " << max_dis << "\n";
        }
    }
    // cout << "\ndone\n";
    return nearest_node;
}

void get_graph(
    ifstream &graph_file,
    Graph &graph,
    vector < array <double, 2> > &nodes)
{
    // for adding edge to graph
    int node1, node2, weight;

    // for knowing node count of graph
    int node_count;

    // for holding cordinations
    array <double, 2> node_cords;

    // for reading cordinations of nodes in the graph
    int node;

    // for reading from files
    stringstream ss;
    string line;

    // read graph from graph_file
    if (graph_file.is_open())
    {

        cout << "reading graph file\n";

        // read nodes count of graph
        getline(graph_file, line);
        ss << line;
        ss >> node_count;

        // create graph
        graph.create(node_count);

        // read graph data
        while ( getline(graph_file, line) )
        {
            // stop reading graph data when we reach cordinations
            if (line == "cords") {
                break;
            }
            // erase stringstream's contents (.clear() is for erasing errors)
            ss.str(string());
            ss.clear();
            ss << line;
            ss >> node1 >> node2 >> weight;

            // add edge
            graph.addEdge(node1, node2, weight);
        }

        // read corndinations of nodes in the graph
        while ( getline(graph_file, line) )
        {
            // erase stringstream's contents (.clear() is for erasing errors)
            ss.str(string());
            ss.clear();
            ss << line;
            ss >> node >> node_cords[0] >> node_cords[1];
            // add node cordinations to nodes vector
            nodes.push_back(node_cords);
        }

        // reading graph data is done
        graph_file.close();
        cout << "reading graph_file done\n";
    }

    else
    {
        cout << "Unable to open graph_file";
        return 0;
    }
}

void get_nodes(
    ifstream &node_input,
    vector < array <double, 2> > &nodes,
    int* start,
    int* dest)
{

    // for holding cordinations
    array <double, 2> node_cords;

    // for reading from files
    stringstream ss;
    string line;
    
    // read source and destination cords from node_input file
    if (node_input.is_open())
    {
        cout << "reading node_input\n";
        // source

        // erase stringstream's contents (.clear() is for erasing errors)
        ss.str(string());
        ss.clear();
        getline(node_input, line);
        ss << line;
        ss >> node_cords[0] >> node_cords[1];
        *start = find_closest_node(node_cords, nodes);
        cout << "start: " << *start << " | " << node_cords[0] << ", " << node_cords[1] << "\n";

        // destination

        // erase stringstream's contents (.clear() is for erasing errors)
        ss.str(string());
        ss.clear();
        getline(node_input, line);
        ss << line;
        ss >> node_cords[0] >> node_cords[1];
        *dest = find_closest_node(node_cords, nodes);
        cout << "dest: " << *dest << " | " << node_cords[0] << ", " << node_cords[1] << "\n";

        // reading cordinations is done
        node_input.close();
        cout << "reading node_input done\n";
    }
    else
    {
        cout << "Unable to open node_input";
        return 0;
    }
}

void write_path(
    ofstream &path_file,
    vector<int> &path,
    vector < array <double, 2> > &nodes)
{

    // write path to file
    if (path_file.is_open())
    {
        cout << "writing path to path_file\n";
        for (int i = 0; i < path.size(); ++i){
            path_file << setprecision(10) << nodes[path[i]][0] <<
            " " << setprecision(10) << nodes[path[i]][1] << "\n";
        }

        // writing is done
        path_file.close();
        cout << "writing path done\n";
    }

    else
    {
        cout << "Unable to open path_file";
        return 0;
    }
}

// driver
int main()
{
    // for finding closest nodes in the
    // graph from start and destination spots
    int* start;
    int* dest;

    // for holding cordinations of all nodes in the graph
    vector < array <double, 2> > nodes;

    // for getting path
    vector<int> path;

    Graph graph;

    // get file directory paths from input
    string graph_data_file, nodes_file, path_file_path;
    getline(cin, graph_data_file);
    getline(cin, nodes_file);
    getline(cin, path_file_path);

    // files to read from
    ifstream graph_file (graph_data_file);
    ifstream node_input (nodes_file);
    ofstream path_file(path_file_path);

    get_graph(graph_file, graph, nodes);

    get_nodes(node_input, nodes, start, dest);

    cout << "starting pathfinding\n";

    // find path between start and destination nodes

    // for holding parent of each node
    vector<int> parents(graph.node_count, INF);

    graph.shortestPath(*start, *dest, parents);
    cout << "pathfinding done\n";

    cout << "getting path\n";
    if (!graph.get_path(*start, *dest, path, parents))
    {
        cout << "couldn't find path\n";
        return 0;
    }
    cout << "getting path done\n";

    write_path(path_file, path, nodes);

    return 0;
}
