import streamlit as st
import serial
import time
import pandas as pd

# ✅ Update this with your correct Arduino Serial Port
SERIAL_PORT = "COM3"  # Windows example (check in Device Manager)
# SERIAL_PORT = "/dev/ttyUSB0"  # Linux/Mac example (use `ls /dev/tty*`)
BAUD_RATE = 9600

# ✅ Try to Connect to Arduino Serial
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Allow time for connection
except Exception as e:
    st.error(f"Error: Could not connect to Arduino on {SERIAL_PORT}. {e}")
    st.stop()

st.title("🔴 Real-time Temperature & Motor Speed Monitoring")
st.write("📡 Live data streaming from Arduino")

# ✅ Create an empty DataFrame
data = pd.DataFrame(columns=["Time", "Temperature (°C)", "PID Output", "Motor Speed (RPM)"])

# ✅ Create a Streamlit placeholder for live updates
placeholder = st.empty()

# ✅ Read Serial Data Continuously
while True:
    try:
        # Read Serial Data from Arduino
        line = ser.readline().decode("utf-8").strip()
        if line:
            print("Received:", line)  # Debug output in console

            # ✅ Parse Data (Expected format: "Temperature: 23.46 °C | PID Output: 91.31 | Motor Speed: 15")
            parts = line.split("|")
            if len(parts) == 3:
                try:
                    temp = float(parts[0].split(":")[1].strip().replace("°C", ""))
                    pid_out = float(parts[1].split(":")[1].strip())
                    speed = int(parts[2].split(":")[1].strip())

                    # ✅ Add new data to DataFrame
                    new_row = pd.DataFrame([[time.strftime("%H:%M:%S"), temp, pid_out, speed]], 
                                           columns=["Time", "Temperature (°C)", "PID Output", "Motor Speed (RPM)"])
                    data = pd.concat([data, new_row], ignore_index=True)

                    # ✅ Convert columns to numeric types (Fixes mixed-type error)
                    data["Temperature (°C)"] = pd.to_numeric(data["Temperature (°C)"], errors="coerce")
                    data["PID Output"] = pd.to_numeric(data["PID Output"], errors="coerce")
                    data["Motor Speed (RPM)"] = pd.to_numeric(data["Motor Speed (RPM)"], errors="coerce")

                    # ✅ Update Streamlit UI
                    with placeholder.container():
                        st.line_chart(data.set_index("Time")[["Temperature (°C)", "PID Output", "Motor Speed (RPM)"]])
                        st.write(data.tail(10))  # Show last 10 rows

                except ValueError:
                    st.warning("Warning: Received invalid data format, skipping entry.")

        time.sleep(0.5)  # Adjust refresh rate

    except KeyboardInterrupt:
        st.write("Stopping...")
        break

# ✅ Close Serial Connection on Exit
ser.close()
