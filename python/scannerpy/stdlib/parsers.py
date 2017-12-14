from __future__ import absolute_import, division, print_function, unicode_literals
import numpy as np
import cv2
import struct

from scannerpy.stdlib.poses import Pose

def bboxes(buf, protobufs):
    (num_bboxes,) = struct.unpack("=Q", buf[:8])
    buf = buf[8:]
    bboxes = []
    for i in range(num_bboxes):
        (bbox_size,) = struct.unpack("=Q", buf[:8])
        buf = buf[8:]
        box = protobufs.BoundingBox()
        box.ParseFromString(buf[:bbox_size])
        buf = buf[bbox_size:]
        bboxes.append(box)
    return bboxes

def poses(buf, protobufs):
    if len(buf) == 1:
        return []

    kp_size = (Pose.POSE_KEYPOINTS +
               Pose.FACE_KEYPOINTS +
               Pose.HAND_KEYPOINTS * 2) * 3
    poses = []
    all_kp = np.frombuffer(buf, dtype=np.float32)
    for j in range(0, len(all_kp), kp_size):
        pose = Pose.from_buffer(all_kp[j:(j+kp_size)].tobytes())
        poses.append(pose)
    return poses


def histograms(bufs, protobufs):
    # bufs[0] is None when element is null
    if bufs[0] is None:
        return None
    return np.split(np.frombuffer(bufs[0], dtype=np.dtype(np.int32)), 3)

def classes(bufs, protobufs):
    if bufs[0] is None:
        return None
    return np.split(np.frombuffer(bufs[0], dtype=np.dtype(np.int32)), 1)


def frame_info(buf, protobufs):
    info = protobufs.FrameInfo()
    info.ParseFromString(buf)
    return info


def flow(bufs, protobufs):
    if bufs[0] is None:
        return None
    output = np.frombuffer(bufs[0], dtype=np.dtype(np.float32))
    info = frame_info(bufs[1], db)
    return output.reshape((info.height, info.width, 2))


def array(ty):
    def parser(bufs, protobufs):
        return np.frombuffer(bufs[0], dtype=np.dtype(ty))
    return parser


def image(bufs, protobufs):
    return cv2.imdecode(np.frombuffer(bufs[0], dtype=np.dtype(np.uint8)),
                        cv2.IMREAD_COLOR)

def raw_frame_gen(shape0, shape1, shape2, typ):
    def parser(bufs, protobufs):
        output = np.frombuffer(bufs, dtype=typ)
        return output.reshape((shape0, shape1, shape2))
    return parser
