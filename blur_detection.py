#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from imutils.video import FileVideoStream
from imutils.video import FPS
import argparse
import imutils
import time
import cv2
import db_helper
import utils


def varianceOfLaplacian(image):
    # compute the Laplacian of the image and then return the focus
    # measure, which is simply the variance of the Laplacian
    return cv2.Laplacian(image, cv2.CV_64F).var()


def qualityMark(fm):
    # return quality mark based on variance of the Laplacian, 0 is the worst,
    # 5 is the best
    if fm < 50:
        return 1
    elif (fm >= 50) and (fm < 100):
        return 2
    elif (fm >= 100) and (fm < 250):
        return 3
    elif (fm >= 250) and (fm < 500):
        return 4
    else:
        return 5


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", required=True, help="path to input video")
ap.add_argument("-s", "--show", action="store_true", help="show video with results")
args = vars(ap.parse_args())

print("[INFO] Starting video processing...")
fvs = FileVideoStream(args["video"]).start()
time.sleep(1.0)

total_frames = int(fvs.stream.get(cv2.CAP_PROP_FRAME_COUNT))
fmSum = 0
data = []

fps = FPS().start()

while(fvs.more()):
    # process the frame
    frame = fvs.read()
    frame = imutils.resize(frame, width=450)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    fm = varianceOfLaplacian(gray)
    quality = qualityMark(fm)
    fmSum += fm
    timestamp = fvs.stream.get(cv2.CAP_PROP_POS_MSEC)

    # append the result to an array
    result = dict(timestamp=timestamp, fm=fm, quality=quality)
    data.append(result)

    # show the frame and the result
    if args["show"]:
        cv2.putText(frame, "{:.2f}".format(fm), (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
        cv2.imshow("Video", frame)

    # update the FPS counter
    cv2.waitKey(1)
    fps.update()

# save results to db
name = utils.basename(args["video"])
avg = fmSum/total_frames
document = {
    "name" : name,
    "avg" : avg,
    "data" : data
}

db_helper.insert("blurDetection", document)
db_helper.printDocumentByName("blurDetection", name)

# stop the timer and display FPS information
fps.stop()
print("[INFO] Avg. variance of Laplacian: {:.2f}".format(avg))
print("[INFO] Elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] Approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
fvs.stop()
