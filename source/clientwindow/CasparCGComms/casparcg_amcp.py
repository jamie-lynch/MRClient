# Jack Connor-Richards - 28th December 2017 - v0.7.2_MR
# CasparCG AMCP communications class to be used with The Match Report CasparCG Custom Client
# written by Jamie Lynch and Jack Connor-Richards for LSU Media

# Version History:
#
# v0.7.1_MR:
# (JCR) Class name changed to CasparAMCP and added to package CasparCGComms
# (JPL) playonload feature added
#
# v0.7.2_MR:
# (JCR) Improved handling of illegal characters in Caspar data

import socket
import os.path
import logging
import logging.handlers as handlers
import html


class CasparAMCP(object):

    logger = None
    casparcg = None
    connected = False
    playing_templates = {}

    def __init__(self):
        global logger
        logger = self.init_logging()
        logger.info("CasparComms | Jack Connor-Richards/Jamie Lynch | Version 0.7.2 - 28th December 2017")
        logger.info("CasparComms Class initialised")

    def init_logging(self):
        global logger

        logging_dir = "C:\\Users\\Public\\CasparComms\\logs"

        logger = logging.getLogger("CasparComms")
        logger.setLevel(logging.DEBUG)

        if os.path.exists(logging_dir) is False:
            os.makedirs(logging_dir)
        else:
            pass

        handler = handlers.RotatingFileHandler(logging_dir + "\CasparComms.log", maxBytes=1024000, backupCount=5)
        handler.setLevel(logging.DEBUG)

        log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', "%d-%m-%Y %H:%M:%S")

        handler.setFormatter(log_format)
        logger.addHandler(handler)

        return logger

    def caspar_connect(self, address, port):

        if self.casparcg is None:
            try:
                self.casparcg = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.casparcg.settimeout(5)
                self.casparcg.connect((address, int(port)))
                logger.info("Connected to CasparCG Server at " + str(address) + ":" + str(port))
                self.connected = True
                self.casparcg.settimeout(None)
                return "Connected to CasparCG"
            except socket.timeout:
                self.casparcg = None
                logger.error("Failed to connect to CasparCG Server in a timely fashion")
                return "Failed to connect to CasparCG Server in a timely fashion"
            except socket.error as e:
                self.casparcg = None
                logger.error("Failed to connect to CasparCG Server with the error " + str(e))
                return "Failed to connect to CasparCG Server with the error " + str(e)

        else:
            logger.warning("Already connected to CasparCG Server")
            return "Already connected to CasparCG Server"

    def string_split(self, params):
        delimited = params.split("|", 1)
        count = delimited.count(1)
        return delimited, count

    def process_return_data(self, data):
        ok = {'200', '201', '202'}
        if data.split()[0] in ok:
            return 1
        else:
            return 0

    def send_command(self, command):
        try:
            logger.info("Sending command: " + command)
            self.casparcg.send((command + "\r\n").encode("UTF-8"))
            received = self.casparcg.recv(1024).decode("UTF-8")
            logger.info("Received from CasparCG: " + received)
            return received
        except socket.error:
            logger.error("Send command failed")
            return "Send command failed"

    def load_video(self, name, channel):
        command = "LOAD " + str(channel) + " " + name

        try:
            logger.info("Sending command: " + command)
            self.casparcg.send((command + '\r\n').encode("UTF-8"))
            received = self.casparcg.recv(1024).decode("UTF-8")
            logger.info("Received from CasparCG: " + received)
            processed_return = self.process_return_data(data=received)
            return processed_return
        except socket.error:
            logger.error("Load command failed")
            return "Load command failed"

    def play_video(self, name, channel, loop=0):
        name = name.replace("\\", "/")
        if loop == 1:
            command = "PLAY " + str(channel) + " " + '"' + name + '"' + " LOOP"
        else:
            command = "PLAY " + str(channel) + " " + '"' + name + '"'

        try:
            logger.info("Sending command: " + command)
            self.casparcg.send((command + '\r\n').encode("UTF-8"))
            received = self.casparcg.recv(1024).decode("UTF-8")
            logger.info("Received from CasparCG: " + received)
            processed_return = self.process_return_data(data=received)
            return 1, processed_return
        except socket.error:
            logger.error("Play command failed")
            return 0, "Play command failed"

    def pause_video(self, channel):
        command = "PAUSE " + str(channel)

        try:
            logger.info("Sending command: " + command)
            self.casparcg.send((command + '\r\n').encode("UTF-8"))
            received = self.casparcg.recv(1024).decode("UTF-8")
            logger.info("Received from CasparCG: " + received)
            return received
        except socket.error:
            logger.error("Pause command failed")
            return "Pause command failed"

    def resume_video(self, channel):
        command = "RESUME " + str(channel)

        try:
            logger.info("Sending command: " + command)
            self.casparcg.send((command + '\r\n').encode("UTF-8"))
            received = self.casparcg.recv(1024).decode("UTF-8")
            logger.info("Received from CasparCG: " + received)
            return received
        except socket.error:
            logger.error("Resume command failed")
            return "Resume command failed"

    def stop_video(self, channel):
        command = "STOP " + str(channel)

        try:
            logger.info("Sending command: " + command)
            self.casparcg.send((command + '\r\n').encode("UTF-8"))
            received = self.casparcg.recv(1024).decode("UTF-8")
            logger.info("Received from CasparCG: " + received)
            return received
        except socket.error:
            logger.error("Stop command failed")
            return "Stop command failed"

    def template(self, name, channel, layer, parameters="", playonload=0):
        try:
            if self.playing_templates[str(channel) + "-" + str(layer)] == str(name):
                logger.info("Found a playing template called " + str(name) + " on " + str(channel) + "-" + str(layer) +
                            ", calling template update function")
                response = self.update_template(channel, layer, parameters)
                return response
        except KeyError:
            logger.info("Found a playing template called " + str(name) + " on " + str(channel) + "-" + str(layer) +
                        ", calling template play function")
            response = self.play_template(name, channel, layer, parameters, playonload)
            return response
        return "Failed"

    def play_template(self, name, channel, layer, parameters="", playonload=0):
        command = 'CG ' + str(channel) + '-' + str(layer) + ' ADD 10 ' + name + ' \"{}\" \"<templateData>'.format(playonload)
        # params,count = self.string_split(parameters)
        delimited = parameters.split("|")
        count = len(delimited)
        for i in range(count):
            command += '<componentData id=\\\"' + html.escape(delimited[i].split("=")[0]) + '\\\"><data id=\\\"text\\\" value=\\\"' + html.escape(delimited[i].split("=")[1]) + '\\\" /></componentData>'
        command += "</templateData>\""
        try:
            logger.info("Sending command: " + command)
            if self.casparcg:
                self.casparcg.send((command + '\r\n').encode("UTF-8"))
                received = self.casparcg.recv(1024).decode("UTF-8")
                if self.process_return_data(received) == 1:
                    self.playing_templates[str(channel) + "-" + str(layer)] = str(name)
                logger.info("Received from CasparCG: " + received)
                return received
            else:
                logger.error("Not connected to CasparCG")
                return "Not connected to CasparCG"
        except socket.error:
            logger.error("Play template command failed")
            return "Play template command failed"

    def actually_play_template(self, channel, layer):
        command = 'CG ' + str(channel) + '-' + str(layer) + ' PLAY 10'
        try:
            logger.info("Sending command: " + command)
            if self.casparcg:
                self.casparcg.send((command + '\r\n').encode("UTF-8"))
                received = self.casparcg.recv(1024).decode("UTF-8")
                logger.info("Received from CasparCG: " + received)
                return received
            else:
                logger.error("Not connected to CasparCG")
                return "Not connected to CasparCG"
        except socket.error:
            logger.error("Play template command failed")
            return "Play template command failed"

    def update_template(self, channel, layer, parameters=""):
        command = 'CG ' + str(channel) + '-' + str(layer) + ' UPDATE 10 \"<templateData>'
        # params,count = self.string_split(parameters)
        delimited = parameters.split("|")
        count = len(delimited)
        for i in range(count):
            command += '<componentData id=\\\"' + html.escape(delimited[i].split("=")[0]) + '\\\"><data id=\\\"text\\\" value=\\\"' + html.escape(delimited[i].split("=")[1]) + '\\\" /></componentData>'
        command += "</templateData>\""
        try:
            logger.info("Sending command: " + command)
            if self.casparcg:
                self.casparcg.send((command + '\r\n').encode("UTF-8"))
                received = self.casparcg.recv(1024).decode("UTF-8")
                logger.info("Received from CasparCG: " + received)
                return received
            else:
                logger.error("Not connected to CasparCG")
                return "Not connected to CasparCG"
        except socket.error:
            logger.error("Update command failed")
            return "Update command failed"

    def invoke_template(self, channel, layer, method):
        command = 'CG '+ str(channel) + '-' + str(layer) + ' INVOKE 10 \"' + str(method) + '\"'
        try:
            logger.info("Sending command: " + command)
            if self.casparcg:
                self.casparcg.send((command + '\r\n').encode("UTF-8"))
                received = self.casparcg.recv(1024).decode("UTF-8")
                logger.info("Received from CasparCG: " + received)
                return received
            else:
                logger.error("Not connected to CasparCG")
                return "Not connected to CasparCG"
        except socket.error:
            logger.error("Invoke command failed")
            return "Invoke command failed"

    def stop_template(self, channel, layer):
        command = 'CG ' + str(channel) + '-' + str(layer) + ' STOP 10'
        try:
            if self.playing_templates[str(channel) + "-" + str(layer)]:
                pass
        except KeyError:
            return "Already stopped OK"
        try:
            logger.info("Sending command: " + command)
            if self.casparcg:
                self.casparcg.send((command + '\r\n').encode("UTF-8"))
                received = self.casparcg.recv(1024).decode("UTF-8")
                if self.process_return_data(received) == 1:
                    del self.playing_templates[str(channel) + '-' + str(layer)]
                logger.info("Received from CasparCG: " + received)
                return received
            else:
                logger.error("Not connected to CasparCG")
                return "Not connected to CasparCG"
        except socket.error:
            logger.error("Stop command failed")
            return "Stop command failed"

    def get_video_list(self):
        video_list = {}
        command = 'CLS'
        try:
            logger.info("Sending command: " + command)
            self.casparcg.send((command + '\r\n').encode("UTF-8"))
            received = self.casparcg.recv(65535).decode("UTF-8")
            logger.info("Received from CasparCG: " + received)

            delimited = received.split("\r\n")
            count=len(delimited)
            for i in range(1, (count - 2)):

                # split current data row based on spaces
                temp_data = delimited[i].split()

                # create dictionary for current video element
                video_list[i] = {}

                name = ""
                name_parts = len(temp_data[:-6])

                # collect data for current video element
                for j in range(name_parts + 1):
                    if j == name_parts:
                        name += temp_data[j]
                    else:
                        name += temp_data[j] + " "

                video_list[i]["name"] = name.replace('"', '')
                video_list[i]["type"] = temp_data[-5]
                video_list[i]["file_size"] = temp_data[-4]
                video_list[i]["date_modified"] = temp_data[-3]
                video_list[i]["frames"] = temp_data[-2]
                video_list[i]["frame_rate"] = temp_data[-1]

            return video_list
        except socket.error:
            logger.error("CLS command failed")
            return "CLS command failed"

    def kill_switch(self):
        for i in range(1, 5):
            command = "CLEAR " + str(i)
            try:
                logger.info("Sending command: " + command)
                self.casparcg.send((command + '\r\n').encode("UTF-8"))
                received = self.casparcg.recv(1024).decode("UTF-8")
                logger.info("Received from CasparCG: " + received)
            except socket.error:
                logger.error("Clear command failed")
            self.playing_templates = {}

    def caspar_disconnect(self):
        if self.casparcg is not None:
            try:
                self.casparcg.close()
                self.casparcg = None
                logger.info("Closing connection to CasparCG")
            except socket.error as e:
                logger.error("Error closing socket" + str(e))
                return "Error closing socket" + str(e)
            self.connected = False
            return "Closed connection to CasparCG Server"
        else:
            logger.warning("Not connected to a CasparCG Server")
            return "Not connected to a CasparCG Server"
