
from matplotlib import pyplot
from matplotlib.patches import Rectangle

import math
import imageIO.png


def createInitializedGreyscalePixelArray(image_width, image_height, initValue = 0):

    new_array = [[initValue for x in range(image_width)] for y in range(image_height)]
    return new_array


# this function reads an RGB color png file and returns width, height, as well as pixel arrays for r,g,b
def readRGBImageToSeparatePixelArrays(input_filename):

    image_reader = imageIO.png.Reader(filename=input_filename)
    # png reader gives us width and height, as well as RGB data in image_rows (a list of rows of RGB triplets)
    (image_width, image_height, rgb_image_rows, rgb_image_info) = image_reader.read()

    print("read image width={}, height={}".format(image_width, image_height))

    # our pixel arrays are lists of lists, where each inner list stores one row of greyscale pixels
    pixel_array_r = []
    pixel_array_g = []
    pixel_array_b = []

    for row in rgb_image_rows:
        pixel_row_r = []
        pixel_row_g = []
        pixel_row_b = []
        r = 0
        g = 0
        b = 0
        for elem in range(len(row)):
            # RGB triplets are stored consecutively in image_rows
            if elem % 3 == 0:
                r = row[elem]
            elif elem % 3 == 1:
                g = row[elem]
            else:
                b = row[elem]
                pixel_row_r.append(r)
                pixel_row_g.append(g)
                pixel_row_b.append(b)

        pixel_array_r.append(pixel_row_r)
        pixel_array_g.append(pixel_row_g)
        pixel_array_b.append(pixel_row_b)

    return (image_width, image_height, pixel_array_r, pixel_array_g, pixel_array_b)

# This method packs together three individual pixel arrays for r, g and b values into a single array that is fit for
# use in matplotlib's imshow method
def prepareRGBImageForImshowFromIndividualArrays(r,g,b,w,h):
    rgbImage = []
    for y in range(h):
        row = []
        for x in range(w):
            triple = []
            triple.append(r[y][x])
            triple.append(g[y][x])
            triple.append(b[y][x])
            row.append(triple)
        rgbImage.append(row)

    return rgbImage
    

# This method takes a greyscale pixel array and writes it into a png file
def writeGreyscalePixelArraytoPNG(output_filename, pixel_array, image_width, image_height):
    # now write the pixel array as a greyscale png
    file = open(output_filename, 'wb')  # binary mode is important
    writer = imageIO.png.Writer(image_width, image_height, greyscale=True)
    writer.write(file, pixel_array)
    file.close()


def computeRGBToGreyscale(pixel_array_r, pixel_array_g, pixel_array_b, image_width, image_height):
    greyscale_pixel_array = createInitializedGreyscalePixelArray(image_width, image_height)

    for y in range(0, image_height):
        for x in range(0, image_width):
            pixel_array_r[y][x] = 0.299 * pixel_array_r[y][x]
            pixel_array_g[y][x] = 0.587 * pixel_array_g[y][x]
            pixel_array_b[y][x] = 0.114 * pixel_array_b[y][x]

            greyscale_pixel_array[y][x] += round(pixel_array_r[y][x] + pixel_array_g[y][x] + pixel_array_b[y][x])

    return greyscale_pixel_array


def scaleTo0And255AndQuantize(pixel_array, image_width, image_height):
    greyscale_pixel_array = createInitializedGreyscalePixelArray(image_width, image_height)

    g_min = 0
    g_max = 255
    for y in range(0, image_height):
        for x in range(0, image_width):

            if y == 0 & x == 0:
                f_low = pixel_array[y][x]
                f_high = pixel_array[y][x]

            if pixel_array[y][x] < f_low:
                f_low = pixel_array[y][x]

            if pixel_array[y][x] > f_high:
                f_high = pixel_array[y][x]

    for y in range(0, image_height):
        for x in range(0, image_width):

            if (pixel_array[y][x] - f_low) == 0:
                greyscale_pixel_array[y][x] += 0
                continue
            else:
                s_out = (pixel_array[y][x] - f_low) * ((g_max - g_min) / (f_high - f_low)) + g_min
                greyscale_pixel_array[y][x] += round(s_out)

    return greyscale_pixel_array


