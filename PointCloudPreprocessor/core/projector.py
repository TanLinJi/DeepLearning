import numpy as np
from PIL import Image


# ============ 基础预处理 ============

def normalize_points(points):
    """归一化点云到 [-1, 1]"""
    center = np.mean(points, axis=0)
    points = points - center
    scale = np.max(np.linalg.norm(points, axis=1))
    return points / scale


# ============ 旋转函数 ============

def rotate_points(points, axis, angle):
    """绕坐标轴旋转点云"""
    angle = np.deg2rad(angle)

    if axis == "x":
        R = np.array([
            [1, 0, 0],
            [0, np.cos(angle), -np.sin(angle)],
            [0, np.sin(angle), np.cos(angle)]
        ])
    elif axis == "y":
        R = np.array([
            [np.cos(angle), 0, np.sin(angle)],
            [0, 1, 0],
            [-np.sin(angle), 0, np.cos(angle)]
        ])
    elif axis == "z":
        R = np.array([
            [np.cos(angle), -np.sin(angle), 0],
            [np.sin(angle), np.cos(angle), 0],
            [0, 0, 1]
        ])
    else:
        raise ValueError("axis must be x/y/z")

    return points @ R.T


# ============ 投影函数 ============

def project_view(points, img_size=224):
    """XY平面投影 + 深度图"""
    proj = points[:, [0, 1]]
    depth = points[:, 2]

    proj = (proj + 1) / 2 * (img_size - 1)
    proj = proj.astype(np.int32)

    img = np.zeros((img_size, img_size))

    for i in range(len(proj)):
        x, y = proj[i]
        if 0 <= x < img_size and 0 <= y < img_size:
            img[y, x] = max(img[y, x], depth[i])

    img = img - img.min()
    if img.max() > 0:
        img = img / img.max()

    return (img * 255).astype(np.uint8)


# ============ 6视角生成 ============

def generate_6_views(points, img_size=224):
    views = {
        "front": points,
        "back": rotate_points(points, "y", 180),
        "left": rotate_points(points, "y", 90),
        "right": rotate_points(points, "y", -90),
        "top": rotate_points(points, "x", -90),
        "bottom": rotate_points(points, "x", 90),
    }

    images = {}

    for name, pts in views.items():
        img = project_view(pts, img_size)
        images[name] = img

    return images


# ============ 保存图片 ============

def save_image(img, path):
    Image.fromarray(img).save(path)