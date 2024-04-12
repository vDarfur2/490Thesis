
#!/bin/bash

video=v8.mp4

echo "using video: $video"

echo "creating videos at different Quantization Parameters (17, 22, 27, 32, 37, 42, 50)" 

ffmpeg -i "$video" -c:v libx264 -qp 17 17.mp4
ffmpeg -i "$video" -c:v libx264 -qp 22 22.mp4
ffmpeg -i "$video" -c:v libx264 -qp 27 27.mp4
ffmpeg -i "$video" -c:v libx264 -qp 32 32.mp4
ffmpeg -i "$video" -c:v libx264 -qp 37 37.mp4
ffmpeg -i "$video" -c:v libx264 -qp 42 42.mp4
ffmpeg -i "$video" -c:v libx264 -qp 50 50.mp4

echo "getting frames from each video" 


ffmpeg -i 17.mp4 17_frames/frame_%04d.png
ffmpeg -i 22.mp4 22_frames/frame_%04d.png
ffmpeg -i 27.mp4 27_frames/frame_%04d.png
ffmpeg -i 32.mp4 32_frames/frame_%04d.png
ffmpeg -i 37.mp4 37_frames/frame_%04d.png
ffmpeg -i 42.mp4 42_frames/frame_%04d.png 
ffmpeg -i 50.mp4 50_frames/frame_%04d.png

