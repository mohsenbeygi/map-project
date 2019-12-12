import os
import re
import xml.etree.ElementTree as etree
from datetime import datetime
import weights

class LoadOsm(object):
    """Parse an OSM file looking for routing information, and do routing with it"""
    def __init__(self, transport):
        """Initialise an OSM-file parser"""
        self.routing = {}
        self.rnodes = {}
        self.transport = transport
        self.weights = weights.RoutingWeights()
        filename = 'map.osm'
        self.loadOsm(filename)

    def _ParseDate(self, DateString):
        result = DateString
        try:
            result = datetime.strptime(DateString, "%Y-%m-%d %H:%M:%S UTC")
        except:
            try:
                result = datetime.strptime(DateString, "%Y-%m-%dT%H:%M:%SZ")
            except:
                pass
            return result

    def getElementAttributes(self, element):    # noqa
            result = {}
            for k, v in element.attrib.items():
                if k == "uid":
                        v = int(v)
                elif k == "changeset":
                        v = int(v)
                elif k == "version":
                        v = int(v)
                elif k == "id":
                        v = int(v)
                elif k == "lat":
                        v = float(v)
                elif k == "lon":
                        v = float(v)
                elif k == "open":
                        v = (v == "true")
                elif k == "visible":
                        v = (v == "true")
                elif k == "ref":
                        v = int(v)
                elif k == "comments_count":
                        v = int(v)
                elif k == "timestamp":
                        v = self._ParseDate(v)
                elif k == "created_at":
                        v = self._ParseDate(v)
                elif k == "closed_at":
                        v = self._ParseDate(v)
                elif k == "date":
                        v = self._ParseDate(v)
                result[k] = v
            return result

    def getElementTags(self, element):
        result = {}
        for child in element:
            if child.tag =="tag":
                k = child.attrib["k"]
                v = child.attrib["v"]
                result[k] = v
        return result

    def parseOsmFile(self, filename):
        result = []
        with open(filename, "r", encoding="utf-8") as f:
            for event, elem in etree.iterparse(f): # events=['end']
                if elem.tag == "node":
                    data = self.getElementAttributes(elem)
                    data["tag"] = self.getElementTags(elem)
                    result.append({
                        "type": "node",
                        "data": data
                    })
                elif elem.tag == "way":
                    data = self.getElementAttributes(elem)
                    data["tag"] = self.getElementTags(elem)
                    data["nd"] = []
                    for child in elem:
                        if child.tag == "nd":
                            data["nd"].append(int(child.attrib["ref"]))
                    result.append({
                        "type": "way",
                        "data": data
                    })
                elif elem.tag == "relation":
                    data = self.getElementAttributes(elem)
                    data["tag"] = self.getElementTags(elem)
                    data["member"] = []
                    for child in elem:
                        if child.tag == " member":
                            data["member"].append(self.getElementAttributes(child))
                    result.append({
                        "type": "relation",
                        "data": data
                    })
                    elem.clear()
        return result


    def loadOsm(self, filename):
        if(not os.path.exists(filename)):
            print("No such data file %s" % filename)
            return

        nodes, ways = {}, {}

        data = self.parseOsmFile(filename)
        # data = [{ type: node|way|relation, data: {}},...]

        for x in data:
            try:
                if x['type'] == 'node':
                    nodes[x['data']['id']] = x['data']
                elif x['type'] == 'way':
                    ways[x['data']['id']] = x['data']
                else:
                    continue
            except KeyError:
                # Don't care about bad data (no type/data key)
                continue
        #end for x in data
        for way_id, way_data in ways.items():
            way_nodes = []
            for nd in way_data['nd']:
                if nd not in nodes:
                    continue
                way_nodes.append([nodes[nd]['id'], nodes[nd]['lat'], nodes[nd]['lon']])
            self.storeWay(way_id, way_data['tag'], way_nodes)


    def storeWay(self, wayID, tags, nodes):
        highway = self.equivalent(tags.get('highway', ''))
        railway = self.equivalent(tags.get('railway', ''))
        oneway = tags.get('oneway', '')
        reversible = not oneway in('yes','true','1')

        # Calculate what vehicles can use this route
        # TODO: just use getWeight != 0
        access = {}
        access['cycle'] = highway in ('primary','secondary','tertiary','unclassified','minor','cycleway','residential', 'track','service')
        access['car'] = highway in ('motorway','trunk','primary','secondary','tertiary','unclassified','minor','residential', 'service')
        access['train'] = railway in('rail','light_rail','subway')
        access['foot'] = access['cycle'] or highway in('footway','steps')
        access['horse'] = highway in ('track','unclassified','bridleway')

        # Store routing information
        last = [None,None,None]

        for node in nodes:
            (node_id,x,y) = node
            if last[0]:
                if(access[self.transport]):
                    weight = self.weights.get(self.transport, railway or highway)
                    self.addLink(last[0], node_id, weight)
                    self.makeNodeRouteable(last)
                    if reversible or self.transport == 'foot':
                        self.addLink(node_id, last[0], weight)
                        self.makeNodeRouteable(node)
            last = node

    def makeNodeRouteable(self,node):
        self.rnodes[node[0]] = [node[1],node[2]]

    def addLink(self,fr,to, weight=1):
        """Add a routeable edge to the scenario"""
        try:
            if to in list(self.routing[fr].keys()):
                return
            self.routing[fr][to] = weight
        except KeyError:
            self.routing[fr] = {to: weight}

    def equivalent(self,tag):
        """Simplifies a bunch of tags to nearly-equivalent ones"""
        equivalent = { \
            "primary_link":"primary",
            "trunk":"primary",
            "trunk_link":"primary",
            "secondary_link":"secondary",
            "tertiary":"secondary",
            "tertiary_link":"secondary",
            "residential":"unclassified",
            "minor":"unclassified",
            "steps":"footway",
            "driveway":"service",
            "pedestrian":"footway",
            "bridleway":"cycleway",
            "track":"cycleway",
            "arcade":"footway",
            "canal":"river",
            "riverbank":"river",
            "lake":"river",
            "light_rail":"railway"
            }
        try:
            return(equivalent[tag])
        except KeyError:
            return(tag)

    def findNode(self,lat,lon):
        """Find the nearest node that can be the start of a route"""
        # self.getArea(lat,lon)
        maxDist = 1E+20
        nodeFound = None
        posFound = None
        for (node_id,pos) in list(self.rnodes.items()):
            dy = pos[0] - lat
            dx = pos[1] - lon
            dist = dx * dx + dy * dy
            if(dist < maxDist):
                maxDist = dist
                nodeFound = node_id
                posFound = pos
        # print("found at %s"%str(posFound))
        return(nodeFound)

# Parse the supplied OSM file
if __name__ == "__main__":
    data = LoadOsm("car")
