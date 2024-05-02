import ffmpeg
def create_output_video():
    # Create the output video from stitched frames
    ffmpeg.input('viewport_output_quic/viewport_%04d.png', framerate=25).output('v27quic_viewport.mp4', codec='libx264').run()

create_output_video()
