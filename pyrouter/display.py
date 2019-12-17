from load.loader import Loader
import mplleaflet
import matplotlib.pyplot as plt

data = Loader('car', read=True)
data.read("./maps/map_graph.json")

lons = []
lats = []
for node in data.rnodes:
    lats.append(data.rnodes[node][0])
    lons.append(data.rnodes[node][1])
fig = plt.figure()

print('here')

plt.plot(lons, lats, "rs")

print('here as well')

mplleaflet.show(fig=fig)
