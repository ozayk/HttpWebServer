#!/usr/bin/python

import socket
import sys
import os
import threading
import subprocess
import ConfigParser

if (len(sys.argv) != 2):
        print "<Usage>: <filename> <configfile>"
        sys.exit()

Config = ConfigParser.ConfigParser()
Config.read(sys.argv[1])
Config.sections()

HOST = Config.get('ServerSocket', 'Host')
PORT = int(Config.get('ServerSocket', 'Port'))

MethodDisabled = {}
MethodDisabled['GET'] = Config.get('MethodDisabled', 'GET')
MethodDisabled['POST'] = Config.get('MethodDisabled', 'POST')
MethodDisabled['PUT'] = Config.get('MethodDisabled', 'PUT')
MethodDisabled['DELETE'] = Config.get('MethodDisabled', 'DELETE')
MethodDisabled['CONNECT'] = Config.get('MethodDisabled', 'CONNECT')

ServerRoot = Config.get('Locations', 'ServerRootLocation')
good_log = Config.get('Locations', 'GoodLog')
bad_log = Config.get('Locations', 'BadLog')

HandleAppBin = Config.get('WebApps', 'UserHandleBin')
HandleAppFile = Config.get('WebApps', 'UserHandleFile')
LoginAppBin = Config.get('WebApps', 'UserLoginBin')
LoginAppFile = Config.get('WebApps', 'UserLoginFile')

try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
        print 'Error while creating socket'
        sys.exit()

try:
        s.bind((HOST,PORT))
except socket.error, msg:
        print "Error while binding host : " + str(msg[0]) + " Message " + msg[1]
        sys.exit()

print "Socket bind successful"

s.listen(3)
print "Socket is now listening, ready for connections"

def parse_header(data):
        h_lines = data.split('\r\n')
        h_words = h_lines[0].split(' ')
        d_words = {}
        l = [h_lines.index(i) for i in h_lines if 'Cookie' in i]
        if (len(l) != 0):
                cookie_value = h_lines[l[0]].split(' ')[1].split('=')[1]
                d_words['Cookie'] = cookie_value
        else:
                d_words['Cookie'] = "DELETED"
        l = [h_lines.index(i) for i in h_lines if 'Content-Length' in i]
        if (len(l) != 0):
                c_length = h_lines[l[0]].split(' ')[1]
                d_words['Content-Length'] = c_length
        else:
                d_words['Content-Length'] = "0"
        d_words['Method'] = h_words[0]
        d_words['Path'] = h_words[1]
        d_words['Version'] = h_words[2][5:8]
        h_lines_len = len(h_lines)
        d_words['Data'] = h_lines[h_lines_len-1]
        if(d_words['Data'].split('&')[0].split('=')[0] == "_method"):
                d_words['Method'] = d_words['Data'].split('&')[0].split('=')[1]
        return d_words

