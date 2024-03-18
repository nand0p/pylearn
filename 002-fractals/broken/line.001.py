import numpy as np
from PIL import Image
import math

def plot_line(from_coordinates, to_coordinates, thickness, colour, pixels):

    # Figure out the boundaries of our pixel array
    max_x_coordinate = len(pixels[0])
    max_y_coordinate = len(pixels)

    # The distances along the x and y axis between the 2 points
    horizontal_distance = to_coordinates[1] - from_coordinates[1]
    vertical_distance = to_coordinates[0] - from_coordinates[0]

    # The total distance between the two points
    distance =  math.sqrt((to_coordinates[1] - from_coordinates[1])**2 \
                + (to_coordinates[0] - from_coordinates[0])**2)

    # How far we will step forwards each time we colour in a new pixel
    horizontal_step = horizontal_distance/distance
    vertical_step = vertical_distance/distance

    # At this point, we enter the loop to draw the line in our pixel array
    # Each iteration of the loop will add a new point along our line
    for i in range(round(distance)):
        
        # These 2 coordinates are the ones at the center of our line
        current_x_coordinate = round(from_coordinates[1] + (horizontal_step*i))
        current_y_coordinate = round(from_coordinates[0] + (vertical_step*i))

        # Once we have the coordinates of our point, 
        # we draw around the coordinates of size 'thickness'
        for x in range (-thickness, thickness):
            for y in range (-thickness, thickness):
                x_value = current_x_coordinate + x
                y_value = current_y_coordinate + y

                if (x_value > 0 and x_value < max_x_coordinate and \
                    y_value > 0 and y_value < max_y_coordinate):
                    pixels[y_value][x_value] = colour


def draw_triangle(center, side_length, thickness, colour, pixels):
    
    # The height of an equilateral triangle is, h = ½(√3a)
    # where 'a' is the side length
    triangle_height = round(side_length * math.sqrt(3)/2)

    # The top corner
    top = [center[0] - triangle_height/2, center[1]]

    # Bottom left corner
    bottom_left = [center[0] + triangle_height/2, center[1] - side_length/2]

    # Bottom right corner
    bottom_right = [center[0] + triangle_height/2, center[1] + side_length/2]

    # Draw a line between each corner to complete the triangle
    plot_line(top, bottom_left, thickness, colour, pixels)
    plot_line(top, bottom_right, thickness, colour, pixels)
    plot_line(bottom_left, bottom_right, thickness, colour, pixels)


def rotate(coordinate, center_point, degrees):
    # Subtract the point we are rotating around from our coordinate
    x = (coordinate[0] - center_point[0])
    y = (coordinate[1] - center_point[1])

    # Python's cos and sin functions take radians instead of degrees
    radians = math.radians(degrees)

    # Calculate our rotated points 
    new_x = (x * math.cos(radians)) - (y * math.sin(radians))
    new_y = (y * math.cos(radians)) + (x * math.sin(radians))

    # Add back our offset we subtracted at the beginning to our rotated points
    return [new_x + center_point[0], new_y + center_point[1]]


# Define the size of our image
pixels = np.zeros( (500,500,3), dtype=np.uint8 )

# Draw a line
plot_line([0,0], [499,499], 1, [255,200,0], pixels)

# Turn our pixel array into a real picture
img = Image.fromarray(pixels)

# Show our picture, and save it
img.show()
#img.save('Line.png')
