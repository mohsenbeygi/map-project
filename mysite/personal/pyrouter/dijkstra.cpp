// Program to find Dijkstra's shortest path using STL set
#include <bits/stdc++.h>
using namespace std;
# define INF 0x3f3f3f3f

// This class represents a directed graph using
// adjacency list representation
class Graph
{
    int node_count; // No. of vertices

    // In a weighted graph, we need to store vertex
    // and weight pair for every edge
    list< pair<int, int> > *adj;

public:
    Graph(int node_count); // Constructor

    // function to add an edge to graph
    void addEdge(int u, int v, int w);

    // prints shortest path from s
    void shortestPath(int s, int sink, vector <int> &parents);

    // creates vector with a path from source to destination
    void get_path(int src, int dest, vector <int> &path, vector <int> &parents);
};

// Allocates memory for adjacency list
Graph::Graph(int node_count)
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

    // Print shortest distances stored in dist[]
    // printf("Vertex Distance from Source\n");
    // for (int i = 0; i < node_count; ++i)
    //     printf("%d \t\t %d\n", i, dist[i]);
}

void Graph::get_path(int src, int dest, vector<int> &path, vector<int> &parents){
    int last = dest;
    // cout << "dest: " << dest;
    // cout << "src: " << src;
    while (last != src) {
        // cout << "last: " << last;
        path.push_back(last);
        last = parents[last];
    }
    path.push_back(src);
}

// Driver program to test methods of graph class
int main()
{

    int node1, node2, weight, node_count, start, dest;

    vector<int> path;

    stringstream ss;
    string line, graph_data_file, nodes_file, path_file_path;

    getline(cin, graph_data_file);
    getline(cin, nodes_file);
    getline(cin, path_file_path);

    ifstream graph_file (graph_data_file);
    ifstream node_input (nodes_file);


    if (graph_file.is_open())
    {
        // read number of nodes
        getline(graph_file, line);
        ss << line;
        ss >> node_count;

        // create graph
        Graph g(node_count);


        while ( getline(graph_file, line) )
        {
            stringstream ss;
            ss << line;
            ss >> node1 >> node2 >> weight;

            // cout << "nums: " << node1 << ", "
            // << node2 << ", " << weight << "\n";

            // add edge
            g.addEdge(node1, node2, weight);

        }

        // source
        stringstream ss;
        getline(node_input, line);
        ss << line;
        ss >> start;
        // destination
        ss.str("");
        ss.clear();
        getline(node_input, line);
        ss << line;
        ss >> dest;

        graph_file.close();

        vector<int> parents(node_count, INF);
        // vector<int> path;


        g.shortestPath(start, dest, parents);
        // cout << dest << " " << start << "\n";
        g.get_path(start, dest, path, parents);
        // // print path
        // cout << endl;
        // for (int i = 0; i < path.size(); ++i){
        //     cout << path[i] << " ";
        // }

    }

    else cout << "Unable to open file";


    ofstream path_file;
    path_file.open(path_file_path);
    // write path to file

    for (int i = 0; i < path.size(); ++i){
        path_file << path[i] << " ";
    }

    path_file.close();

    return 0;
}
