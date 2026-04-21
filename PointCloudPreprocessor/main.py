import os
import numpy as np
from core.io import load_point_cloud
from core.projector import normalize_points, generate_6_views, save_image


def pcd_to_numpy(pcd):
    return np.asarray(pcd.points)


if __name__ == "__main__":
    import sys

    file_path = sys.argv[1]
    pcd = load_point_cloud(file_path)

    points = normalize_points(pcd_to_numpy(pcd))

    os.makedirs("output", exist_ok=True)

    views = generate_6_views(points)

    for name, img in views.items():
        path = f"output/{name}.png"
        save_image(img, path)
        print("Saved:", path)