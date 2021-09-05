import cv2
import numpy as np


class TwoDimMover:
    def __init__(self, dimensions: list) -> np.array([]):
        """
        This class acts as a workhorse to move a rectangle arround
        :param dimensions: [x,y] screen size
        """
        self.frame = np.zeros(dimensions)
        self.returnframe = self.frame
        self.start = [200, 200]
        self.armlength = 50
        self.cur_pos = self.start
        self.dy = 10
        self.dx = 10
        self.points = []

    def move(self, direction: str):
        if direction == 'up':
            self.cur_pos += [0, self.dy]
        if direction == 'down':
            self.cur_pos += [0, -self.dy]
        if direction == 'left':
            self.cur_pos += [-self.dx, 0]
        if direction == 'right':
            self.cur_pos += [self.dx, 0]
        self.get_points()
        return self.draw_rect()

    def get_points(self) -> None:
        """
        This class acts as a workhorse to move a rectangle arround
        :param dimensions: [x,y] screen size
        :return: np.array with the information inside
        """
        self.points = []
        self.points.append(self.start)
        self.points.append(self.points[-1] + [50, 0])
        self.points.append(self.points[-1] + [0, 50])
        self.points.append(self.points[-1] + [-50, 0])
        self.points.append(self.start)
        return None

    def draw_rect(self):
        """this ting be drawing rects"""
        out = self.frame
        for x in range(0, 4):
            begin = tuple(self.points[x])
            end = tuple(self.points[x+1])
            cv2.line(out, begin, end, 255, 4)

        return out
