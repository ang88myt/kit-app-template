import json
import time
import paho.mqtt.client as mqtt
import pandas as pd
import math
import threading
from pickle import TRUE
from pathlib import Path
import requests
import warnings
warnings.filterwarnings("ignore")

pd.options.mode.chained_assignment = None
pd.set_option('display.max_columns', None)

MQTT_PORT = 1883
MQTT_TOPIC = 'device/dev01'
HTTP_ENDPOINT = 'https://digital-twin.expangea.com/device/'
API_HEADERS = {
    'X-API-KEY': '2c38e689-8bac-4ec6-9e0e-70e98222dc2d',
    'Content-Type': 'application/json'
}

mqttBroker ="192.168.38.161"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1,"Smartphone")
client.connect(mqttBroker)

client.loop_start()
line = ""
jason_topic = "device/dev01"
# mqttBroker_jason ="192.168.38.138" #Jason PC
mqttBroker_jason ="169.254.83.107"
client_jason = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "zack_UWB")
client_jason.connect(mqttBroker_jason)
client_jason.loop_start()

ADD_LENGTH = 2
N_ANCHORS = 4

current_tag_position = [[0.0, 0.0],
                        [0.0, 0.0],
                        [0.0, 0.0],
                        [0.0, 0.0],
                        [0.0, 0.0],
                        [0.0, 0.0],
                        [0.0, 0.0],
                        [0.0, 0.0],
                        [0.0, 0.0],
                        [0.0, 0.0]]
current_distance_rmse = 0.0

anchor_loc_df = None

anchor_loc_df = pd.read_csv("D:/git/mqtt_sample-1.0.0/exts/ai.synctwin.mqtt_sample/ai/synctwin/mqtt_sample/tests/anchor_matrix.csv")


# Passed a dictionary to astype() function to define the type of data
anchor_loc_df = anchor_loc_df.astype({"id":'category', "X":'float64', "Y":'float64', "Z":'float64'})

# Z values are ignored in this code, except to compute RMS distance error

# Set up the fixed anchor points
anchor_points = {
    'A': [0, 0],
    'B': [-anchor_loc_df.X.iloc[1], 0],
    'C': [0, anchor_loc_df.Y.iloc[2]],
    'D': [-anchor_loc_df.X.iloc[3], anchor_loc_df.Y.iloc[3]]
}

# TODO: To fix the coordinates of each anchor in the DF.
# Can also read from CSV file.
X = 0
Y = 1
Z = 2

ADDRESS = 0
DISTANCE = 1
ORG_ADDRESS = 2

MIN_DIST = 0
MAX_DIST = 30

REST = 0.001

temp_current_tag_position = [0, 0]

dict_bind = {"address": [], "distance":[], "reporting_anchor":[], "time_stamp":[], "X":[], "Y":[], "Z":[]}
df = pd.DataFrame(dict_bind)

# Passed a dictionary to astype() function to define the type of data
df = df.astype({"address":'category', "distance":'float64', "reporting_anchor":'category', "time_stamp":'int64', "X":'float64', "Y":'float64', "Z":'float64'})

# Global variables to store the latest tag point
latest_tag_point = [0, 0]


new_x = 0.0
new_y = 0.0

def on_message(client, userdata, message):
    global line
    line = str(message.payload.decode("utf-8"))

