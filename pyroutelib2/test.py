import mplleaflet
import matplotlib.pyplot as plt

lats = [35.804148]
lons = [51.439114] 

fig = plt.figure()    #This is missing in your code.
plt.plot(lons, lats, 'b') # Draw blue line

#And after this call the funtion:

mplleaflet.show(fig=fig)
#It will display the matplotlib object created by plot function
