import pygame as pg
import json
from path.dijkstra import *
vec = pg.math.Vector2

# screen
WIDTH = 1400
HEIGHT = 850
graph_w = WIDTH
graph_h = HEIGHT
FPS = 60

# infinty
inf = float("inf")

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


def to_xy(node, move_x, move_y):

    screen_x = round((WIDTH - graph_w) / 2) + move_x
    screen_y = round((HEIGHT - graph_h) / 2) + move_y
    y, x = node
    if min_lon < y < max_lon and min_lat < x < max_lat:
        pos = [
            screen_x + round((x * ratio_x + start_x)),
            screen_y + graph_h - round((y * ratio_y + start_y))
            ]
    else:
        return [-1, -1]
    return pos


def draw_line(pos1, pos2, move_x, move_y):
    pg.draw.line(screen, BLACK, pos1, pos2, 1)


def screen_graph_ratio(cords):
    min_x = inf
    min_y = inf
    max_x = -inf
    max_y = -inf

    for node in cords:
        if cords[node][1] < min_x:
            min_x = cords[node][1]

        if cords[node][1] > max_x:
            max_x = cords[node][1]

        if cords[node][0] < min_y:
            min_y = cords[node][0]

        if cords[node][0] > max_y:
            max_y = cords[node][0]

    ratio_x = graph_w / (max_x - min_x)
    ratio_y = graph_h / (max_y - min_y)

    start_x = 0 - min_x * ratio_x
    start_y = 0 - min_y * ratio_y

    return ratio_x, ratio_y, start_x, start_y


def is_on_screen(pos):
    if 0 <= pos[0] <= WIDTH and 0 <= pos[1] <= HEIGHT:
        return True
    return False


def draw_arrow(pos1, pos2, move_x, move_y):
    line = vec(pos1[0] - pos2[0], pos1[1] - pos2[1])
    arr1 = line.rotate(20)
    arr2 = line.rotate(-20)
    if arr1.length_squared() != 0 and arr2.length_squared() != 0:
        # print(arr1.length, arr2.length)
        arr1.scale_to_length(10)
        arr2.scale_to_length(10)
        arr1 = [pos2[0] + arr1.x, pos2[1] + arr1.y]
        arr2 = [pos2[0] + arr2.x, pos2[1] + arr2.y]
        # pg.draw.line(screen, BLACK, arr1, pos2, 1)
        # pg.draw.line(screen, BLACK, arr2, pos2, 1)
        pg.draw.polygon(screen, BLACK, (arr1, arr2, pos2))



def draw_graph(graph, cords, move_x, move_y):
    # draw nodes
    for node in cords:
        if node in graph:
            pos = to_xy(cords[node], move_x, move_y)
            if is_on_screen(pos):
                pg.draw.circle(
                    screen,
                    RED,
                    pos,
                    5
                    )

    # draw edges
    for node in graph:
        for succ in graph[node]:
            pos1 = to_xy(cords[node], move_x, move_y)
            pos2 = to_xy(cords[succ], move_x, move_y)
            if is_on_screen(pos1) and is_on_screen(pos2):
                draw_line(
                    pos1,
                    pos2,
                    move_x,
                    move_y)
                draw_arrow(
                    pos1,
                    pos2,
                    move_x,
                    move_y)


def get_difference(pos1, pos2):
    return [pos1[0] - pos2[0], pos1[1] - pos2[1]]


def vector_len(vector):
    return (vector[0] ** 2 + vector[1] ** 2) ** 0.5


def mult_vector(vector, coefficient):
    vector[0] *= coefficient
    vector[1] *= coefficient


def influence_barriers(mouse, graph_w, graph_h):
    x = min(
        mouse[0],
        WIDTH - ((WIDTH - graph_w) / 2) + move_x
        )

    x = max(
        mouse[0],
        ((WIDTH - graph_w) / 2) + move_x
        )

    y = min(
        mouse[1],
        HEIGHT - ((HEIGHT - graph_h) / 2) + move_y
        )

    y = max(
        mouse[1],
        ((HEIGHT - graph_h) / 2) + move_y
        )

    return [x, y]


