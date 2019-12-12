import loader
from dijkstra import *
import mplleaflet
import matplotlib.pyplot as plt

inf = float('inf')

data = loader.LoadOsm("car")
# print(data.routing)

node1 = (35.80521454717427, 51.43798828125)
node2 = (35.79745295182983, 51.43717288970948)

node1 = data.findNode(*node1)
node2 = data.findNode(*node2)

print(data.rnodes[node1])
print(data.rnodes[node2])

# get costs
costs = {}
for node in data.routing:
        if node == node1:
                costs[node] = 0
        else:
                costs[node] = inf


previus = dijkstra(costs, data.routing)
# print("Costs: ", costs)
route = get_path(previus, node1, node2)[::-1]
# print('Shortest path from ', node1, ' to ', node2, ' is: ', route)

lons = []
lats = []
for i in route:
    node = data.rnodes[i]
    lats.append(node[0])
    lons.append(node[1])
fig = plt.figure()
plt.plot(lons, lats, color="purple", linewidth=10)
plt.plot([data.rnodes[node1][1]], [data.rnodes[node1][0]], "rs")
plt.plot([data.rnodes[node2][1]], [data.rnodes[node2][0]], "rs")
mplleaflet.show(fig=fig)