def ConnHandler(ConnSock,addr):
        data = ConnSock.recv(1024)
        print "Recieved Request:\n"
        print data
        parsed_fields = {}
        parsed_fields = parse_header(data)


        if(parsed_fields['Version'] != "1.1"):
                response_header = ("HTTP/1.1 505 HTTP Version Not Supported\r\n\r\n")
                with open(bad_log, "a") as f2:
                        f2.write("HTTP Version Not Supported\n")

        if(parsed_fields['Method'] == 'GET' and MethodDisabled['GET'] == 'NO'):
                path_split = parsed_fields['Path'].split('?')
                if(len(path_split[0])==1):
                        req_file = ServerRoot + "index.html"
                else:
                        req_file = path_split[0]
                if(len(path_split) > 1):
                        url_fields = path_split[1].split('&')
                        url_fields_len = len(url_fields)

                        url_params = {}
                        for fields in url_fields:
                                field_split = fields.split('=')
                                url_params[field_split[0]] = field_split[1]

                        if (parsed_fields['Cookie'] == "DELETED"):
                                loginapp = ServerRoot + LoginAppFile
                                os.system("{} {} {} {}> login_result.txt".format(LoginAppBin, loginapp, url_params['username'], url_params['password']))
                                with open("login_result.txt") as f:
                                        login_result = f.read(1)

                                if (login_result == '1'):
                                        response_header = ('HTTP/1.1 301 Moved Permanently\r\nSet-Cookie: Session-id=' + str(url_params['username']) + '\r\nLocation: http://' + str(HOST) + ':' + str(PORT) + ServerRoot + 'welcome.html\r\n\r\n')
                                        req_file = ServerRoot + "welcome.html"
                                        with open(good_log, "a") as f1:
                                                f1.write("Login Successful.\n")
                                else:
                                        response_header = ('HTTP/1.1 301 Moved Permanently\r\nLocation: http://' + str(HOST) + ':' + str(PORT) + ServerRoot + 'logon_failure.html\r\n\r\n')
                                        req_file = ServerRoot + "logon_failure.html"
                                        with open(bad_log, "a") as f2:
                                                f2.write("Login Failed\n")
                        else:
                                response_header = ("HTTP/1.1 200 OK\r\n\r\n")
                                req_file = ServerRoot + "welcome.html"
                                with open(good_log, "a") as f1:
                                        f1.write("Login Success from Cookie.\n")


                else:
                        if (parsed_fields['Cookie'] == "DELETED"):
                                if(os.path.isfile(req_file)):
                                        response_header = ("HTTP/1.1 200 OK\r\n\r\n")
                                        with open(good_log, "a") as f1:
                                                log_str = "Requested file: " + req_file + " is avaible.\n"
                                                f1.write(log_str)

                                else:
                                        response_header = ("HTTP/1.1 404 File Not Found\r\n\r\n")
                                        req_file = ServerRoot + "404.html"
                                        with open(bad_log, "a") as f2:
                                                log_str = "Requested file is NOT avaible.\n"
                                                f2.write(log_str)


                        else:
                                file_path = ServerRoot + "logout.html"
                                if(req_file == file_path or req_file == "/logout.html"):
                                        req_file = file_path
                                        response_header = ('HTTP/1.1 200 OK\r\nLocation: http://' + str(HOST) + ":" + str(PORT) + file_path + '\r\nSet-Cookie: Session-id="DELETED"\r\n\r\n')
                                        with open(good_log, "a") as f1:
                                                f1.write("User Logged Out\n")


                                else:
                                        response_header = ("HTTP/1.1 200 OK\r\n\r\n")
                                        req_file = ServerRoot + "welcome.html"


                file_content = open(req_file,"r")
                response_body = file_content.read()
                ConnSock.sendall(response_header)
                ConnSock.sendall(response_body)
                file_content.close()
                ConnSock.close()

        if(parsed_fields['Method'] == 'POST' and MethodDisabled['POST'] == 'NO'):
                data_split = parsed_fields['Data'].split('&')
                data_params = {}
                for d_fields in data_split:
                        data_fields = d_fields.split('=')
                        data_params[data_fields[0]] = data_fields[1]
                req_file = ServerRoot + "user_handle.php"
                if (parsed_fields['Content-Length'] == "0"):
                        response_header = ("HTTP/1.1 411 Length Required\r\n\r\n")
                        req_file = ServerRoot + "411.html"
                        with open(bad_log, "a") as f2:
                                f2.write("Error: Content Length Required\n")

                else:
                        if(os.path.isfile(req_file)):
                                response_header = ("HTTP/1.1 200 OK\r\n\r\n")
                                appfile = ServerRoot + HandleAppFile
                                os.system("{} {} {} {} {}> register_result.txt".format(HandleAppBin, appfile, data_params['username'], data_params['password'], data_params['email']))
                                with open("register_result.txt") as f:
                                        register_result = f.read(1)
                                if (register_result == "0"):
                                        req_file = ServerRoot + "register_error.html"
                                        response_header = ("HTTP/1.1 422 Unprocessable Entity\r\n\r\n")
                                        with open(bad_log, "a") as f2:
                                                f2.write("Error: Registration Failed\n")
                                elif (register_result == "1"):
                                        req_file = ServerRoot + "register_success.html"
                                        response_header = ('HTTP/1.1 301 Moved Permanently\r\nLocation: http://' + str(HOST) + ':' + str(PORT) + req_file + '\r\n\r\n')
                                        with open(good_log, "a") as f1:
                                                f1.write("Registration Successful.\n")
                                else:
                                        req_file = ServerRoot + "register_error.html"
                                        response_header = ("HTTP/1.1 422 Unprocessable Entity\r\n\r\n")
                                        with open(bad_log, "a") as f2:
                                                f2.write("Error: Registration Failed\n")

                        else:
                                response_header = ("HTTP/1.1 404 File Not Found\r\n\r\n")
                                req_file = ServerRoot + "404.html"

                file_content = open(req_file, "r")
                response_body = file_content.read()
                ConnSock.sendall(response_header)
                ConnSock.sendall(response_body)
                ConnSock.close()

        if(parsed_fields['Method'] == 'PUT' and MethodDisabled['PUT'] == 'NO'):
                put_data = parsed_fields['Data']
                req_file = ServerRoot + "user_handle.php"
                if(parsed_fields['Content-Length'] == "0"):
                        response_header = ("HTTP/1.1 411 Length Required\r\n\r\n")
                        with open(bad_log, "a") as f2:
                                f2.write("Error: Content Length Required\n")
                else:
                        if(os.path.isfile(req_file)):
                                response_header = ("HTTP/1.1 200 OK\r\n\r\n")
                                appfile = ServerRoot + HandleAppFile
                                os.system("{} {} {} {}> update_result.txt".format(HandleAppBin, appfile, parsed_fields['Cookie'], put_data.split('&')[1].split('=')[1]))
                                with open("update_result.txt") as f:
                                        register_result = f.read(1)
                                if (register_result == "0"):
                                        req_file = ServerRoot + "update_error.html"
                                        response_header = ("HTTP/1.1 422 Unprocessable Entity\r\n\r\n")
                                        with open(bad_log, "a") as f2:
                                                f2.write("Error Updating Email.\n")
                                elif (register_result == "1"):
                                        req_file = ServerRoot + "update_success.html"
                                        response_body = ""
                                        with open(good_log, "a") as f1:
                                                f1.write("Email Updated Successfuly\n")
                                else:
                                        req_file = ServerRoot + "update_error.html"
                                        response_header = ("HTTP/1.1 422 Unprocessable Entity\r\n\r\n")
                                        with open(bad_log, "a") as f2:
                                                f2.write("Error Updating Email.\n")
                        else:
                                response_header = ("HTTP/1.1 404 File Not Found\r\n\r\n")
                                req_file = ServerRoot + "404.html"

                file_message = open(req_file,"r")
                response_body = file_message.read()
                serve_file = ServerRoot + "welcome.html"
                file_content = open(serve_file, "r")
                response_body += file_content.read()
                ConnSock.sendall(response_header)
                ConnSock.sendall(response_body)
                ConnSock.close()

        if(parsed_fields['Method'] == 'DELETE' and MethodDisabled['DELETE'] == 'NO'):
                msg_file = ""
                appfile = ServerRoot + HandleAppFile
                os.system("{} {} {}> delete_result.txt".format(HandleAppBin, appfile, parsed_fields['Cookie']))
                with open("delete_result.txt") as f:
                        delete_result = f.read(1)
                        if (delete_result == "0"):
                                msg_file = ServerRoot + "delete_error.html"
                                req_file = ServerRoot + "welcome.html"
                                response_header = ("HTTP/1.1 422 Unprocessable Entity\r\n\r\n")
                                with open(bad_log, "a") as f2:
                                        f2.write("Error Deleting user.\n")
                        elif (delete_result == "1"):
                                msg_file = ServerRoot + "delete_success.html"
                                req_file = ServerRoot + "index.html"
                                response_header = ('HTTP/1.1 200 OK\r\nSet-Cookie: Session-id="DELETED"\r\n\r\n')
                                with open(good_log, "a") as f1:
                                        f1.write("User Deleted Successfuly.\n")
                file_message = open(msg_file, "r")
                response_body = file_message.read()
                file_content = open(req_file, "r")
                response_body += file_content.read()
                ConnSock.sendall(response_header)
                ConnSock.sendall(response_body)
                ConnSock.close()

        else:
                response_header = ("HTTP/1.1 405 Method Not Allowed\r\n\r\n")
                req_file = ServerRoot + "405.html"
                file_content = open(req_file, "r")
                response_body = file_content.read()
                ConnSock.sendall(response_header)
                ConnSock.sendall(response_body)
                ConnSock.close()



while True:
        ConnSock, addr = s.accept()
        log_str = "Connected to: " + addr[0] + ":" + str(addr[1]) + "\n"
        print log_str
        with open(good_log, "a") as f1:
                f1.write(log_str)

        UseConnectionThreads = threading.Thread(target=ConnHandler, args=(ConnSock,addr),)
        UseConnectionThreads.start()

ConnSock.close()
s.close()
