import cv2
import numpy as np
import os
import csv

def select_rois(image_path):
    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Unable to read image at {image_path}")
        return None

    # Create a window
    window_name = f"Select ROIs - {os.path.basename(image_path)}"
    cv2.namedWindow(window_name)

    # Create a copy of the image for drawing
    img_copy = image.copy()
    overlay = image.copy()

    # Variables to store rectangle properties
    rect_start = None
    rect_end = None
    drawing = False
    rois = []

    def mouse_callback(event, x, y, flags, param):
        nonlocal rect_start, rect_end, drawing, img_copy, overlay

        if event == cv2.EVENT_LBUTTONDOWN:
            rect_start = (x, y)
            drawing = True
            overlay = img_copy.copy()

        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing:
                overlay = img_copy.copy()
                cv2.rectangle(overlay, rect_start, (x, y), (0, 255, 0), 2)

        elif event == cv2.EVENT_LBUTTONUP:
            rect_end = (x, y)
            drawing = False
            cv2.rectangle(img_copy, rect_start, rect_end, (0, 255, 0), 2)
            overlay = img_copy.copy()

    cv2.setMouseCallback(window_name, mouse_callback)

    print("\nInstructions:")
    print("- Click and drag to draw an ROI")
    print("- Press 'a' to add the current ROI")
    print("- Press 'r' to reset all ROIs")
    print("- Press 's' to save all ROIs and move to the next image")
    print("- Press 'q' to quit without saving")

    while True:
        display_img = overlay.copy()
        cv2.imshow(window_name, display_img)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            cv2.destroyAllWindows()
            return None
        elif key == ord('a') and rect_start and rect_end:
            roi = (min(rect_start[0], rect_end[0]),
                   min(rect_start[1], rect_end[1]),
                   abs(rect_end[0] - rect_start[0]),
                   abs(rect_end[1] - rect_start[1]))
            rois.append(roi)
            print(f"ROI added: x={roi[0]}, y={roi[1]}, width={roi[2]}, height={roi[3]}")
            rect_start = None
            rect_end = None
        elif key == ord('r'):
            rois = []
            img_copy = image.copy()
            overlay = img_copy.copy()
            print("All ROIs reset")
        elif key == ord('s'):
            cv2.destroyAllWindows()
            return rois

def process_images(image_folder, output_csv):
    # Ensure the image folder exists
    if not os.path.isdir(image_folder):
        print(f"Error: The folder {image_folder} does not exist.")
        return

    # Get all image files in the folder
    image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if not image_files:
        print(f"No image files found in {image_folder}")
        return

    # Prepare CSV file
    with open(output_csv, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['image_name', 'roi_id', 'roi_x', 'roi_y', 'roi_width', 'roi_height'])

        for image_file in image_files:
            image_path = os.path.join(image_folder, image_file)
            print(f"\nProcessing: {image_file}")
            
            rois = select_rois(image_path)
            
            if rois:
                for i, roi in enumerate(rois):
                    csvwriter.writerow([image_file, i+1, roi[0], roi[1], roi[2], roi[3]])
                print(f"{len(rois)} ROIs saved for {image_file}")
            else:
                print(f"Skipped {image_file}")

    print(f"\nROI information saved to {output_csv}")

if __name__ == "__main__":
    image_folder = "./images"  # Replace with your image folder path
    output_csv = "./roi_info.csv"  # Name of the output CSV file
    process_images(image_folder, output_csv)

