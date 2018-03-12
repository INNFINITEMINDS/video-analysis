#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from __future__ import division
from imutils.video import FileVideoStream
from imutils.video import FPS
import argparse
import imutils
import time
import cv2
import face_recognition
from utils import basename
import db_helper

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", required=True, help="path to input video")
ap.add_argument("-s", "--show", action="store_true", help="show video with results")
args = vars(ap.parse_args())

faces = []
faces_count = []
data = []
tolerance = 0.55
name = basename(args["video"])

print("[INFO] Video name: " + name)
print("[INFO] Starting video processing...")
fvs = FileVideoStream(args["video"]).start()
time.sleep(1.0)

total_frames = int(fvs.stream.get(cv2.CAP_PROP_FRAME_COUNT))
frames_with_face = 0
frame_position = 0

fps = FPS().start()

while(fvs.more()):
    indexes = []
    frame_position += 1

    # process the frame
    frame = fvs.read()
    frame = imutils.resize(frame, width=450)
    rgb_frame = frame[:, :, ::-1]
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    timestamp = fvs.stream.get(cv2.CAP_PROP_POS_MSEC)

    if(len(face_encodings) > 0):
        frames_with_face += 1

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        index = -1
        matches = face_recognition.compare_faces(faces, face_encoding, tolerance)
        if True in matches:
            index = matches.index(True)
            faces_count[index] += 1
        else:
            faces.append(face_encoding)
            faces_count.append(1)
            index = len(faces) - 1

        indexes.append(index)

        if args["show"]:
            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label below the face
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, str(index), (left + 3, bottom - 3), font, 0.45,
                (0, 0, 255), 1)

    result = dict(id=frame_position, timestamp=timestamp, faces=indexes)
    data.append(result)

    if args["show"]:
        cv2.imshow("Video", frame)

    # update the FPS counter
    cv2.waitKey(1)
    fps.update()

frames_with_face_ratio = frames_with_face/total_frames
faces_relevance = []
for index, count in enumerate(faces_count):
    relevance = count / total_frames
    result = dict(index=index, relevance=relevance)
    faces_relevance.append(result)

document = {
    "name" : name,
    "frames_with_face_ratio" : frames_with_face_ratio,
    "faces_relevance" : faces_relevance,
    "data" : data
}

db_helper.insert("faceDetection", document)
db_helper.printDocumentByName("faceDetection", name)

# stop the timer and display FPS information
fps.stop()
print("[INFO] Elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] Approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
fvs.stop()
