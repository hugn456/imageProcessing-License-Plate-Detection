# imageProcessing-License-Plate-Detection
![image](https://user-images.githubusercontent.com/90328373/177265003-a850cc1f-ac67-45a2-b8ec-bac41255e1ba.png)

**Aim: Detect Bounding Box around the license plate in an 
image of a car**

**HOW?**

**1) Conversion to Greyscale**
+ Read the input image, convert RGB data to greyscale and stretch the values to lie between 0 and 255.

![image](https://user-images.githubusercontent.com/90328373/177266006-c0b56b3d-cd86-4bd6-887c-03cd36dc4835.png)

**2) Contrast Stretching**
+ Find structures with high contrast in the image by computing the standard deviation in the pixel neighbourhood.
+ Use a 5x5 neighbourhood and stretch the result between 0 and 255.

![image](https://user-images.githubusercontent.com/90328373/177266447-3b9a0f3f-1a07-48a0-987d-d829fe990974.png)

**3) Thresholding for Segmentation**
+ Perform a thresholding operation to get the high contrast regions as a binary image ( a good threshold value is 
around 150).

![image](https://user-images.githubusercontent.com/90328373/177266761-1f323b33-1dfa-409b-8291-8548ac35b3ed.png)

**4) Morphological operations**
+ Perform several 3x3 dilation steps followed by several 3x3 erosion steps to get a “blob” region for the license plate (morphological closing).

![image](https://user-images.githubusercontent.com/90328373/177267024-40cba0bd-21b7-4c27-97e1-f66973c5154e.png)

**5) Connected component analysis**
+ Perform a connected component analysis to find the largest connected object.
+ Additionally, you could also analyze the aspect ratio of the generated bounding box and look for the largest connected component within an aspect ratio (i.e. width / height) range between 1.5 and 5.

**6) Extract the final bounding box**
+ Extract the final bounding box around this region, by looping over the image and looking for the minimum and maximum x and y coordinates of the pixels of the previously determined connected component.

![image](https://user-images.githubusercontent.com/90328373/177267534-823dde4d-32f3-4440-ac73-56fa1d8b1730.png)



