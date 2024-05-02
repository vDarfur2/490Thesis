import cv2
import os
import numpy as np


frame_width = 3840
frame_height = 1920
tile_width = frame_width / 12
tile_height = frame_height / 12

vp_width = tile_width * 5 # 5 tiles across
vp_height = tile_height * 7 # 7 tiles high

def degrees_to_pixels(yaw, pitch, frame_width=3840, frame_height=1920):
    
    # Convert degrees to pixel coordinates
    #x = int((yaw / 360.0) * frame_width)
    x = int(( yaw / 360.0) * frame_width) # swapping x direction

    y = int((pitch / 180.0) * frame_height)

    return x, y


def extract_viewport(frame, center_x, center_y, viewport_width=vp_width, viewport_height=vp_height):
    # Calculate the top left corner based on the center coordinates
    center_x = int(center_x)
    center_y = int(center_y)
    viewport_width = int(viewport_width)
    viewport_height = int(viewport_height)

    half_width = viewport_width // 2
    half_height = viewport_height // 2

    top_left_x = (center_x - half_width) % frame_width
    top_left_y = max(0, center_y - half_height)
    bottom_right_y = min(frame_height, center_y + half_height)

    if top_left_x + viewport_width > frame_width:
        # Wrap around horizontally
        right_width = frame_width - top_left_x
        left_width = viewport_width - right_width
        viewport_right = frame[top_left_y:bottom_right_y, top_left_x:frame_width]
        viewport_left = frame[top_left_y:bottom_right_y, 0:left_width]
        viewport = np.concatenate((viewport_right, viewport_left), axis=1)
    else:
        viewport = frame[top_left_y:bottom_right_y, top_left_x:top_left_x + viewport_width]

    return viewport

viewports = []
angles = []
coords_file = 'v14/vp_corr.txt'
with open(coords_file, 'r') as file:
    for line in file:
        yaw, pitch = map(float, line.split(','))
        angles.append((yaw, pitch))

frame_folder = "output_frames_mptcp_h"
frames = []
frame_files = sorted(os.listdir(frame_folder))  # Ensure frames are sorted correctly

for frame_file in frame_files:
    frame_path = os.path.join(frame_folder, frame_file)
    frame = cv2.imread(frame_path)
    frames.append(frame)


output_path = "viewport_output_mptcp_h/viewport_%04d.png"
for i, (frame, (yaw, pitch)) in enumerate(zip(frames, angles)):
    center_x, center_y = degrees_to_pixels(yaw, pitch)
    viewport = extract_viewport(frame, center_x, center_y)
    cv2.imwrite(output_path % i, viewport)  # Save each viewport as an image


