import cv2

VIDEO_PATH = 'video2.mp4'
SCREEN_WIDTH = 128
SCREEN_HEIGTH = 68
FRAME_DELAY = 16
OUTPUT_FILE = 'frame_data2.h'

def convert_video():

    frame_list = []

    cap = cv2.VideoCapture(VIDEO_PATH)

    print("Extracting and Processing frame using Otsu's Algorithm")

    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            break

        # Adkust the frame to the OLED screen Resolution
        re_frame = cv2.resize(frame, (SCREEN_WIDTH, SCREEN_HEIGTH))

        # Convert the video in gray video
        gray  = cv2.cvtColor(re_frame, cv2.COLOR_BGR2GRAY)

        # Otsu Algorithm applying
        _, otsu = cv2.threshold(gray, 0,255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)


        flat = otsu.flatten()
        byte_array = []

        for i in range(0, len(flat), 8):
            byte_val = 0
            for bit in range(8):
                if flat[i+bit] > 0:
                    byte_val|= (1 << (7-bit))
                    # print(byte_val)

            byte_array.append(f"0x{byte_val:02x}")
            # print(byte_array)

        frame_list.append(byte_array)
        # print(frame_list)


        # cv2.imshow("Original Video",re_frame)
        # cv2.imshow("Gray Video",gray)
        # cv2.imshow("Gray Video",otsu)
    
    cap.release()

    # Calculate exact array sizes
    num_frames = len(frame_list)
    bytes_per_frame = (SCREEN_WIDTH * SCREEN_HEIGTH) // 8

    print(f"Formatting {num_frames} frames into flawless C++...")

    # 5. WRITE TO C++ HEADER FILE (Fixing all comma errors)
    with open(OUTPUT_FILE, 'w') as f:
        # Standard includes for ESP32 PROGMEM
        f.write("#include <Arduino.h>\n")
        f.write("#include <pgmspace.h>\n\n")
        
        f.write(f"#define FRAME_WIDTH {SCREEN_WIDTH}\n")
        f.write(f"#define FRAME_HEIGHT {SCREEN_HEIGTH}\n")
        f.write(f"#define FRAME_DELAY {FRAME_DELAY}\n")
        f.write(f"#define NUM_FRAMES {num_frames}\n\n")

        # Start the 2D array
        f.write(f"const unsigned char frames[{num_frames}][{bytes_per_frame}] PROGMEM = {{\n")

        # Safely wrap every frame inside its own { } to prevent C++ compiler errors
        for i, frame_bytes in enumerate(frame_list):
            f.write(f"  {{ // Frame {i}\n    ")
            
            # Format bytes into neat rows of 16
            lines = []
            for j in range(0, len(frame_bytes), 16):
                lines.append(", ".join(frame_bytes[j : j + 16]))
            
            f.write(",\n    ".join(lines))
            
            # Close the frame's bracket. Add a comma ONLY if it's not the last frame.
            if i < num_frames - 1:
                f.write("\n  },\n")
            else:
                f.write("\n  }\n") # NO COMMA on the last frame!

        f.write("};\n")

    print(f"Success! Saved to {OUTPUT_FILE}. Ready to compile in PlatformIO.")




if __name__ == '__main__':
    convert_video()