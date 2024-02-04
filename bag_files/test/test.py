import csv
import sqlite3
from rosidl_runtime_py.utilities import get_message
from rclpy.serialization import deserialize_message

# import matplotlib.pyplot as plt

class BagFileParser():
    def __init__(self, bag_file):
        self.conn = sqlite3.connect(bag_file)
        self.cursor = self.conn.cursor()

        ## create a message type map
        topics_data = self.cursor.execute("SELECT id, name, type FROM topics").fetchall()
        self.topic_type = {name_of:type_of for id_of,name_of,type_of in topics_data}
        self.topic_id = {name_of:id_of for id_of,name_of,type_of in topics_data}
        self.topic_msg_message = {name_of:get_message(type_of) for id_of,name_of,type_of in topics_data}

    def __del__(self):
        self.conn.close()

    # Return [(timestamp0, message0), (timestamp1, message1), ...]
    def get_messages(self, topic_name):

        topic_id = self.topic_id[topic_name]
        # Get from the db
        rows = self.cursor.execute("SELECT timestamp, data FROM messages WHERE topic_id = {}".format(topic_id)).fetchall()
        # Deserialise all and timestamp them
        return [ (timestamp,deserialize_message(data, self.topic_msg_message[topic_name])) for timestamp,data in rows]



if __name__ == "__main__":

        bag_file = '/home/bhavesh/Downloads/bag_files/testBag/testBag.db3'

        parser = BagFileParser(bag_file)

        # trajectory = parser.get_messages("/turtle1/cmd_vel")[0][1] 
        # p_des_1 = [trajectory.points[i].positions[0] for i in range(len(trajectory.points))]
        # t_des = [trajectory.points[i].time_from_start.sec + trajectory.points[i].time_from_start.nanosec*1e-9 for i in range(len(trajectory.points))]

        # actual = parser.get_messages("/turtle1/cmd_vel")
        # print(type(actual[0][1].linear))
        # for i in actual:
        #     print(i[1].linear.x)

        # plt.plot(t_des, p_des_1)

        # plt.show()

        actualScan = parser.get_messages("/scan")
        actualCmdVel = parser.get_messages("/cmd_vel")
        # print(len(actualScan[0][1].ranges))
        # print(actualScan[0][1].ranges[0])
        # for i in range(10):
            # print(actualScan[i])

        csv_file_path = "test.csv"

        data = [
            []
        ]

        for i in range(360):
            data[0].append("Ranges" + str(i+1))
        data[0].append("x")
        data[0].append("y")
        data[0].append("z")
        data[0].append("i")
        data[0].append("j")
        data[0].append("k")

        for i in range (100):
            temp = []

            for k in range(360):
                temp.append(actualScan[i][1].ranges[k])

            temp.append(actualCmdVel[i][1].linear.x)
            temp.append(actualCmdVel[i][1].linear.y)
            temp.append(actualCmdVel[i][1].linear.z)
            temp.append(actualCmdVel[i][1].angular.x)
            temp.append(actualCmdVel[i][1].angular.y)
            temp.append(actualCmdVel[i][1].angular.z)

            data.append(temp)

        with open(csv_file_path, mode='w', newline='') as file:
            # Create a CSV writer object
            csv_writer = csv.writer(file)
            # Write the data to the CSV file
            csv_writer.writerows(data) 
            
        