def computeVerticalEdgesSobelAbsolute(pixel_array, image_width, image_height):
    array = createInitializedGreyscalePixelArray(image_width, image_height)

    for h in range(1, image_height - 1):
        for w in range(1, image_width - 1):
            newvalue = -1 * pixel_array[h - 1][w - 1] + pixel_array[h - 1][w + 1] + -2 * pixel_array[h][w - 1] + 2 * \
                       pixel_array[h][w + 1] + -1 * pixel_array[h + 1][w - 1] + pixel_array[h + 1][w + 1]
            array[h][w] = newvalue / 8

    return array


def computeHorizontalEdgesSobelAbsolute(pixel_array, image_width, image_height):
    array = createInitializedGreyscalePixelArray(image_width, image_height)

    for h in range(1, image_height - 1):
        for w in range(1, image_width - 1):
            newvalue = 1 * pixel_array[h - 1][w - 1] + 2 * pixel_array[h - 1][w] + pixel_array[h - 1][w + 1] + -1 * \
                       pixel_array[h + 1][w - 1] + -2 * pixel_array[h + 1][w] + -1 * pixel_array[h + 1][w + 1]
            array[h][w] = newvalue / 8

    return array


def computeBoxAveraging3x3(pixel_array, image_width, image_height):
    array = createInitializedGreyscalePixelArray(image_width, image_height)

    for h in range(1, image_height - 1):
        for w in range(1, image_width - 1):
            newvalue = pixel_array[h - 1][w - 1] + pixel_array[h - 1][w] + pixel_array[h - 1][w + 1] + pixel_array[h][
                w - 1] + pixel_array[h][w] + pixel_array[h][w + 1] + pixel_array[h + 1][w - 1] + pixel_array[h + 1][w] + \
                       pixel_array[h + 1][w + 1]
            array[h][w] = abs(newvalue) / 9

    return array


def computeThresholdGE(pixel_array, threshold_value, image_width, image_height):
    for h in range(0, image_height):
        for w in range(0, image_width):
            if pixel_array[h][w] >= threshold_value:
                pixel_array[h][w] = 255
            else:
                pixel_array[h][w] = 0

    return pixel_array

def main():
    filename = "./images/covid19QRCode/poster1small.png"
    output_filename = "./images/covid19QRCode/poster2small.png"

    # we read in the png file, and receive three pixel arrays for red, green and blue components, respectively
    # each pixel array contains 8 bit integer values between 0 and 255 encoding the color values
    (image_width, image_height, px_array_r, px_array_g, px_array_b) = readRGBImageToSeparatePixelArrays(filename)


    pyplot.imshow(prepareRGBImageForImshowFromIndividualArrays(px_array_r, px_array_g, px_array_b, image_width, image_height))

    greyscale_array = computeRGBToGreyscale(px_array_r, px_array_g, px_array_b, image_width, image_height)
    quantize_array = scaleTo0And255AndQuantize(greyscale_array, image_width, image_height)

    verticalSobel_array = computeVerticalEdgesSobelAbsolute(quantize_array, image_width, image_height)
    horizontalSobel_array = computeHorizontalEdgesSobelAbsolute(quantize_array, image_width, image_height)

    edge_mag_array = createInitializedGreyscalePixelArray(image_width, image_height)

    for h in range(image_height):
        for w in range(image_width):
            edge_mag_array[h][w] = math.sqrt(verticalSobel_array[h][w] ** 2) + math.sqrt(horizontalSobel_array[h][w] ** 2)


    for i in range(0,9):
        edge_mag_array = computeBoxAveraging3x3(edge_mag_array, image_width, image_height)
    stretch_array = scaleTo0And255AndQuantize(edge_mag_array, image_width, image_height)

    threshold_array = computeThresholdGE(stretch_array, 70, image_width, image_height)

    pyplot.imshow(threshold_array, cmap="gray")


    # get access to the current pyplot figure
    axes = pyplot.gca()
    # create a 70x50 rectangle that starts at location 10,30, with a line width of 3
    rect = Rectangle( (10, 30), 70, 50, linewidth=3, edgecolor='g', facecolor='none' )
    # paint the rectangle over the current plot

    # plot the current figure

    pyplot.show()



if __name__ == "__main__":
    main()