import csv
from ultralytics import YOLO
import cv2
from datetime import datetime, timedelta

def calculate_weighted_sum(input_dict):
    vehicle_weights = {
        'pedestrian': 1, 'people': 2, 'bicycle': 5, 'car': 20,
        'van': 50, 'truck': 100, 'bus': 100, 'motor': 10,
        'tricycle': 7, 'awning-tricycle': 8
    }

    result = {}
    for section, vehicles in input_dict.items():
        weighted_sum = sum(count * vehicle_weights[vehicle_type] for vehicle_type, count in vehicles.items())
        result[section] = weighted_sum

    return result

def generate_vehicle_schedule(weighted_sums):
    current_time = datetime.now()
    schedule = {}
    sorted_sections = sorted(weighted_sums.items(), key=lambda x: x[1], reverse=True)

    for section, weight in sorted_sections:
        duration = timedelta(seconds=weight * 0.2)
        end_time = current_time + duration
        schedule[section] = {
            'start_time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'duration': str(duration)
        }
        current_time = end_time

    return schedule

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

# Define object classes based on VISDRONE dataset
visdrone_classes = ['pedestrian', 'people', 'bicycle', 'car', 'van', 'truck', 'bus', 'motor', 'tricycle', 'awning-tricycle']

# Iterate through each ROI from the CSV data
for roi in roi_data:
    roi_id, roi_x, roi_y, roi_width, roi_height = roi

    # Create an empty dictionary to hold the object counts for this ROI
    object_counts[f"s{roi_id}"] = {class_name: 0 for class_name in visdrone_classes}
    
    # Define the bounding box for the ROI
    roi_bbox = (roi_x, roi_y, roi_x + roi_width, roi_y + roi_height)

    # Draw ROI rectangle on the image (green for ROI)
    cv2.rectangle(image, (roi_x, roi_y), (roi_x + roi_width, roi_y + roi_height), (0, 255, 0), 2)
    cv2.putText(image, f"ROI {roi_id}", (roi_x, roi_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Process each result (bounding boxes)
    for result in results:
        boxes = result.boxes  # Get detected bounding boxes

        for box in boxes:
            xyxy = box.xyxy[0].cpu().numpy()  # Bounding box coordinates (Xmin, Ymin, Xmax, Ymax)
            conf = box.conf[0].cpu().numpy()  # Confidence score
            cls_idx = int(box.cls[0].cpu().numpy())  # Class index

            # Ensure class index is within the range of available classes
            if cls_idx < len(visdrone_classes):
                class_name = visdrone_classes[cls_idx]
            else:
                continue  # Skip if class index is out of range

            # Extract bounding box coordinates
            xmin, ymin, xmax, ymax = map(int, xyxy)

            # Check if the bounding box intersects with the ROI
            if not (xmax < roi_x or xmin > roi_x + roi_width or ymax < roi_y or ymin > roi_y + roi_height):
                # Increment count for the detected object
                object_counts[f"s{roi_id}"][class_name] += 1

                # Draw the bounding box for the detected object (in blue)
                cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (255, 0, 0), 2)
                label = f'{class_name} {conf:.2f}'
                cv2.putText(image, label, (xmin, ymin - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

# Print the resulting dictionary with object counts in each ROI
print("Object Counts:")
print(object_counts)

# Calculate weighted sums
weighted_sums = calculate_weighted_sum(object_counts)
print("\nWeighted Sums:")
print(weighted_sums)

# Generate schedule
schedule = generate_vehicle_schedule(weighted_sums)
print("\nSchedule:")
for section, times in schedule.items():
    print(f"{section}: {times}")

# Show the resulting image with ROIs and detections
cv2.imshow('Detections with ROIs', image)

# Save the output image with the visualized results
cv2.imwrite('./results/result_with_rois.jpg', image)

# Wait for a key press to close the image window
cv2.waitKey(0)
cv2.destroyAllWindows()