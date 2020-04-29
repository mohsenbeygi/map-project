// This program reads osm file (like a xml file)
// and extracts a graph made up of the map's roads
#include <iostream>
#include <string>
#include <map>
#include <vector>
#include <fstream>
#include <cmath>
#include <iomanip>
#include "pugixml.cpp"

using namespace std;
using namespace pugi;

const string CAR_HIGHWAY[16] = 
{"motorway", "trunk", "primary", "secondary", "tertiary", 
"unclassified", "minor", "residential", "service", "primary_link",
"trunk_link", "secondary_link", "tertiary", "tertiary_link",
"driveway", "track"};

const double CAR_HIGHWAY_WEIGHT[16] = 
{1, 1, 8.5, 8.5, 9, 9, 9, 9.5, 9, 8.5, 8.5, 8.5, 8.5, 8.5, 9, 9};

const double EARTH_RADIUS = 6378.137;


struct Way
{
    string oneway;

    vector <int> nd;

    double weight;

};

bool car_access(string highway)
{
    int size = sizeof(CAR_HIGHWAY) / sizeof(CAR_HIGHWAY[0]);
    for (int i = 0; i < size; i++)
    {
        if (CAR_HIGHWAY[i] == highway)
        {
            return true;
        }
    }
    return false;
}

double get_weight(string highway)
{
    int size = sizeof(CAR_HIGHWAY) / sizeof(CAR_HIGHWAY[0]);
    for (int i = 0; i < size; i++)
    {
        if (CAR_HIGHWAY[i] == highway)
        {
            return CAR_HIGHWAY_WEIGHT[i];
        }
    }
    return 100;
}

// Utility function for  
// converting degrees to radians 
double toRadians(const double degree) 
{ 
    // cmath library in C++  
    // defines the constant 
    // M_PI as the value of 
    // pi accurate to 1e-30 
    double one_deg = (M_PI) / 180; 
    return (one_deg * degree); 
} 
  
double geo_to_meter(double lat1, double long1,
                    double lat2, double long2)
{ 
    // Convert the latitudes  
    // and longitudes 
    // from degree to radians. 
    lat1 = toRadians(lat1); 
    long1 = toRadians(long1); 
    lat2 = toRadians(lat2); 
    long2 = toRadians(long2); 
      
    // Haversine Formula 
    double dlong = long2 - long1; 
    double dlat = lat2 - lat1; 
  
    double ans = pow(sin(dlat / 2), 2) +  
                 cos(lat1) * cos(lat2) *  
                 pow(sin(dlong / 2), 2); 
  
    ans = 2 * asin(sqrt(ans)); 
  
    // Radius of Earth in  
    // Kilometers, R = 6371 
    // Use R = 3956 for miles  

    // Calculate the result 
    ans = ans * EARTH_RADIUS; 
  
    return ans;
}


