import serial
import pandas as pd
from datetime import datetime
import os

# -----------------------------
# Arduino serial configuration
# -----------------------------
SERIAL_PORT = '/dev/ttyUSB0'  # Linux serial port
BAUD_RATE = 9600
csv_file = 'Students_Data.csv'

# CSV columns
columns = ['ID', 'Name', 'Status', 'ClassesAttended', 'TimeIn', 'TimeOut', 'Img_Path']

# -----------------------------
# Initialize CSV if missing
# -----------------------------
if not os.path.exists(csv_file) or os.path.getsize(csv_file) == 0:
    df = pd.DataFrame(columns=columns)
    df.to_csv(csv_file, index=False)

print("Waiting for RFID scans... (Press Ctrl+C to stop)")

# -----------------------------
# Helper functions
# -----------------------------
def format_student_id(number: int) -> str:
    """Format student ID as 00-001, 00-002, etc."""
    return f"00-{int(number):03d}"

def get_image_path(name: str) -> str:
    """Generate image path from name (replace spaces with nothing, default jpeg)."""
    filename = name.replace(" ", "") + ".jpeg"
    return f"assets/profiles/{filename}"

# -----------------------------
# Connect to Arduino
# -----------------------------
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
except serial.SerialException as e:
    print(f"Error connecting to {SERIAL_PORT}: {e}")
    exit(1)

# -----------------------------
# Main loop
# -----------------------------
while True:
    try:
        ser.reset_input_buffer()
        rfid_line = ser.readline().decode(errors='ignore').strip()  # safely decode

        if rfid_line:
            try:
                name, number, status = [x.strip() for x in rfid_line.split(",")]
            except ValueError:
                print(f"Bad line received: {rfid_line}")
                continue

            student_id = format_student_id(number)
            time_in = datetime.now().strftime("%-I:%M %p")  # Linux-friendly 7:40 AM
            img_path = get_image_path(name)

            # Read existing CSV
            df = pd.read_csv(csv_file)

            if student_id in df['ID'].values:
                # Update existing student
                idx = df.index[df['ID'] == student_id][0]
                if status.lower() == "present":
                    df.at[idx, 'ClassesAttended'] += 1
                    df.at[idx, 'TimeIn'] = time_in
                df.at[idx, 'Status'] = status
                df.at[idx, 'TimeOut'] = ''  # Reset or fill later
            else:
                # Add new student
                new_row = pd.DataFrame([{
                    'ID': student_id,
                    'Name': name,
                    'Status': status,
                    'ClassesAttended': 1 if status.lower() == "present" else 0,
                    'TimeIn': time_in if status.lower() == "present" else '',
                    'TimeOut': '',
                    'Img_Path': img_path
                }])
                df = pd.concat([df, new_row], ignore_index=True)

            # Save CSV
            df.to_csv(csv_file, index=False)

            # Console feedback
            print(f"{name} ({student_id}) -> {status}")

    except KeyboardInterrupt:
        print("\nExiting...")
        break
    except Exception as e:
        print(f"Unexpected error: {e}")
