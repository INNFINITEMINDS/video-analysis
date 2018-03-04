#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from imutils.video import FileVideoStream
from imutils.video import FPS
import argparse
import imutils
import time
import cv2


def variance_of_laplacian(image):
    # compute the Laplacian of the image and then return the focus
    # measure, which is simply the variance of the Laplacian
    return cv2.Laplacian(image, cv2.CV_64F).var()


def quality_mark(fm):
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
ap.add_argument("-o", "--output", required=True, help="path to video processing results")
ap.add_argument("-s", "--show", action="store_true", help="show video with results")
args = vars(ap.parse_args())

print("[INFO] Starting video processing...")
fvs = FileVideoStream(args["video"]).start()
time.sleep(1.0)

total_frames = int(fvs.stream.get(cv2.CAP_PROP_FRAME_COUNT))
fm_sum = 0

file = open(args["output"], 'wb')
file.write('Timestamp, Variance of Laplacian, Quality Mark')
file.write('\n')

fps = FPS().start()

while(fvs.more()):
    # process the frame
    frame = fvs.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    fm = variance_of_laplacian(gray)
    fm_sum += fm
    timestamp = fvs.stream.get(cv2.CAP_PROP_POS_MSEC)

    # save results to file
    file.write('{0}, {1}, {2}'.format(timestamp, fm, quality_mark(fm)))
    file.write('\n')

    # show the frame and the result
    if args["show"]:
        frame = imutils.resize(frame, width=450)
        cv2.putText(frame, "{:.2f}".format(fm), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
        cv2.rectangle(frame, (0, 1080), (int(fm*1.6), 1040), (0, 0, 255), thickness=cv2.FILLED)
        cv2.imshow("Video", frame)

    # update the FPS counter
    cv2.waitKey(1)
    fps.update()

# stop the timer and display FPS information
fps.stop()
print("[INFO] Avg. variance of Laplacian: {:.2f}".format(fm_sum/total_frames))
print("[INFO] Elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] Approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
fvs.stop()
file.close()
