import sys
import time
import numpy as np
import imufusion
PATH = r'C:\Users\Siyang_Wang_work\USC\IEEE\Design_Team\Sensors\src_cd\mpu6050-master'
sys.path.insert(1, PATH)

import datetime
from mpu6050 import mpu6050
sensor = mpu6050(0x68)
pi = 3.14169265


# zeroth order calibration
def gyro_calibration(sample_rate, duration):
    global sensor
    print("MPU6050 gyro calibrating...")
    max_sample_cnt = duration * sample_rate
    delta_t = 1/sample_rate
    omega_x = np.empty([max_sample_cnt, 1])
    omega_y = np.empty([max_sample_cnt, 1])
    omega_z = np.empty([max_sample_cnt, 1])

    for t in range(max_sample_cnt):
        omega_sensor = sensor.get_gyro_data()
        omega_x[t] = omega_sensor['x']
        omega_y[t] = omega_sensor['y']
        omega_z[t] = omega_sensor['z']
        time.sleep(delta_t)
    avg_x = np.mean(omega_x)
    avg_y = np.mean(omega_y)
    avg_z = np.mean(omega_z)
    gyro_bias = [avg_x, avg_y, avg_z]
    print("Gyro calibration finished. Gyro bias is w_x=" + str(avg_x) + ", w_y=" + str(avg_y) + ", w_z=" + str(avg_z))
    time.sleep(1)
    return gyro_bias


# return an array of timestamps and sensor data (realistic)
def sensor_data_sampling(duration, sample_rate):
    global sensor
    sample_count = duration * sample_rate
    delta_t = 2/sample_rate
    # calibrate gyro bias
    gyro_bias = gyro_calibration(sample_rate, 5)

    data_mat = np.zeros([10, sample_count])
    # includes integrating gyro angle
    ang_int_x = 0
    ang_int_y = 0
    ang_int_z = 0
    t_0 = datetime.datetime.now()
    for t in range(sample_count):
        # TODO: measure time
        sample_time = datetime.datetime.now()-t_0  # temporarily assume no delay in sampling
        sample_timestamp = sample_time.microseconds * 10E-6
        # get sensor data
        accel_dict = sensor.get_accel_data()
        gyro_dict = sensor.get_gyro_data()
        data_mat[t][0] = sample_timestamp
        data_mat[t][1] = gyro_dict['x'] - gyro_bias[0]
        data_mat[t][2] = gyro_dict['y'] - gyro_bias[1]
        data_mat[t][3] = gyro_dict['z'] - gyro_bias[2]
        data_mat[t][4] = accel_dict['x']
        data_mat[t][5] = accel_dict['y']
        data_mat[t][6] = accel_dict['z']
        data_mat[t][7] = ang_int_x
        data_mat[t][8] = ang_int_y
        data_mat[t][9] = ang_int_z
        # integrate angle
        ang_int_x += data_mat[t][1] * delta_t
        ang_int_y += data_mat[t][2] * delta_t
        ang_int_z += data_mat[t][3] * delta_t

        return data_mat
    else:
        return -1


# implement sensor fusion and prints orientation live
def ahrs_filter_live(sample_rate, time_out):
    global sensor
    ahrs = imufusion.Ahrs()
    sample_cnt = 0
    max_sample_cnt = sample_rate*time_out
    gyro_bias = gyro_calibration(sample_rate, 5)
    print("Orientation calculated from accel and gyro")
    # accel_mat = np.zeros([max_sample_cnt, 3])
    # gyro_mat = np.zeros([max_sample_cnt, 3])
    t_0 = datetime.datetime.now()
    while sample_cnt < max_sample_cnt:
        accel_data = np.asarray([sensor.get_accel_data()['x'], sensor.get_accel_data()['y'], sensor.get_accel_data()['z']])
        gyro_data = np.asarray([sensor.get_gyro_data()['x'], sensor.get_gyro_data()['y'], sensor.get_gyro_data()['z']])
        gyro_data = gyro_data - gyro_bias
        sample_time = datetime.datetime.now()-t_0
        sample_timedelta = sample_time.microseconds * 10E-6
        ahrs.update_no_magnetometer(gyro_data, accel_data, sample_timedelta)
        t_0 = datetime.datetime.now()
        euler_ang = ahrs.quaternion.to_euler()
        if sample_cnt % 20 == 0:
            print("x= %.2f" % euler_ang[0] + ", y= %.2f" % euler_ang[1] + ", z= %.2f" % euler_ang[2])
            # print("accel_data", accel_data)
            # print("gyro_data", gyro_data)
        sample_cnt += 1
    return 0


def main():
    sample_rate = int(sys.argv[1])
    duration = int(sys.argv[2])
    sensor.set_gyro_range(0x08)
    gyro_range = sensor.read_gyro_range()
    print("Gyro_range set to: " + str(gyro_range))
    if sys.argv[3] == "get_angle":
        ahrs_filter_live(sample_rate, duration)
    else:
        imu_data = sensor_data_sampling(10, 100)
        np.savetxt("sensor_data_test1.csv", imu_data, delimiter=",")


main()

