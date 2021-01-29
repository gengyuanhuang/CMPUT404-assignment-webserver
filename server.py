#!/usr/bin/env python3

"""
Copyright 2021 Abram Hindle, Eddie Antonio Santos, Gengyuan Huang

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Furthermore it is derived from the Python documentation examples thus
some of the code is Copyright © 2001-2013 Python Software
Foundation; All Rights Reserved

http://docs.python.org/2/library/socketserver.html

"""

import socketserver
import os

ENCODING_METHOD = 'utf-8'       # encoding method
LOG_TO_STDOUT = True            # set to True will print log to stdout
LOG_DEEP = False                # set to True if you want complete log
HOST, PORT = "localhost", 8080  # server address

# helpers - parser
def convertByteToStr(byteData):
    # convert byte data to string using encoding method
    stringData = byteData.decode(ENCODING_METHOD)
    return stringData

def assertRequestValidity(stringData):
    # script for checking http request format
    # add more later
    
    # not empty
    assert (len(stringData) != 0)

def parseRequest(stringData):
    # parse the http request, return a dictionary of all request
    # assume correct format
    request_dict = dict()
    data_splited = stringData.split("\r\n")

    header_done = False
    method_done = False
    for data in data_splited:
        if method_done:
            if header_done:
                request_dict["body"] += data    # store body
            else:
                if data == '':                  # header done
                    header_done = True
                    request_dict["body"] = ""   # init body entry
                else:
                    # form: XXX: XXXXXXX
                    dataline = data.replace(": ", "\r\n", 1)        # replace first ": " with a delimiter "\r\n" that for sure wont occurs in message body
                    dataline_splited = dataline.split("\r\n")       # split data line into two
                    request_dict[dataline_splited[0].strip()] = dataline_splited[1].strip()     # store the key value pair
        else:
            method_done = True
            request_dict["method"] = data   # store first line to dictionary

    return request_dict

def parseValidRequest(stringData):
    # wrapping parseRequest, add checking method
    try:
        assertRequestValidity(stringData)   # checking validity
        return parseRequest(stringData)     # return dictionary. Note: exception may also happend at this step
    except:
        return None                         # exception happened, possibility wrong format, less checking for simplicity

# helpers - file
os.chdir("www")

def autoCorrectPath(path):
    # check if given path exist
    # if not then 
    # path /xxx

    path = os.path.realpath(path)       # get the real path
    path_check = "." + path


    if os.path.exists(path_check):
        # can be a directory or file
        # if path[-1] == '/' then directory
        # else, could be file or directory
        if path_check[-1] == '/':
            return path
        else:
            if os.path.isfile(path_check):
                return path
            else:
                return path + "/"
    else:
        # not found
        return None

# respond headers
def headerStatusCode(statusCode):
    # assume status Code exist, will raise exception if status code doesnot exist
    statusCodeDict = {
        100: "Continue",
        101: "Switching Protocols",
        200: "OK",
        201: "Created",
        202: "Accepted",
        203: "Non-Authoritative Infomation",
        204: "No Content",
        205: "Reset Content",
        206: "Partial Content",
        300: "Multiple Choices",
        301: "Moved Permanently",
        302: "Found",
        303: "See Other",
        304: "Not Modified",
        305: "Use Proxy",
        307: "Temporary Redirect",
        400: "Bad Request",
        401: "Unauthorized",
        402: "Payment required",
        403: "Forbidden",
        404: "Not Found",
        405: "Method not allowed",
        406: "Not Acceptable",
        407: "Proxy Authentication Required",
        500: "Internal Server Error"
    }

    return str(statusCode) + " " + statusCodeDict[statusCode]

def headerConnection(connectionStr):
    return "Connection: " + connectionStr

def headerContent(contentStr):
    return "Content-Type: " + contentStr

def headerHTTPVersion(version):
    return "HTTP"+"/"+str(version)

def headerLocation(location):
    return "Location: " + location

