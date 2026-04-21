import open3d as o3d
import numpy as np

def render_view(pcd, output_path):
    vis = o3d.visualization.Visualizer()
    vis.create_window(visible=False)

    vis.add_geometry(pcd)
    vis.poll_events()
    vis.update_renderer()

    vis.capture_screen_image(output_path)
    vis.destroy_window()

    print(f"Saved view -> {output_path}")