from imutils.object_detection import non_max_suppression
import numpy as np
import time
import cv2
from PIL import Image

def detect_text(
        input_path,
        output_path,
        net,
        width=None,
        height=None,
        min_confidence=0.5,
        blur = False,
        strength = 25,
        sigma = 20,
        bounding_box = True):

    image = cv2.imread(input_path)
    orig = image.copy()
    (H, W) = image.shape[:2]
    
    if width is None:
        width = W

    if height is None:
        height = H

    # set the new width and height and then determine the ratio in change
    # for both the width and height
    (newW, newH) = (width, height)
    rW = W / float(newW)
    rH = H / float(newH)

    # resize the image and grab the new image dimensions
    image = cv2.resize(image, (newW, newH))
    (H, W) = image.shape[:2]

    # define the two output layer names for the EAST detector model that
    # we are interested -- the first is the output probabilities and the
    # second can be used to derive the bounding box coordinates of text
    layerNames = [
	   "feature_fusion/Conv_7/Sigmoid",
	   "feature_fusion/concat_3"
       ]

    # construct a blob from the image and then perform a forward pass of
    # the model to obtain the two output layer sets
    blob = cv2.dnn.blobFromImage(image, 1.0, (W, H),
    (123.68, 116.78, 103.94), swapRB=True, crop=False)
    start = time.time()
    net.setInput(blob)
    (scores, geometry) = net.forward(layerNames)
    end = time.time()
    # grab the number of rows and columns from the scores volume, then
    # initialize our set of bounding box rectangles and corresponding
    # confidence scores
    (numRows, numCols) = scores.shape[2:4]
    rects = []
    confidences = []

    # loop over the number of rows
    for y in range(0, numRows):
        # extract the scores (probabilities), followed by the geometrical
        # data used to derive potential bounding box coordinates that
        # surround text
        scoresData = scores[0, 0, y]
        xData0 = geometry[0, 0, y]
        xData1 = geometry[0, 1, y]
        xData2 = geometry[0, 2, y]
        xData3 = geometry[0, 3, y]
        anglesData = geometry[0, 4, y]

        # loop over the number of columns
        for x in range(0, numCols):
            # if our score does not have sufficient probability, ignore it
            if scoresData[x] < min_confidence:
               continue

            # compute the offset factor as our resulting feature maps will
            # be 4x smaller than the input image
            (offsetX, offsetY) = (x * 4.0, y * 4.0)

            # extract the rotation angle for the prediction and then
            # compute the sin and cosine
            angle = anglesData[x]
            cos = np.cos(angle)
            sin = np.sin(angle)

            # use the geometry volume to derive the width and height of
            # the bounding box
            h = xData0[x] + xData2[x]
            w = xData1[x] + xData3[x]

            # compute both the starting and ending (x, y)-coordinates for
            # the text prediction bounding box
            endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
            endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
            startX = int(endX - w)
            startY = int(endY - h)

            # add the bounding box coordinates and probability score to
            # our respective lists
            rects.append((startX, startY, endX, endY))
            confidences.append(scoresData[x])

    # apply non-maxima suppression to suppress weak, overlapping bounding
    # boxes
    boxes = non_max_suppression(np.array(rects), probs=confidences)

    # loop over the bounding boxes
    for (startX, startY, endX, endY) in boxes:
    	# scale the bounding box coordinates based on the respective
    	# ratios
        startX = int(startX * rW * 0.95)
        startY = int(startY * rH * 0.95)
        endX = int(endX * rW * 1.05)
        endY = int(endY * rH * 1.05)

        widthX = (endX-startX)
        heightY = (endY-startY)

        if blur:
            text = orig[startY:endY, startX:endX]
            # apply a gaussian blur on this new recangle image
            text = cv2.GaussianBlur(text,(strength, strength), sigma)
            # merge this blurry rectangle to our final image
            orig[startY:startY+text.shape[0], startX:startX+text.shape[1]] = text
        if bounding_box:
            cv2.rectangle(orig, (startX, startY), (endX, endY), (0, 255, 0), 2)

    # save image
    cv2.imwrite(output_path, orig)


