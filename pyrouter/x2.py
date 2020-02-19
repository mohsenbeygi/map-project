import matplotlib.pyplot as plt
import json

# read graph
with open("maps/map_graph1.json", "r") as file:
    file = json.load(file)
    graph = file["routing_graph"]
    cords = file["node_cords"]

for node in cords:
    if node in graph:
        plt.plot([cords[node][1]],
                 [[cords[node][0]]],
                 "bo", markersize=3)


for node in graph:
    for succ in graph[node]:
        lons = [cords[node][1], cords[succ][1]]
        lats = [cords[node][0], cords[succ][0]]
        plt.plot(lons, lats, color="black",
                 linewidth=1)

        plt.arrow(
            lons[0], lats[0], lons[1] - lons[0], lats[1] - lats[0],
            length_includes_head=True,
            head_width=0.08, head_length=0.00002)

print(1)
plt.show()
