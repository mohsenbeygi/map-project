import os


def get_download_path():
    """
    returns the default downloads
    path for any os (linux or windows or mac)
    """
    if os.name == 'nt':
        return os.path.join(os.path.expanduser('~'),
                            'Downloads')
    else:
        print("123")
        return os.path.join(os.path.expanduser('~'),
                            'downloads')


def get_cords(filename):
    '''
    read file extract first
    cord (longitude or latitude)
    '''

    path = os.path.exists(os.path.join(get_download_path(),
                                       filename))

    if not os.path.exists(os.path.join(get_download_path(),
                                       filename)):
        print(filename + " doesn't exist")
        return

    delete = False

    with open(os.path.join(get_download_path(),
                           filename), 'r') as file:
        data = file.readline()

        if len(data) < 2:
            print(filename + " is empty (no cordinations)")

            # empty so remove it
            delete = True

        else:
            index = data.find(',')
            cord = float(data[:index])

    if delete:
        delete_file(filename)
        return

    with open(os.path.join(get_download_path(),
                           filename), 'w') as file:
        file.write(data[index + 1:])

    return cord


def delete_file(filename):
    # empty so remove it
    os.remove(os.path.join(get_download_path(),
                           filename))
    print("deleted " + filename)
    return


def valid_data(node1, node2, filename):
    if node1[0] is None or node1[1] is None:
        raise ValueError(" cordination data in file " +
                         filename + ", wasn't valid !")

    if node2[0] is None or node2[1] is None:
        raise ValueError(" cordination data in file " +
                         filename + ", wasn't valid !")


def get_node_cords(filename):
    # read from file
    lat1 = get_cords(filename)
    lon1 = get_cords(filename)
    node1 = (lat1, lon1)
    print("node1: ", node1)

    lat2 = get_cords(filename)
    lon2 = get_cords(filename)
    node2 = (lat2, lon2)
    print("node2: ", node2)

    valid_data(node1, node2, filename)

    # delete file
    get_cords(filename)

    return node1, node2


if __name__ == "__main__":
    filename = "cords.txt"
    print(get_cords(filename))
