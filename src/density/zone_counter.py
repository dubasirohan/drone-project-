import cv2
import csv
from ultralytics import YOLO

# -----------------------------
# Configuration
# -----------------------------
MODEL_PATH = "yolov8x.pt"
VIDEO_PATH = "data/input/clip.mp4"

OUTPUT_VIDEO = "outputs/density/density_output.mp4"
OUTPUT_CSV = "outputs/density/zone_counts.csv"

CONFIDENCE = 0.15
IMG_SIZE = 960

ROWS = 3
COLS = 4


# -----------------------------
# Setup
# -----------------------------
model = YOLO(MODEL_PATH)

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    raise RuntimeError(f"Could not open video: {VIDEO_PATH}")

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

cell_width = width / COLS
cell_height = height / ROWS

fourcc = cv2.VideoWriter_fourcc(*"mp4v")

out = cv2.VideoWriter(
    OUTPUT_VIDEO,
    fourcc,
    fps,
    (width, height)
)

# CSV header
csv_file = open(OUTPUT_CSV, "w", newline="")
writer = csv.writer(csv_file)

header = ["frame", "total_people"]

for zone in range(1, ROWS * COLS + 1):
    header.append(f"zone_{zone}")

writer.writerow(header)


# -----------------------------
# Process video
# -----------------------------
frame_number = 0

while True:

    success, frame = cap.read()

    if not success:
        break

    frame_number += 1

    # YOLO detection
    results = model.predict(
        frame,
        device="mps",
        classes=[0],       # person only
        conf=CONFIDENCE,
        imgsz=IMG_SIZE,
        verbose=False
    )

    zone_counts = [0] * (ROWS * COLS)

    # Process detections
    boxes = results[0].boxes

    if boxes is not None:

        for box in boxes:

            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

            # Center of bounding box
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2

            # Determine grid position
            col = int(cx / cell_width)
            row = int(cy / cell_height)

            # Keep within grid
            col = min(max(col, 0), COLS - 1)
            row = min(max(row, 0), ROWS - 1)

            zone_index = row * COLS + col

            zone_counts[zone_index] += 1

            # Draw person bounding box
            cv2.rectangle(
                frame,
                (int(x1), int(y1)),
                (int(x2), int(y2)),
                (255, 255, 255),
                2
            )

    total_people = sum(zone_counts)

    # -----------------------------
    # Draw grid
    # -----------------------------

    for r in range(1, ROWS):
        y = int(r * cell_height)

        cv2.line(
            frame,
            (0, y),
            (width, y),
            (255, 255, 255),
            2
        )

    for c in range(1, COLS):
        x = int(c * cell_width)

        cv2.line(
            frame,
            (x, 0),
            (x, height),
            (255, 255, 255),
            2
        )

    # Zone labels
    for r in range(ROWS):

        for c in range(COLS):

            zone_index = r * COLS + c
            zone_number = zone_index + 1

            x = int(c * cell_width + 20)
            y = int(r * cell_height + 45)

            text = f"Z{zone_number}: {zone_counts[zone_index]}"

            cv2.putText(
                frame,
                text,
                (x, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (255, 255, 255),
                2
            )

    # Total count
    cv2.putText(
        frame,
        f"TOTAL PEOPLE: {total_people}",
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        (255, 255, 255),
        3
    )

    # Save CSV row
    writer.writerow(
        [frame_number, total_people] + zone_counts
    )

    # Save video frame
    out.write(frame)


# -----------------------------
# Cleanup
# -----------------------------
cap.release()
out.release()
csv_file.close()

print("Density processing complete.")
print(f"Video: {OUTPUT_VIDEO}")
print(f"CSV:   {OUTPUT_CSV}")
