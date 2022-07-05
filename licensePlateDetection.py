import math
import sys
from pathlib import Path

from matplotlib import pyplot
from matplotlib import image
from matplotlib.patches import Rectangle

# import our basic, light-weight png reader library
import imageIO.png

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


# a useful shortcut method to create a list of lists based array representation for an image, initialized with a value
def createInitializedGreyscalePixelArray(image_width, image_height, initValue = 0):

    new_array = [[initValue for x in range(image_width)] for y in range(image_height)]
    return new_array
# Read the input image, convert RGB data to greyscale and stretch the values to lie between 0 and 255
def computeRGBToGreyscale(pixel_array_r, pixel_array_g, pixel_array_b, image_width, image_height):
    
    greyscale_pixel_array = createInitializedGreyscalePixelArray(image_width, image_height)
    
    for i in range(image_height ):
        for j in range(image_width ):
            greyscale_pixel_array[i][j]=int(round(0.299*pixel_array_r[i][j]+0.587*pixel_array_g[i][j]+0.114*pixel_array_b[i][j]))
    
    return greyscale_pixel_array

# Find structures with high contrast in the image by computing the standard deviation in the pixel neighbourhood
def computeStandardDeviationImage5x5(pixel_array, image_width, image_height):
    array=createInitializedGreyscalePixelArray(image_width, image_height)
    for x in range (image_height):
        for y in range(image_width):
            if (x==0) or (x==1) or (y==0) or (y==1) or (x==image_height-1) or (x==image_height-2) or (y==image_width-1) or (y==image_width-2): 
                array[x][y]=0.000
            else:
                outputPixel=0.000
                for xx in [-2,-1,0,1,2]:
                    for yy in [-2,-1,0,1,2]:
                        outputPixel+=pixel_array[x+xx][y+yy]
                meann=outputPixel/25.0
                summ=0.000
                
                for xx in [-2,-1,0,1,2]:
                    for yy in [-2,-1,0,1,2]:
                        summ+=(pixel_array[x+xx][y+yy]-meann)*(pixel_array[x+xx][y+yy]-meann)
                summ=math.sqrt(summ/25.0)
                array[x][y]=round(summ,3)
    return array

# contrast stretching
def scaleTo0And255AndQuantize(pixel_array, image_width, image_height):
    greyscale_pixel_array = createInitializedGreyscalePixelArray(image_width, image_height)
    minValue=255
    maxValue=0
    for i in range(image_height ):
        for j in range(image_width ):
            minValue=min(minValue,pixel_array[i][j])
            maxValue=max(maxValue,pixel_array[i][j])
    if minValue==maxValue:
        return greyscale_pixel_array
    else:
        for i in range(image_height ):
            for j in range(image_width ):
                greyscale_pixel_array[i][j]=int(round((255/(maxValue-minValue))*(pixel_array[i][j]-minValue)))
                
            
    return greyscale_pixel_array
# compute thresshold
def computeAdaptiveThreshold(pixel_array, image_width, image_height):
    summ=0.0
    for i in range(image_height):
        for j in range(image_width):
            summ+=pixel_array[i][j]
    summ=summ/(image_width*image_height)
    adaptiveThreshold=-1
    while adaptiveThreshold!= summ:
        adaptiveThreshold=summ
        left_count=0
        left_sum=0.0
        right_count=0
        right_sum=0.0
        for i in range(image_height):
            for j in range(image_width):
                if pixel_array[i][j]<summ:
                    left_count+=1
                    left_sum+=pixel_array[i][j]
                else:
                    right_count+=1
                    right_sum+=pixel_array[i][j]
        
        summ= round((left_sum/(left_count*1.0) + right_sum/(right_count*1.0))/2.0)
    return summ

# perform a thresholding operation to get the high contrast regions as a binary image
def computeThresholdGE(pixel_array, threshold_value, image_width, image_height):
    
    new_list=createInitializedGreyscalePixelArray(image_width, image_height)
    for i in range(image_height ):
        for j in range(image_width):
            if (threshold_value >pixel_array[i][j]):
                new_list[i][j]=0
            else:
                new_list[i][j]=255
    return new_list

# Erosion computation
def computeErosion8Nbh3x3FlatSE(pixel_array, image_width, image_height):
    new_array= createInitializedGreyscalePixelArray(image_width, image_height)
    for x in range(image_height):
        for y in range(image_width):
            if (x!=0) and (y!=0) and (x!=image_height-1) and (y!=image_width-1):
                check=True
                for xx in [-1,0,1]:
                    for yy in [-1,0,1]:
                        if pixel_array[x+xx][y+yy]==0:
                            check=False 
                            break
                    else:
                        
                        continue
                    break
                if check:
                    new_array[x][y]=1
    return new_array

