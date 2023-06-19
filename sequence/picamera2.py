import picamera2 as picamera
import time
import traceback
import os

camera = Picamera2()

camera_config = camera.create_still_configuration(main={"size": (1920, 1080)}, lores={"size": (640, 480)}, display="lores")
camera.configure(camera_config)
camera.start()
time.sleep(2)
camera.capture_file("sample.jpg")

print("done")
