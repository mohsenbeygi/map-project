import json


def json_to_txt(jsonfile, txtfile):

    with open(jsonfile, "r") as file:
        data = json.load(file)
        routing_graph = data["routing_graph"]
        node_cords = data["node_cords"]
        # deleted = data["deleted"]
        # graph = data["graph"]

        node_count = len(routing_graph)

    node_indexes = {}
    indexes_to_nodes = {}

    index = 0

    with open(txtfile, "w") as file:
        file.write("{}\n".format(node_count))
        for node in routing_graph:
            for neighbour in routing_graph[node]:
                if node in node_indexes:
                    node_index = node_indexes[node]

                else:
                    node_indexes[node] = index
                    node_index = index
                    indexes_to_nodes[index] = node
                    index += 1
                if neighbour in node_indexes:
                    neighbour_index = node_indexes[neighbour]
                else:
                    node_indexes[neighbour] = index
                    neighbour_index = index
                    indexes_to_nodes[index] = neighbour
                    index += 1

                edge = "{} {} {}\n".format(
                    node_index,
                    neighbour_index,
                    routing_graph[node][neighbour]
                    )
                file.write(edge)

    data["node_indexes"] = node_indexes
    data["indexes_to_nodes"] = indexes_to_nodes

    with open(jsonfile, "w") as file:
        json.dump(data, file)


if __name__ == '__main__':

    txtfile = "graph_data.txt"
    jsonfile = "maps/map_graph.json"


    json_to_txt(jsonfile, txtfile)
