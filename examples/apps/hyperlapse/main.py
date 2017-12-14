from scannerpy import Database, DeviceType, Job
from scannerpy.stdlib import parsers, video
import numpy as np
import math
from scipy import sparse
import matplotlib.pyplot as plt
import cv2
from timeit import default_timer as now

class Constants:
    def __init__(self, iw, ih, T):
        self.iw = iw
        self.ih = ih
        self.T =T
        self.d = math.floor(math.sqrt(self.ih**2 + self.iw**2))
        self.tau_c = 0.1 * self.d
        self.gamma = 0.5 * self.d

    w = 32
    g = 4
    lam_s = 200
    lam_a = 80
    # lam_s = .01
    # lam_a = .01
    tau_s = 200
    tau_a = 200

    # Speedup should be user defined
    v = 12

with Database(debug=True) as db:
    def create_database():
        db.ingest_videos([('example', '/n/scanner/datasets/hyperlapse/long.mp4')],
                         force=True)

    def extract_features():
        frame = db.table('example').as_op().range(0, 1000, item_size=100)
        features, keypoints = db.ops.FeatureExtractor(
            frame = frame,
            feature_type = db.protobufs.SURF,
            device = DeviceType.GPU)
        job = Job(columns = [features, keypoints], name = 'example_surf')
        db.run(job, force = True)

    def compute_matches():
        features, keypoints = db.table('example_surf').as_op().all(item_size=100)
        frame = db.table('example').as_op().range(0, 1000, item_size=100)
        frame_info = db.ops.InfoFromFrame(frame = frame, device = DeviceType.GPU)
        cost_matrix = db.ops.FeatureMatcher(
            features = features, keypoints = keypoints, frame_info = frame_info,
            stencil = range(0, 32),
            device = DeviceType.GPU)
        job = Job(columns = [cost_matrix], name = 'example_matches')
        db.run(job, force = True)

    def build_path():
        matches = db.table('example_matches')
        T = matches.num_rows()

        C = Constants(1080, 1920, T)
        Cm = np.zeros((C.T+1, C.T+1))
        # Cm = sparse.eye(C.T+1, C.T+1, format='lil')

        rows = matches.load(['cost_matrix'], parsers.array(np.float32))
        for i, row in rows:
            l = min(len(row), C.T+1 - (i+2+C.w))
            if l == 0: break
            Cm[i+1, (i+2):(i+2+l)] = row[:l]

        def vel_cost(i, j):
            return min(((j - i) - C.v) ** 2, C.tau_s)

        def acc_cost(h, i, j):
            return min(((j - i) - (i - h)) ** 2, C.tau_a)

        Dv = np.zeros((C.T+1, C.T+1))
        Tv = np.zeros((C.T+1, C.T+1), dtype=np.int32)

        # Initialization
        for i in range(1, C.g+1):
            for j in range(i+1, i+C.w+1):
                Dv[i,j] = Cm[i,j] + C.lam_s * vel_cost(i, j)

        # First pass: populate Dv
        for i in range(C.g, C.T+1):
            for j in range(i+1, min(i+C.w+1, C.T+1)):
                c = Cm[i,j] + C.lam_s * vel_cost(i, j)
                a = [Dv[i-k,i] + C.lam_a * acc_cost(i-k, i, j)
                     for k in range(1, C.w+1)]
                Dv[i,j] = c + min(a)
                Tv[i,j] = int(i - (np.argmin(a) + 1))

        # Second pass: trace back min cost path
        s = 0
        d = 0
        dmin = float("inf")
        for i in range(C.T-C.g, C.T+1):
            for j in range(i+1, min(i+C.w+1, C.T+1)):
                if Dv[i,j] < dmin:
                    dmin = Dv[i,j]
                    s = i
                    d = j

        path = [d]
        while s > C.g:
            path.insert(0, s)
            b = Tv[s, d]
            d = s
            s = b

        print path

        return path

    def encode_video(path):
        frames = list(db.table('example').load(['frame']))
        video.write_video(
            'hyperlapse.mkv',
            [f[0] for i, f in frames if i-1 in path],
            fps=12.0)
        # video.write_video(
        #     'timelapse.mkv',
        #     [f[0] for i, f in frames if i % 12 == 0],
        #     fps=12.0)


    # create_database()
    t = now()
    extract_features()
    print 'extract: {:.3f}'.format(now() - t)
    t = now()
    compute_matches()
    print 'match: {:.3f}'.format(now() - t)
    # path = build_path()
    # encode_video(path)