def centerize(mouse, move_x, move_y, graph_w, graph_h):
    mouse = influence_barriers(mouse, graph_w, graph_h)
    move_vector = [
        0.5 * WIDTH - mouse[0],
        0.5 * HEIGHT - mouse[1]
        ]
    length = vector_len(move_vector)
    mult_vector(move_vector, ((0.1 * length)  / length))
    move_x += move_vector[0]
    move_y += move_vector[1]

    return round(move_x), round(move_y)


def decenterize(mouse, move_x, move_y, graph_w, graph_h):
    mouse = influence_barriers(mouse, graph_w, graph_h)
    move_vector = [
        0.5 * WIDTH - mouse[0],
        0.5 * HEIGHT - mouse[1]
        ]
    length = vector_len(move_vector)
    mult_vector(move_vector, ((0.1 * length)  / length))
    move_x -= move_vector[0]
    move_y -= move_vector[1]

    return round(move_x), round(move_y)


# initialize pygame and create window
pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()

# read graph
with open("maps/map_graph.json", "r") as file:
    file = json.load(file)
    graph = file["routing_graph"]
    cords = file["node_cords"]


# draw graph

max_lon = inf
min_lon = -inf
max_lat = inf
min_lat = -inf

max_lon = 35.8
min_lon = 35.7
max_lat = 51.5
min_lat = 51.0

move_x = 0
move_y = 0

screen.fill(WHITE)
dimensions = screen_graph_ratio(cords)
ratio_x, ratio_y, start_x, start_y = dimensions
draw_graph(graph, cords, move_x, move_y)
pg.display.update()

# loop
running = True
click = False
click_pos = [0, 0]
while running:
    # keep loop running at the right speed
    clock.tick(FPS)
    # Process input (events)
    zoomout = False
    zoomin = False
    for event in pg.event.get():
        # check for closing window
        if event.type == pg.QUIT:
            running = False

        if event.type == pg.MOUSEBUTTONDOWN:
            # zoom out
            if event.button == 4:
                zoomout = True
            # zoom in
            elif event.button == 5:
                zoomin = True


    # Update
    running_fps = "{:.2f}".format(clock.get_fps())
    # print(zoomin, zoomout)
    if zoomin:
        graph_w = round(graph_w * 102 / 100)
        graph_h = round(graph_h * 102 / 100)
        # mouse = pg.mouse.get_pos()
        # move_x, move_y = \
        #     centerize(
        #         mouse,
        #         move_x,
        #         move_y,
        #         graph_w,
        #         graph_h
        #         )

    if zoomout:
        graph_w = round(graph_w * 98 / 100)
        graph_h = round(graph_h * 98 / 100)
        # mouse = pg.mouse.get_pos()
        # move_x, move_y = \
        #     decenterize(
        #         mouse,
        #         move_x,
        #         move_y,
        #         graph_w,
        #         graph_h
        #         )

    keys = pg.mouse.get_pressed()
    moved = False
    if keys[0]:
        if not click:
            click = True
            click_pos = pg.mouse.get_pos()
        else:
            new_pos = pg.mouse.get_pos()
            diff = get_difference(click_pos, new_pos)
            move_x -= diff[0] * 2
            move_y -= diff[1] * 2
            moved = True
            click_pos = new_pos

    else:
        click = False

    # show node id
    # mouse_pos = pg.mouse.get_pos()
    # color = screen.get_at(mouse_pos)
    # print(color)



    # Draw / render
    pg.display.set_caption(running_fps)

    # draw graph
    if zoomin or zoomout or moved:
        screen.fill(WHITE)
        dimensions = screen_graph_ratio(cords)
        ratio_x, ratio_y, start_x, start_y = dimensions
        draw_graph(graph, cords, move_x, move_y)
        pg.display.update()


pg.quit()
