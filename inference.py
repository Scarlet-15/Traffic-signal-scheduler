import csv
from ultralytics import YOLO
import cv2

# Initialize YOLO model
model = YOLO("./models/model.pt")

# Load the image
image_path = "./images/sample.jpg"
image = cv2.imread(image_path)

# Load ROI data from the CSV file
roi_file = './roi_selection/roi_info.csv'
roi_data = []

with open(roi_file, mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        if row['image_name'] == 'sample.jpg':  # Filter rows for the current image
            roi_data.append([int(row['roi_id']), int(row['roi_x']), int(row['roi_y']), int(row['roi_width']), int(row['roi_height'])])

# Perform inference on the image
results = model([image])

# Initialize dictionary to hold object counts in each ROI
object_counts = {}

# Define object classes based on VISDRONE dataset (Adjust based on your model's class indices)
visdrone_classes = ['pedestrian', 'people', 'bicycle', 'car', 'van', 'truck', 'bus', 'motor', 'tricycle', 'awning-tricycle']

# Iterate through each ROI from the CSV data
for roi in roi_data:
    roi_id, roi_x, roi_y, roi_width, roi_height = roi
    
    # Create an empty dictionary to hold the object counts for this ROI
    object_counts[f"s{roi_id}"] = {class_name: 0 for class_name in visdrone_classes}
    
    # Define the bounding box for the ROI
    roi_bbox = (roi_x, roi_y, roi_x + roi_width, roi_y + roi_height)

    # Process each result (bounding boxes)
    for result in results:
        boxes = result.boxes  # Get detected bounding boxes
        
        for box in boxes:
            xyxy = box.xyxy[0].cpu().numpy()  # Bounding box coordinates (Xmin, Ymin, Xmax, Ymax)
            cls_idx = int(box.cls[0].cpu().numpy())  # Class index
            class_name = visdrone_classes[cls_idx]  # Class name
            
            # Check if the bounding box is inside the ROI
            xmin, ymin, xmax, ymax = xyxy
            if xmin >= roi_bbox[0] and ymin >= roi_bbox[1] and xmax <= roi_bbox[2] and ymax <= roi_bbox[3]:
                # Increment count for the detected object
                object_counts[f"s{roi_id}"][class_name] += 1

# Print the resulting dictionary with object counts in each ROI
print(object_counts)
