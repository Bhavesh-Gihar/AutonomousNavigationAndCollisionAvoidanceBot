import csv
import sqlite3
from rosidl_runtime_py.utilities import get_message
from rclpy.serialization import deserialize_message

class BagFileParser():
    def __init__(self, bag_file):
        self.conn = sqlite3.connect(bag_file)
        self.cursor = self.conn.cursor()

        topics_data = self.cursor.execute("SELECT id, name, type FROM topics").fetchall()
        self.topic_type = {name_of:type_of for id_of,name_of,type_of in topics_data}
        self.topic_id = {name_of:id_of for id_of,name_of,type_of in topics_data}
        self.topic_msg_message = {name_of:get_message(type_of) for id_of,name_of,type_of in topics_data}

    def __del__(self):
        self.conn.close()

    def get_messages(self, topic_name):
        topic_id = self.topic_id[topic_name]
        rows = self.cursor.execute("SELECT timestamp, data FROM messages WHERE topic_id = {}".format(topic_id)).fetchall()
        return [ (timestamp,deserialize_message(data, self.topic_msg_message[topic_name])) for timestamp,data in rows]



if __name__ == "__main__":

        bag_file = '/home/bhavesh/Documents/AutonomousNavigationAndCollisionAvoidanceBot/bag_files/squareMaze/squareMazeRecording/recording.db3'

        parser = BagFileParser(bag_file)

        actualScan = parser.get_messages("/scan")
        actualCmdVel = parser.get_messages("/cmd_vel")

        csv_file_path = "circleMaze.csv"

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

        for i in range (100, 2500):
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
            csv_writer = csv.writer(file)
            csv_writer.writerows(data) 
            
        