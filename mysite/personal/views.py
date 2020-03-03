from django.shortcuts import render
from personal.pyrouter.router import *

# Create your views here.

router = Router("car")

def index(request):
    return render(request, 'personal/map.html')

def display_path(request, data):
    data = list(map(float, data.split(",")))
    path = router.cpp_find_path(
        data[:2],
        data[2:],
        file_pathfinding,
        file_cords,
        file_path
    )
    return render(request, 'personal/path.html', {"path": path})
