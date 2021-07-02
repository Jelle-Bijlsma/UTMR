import cv2

# construct VideoCapture
cap = cv2.VideoCapture("video.avi")

while cap.isOpened():
    # .read returns a bool (ret) and the frame
    ret, frame = cap.read()

    # not read correctly means the stream ended
    if not ret:
        print("stream ended")
        break

    cv2.imshow('frame',frame)

    # set a speed. Time is in ms
    # 15 fps is approx 67 ms.
    if cv2.waitKey(67) == ord('q'):
        # wait for 67 ms each frame. If 'q' is pressed break
        break

cap.release()
cv2.destroyAllWindows()


# https://docs.opencv.org/master/dd/d43/tutorial_py_video_display.html
