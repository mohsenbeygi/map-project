import osmgraph
# import matplotlib.pyplot as plt
import networkx as nx
import json
import random

def compare(cord1, cord2):
    flag = True
    for i in range(2):
        if round(cord1[i], 5) != round(cord2[i], 5):
            flag = False
            break
    return flag


file = './maps/map.osm'
g = osmgraph.parse_file(file, parse_direction=True)
# nx.draw(g)  # networkx draw()
# plt.show()  # pyplot draw()
print(g.nodes())
latitude_list = []
longitude_list = []
for node in g.nodes():
    latitude_list.append(g.node[node]['coordinate'][1])
    longitude_list.append(g.node[node]['coordinate'][0])

# print(path)

# import gmplot package
import gmplot
gmap3 = gmplot.GoogleMapPlotter(35.8024002,51.4351605,15.69)
gmap3.scatter( latitude_list, longitude_list, '# FF0000',
                              size = 5, marker = False )
gmap3.draw( "map13.html" )
