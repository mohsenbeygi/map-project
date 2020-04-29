import os
from subprocess import Popen, PIPE, run
import zipfile
import sys


def get_path(data):
    print("\nWriting node cordinations to ->  " + cpp_nodes)
    write_node_cords(data[0:2], data[2:], file_cords)
    print("\nWriting node cordinations done.")
    print("\nRunning c++ file ->  " + file_pathfinding)
    run_file(file_pathfinding)
    print("\nRunning c++ file done.")
    return read_path(file_path)

def write_node_cords(node1, node2, filename):
    with open(filename, "w") as file:
        file.write("{} {}\n".format(*node1))
        file.write("{} {}\n".format(*node2))

def run_file(filename):
    p = Popen([filename], shell=True, stdin=PIPE)

    value = cpp_graph_data + '\n'
    value = bytes(value, 'UTF-8')  # Needed in Python 3.
    p.stdin.write(value)
    p.stdin.flush()

    value = cpp_nodes + '\n'
    value = bytes(value, 'UTF-8')
    p.stdin.write(value)
    p.stdin.flush()

    value = cpp_path + '\n'
    value = bytes(value, 'UTF-8')
    p.stdin.write(value)
    p.stdin.flush()

    p.wait()

    return

def read_path(filename):
    path = []
    with open(filename, "r") as file:
        nodes = file.readlines()
        for node in nodes:
            node = node.strip()
            node = list(map(float, node.split()))
            path.append(node)

    return path


file_cords = "nodes.txt"
file_cords = \
    os.path.abspath(os.path.join(os.path.dirname( __file__ ), file_cords))
file_path = "path.txt"
file_path = \
    os.path.abspath(os.path.join(os.path.dirname( __file__ ), file_path))

"""
windows ("nt")  =>  "find_path.exe"
mac or linux ("posix")  =>  "find_path"
"""
if os.name == "posix":
    # mac or linux
    file_pathfinding = "find_path"
    file_pathfinding = \
        os.path.abspath(os.path.join(os.path.dirname( __file__ ), file_pathfinding))
elif os.name == "nt":
    # windows
    file_pathfinding = "find_path.exe"
    file_pathfinding = \
        os.path.abspath(os.path.join(os.path.dirname( __file__ ), file_pathfinding))

cpp_graph_data = "graph_data.txt"
cpp_graph_data = \
    os.path.abspath(os.path.join(os.path.dirname( __file__ ), cpp_graph_data))
if not os.path.exists(cpp_graph_data):
    try:
        zip_cpp_graph_data = "map.txt.zip"
        zip_cpp_graph_data = \
            os.path.abspath(os.path.join(os.path.dirname( __file__ ), zip_cpp_graph_data))
        with zipfile.ZipFile(zip_cpp_graph_data, 'r') as zip_ref:
            zip_ref.extractall(os.path.dirname( __file__ ))
        os.remove(zip_cpp_graph_data)
    except:
        print("\nMap file doesn't exist.")
        sys.exit()
cpp_nodes = "nodes.txt"
cpp_nodes = \
    os.path.abspath(os.path.join(os.path.dirname( __file__ ), cpp_nodes))
if not os.path.exists(cpp_nodes):
    file = open(cpp_nodes, "w")
    file.close()
cpp_path = "path.txt"
cpp_path = \
    os.path.abspath(os.path.join(os.path.dirname( __file__ ), cpp_path))
if not os.path.exists(cpp_path):
    file = open(cpp_path, "w")
    file.close()


if __name__ == "__main__":
    # print("\n\n\n\n", data, "\n\n\n\n")

    data = [
        35.69104278949384, 51.245040893554695,
        35.72811963001227, 51.452751159667976]

    print("\n\n\n\nStarting pathfinding ...")

    path = get_path(data)

    print("\nPath:")
    print(*path, sep=", ")
    print("\n\nPathfinding done.")