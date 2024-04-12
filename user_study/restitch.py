import ffmpeg


frameWidth = 3840
frameHeight = 2048
widthTiles = 12
heightTiles = 12
total_frames = 1500  # Assuming a 1-minute video at 25 fps
num_tiles_x = 12
num_tiles_y = 12

tile_width = frameWidth / widthTiles
tile_height = frameHeight / heightTiles


# Mapping from quality in play log to  
qp_dict = {0: 17, 1:22, 2:27, 3:32, 4:37, 5:42, 6:50}

def get_tiles_quality_by_frame_id(frame_id, file_path):
    with open(file_path, 'r') as file:
        next(file)
        for line in file:
            elements = line.split()

            if int(elements[0]) == frame_id:
                # Return the tiles_quality for the matching frame ID
                
                return elements[-1]  # Assuming tiles_quality is the last element in the line

    return None


# Tiles available at a frame
def tiles_in_frame(frame_trace_file):
    tile_dict = {}
    with open(frame_trace_file, 'r') as file:
        for line in file:
            elements = line.strip().split()

            frame_id = int(elements[0])
            # The remaining elements represent tiles in the frame
            tiles = elements[2:]
            # Store the tiles in the dictionary with the frame ID as the key
            tile_dict[frame_id] = tiles

    return tile_dict

# Given tiles quality list, create a dictionary that maps a tile_id to a tile quality
def assign_tile_quality(tiles_quality):
    vp_quality_dict = {}
    vp_tile_quality_list = tiles_quality.split(',')
    xy_dict = tile_id_to_xy(widthTiles, heightTiles)
    for tq in vp_tile_quality_list:
        tile, quality = tq.split('_')
        tile = int(tile)
        quality = int(quality)
        vp_quality_dict[xy_dict[tile]] = qp_dict[quality]
    
    quality_dict = {}
    for i in range(0, widthTiles):
        for j in range(0, heightTiles):
            if (i, j) in vp_quality_dict:
                quality_dict[(i,j)] = vp_quality_dict[(i,j)]
            else:
                quality_dict[(i,j)] = qp_dict[0]
   
    quality_dict = dict(sorted(quality_dict.items(), key=lambda item: item[0][1]))
   
    return quality_dict


def apply_quality_to_tiles(frame_number, frame_quality_dict):
    # Iterate over each tile in the frame and assign the quality value
    index = 0
    
    for tile_coords, quality_value in frame_quality_dict.items():
        x, y = tile_coords
        # Define the crop filter to extract the specific tile
        crop_filter = 'crop={w}:{h}:{x}:{y}'.format(w=tile_width, h=tile_height, x=x * tile_width, y=y * tile_height)
        # Use FFmpeg to create a tile with the assigned quality value
        input_filename = 'v8/%d_frames/frame_%04d.png' % (quality_value, frame_number)
        output_filename = 'output_tiles/temp_%03d_%04d.png' % (index, frame_number)
        ffmpeg.input(input_filename)\
            .output(output_filename, vf=crop_filter, loglevel="quiet")\
            .run()
        
        index += 1


# Map tile IDs to x,y Coordinates
def tile_id_to_xy(widthTiles, heightTiles):
    tile_id = 0
    tile_dict = {}
    for i in range(0, widthTiles):
        for j in range(0, heightTiles):
            tile_dict[tile_id] = (j ,i)
            tile_id += 1

    return tile_dict

# File list for ffmpeg stitching
def create_file_list(frame_number, num_tiles=144):
    with open('input_files.txt', 'w') as f:
        for i in range(num_tiles):
            f.write(f"file 'output_tiles/temp_{i:03d}_{frame_number:04d}.png'\n")

def restitch_frames(frame_number):
    num_tiles = 144
    # Create the file list
    create_file_list(frame_number, num_tiles)
    
    # Command to stitch images using the tile filter
    (
        ffmpeg
        .input('input_files.txt', format='concat', safe=0)
        .filter('tile', layout='12x12')
        .output(f'output_frames/final_frame_{frame_number:04d}.png', loglevel="quiet")
        .run()
    )




def create_output_video():
    # Create the output video from stitched frames
    ffmpeg.input('output_frames/stitched_%04d.png', framerate=25).output('output_video.mp4', codec='libx264').run()

def main():
    
    file_path = 'v8/play_log_2024-04-04_03_43_21.txt'
    # Iterate over each frame
    for frame_number in range(1, total_frames + 1):
        frame_quality_dict = assign_tile_quality(get_tiles_quality_by_frame_id(frame_number, file_path))
        # Assign quality values for tiles in the current frame

        # Apply quality values to tiles in the current frame
        apply_quality_to_tiles(frame_number, frame_quality_dict)

        # Restitch the tiled frames back into a video
        restitch_frames(frame_number)

    # Create the output video from stitched frames
    create_output_video()




if __name__ == "__main__":
    main()