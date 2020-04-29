# Router

Router is Python project for pathfinding and routing (using osm (open street map) data).
(Although mostly written in c++ for speed.)

## Installation

Download the "project" folder and run pathfinding.py in it (make sure all the other files exist next to it).

## Usage

For usage download an osm map file (e.g. planet.osm) and put in the same directory as "extract.cpp" (inside "project" folder). Then compile and run "extract.cpp" to parse the map file (it will put the parsed data in "map.txt" in the same directory). Finally run "pathfinding.py". (You can enter any longitude and latitude for the start and destination nodes and "pathfinding.py" will find the shortest path between them.)

```bash

$ g++ -std=c++11 extract.cpp -o parse

$ ./parse
planet.osm

$ python pathfinding.py
    .
    .
    .

```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
We don't have one.