import cv2
import numpy as np
from typing import List
import json

from vec2 import Vector2

# globals
clicks: int = 0
create_cutout: bool = False
cutout_rect_created: bool = False

selection_rect: List[Vector2] = []
visible_rect: List[List[int]] = [[0, 0], [640, 0], [640, 360], [0, 360]]


def define_cutout(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global clicks
        clicks += 1
        p: Vector2 = Vector2(x, y)
        selection_rect.append(p)

        if len(selection_rect) > 1:
            global create_cutout
            create_cutout = True

        print(x, y)


def get_point_on_vector(a: Vector2, b: Vector2, distance):
    direction: Vector2 = (b - a).normalized()
    final_x = a.x + distance * direction.x
    final_y = a.y + distance * direction.y
    return Vector2(final_x, final_y)


def main():
    # create and setup video capture
    VIDEO_CAPTURE: cv2.VideoCapture = cv2.VideoCapture(0)
    VIDEO_CAPTURE.set(cv2.CAP_PROP_FRAME_WIDTH, 640.0)
    VIDEO_CAPTURE.set(cv2.CAP_PROP_FRAME_HEIGHT, 360.0)

    # create image with mouse callback
    cv2.namedWindow("image")
    cv2.setMouseCallback("image", define_cutout)

    while VIDEO_CAPTURE.isOpened():
        ret, frame = VIDEO_CAPTURE.read()

        # get
        global clicks, cutout_rect_created, visible_rect
        if clicks % 2 == 0:
            global create_cutout
            if create_cutout:
                tl: Vector2 = selection_rect[0]
                tr: Vector2 = selection_rect[1]
                t_distance: float = (tl - tr).magnitude()

                bl_vec: Vector2 = tr.rotate_around(tl, -90)
                br_vec: Vector2 = tl.rotate_around(tr, 90)

                v_distance = t_distance / (16 / 9)

                bl_f = get_point_on_vector(tl, bl_vec, v_distance)
                br_f = get_point_on_vector(tr, br_vec, v_distance)

                selection_rect.append(Vector2(int(br_f.x), int(br_f.y)))
                selection_rect.append(Vector2(int(bl_f.x), int(bl_f.y)))

                create_cutout = False
                cutout_rect_created = True

        for point in selection_rect:
            cv2.circle(frame, point.to_tuple(), 2, (255, 0, 0), 1)

        # convert vec2 to lists
        selection_rect_ = []
        for point in selection_rect:
            selection_rect_.append(point.to_list())

        dst = None
        if cutout_rect_created:
            selection_rect_np = np.array(selection_rect_, np.float32)
            selection_rect_umat = cv2.UMat(selection_rect_np)

            visible_rect_np = np.array(visible_rect, np.float32)
            visible_rect_umat = cv2.UMat(visible_rect_np)

            M = cv2.getPerspectiveTransform(selection_rect_umat, visible_rect_umat)
            dst = cv2.warpPerspective(frame, M, (640, 360))
            # cutout_rect_created = False

        # show image
        if dst is not None:
            cv2.imshow('image', dst)
        else:
            cv2.imshow('image', frame)

        # wait for key input
        k = cv2.waitKey(int(100 / 30))
        if k == 27:  # wait for ESC key to exit
            cv2.destroyAllWindows()
            break
        elif k == 115:
            d: dict = dict()
            d['selected_rect'] = selection_rect_
            d['visible_rect'] = visible_rect
            json_string = json.dumps(d)
            with open('capture_area.json', 'w') as jsonfile:
                jsonfile = json_string
            print("saving")


if __name__ == '__main__':
    main()
