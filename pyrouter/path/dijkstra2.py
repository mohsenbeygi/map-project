from .fibHeap import FibonacciHeap


inf = float('inf')


def dijkstra(adj_list, source, dest_distances, sink = None):
    # intentionally 1 more than the
    # number of vertices, keep the
    # 0th entry free for convenience
    n = len(adj_list)
    visited = {}
    distance = {}
    parents = {}
    for node in adj_list:
        visited[node] = False
        distance[node] = inf
        parents[node] = None

    heap_nodes = [None] * n
    heap = FibonacciHeap()
    index = 0
    node_indexes = {}
    for node in adj_list:
        node_indexes[node] = index
        heap_nodes[index] = heap.insert(float('inf'),
                                        node)
        # distance, label
        index += 1

    distance[source] = 0
    heap.decrease_key(heap_nodes[node_indexes[source]], 0)

    while heap.total_nodes:
        current = heap.extract_min().value
        visited[current] = True

        # early exit
        if sink and current == sink:
            break

        for neighbor in adj_list[current]:
            cost = adj_list[current][neighbor]
            if not visited[neighbor]:
                cost_from = distance[current] + cost
                if cost_from + dest_distances[neighbor] < \
                    distance[neighbor]:
                    distance[neighbor] = cost_from
                    heap.decrease_key(
                        heap_nodes[node_indexes[neighbor]],
                        distance[neighbor])
                    parents[neighbor] = current



    return parents


def get_path(parents, beg, des):
    path = [des]
    last = des
    while last != beg:
        last = parents[last]
        path.append(last)
    return path