# dilation computation
def computeDilation8Nbh3x3FlatSE(pixel_array, image_width, image_height):
    new_array= createInitializedGreyscalePixelArray(image_width, image_height)
    for x in range(image_height):
        for y in range(image_width):
            if pixel_array[x][y]!=0:
                for xx in [-1,0,1]:
                    for yy in [-1,0,1]:
                        if x+xx>= 0 and x+xx <image_height and y+yy>= 0 and y+yy <image_width :
                            new_array[x+xx][y+yy]=1
                        
    return new_array

# perform a connected component analysis
class Queue:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0,item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)

def computeConnectedComponentLabeling(pixel_array, image_width, image_height):
    count=1
    dictt={}
    check_dict={}
    for x in range(image_height):
        for y in range(image_width):
           if  pixel_array[x][y]!=0 and (x,y) not in check_dict.keys():
               new_queue=Queue()
               new_queue.enqueue((x,y))
               while new_queue.isEmpty()== False:
                   (xxx,yyy)=new_queue.dequeue()
                   
                   pixel_array[xxx][yyy]=count
                   check_dict[(xxx,yyy)]=1
                   if yyy-1>=0 and (xxx,yyy-1) not in check_dict.keys() and pixel_array[xxx][yyy-1]!=0:
                       check_dict[(xxx,yyy-1)]=1
                       new_queue.enqueue((xxx,yyy-1))
                   if yyy+1< image_width and (xxx,yyy+1) not in check_dict.keys() and pixel_array[xxx][yyy+1]!=0:
                       check_dict[(xxx,yyy+1)]=1
                       new_queue.enqueue((xxx,yyy+1))
                   if xxx-1>=0  and (xxx-1,yyy) not in check_dict.keys() and pixel_array[xxx-1][yyy]!=0:
                       check_dict[(xxx-1,yyy)]=1
                       new_queue.enqueue((xxx-1,yyy))
                   if xxx+1< image_height and (xxx+1,yyy) not in check_dict.keys() and pixel_array[xxx+1][yyy]!=0:
                       check_dict[(xxx+1,yyy)]=1
                       new_queue.enqueue((xxx+1,yyy))
               count+=1
    
    for i in range (image_height):
        for j in range ( image_width):
            if pixel_array[i][j] !=0:
                if pixel_array[i][j] not in dictt.keys():
                    dictt[pixel_array[i][j] ]=1
                else:
                    dictt[pixel_array[i][j] ]+=1
                    
    return (pixel_array,dictt)    
