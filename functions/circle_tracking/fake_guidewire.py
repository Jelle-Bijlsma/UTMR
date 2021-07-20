import cv2
import numpy as np

# draw 10 random circles in an image. The

window_name = 'Image'
radius = 10
thickness = 2
dx = 50
dy = 50
border = [0, 500]

seed_x = np.random.randint(50, 450)
seed_y = np.random.randint(50, 100)
coordinates = [seed_x, seed_y]



while True:
    image = np.zeros([500, 500], np.uint8)
    seed_x = np.random.randint(50, 450)
    seed_y = np.random.randint(50, 100)

    coordinates = [seed_x, seed_y]

    for element in range(1, 10):
        coord_add_x = np.random.randint(-dx, dy)
        coord_add_y = np.random.randint(20, dy)
        coord_add = np.stack((coord_add_x, coord_add_y))
        # print(coord_add)
        coordinates = [sum(x) for x in zip(coordinates, coord_add)]
        # for element in centre_list:
        # print(coordinates)
        # abc = np.column_stack((coordinates[0], coordinates[1]))
        # print(abc[0])
        # image = cv2.circle(img=image, center=abc, radius=radius, color=255, thickness=thickness)
        image = cv2.circle(img=image, center=coordinates, radius=radius, color=255, thickness=thickness)
        row, col = image.shape
        mean = 0
        var = 0.1
        sigma = var ** 0.5
        gauss = np.random.normal(mean, sigma, (row, col))
        gauss = gauss.reshape(row, col)
        noisy = np.ndarray.astype(gauss, 'uint8')
        image += noisy
        print(type(image))
        image = np.ndarray.astype(image,'uint8')
        print(type(image))
        blur = cv2.GaussianBlur(noisy, (5, 5), 0)
        image = np.ndarray.astype(blur,'uint8')

    output = image.copy()
    circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, 4, 20, minRadius=5, maxRadius=15)
    print(circles)
    # ensure at least some circles were found
    if circles is not None:
        print("hey")
        # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")
        # loop over the (x, y) coordinates and radius of the circles
        for (x, y, r) in circles:
            # draw the circle in the output image, then draw a rectangle
            # corresponding to the center of the circle
            cv2.circle(output, (x, y), r, 255, 4)
            # cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
        # show the output image
        cv2.imshow("output", np.hstack([image, output]))
        cv2.waitKey(0)