# handler
def handleRequestGET(requestDict):
    # handling GET request
    # return responds
    # assume correct format
    # simplified

    # parse method line, get path
    methodline = requestDict["method"]
    methodline_splited = methodline.split()
    host = requestDict["Host"]
    path = methodline_splited[1]
    path_corrected = autoCorrectPath(path)

    # respond and close connection if path not exist or not correct
    if path_corrected == None:
        header = \
            headerHTTPVersion(1.1) + " "                                + \
                headerStatusCode(404) + "\r\n"                          + \
                    headerConnection("Closed") + "\r\n\r\n"
        return bytearray(header, ENCODING_METHOD), b''

    if path_corrected != path:
        header = \
            headerHTTPVersion(1.1) + " "                                            + \
                headerStatusCode(301) + "\r\n"                                      + \
                    headerLocation("http://" + host + path_corrected) + "\r\n"      + \
                        headerConnection("Closed") + "\r\n\r\n"
        return bytearray(header, ENCODING_METHOD), b''

    # retrive data
    # for this assignment only suppose css and html file
    path_real = "." + path_corrected
    if os.path.isdir(path_real):
        # serve index.html
        header = \
            headerHTTPVersion(1.1) + " "                                        + \
                headerStatusCode(200) + "\r\n"                                  + \
                    headerContent("text/html") + "\r\n"                         + \
                        headerConnection("Closed") + "\r\n\r\n"
        response = b''
        # get content, append at the end of response
        with open(path_real + "/" + "index.html", "rb") as f:
            response += f.read()
        
        # return respond
        return bytearray(header, ENCODING_METHOD), response
    else:
        # serve file
        # only support html/css
        # all other file will be treated as text/plain
        
        # get extension
        filename = path_real.split()[-1]
        filename_splited = filename.split(".")
        filename_extension = ''
        if len(filename_splited) != 1:
            filename_extension = filename_splited[-1]

        # define file type
        content_type = "text/plain"             # default: text/plain
        if filename_extension == "css":
            content_type = "text/css"
        elif filename_extension == "html":
            content_type = "text/html"
        elif filename_extension == "xml":
            content_type = "text/xml"
        elif filename_extension == "csv":
            content_type = "text/csv"
        elif filename_extension == "pdf":
            content_type = "application/pdf"

        # serve
        header = \
            headerHTTPVersion(1.1) + " "                                        + \
                headerStatusCode(200) + "\r\n"                                  + \
                    headerContent(content_type) + "\r\n"                         + \
                        headerConnection("Closed") + "\r\n\r\n"

        # get content, append at the end of response
        response = b''
        with open(path_real, "rb") as f:
            response += f.read()
        
        # return respond
        return bytearray(header, ENCODING_METHOD), response

def handleRequest(byteData):
    # handling all requests
    # return the respond data

    # parse the byteData
    stringData = convertByteToStr(byteData)
    requestDict = parseValidRequest(stringData)
    if requestDict == None:
        header = \
            headerHTTPVersion(1.1) + " "                                + \
                headerStatusCode(400) + "\r\n"                          + \
                    headerConnection("Closed") + "\r\n\r\n"
        return bytearray(header, ENCODING_METHOD), b''

    # log
    if LOG_TO_STDOUT:
        print("HTTP Request: %s\n" % requestDict["method"])

    # parse method line - firstline of the data
    methodline = requestDict["method"]
    methodline_splited = methodline.split()
    if len(methodline_splited) != 3:
        header = \
            headerHTTPVersion(1.1) + " "                                + \
                headerStatusCode(400) + "\r\n"                          + \
                    headerConnection("Closed") + "\r\n\r\n"
        return bytearray(header, ENCODING_METHOD), b''

    else:
        # direct to each method's function
        if methodline_splited[0] == 'GET':
            return handleRequestGET(requestDict)
        else:
            # cannot handle
            header = \
                headerHTTPVersion(1.1) + " "                            + \
                    headerStatusCode(405) + "\r\n"                      + \
                        headerConnection("Closed") + "\r\n\r\n"
            return bytearray(header, ENCODING_METHOD), b''

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        # get data
        self.data = self.request.recv(1024).strip()
        
        # log
        if LOG_TO_STDOUT:
            if LOG_DEEP:
                print("Receives Data: \n%s\n" % self.data)
        
        # repond data
        header, body = handleRequest(self.data)             # header and body are both of type bytes

        # log
        if LOG_TO_STDOUT:
            print("Responds with: \n%s\n" % header)

        # send back response
        self.request.sendall(header + body)

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