def trilat2D_3A(df):
    no_of_anchors = 3

    #for i in df.index:
    #    print("Reporting_Anchor: ", df.reporting_anchor.iloc[i], " Distance: ", df.distance.iloc[i])

    first = True
    # distances from anchors
    b = [0.0, 0.0] 
    d = [0.0, 0.0, 0.0]
    k = [0.0, 0.0, 0.0]
    A_inv = [[0.0, 0.0],
             [0.0, 0.0]]
    
    temp_current_tag_position = [0, 0]
             
    i = 0
    
    for i in range(no_of_anchors):
        d[i] = df.distance.iloc[i][0]

    if first:
        first = False

        # intermediate vectors
        _x = [0.0, 0.0, 0.0, 0.0]
        _y = [0.0, 0.0, 0.0, 0.0]

        # the A matrix for system of equations to solve
        A = [[0.0, 0.0],
             [0.0, 0.0]]
             
        for i in range(no_of_anchors):
            _x[i] = df.X.iloc[i]
            _y[i] = df.Y.iloc[i]
            k[i] = df.X.iloc[i]**2 + df.Y.iloc[i]**2
            
            #print(k)

            # set up the A matrix
            if i > 0:
                A[i-1][X] = _x[i] - _x[0]
                A[i-1][Y] = _y[i] - _y[0]
                
        #for i in A:
        #    print(i)
        #print(A)

        det = 0.0
        det = A[0][0] * A[1][1] - A[1][0] * A[0][1]
        #print(det)

        
        if (abs(det) < 1.0E-4):
            raise ValueError("The matrix is singular and cannot be inverted.")
            while True: #hang
                time.sleep(5)
                pass
        
        det = 1.0 / det
        
        # Ainv is static
        # SCALE_ADJOINT_3X3 (Ainv, det, A); 
        A_inv[0][0] = det * A[1][1]
        A_inv[0][1] = det * A[0][1]
        A_inv[1][0] = det * A[1][0]
        A_inv[1][1] = det * A[0][0]
        
    # set up least squares equation
    for i in range(1, no_of_anchors):
        b[i-1] = float(d[0])**2 - float(d[i])**2 + k[i] - k[0]
        
    #MAT_DOT_VEC_3X3(posn2, Ainv, b);
    temp_current_tag_position[0] = 0.5 * (A_inv[0][0]*b[0] + A_inv[0][1]*b[1])
    temp_current_tag_position[1] = 0.5 * (A_inv[1][0]*b[0] + A_inv[1][1]*b[1])
        
    # rms error in measured versus calculated distances
    _x = [0.0, 0.0, 0.0]
    rmse = 0.0
    dc = 0.0
    for i in range(no_of_anchors):   
        _x[0] = temp_current_tag_position[X] - df.X.iloc[i]
        _x[1] = temp_current_tag_position[Y] - df.Y.iloc[i]
        _x[0] = float(d[i]) - math.sqrt(_x[0]**2 + _x[1]**2)
        rmse += (float(_x[0]))**2
        
    current_distance_rmse = math.sqrt(rmse / no_of_anchors); #copy to global

    return temp_current_tag_position       


# Function to generate new data points for the moving tag point
def generate_new_data():
    global temp_current_tag_position
    while True:
        for i in df.address.unique():
            temp_df = df.loc[df['address'] == i]
            
            for j in temp_df.index.to_list():
                try:
                    if len(temp_df.distance.loc[j]) < 10:
                        temp_df = temp_df.drop(j)
                    temp_df = temp_df.sort_values(by=['address', 'reporting_anchor'])
                    temp_df = temp_df.reset_index(drop=True)
                except:
                    continue
            
            if len(temp_df.index) >= 3:
                temp_current_tag_position = trilat2D_3A(temp_df) 
        current_tag_position[9] = current_tag_position[8]
        current_tag_position[8] = current_tag_position[7]
        current_tag_position[7] = current_tag_position[6]
        current_tag_position[6] = current_tag_position[5]
        current_tag_position[5] = current_tag_position[4]
        current_tag_position[4] = current_tag_position[3]
        current_tag_position[3] = current_tag_position[2]
        current_tag_position[2] = current_tag_position[1]
        current_tag_position[1] = current_tag_position[0]
        
        
        current_tag_position[0][X] = (temp_current_tag_position[X] + current_tag_position[1][X] + current_tag_position[2][X]) / 3
        current_tag_position[0][Y] = (temp_current_tag_position[Y] + current_tag_position[1][Y] + current_tag_position[2][Y]) / 3
        # current_tag_position[0][Z] = (temp_current_tag_position[Z] + current_tag_position[1][Z] + current_tag_position[2][Z]) / 3    
        new_x = -round(current_tag_position[0][X],2)
        new_y = round(current_tag_position[0][Y],2)
        # new_z = round(current_tag_position[0][Z],2)
        # print("x: ", new_x, " y: ", new_y)
        yield new_x, new_y