# This is our code skeleton that performs the license plate detection.
# Feel free to try it on your own images of cars, but keep in mind that with our algorithm developed in this lecture,
# we won't detect arbitrary or difficult to detect license plates!
def main():

    command_line_arguments = sys.argv[1:]

    SHOW_DEBUG_FIGURES = True

    # this is the default input image filename
    input_filename = "numberplate5.png"

    if command_line_arguments != []:
        input_filename = command_line_arguments[0]
        SHOW_DEBUG_FIGURES = False

    output_path = Path("output_images")
    if not output_path.exists():
        # create output directory
        output_path.mkdir(parents=True, exist_ok=True)

    output_filename = output_path / Path(input_filename.replace(".png", "_output.png"))
    if len(command_line_arguments) == 2:
        output_filename = Path(command_line_arguments[1])


    # we read in the png file, and receive three pixel arrays for red, green and blue components, respectively
    # each pixel array contains 8 bit integer values between 0 and 255 encoding the color values
    (image_width, image_height, px_array_r, px_array_g, px_array_b) = readRGBImageToSeparatePixelArrays(input_filename)

    

    # STUDENT IMPLEMENTATION here

    px_array = px_array_r
    # Conversion to Greyscale and stretching

    greyscale_pixel_array = computeRGBToGreyscale(px_array_r, px_array_g, px_array_b, image_width, image_height)
    stretched_greyscale_pixel_array=scaleTo0And255AndQuantize(greyscale_pixel_array, image_width, image_height)
    
    # Contrast Stretching
    smoothed_image = computeStandardDeviationImage5x5(stretched_greyscale_pixel_array, image_width, image_height)
    contrast_stretched_pixel_array= scaleTo0And255AndQuantize(smoothed_image, image_width, image_height)

    
    # thresholding operation
    
    threshold_value=150
    
    thresholded = computeThresholdGE(contrast_stretched_pixel_array, threshold_value, image_width, image_height) 
    dilated_eroded_image=list(thresholded)
   
   
      

    #perform dilations and erosions
    # several dilations
    for i in range(4):
        dilated_eroded_image =computeDilation8Nbh3x3FlatSE(dilated_eroded_image , image_width, image_height)

    # followed by several erosions
    for j in range(4):
        dilated_eroded_image=computeErosion8Nbh3x3FlatSE(dilated_eroded_image, image_width, image_height)
    
    # perform connected component analysis
    (ccimg,ccsizedict) = computeConnectedComponentLabeling(dilated_eroded_image ,image_width,image_height)
    
    for lbl in ccsizedict.keys():
        print("{}: {}".format(lbl, ccsizedict[lbl]))
    
    # initialize key_list and val_list of ccsizzeddict
    key_list=list(ccsizedict.keys())
    val_list=list(ccsizedict.values())
    sorted_connected_list=list(ccsizedict.values())
    sorted_connected_list.sort(reverse= True)
    
    # compute minx_x, max_x, min_y, max_y of conntected components of 1<=ration <=5
    for val in sorted_connected_list:
        connected_val=key_list[val_list.index(val)]
        min_x=image_width
        max_x=-1
        min_y=image_height
        max_y=-1
        for i in range (image_height):
            for j in range(image_width):
                if ccimg[i][j]== connected_val:
                    if i >= max_y:
                        max_y=i
                    if i<= min_y:
                        min_y=i
                    if j>= max_x:
                        max_x=j
                    if j<= min_x:
                        min_x=j 
        if (abs(max_x-min_x)/abs(max_y-min_y)<=5 and abs(max_x-min_x)/abs(max_y-min_y)>=1.5):    
            break
    print(connected_val)
    # setup the plots for intermediate results in a figure
    imagee=image.imread(input_filename)
    fig1, axs1 = pyplot.subplots(3, 2)
    axs1[0, 0].set_title('Original')
    axs1[0, 0].imshow(imagee)
    axs1[0, 1].set_title('Gray Scale')
    axs1[0, 1].imshow(stretched_greyscale_pixel_array, cmap='gray')
    axs1[1, 0].set_title('Contrast Stretching')
    axs1[1, 0].imshow(contrast_stretched_pixel_array, cmap='gray')
    axs1[1, 1].set_title('Thresholding')
    axs1[1, 1].imshow(thresholded, cmap='gray')
    axs1[2, 0].set_title('Dilitations and Erosions')
    axs1[2, 0].imshow(dilated_eroded_image, cmap='gray')
    axs1[2, 1].set_title('Final Image')
    axs1[2, 1].imshow(imagee)
    
    rect1 = Rectangle((min_x, min_y), max_x - min_x, max_y - min_y, linewidth=3,
                     edgecolor='g', facecolor='none')
    rect2=  Rectangle((min_x, min_y), max_x - min_x, max_y - min_y, linewidth=3,
                     edgecolor='g', facecolor='none')
    axs1[2, 0].add_patch(rect1)
    axs1[2, 1].add_patch(rect2)
    
    
    
    '''# compute a dummy bounding box centered in the middle of the input image, and with as size of half of width and height
    center_x = image_width / 2.0
    center_y = image_height / 2.0
    bbox_min_x = center_x - image_width / 4.0
    bbox_max_x = center_x + image_width / 4.0
    bbox_min_y = center_y - image_height / 4.0
    bbox_max_y = center_y + image_height / 4.0'''





    # Draw a bounding box as a rectangle into the input image
    '''axs1[1, 1].set_title('Final image of detection')
    axs1[1, 1].imshow(px_array, cmap='gray')
    rect = Rectangle((bbox_min_x, bbox_min_y), bbox_max_x - bbox_min_x, bbox_max_y - bbox_min_y, linewidth=1,
                     edgecolor='g', facecolor='none')
    axs1[1, 1].add_patch(rect)



    # write the output image into output_filename, using the matplotlib savefig method
    extent = axs1[1, 1].get_window_extent().transformed(fig1.dpi_scale_trans.inverted())
    pyplot.savefig(output_filename, bbox_inches=extent, dpi=600)'''

    if SHOW_DEBUG_FIGURES:
        # plot the current figure
        pyplot.show()


if __name__ == "__main__":
    main()
