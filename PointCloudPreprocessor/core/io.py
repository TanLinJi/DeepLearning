import open3d as o3d

def load_point_cloud(file_path: str):
    """
    读取点云文件
    支持: .ply .pcd .xyz
    """
    print(f"Loading point cloud: {file_path}")
    pcd = o3d.io.read_point_cloud(file_path)

    if pcd.is_empty():
        raise ValueError("Point cloud is empty or failed to load.")

    print("Point cloud loaded successfully!")
    print(pcd)

    return pcd


def visualize_point_cloud(pcd):
    """
    可视化点云
    """
    o3d.visualization.draw_geometries([pcd])