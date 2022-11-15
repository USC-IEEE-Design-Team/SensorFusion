import numpy as np
import matplotlib.pyplot as plt
import imufusion
import time
import sys
PATH = r'C:\Users\Siyang_Wang_work\USC\IEEE\Design_Team\Sensors\src_cd\mpu6050-master'
sys.path.insert(1, PATH)
from mpu6050 import mpu6050
sensor = mpu6050(0x68)


def acc_gyro_live_plot(duration, sample_rate):
    global sensor
    sample_cnt = duration * sample_rate
    # init filter
    ahrs = imufusion.Ahrs()
    accelerometer = np.zeros((len(sample_cnt), 3))
    gyroscope = np.zeros((len(sample_cnt), 3))
    euler = np.zeros((len(sample_cnt), 3))

    timestamp = np.arange(0, duration, 1/sample_rate)
    # setup plot

    _, axes = plt.subplots(nrows=3, sharex=True)

    for t in range(sample_cnt):
        # sensor data acquisition
        # accel_data = [sensor.get_accel_data['x'], sensor.get_accel_data['y'], sensor.get_accel_data['z']]
        # gyro_data = [sensor.get_gyro_data['x'], sensor.get_gyro_data['y'], sensor.get_gyro_data['z']]
        accel_data = [0, 0, 1]
        gyro_data = [0.5, 0.5, 0]
        # get filtered value
        ahrs.update_no_magnetometer(accel_data, gyro_data, 1/sample_rate)
        accelerometer[t] = accel_data
        gyroscope[t] = gyro_data
        euler[t] = ahrs.quaternion.to_euler()
        # update plot

        axes[0].plot(timestamp, gyroscope[:, 0], "tab:red", label="X")
        axes[0].plot(timestamp, gyroscope[:, 1], "tab:green", label="Y")
        axes[0].plot(timestamp, gyroscope[:, 2], "tab:blue", label="Z")
        axes[0].set_title("Gyroscope")
        axes[0].set_ylabel("Degrees/s")
        axes[0].grid()
        axes[0].legend()

        axes[1].plot(timestamp, accelerometer[:, 0], "tab:red", label="X")
        axes[1].plot(timestamp, accelerometer[:, 1], "tab:green", label="Y")
        axes[1].plot(timestamp, accelerometer[:, 2], "tab:blue", label="Z")
        axes[1].set_title("Accelerometer")
        axes[1].set_ylabel("g")
        axes[1].grid()
        axes[1].legend()

        axes[2].plot(timestamp, euler[:, 0], "tab:red", label="Roll")
        axes[2].plot(timestamp, euler[:, 1], "tab:green", label="Pitch")
        axes[2].plot(timestamp, euler[:, 2], "tab:blue", label="Yaw")
        axes[2].set_title("Euler angles")
        axes[2].set_xlabel("Seconds")
        axes[2].set_ylabel("Degrees")
        axes[2].grid()
        axes[2].legend()

        plt.draw()

        time.sleep(0.5)

