import subprocess
import csv

input_video = "path/to/your/360video.mp4"
output_path = "path/to/output/viewport_%04d.png"  # Saving frames as individual images

# Function to convert x,y to yaw,pitch (dummy function, replace with your actual conversion logic)
def xy_to_yaw_pitch(x, y):
    return (x-640) * 0.1, (y-360) * 0.1  # Example conversion

with open('coordinates.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        frame = int(row['frame'])
        x_center = int(row['x_center'])
        y_center = int(row['y_center'])
        
        # Convert x,y to yaw,pitch
        yaw, pitch = xy_to_yaw_pitch(x_center, y_center)
        
        # Generate FFmpeg command
        cmd = [
            'ffmpeg',
            '-i', input_video,
            '-vf', f'v360=input=e:output=e:yaw={yaw}:pitch={pitch}',
            '-frames:v', '1',
            output_path % frame
        ]
        
        # Execute the command
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
