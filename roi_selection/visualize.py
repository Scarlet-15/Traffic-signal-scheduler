import cv2
import pandas as pd
import matplotlib.pyplot as plt

def visualize_rois(image_path, csv_path):
    # Load the image
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert from BGR to RGB for matplotlib

    # Load ROI data from CSV
    roi_data = pd.read_csv(csv_path)

    # Process each ROI entry in the CSV
    for _, row in roi_data.iterrows():
        roi_id = int(row['roi_id'])
        x = int(row['roi_x'])
        y = int(row['roi_y'])
        width = int(row['roi_width'])
        height = int(row['roi_height'])

        # Define bottom-right corner of the bounding box
        x2 = x + width
        y2 = y + height

        # Draw the bounding box
        color = (255, 0, 0)  # Red color for the box
        cv2.rectangle(image, (x, y), (x2, y2), color, 2)

        # Add the ROI ID label
        label = f"ROI {roi_id}"
        cv2.putText(image, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Show the image with bounding boxes
    plt.imshow(image)
    plt.axis('off')
    plt.show()

# Usage example:
image_path = './images/sample.jpg'
csv_path = r'D:\SEMESTER 7\PJT\SignalScheduler\roi_selection\roi_info.csv'
visualize_rois(image_path, csv_path)
