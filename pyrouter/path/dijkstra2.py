from path.fibHeap import FibonacciHeap


inf = float('inf')


def dijkstra(adjList, source, sink = None):
    # intentionally 1 more than the
    # number of vertices, keep the
    # 0th entry free for convenience
    n = len(adjList)
    visited = {}
    distance = {}
    parents = {}
    for node in adjList:
        visited[node] = False
        distance[node] = inf
        parents[node] = None

    heapNodes = [None]*n
    heap = FibonacciHeap()
    index = 0
    node_indexes = {}
    for node in adjList:
        node_indexes[node] = index
        heapNodes[index] = heap.insert(float('inf'), node)
        # distance, label
        index += 1

    distance[source] = 0
    heap.decrease_key(heapNodes[node_indexes[source]], 0)

    while heap.total_nodes:
        current = heap.extract_min().value
        visited[current] = True

        # early exit
        if sink and current == sink:
            break

        for neighbor in adjList[current]:
            cost = adjList[current][neighbor]
            if not visited[neighbor]:
                if distance[current] + cost < distance[neighbor]:
                    distance[neighbor] = distance[current] + cost
                    heap.decrease_key(
                        heapNodes[node_indexes[neighbor]],
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


# Convention: Avoid 0-indexing. Keep 0th entry unused if necessary
# Convention: adjList[i] = [(neighbor, weight) for all neighbors]

'''
adjList = [
[],
[(2, 7), (3, 9), (6, 14)],
[(1, 7), (4, 15), (3, 10)],
[(1, 9), (2, 10), (4, 11), (6, 2)],
[(2, 15), (3, 11), (5, 6)],
[(4, 6), (6, 9)],
[(5, 9), (1, 14)]
]
'''
