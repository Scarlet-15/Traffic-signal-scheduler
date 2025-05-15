import cv2
import csv

# List to store the coordinates
coordinates = []

# Mouse callback function to capture click events and save the coordinates
def mark_coordinates(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:  # Left mouse click
        coordinates.append((x, y))  # Save the coordinates to the list
        print(f"Marked coordinates: {x}, {y}")
        # Draw a small circle to visualize the marking
        cv2.circle(image, (x, y), 5, (0, 255, 0), -1)  # Green dot

# Load the image of the junction
image = cv2.imread('./signal.jpg')

# Resize the image to 50% of its original size (adjust scaling factor as needed)
scale_percent = 50  # Percent of the original size
new_width = int(image.shape[1] * scale_percent / 100)
new_height = int(image.shape[0] * scale_percent / 100)
dim = (new_width, new_height)

# Resize the image
image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

# Create a window and set a mouse callback to capture clicks
cv2.namedWindow('Mark Traffic Signals')
cv2.setMouseCallback('Mark Traffic Signals', mark_coordinates)

print("Click on the image to mark the locations where signals should be placed.")

while True:
    # Display the image and wait for clicks
    cv2.imshow('Mark Traffic Signals', image)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Destroy the window
cv2.destroyAllWindows()

# Save the coordinates to a CSV file
with open('signal_coordinates.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['X', 'Y'])  # Write the header
    writer.writerows(coordinates)  # Write the coordinates

print("Coordinates saved to 'signal_coordinates.csv'.")