int main()
{

    // read file and extract <node> and <way> tags.

    // the following area what nodes and ways have been parsed into.

    // each node tag consists of three thing:
    // - id ( basicly a big number, which is the nodes name )
    // - lon ( longitude )
    // - lat ( latitude )

    // each way tag consists of three thing (structure):
    // - nd ( vector of nodes that make the way )
    // - highway ( way type (road type, e.g. residential))
    // - oneway ( indicates wether the way is twoway or oneway )

    string filename;
    cin >> filename;

    xml_document doc;

    if (!doc.load_file(filename.c_str()))
    {
        cout << "\n" << "Couldn't read file." << "\n\n";
        return -1;
    }
    else
    {
        cout << "\n" << "read file." << "\n\n";
    }

    xml_node osm = doc.child("osm");

    string name;
    string elem_name;
    string elem_value;
    string attr_name;
    string attr_value;

    int node_index = 0;
    string node_id;
    array <double, 2> node_cords;
    map <string, int> id_to_index;
    map <int, string> index_to_id;
    string highway;
    string oneway;

    vector < array <double, 2> > nodes;
    vector <struct Way> ways;

    struct Way way;

    xml_attribute attr;
    xml_attribute elem_attr;

    bool road = false;

    for (xml_node child = osm.first_child(); child; child = child.next_sibling())
    {

        name = child.name();

        // child names can be: way, node, relation.

        if (name == "way") {

            way.nd.clear();

            road = false;

            for (
                xml_node elem = child.first_child();
                elem;
                elem = elem.next_sibling())
            {
            
                elem_name = elem.name();
                // names can be: nd, tag.

                if (elem_name == "nd")
                {
                    elem_attr = elem.attribute("ref");
                    elem_value = elem_attr.value();
                    way.nd.push_back(id_to_index[elem_value]);
                }
                else if (elem_name == "tag")
                {
                    elem_attr = elem.attribute("k");
                    elem_value = elem_attr.value();
                    if (elem_value == "highway") {
                        elem_attr = elem.attribute("v");
                        elem_value = elem_attr.value();
                        // check if the way is for cars
                        if (car_access(elem_value))
                        {
                            road = true;
                            way.weight = get_weight(elem_value);
                        }

                    }
                    else if (elem_value == "oneway")
                    {
                        elem_attr = elem.attribute("v");
                        elem_value = elem_attr.value();
                        way.oneway = elem_value;
                    }

                }
            
            }

            if (road)
            {
                ways.push_back(way);
            }

        }

        else if (name == "node") {

            attr = child.attribute("id");
            attr_value = attr.value();
            node_id = attr_value;

            attr = child.attribute("lat");
            attr_value = attr.value();
            node_cords[0] = stod(attr_value);
    
            attr = child.attribute("lon");
            attr_value = attr.value();
            node_cords[1] = stod(attr_value);

            id_to_index[node_id] = node_index;
            index_to_id[node_index] = node_id;

            node_index++;

            nodes.push_back(node_cords);

        }
    }

    // int count;
    // cin >> count;
    // list < pair <int, int> > *adj;
    // adj = new list < pair <int, int> >[count];
    // adj[0].push_back(make_pair(1, 2));
    // adj[0].push_back(make_pair(4, 3));
    // cout << "\n";
    // list< pair<int, int> >::iterator i;
    // for(i = adj[0].begin(); i != adj[0].end(); ++i) 
    // {
    //     cout << "p  " << (*i).first << ", " << (*i).second << "\n"; 
    // }
    // for (int i = 0; i < ways.size(); i++)
    // {
    //     cout << ways[i].highway << "\n";
    // }

    // write the data parsed as a graph to a file

    ofstream map_file;
    filename = "map.txt";
    map_file.open(filename);

    double dis;
    // for increasing the weight of paths with more nodes
    // (e.g. the bigger it is the more likely it will be to
    // choose highways for the shortest path)
    double node_count_constant = 5;

    if (map_file.is_open())
    {
        // write the number of nodes in the graph
        map_file << nodes.size() << "\n";
    
        // write the graph
        for (int i = 0; i < ways.size(); i++)
        {
            for (int node_index = 0; node_index < ways[i].nd.size() - 1; node_index++)
            {
                dis = geo_to_meter(
                    nodes[ways[i].nd[node_index]][0],
                    nodes[ways[i].nd[node_index]][1],
                    nodes[ways[i].nd[node_index + 1]][0],
                    nodes[ways[i].nd[node_index + 1]][1]);


                map_file << ways[i].nd[node_index] << " "
                << ways[i].nd[node_index + 1] << " " << setprecision(5)
                << ways[i].weight * dis * node_count_constant << "\n";
            
                // if road is twoway
                if (ways[i].oneway != "yes" &&
                    ways[i].oneway != "true" &&
                    ways[i].oneway != "1")
                {
                    map_file << ways[i].nd[node_index + 1] << " "
                    << ways[i].nd[node_index] << " " << setprecision(5)
                    << ways[i].weight * dis * node_count_constant << "\n";
                }
            }
        }

        // write the cordinations of nodes in the graph
        map_file << "cords\n";
        for (int i = 0; i < nodes.size(); i++)
        {
            map_file << i << " " << setprecision(10) << nodes[i][0]
            << " " << setprecision(10) << nodes[i][1] << "\n";
        }

        cout << "wrote to file.\n\n";

    }
    else
    {
        cout << "Unable to write to file (opening file problem)\n\n";
    }

    map_file.close();


    return 0;

}
