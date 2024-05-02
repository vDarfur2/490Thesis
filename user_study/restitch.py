import ffmpeg
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

frameWidth = 3840 # for frameWidth and frameHeight adjust based on video dimensions
frameHeight = 1920
widthTiles = 12
heightTiles = 12
total_frames = 1475 # adjust based on frames in your processed video
num_tiles_x = 12
num_tiles_y = 12

tile_width = frameWidth / widthTiles
tile_height = frameHeight / heightTiles
file_lock = threading.Lock()

# Mapping from quality in play log to  qp value
qp_dict = {0: 42, 2:37, 3:32, 4:27, 5:22}

def get_tiles_quality_by_frame_id(frame_id, file_path):
    with open(file_path, 'r') as file:
        next(file)
        for line in file:
            elements = line.split()

            if int(elements[0]) == frame_id:
                # Return the tiles_quality for the matching frame ID
                
                return elements[-1]  # Assuming tiles_quality is the last element in the line

    return None

# Given tiles quality list, create a dictionary that maps a tile_id to a tile quality
def assign_tile_quality(tiles_quality):
    vp_quality_dict = {}
    vp_tile_quality_list = tiles_quality.split(',')
    xy_dict = tile_id_to_xy(widthTiles, heightTiles)
    for tq in vp_tile_quality_list:
        tile, quality = tq.split('_')
        tile = int(tile)
        if tile == 0:
            continue
        quality = int(quality)
        temp = xy_dict[tile]
        vp_quality_dict[temp] = qp_dict[quality]
    
    quality_dict = {}
    for i in range(1, widthTiles+1):
        for j in range(1, heightTiles+1):
            if (i, j) in vp_quality_dict:
                quality_dict[(i,j)] = vp_quality_dict[(i,j)]
            else:
                quality_dict[(i,j)] = qp_dict[0]
   
    quality_dict = dict(sorted(quality_dict.items(), key=lambda item: item[0][1]))
    
    return quality_dict

# For all tiles in frame, gets tile of the quality defined for that tile in the frame_quality_dict
def apply_quality_to_tiles(frame_number, frame_quality_dict):
    index = 1

    for tile_coords, quality_value in frame_quality_dict.items():
        x, y = tile_coords
        x -= 1
        y -= 1
        # Define the crop filter to extract the specific tile
        crop_filter = 'crop={w}:{h}:{x}:{y}'.format(w=tile_width, h=tile_height, x=x * tile_width, y=y * tile_height)
        # Use FFmpeg to create a tile with the assigned quality value
        input_filename = 'v27/%d_frames/frame_%04d.png' % (quality_value, frame_number)
        output_filename = 'output_tiles/temp_%03d_%04d.png' % (index, frame_number)
        ffmpeg.input(input_filename)\
            .output(output_filename, vf=crop_filter, loglevel="quiet")\
            .run()
        
        index += 1


# Map tile IDs to x,y Coordinates
def tile_id_to_xy(widthTiles, heightTiles):
    tile_id = 1
    tile_dict = {}
    for i in range(1, widthTiles+1):
        for j in range(1, heightTiles+1):
            tile_dict[tile_id] = (j ,i)
            tile_id += 1

    return tile_dict

# File list for ffmpeg stitching
def create_file_list(frame_number):
    num_tiles = 144
    with file_lock:
        with open(f'input_files/input_files_{frame_number:04d}.txt', 'w') as f:
            for i in range(1, num_tiles+1):
                f.write(f"file '../output_tiles/temp_{i:03d}_{frame_number:04d}.png'\n")

def process_frame(frame_number, file_path):
    frame_quality_dict = assign_tile_quality(get_tiles_quality_by_frame_id(frame_number, file_path))
    apply_quality_to_tiles(frame_number, frame_quality_dict)
    restitch_frames(frame_number)

def restitch_frames(frame_number):
    num_tiles = 144
    # Create the file list
    create_file_list(frame_number)   
    (
        ffmpeg
        .input(f'input_files/input_files_{frame_number:04d}.txt', format='concat', safe=0)
        .filter('tile', layout='12x12')
        .output(f'output_frames_tcp_v27/final_frame_{frame_number:04d}.png')
        .run()
    )

def main():
    
    file_path = 'v14/mptcp_play_log.txt'
    protocol = sys.argv[1]
    # Using ThreadPoolExecutor to parallelize frame processing
    with ThreadPoolExecutor(max_workers=12) as executor:  # Adjust max_workers based on your system's capabilities
        futures = [executor.submit(process_frame, frame_number, file_path) for frame_number in range(1, total_frames + 1)]
        for future in as_completed(futures):
            future.result()


if __name__ == "__main__":
    main()


