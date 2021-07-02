import cv2

a = cv2.imread("../dicom/png/IM_0011.png")
cv2.imshow("kk",a)

a = a + round(a*0.3)

cv2.waitKey(0)

# closing all open windows
cv2.destroyAllWindows()