def update_data():
    global df
    last_time = 0
    while True:
        # Your data update code here

        if len(line) != 0:
            line_split = line.split(":")
            if len(line_split[ADDRESS]) == ADD_LENGTH and len(line_split[ORG_ADDRESS]) == ADD_LENGTH:
                temp_df = df.loc[df['address'] == line_split[ADDRESS]]

                for i in range(len(anchor_loc_df.index)):
                    if str(anchor_loc_df.id.iloc[i]) == line_split[ORG_ADDRESS]:
                        temp_anchor_loc = anchor_loc_df.iloc[i]
                if float(line_split[DISTANCE]) > MIN_DIST and float(line_split[DISTANCE]) < MAX_DIST:                
                    if len(temp_df.loc[temp_df['reporting_anchor']==line_split[ORG_ADDRESS]]) > 0:
                        time_stamp = time.time()

                        temp_index = temp_df.loc[temp_df['reporting_anchor']==line_split[ORG_ADDRESS]].index.to_list()[0]
                        
                        temp_df.X = temp_anchor_loc.X
                        temp_df.Y = temp_anchor_loc.Y
                        temp_df.Z = temp_anchor_loc.Z
                        
                        # Check that there are at least 5 entries in the distance array
                        if len(df.distance.loc[temp_index]) > 5:
                            temp_dist = (float(line_split[DISTANCE]) + float(df.distance.loc[temp_index][0]) + float(df.distance.loc[temp_index][1]))/3
                            df.distance.loc[temp_index].insert(0, round(temp_dist, 2))
                        else:
                            df.distance.loc[temp_index].insert(0, line_split[DISTANCE])

                        # Retaining only 10 entries in the distance array
                        if len(df.distance.loc[temp_index]) > 10:
                            df.distance.loc[temp_index].pop()
                        df.time_stamp.loc[temp_index] = time_stamp
                    else:
                        time_stamp = time.time()
                        df.loc[len(df)] = [line_split[ADDRESS],[line_split[DISTANCE]],line_split[ORG_ADDRESS],time_stamp,temp_anchor_loc.X,temp_anchor_loc.Y,temp_anchor_loc.Z]

                for i in df.index.to_list():
                    time_diff = time_stamp - df.time_stamp.loc[i]
                    #To delete the record after 5 seconds if it has been inactive.
                    if time_diff > 3:
                        df = df.drop(i)
                df = df.sort_values(by=['address', 'reporting_anchor'])
                df = df.reset_index(drop=True)

        time.sleep(REST)  # Wait for 5 seconds before updating the data again

def send_sync():
    while(1):
        #client.publish("pubTopic", "85:1:86:2:87:3:88:4")
        client.publish("pubTopic", "81:1:82:2:83:3:84:4")
        # To periodically send out signal to synchronise across all anchors
        # Can alter to longer timing as necessary
        time.sleep(5) # To sleep for 10 sec.

# def send_loc():
#     while(1):
#         #jason_topic
#         test_string2 = "{\"name\": \"Cube\", \"position\": {\"x\": " + str(latest_tag_point[0]) + ", \"y\": "+ str(latest_tag_point[1]) + ", \"z\": 0.0}}"
#         # test_string2 = f'{{"name": "Cube", "position": {{"x": {latest_tag_point[0]}, "y": {latest_tag_point[1]}, "z": "0.0"}}}}'
#
#         client_jason.publish(jason_topic, test_string2)
#
#         print(test_string2)
#
#         time.sleep(0.1) # To sleep for 10 sec.
def send_loc():
    while True:
        # Construct the payload
        payload = {
            "name": "Cube",
            "position": {
                "x": latest_tag_point[0],
                "y": latest_tag_point[1],
                "z": 0.0  # Adjust Z value as needed
            }
        }

        json_payload = json.dumps(payload)

        # Send the payload to the HTTP endpoint
        try:
            response = requests.post(HTTP_ENDPOINT, headers=API_HEADERS, json=payload)
            response.raise_for_status()  # Raise an exception for HTTP errors
            print(f"Data sent to {HTTP_ENDPOINT}: {json_payload}")
            print(f"Response: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to send data to HTTP endpoint: {e}")

        # Publish the payload to the MQTT broker
        try:
            client_jason.publish(jason_topic, json_payload)
            print(f"Data published to MQTT topic '{jason_topic}': {json_payload}")
        except Exception as e:
            print(f"Failed to publish data to MQTT broker: {e}")

        time.sleep(0.1)  # Sleep for 0.1 seconds before sending the next data point


def update_loc():
    global latest_tag_point
    while(1):
        # Get the latest tag point from the data generator
        data_gen = generate_new_data()
        new_x, new_y = next(data_gen)

        # Update the tag point
        latest_tag_point = [new_x, new_y]
        # print(latest_tag_point)
    
def main():
    client.subscribe("testTopic")
    client.on_message=on_message

    # Update the data in the main thread or another separate thread
    data_thread = threading.Thread(target=update_data, daemon=True)
    data_thread.start()

    # Update the data in the main thread or another separate thread
    update_loc_thread = threading.Thread(target=update_loc, daemon=True)
    update_loc_thread.start()

    # Sending message to synchronise anchors
    sync_thread = threading.Thread(target=send_sync, daemon=True)
    sync_thread.start()

    loc_thread = threading.Thread(target=send_loc, daemon=True)
    loc_thread.start()
    
    while True:
        time.sleep(1)  # main thread alive

if __name__ == '__main__':
    main()




