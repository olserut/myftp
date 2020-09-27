import socket
import sys
import os

def sendMsg(param):
    s.send(param.encode())
    data = s.recv(1024).decode()
    print(data)
    return data

def PASV():
    pasvReq = ('PASV\n')
    s.send(pasvReq.encode())
    pasvResp = s.recv(1024).decode()
    return pasvResp

def login():
    username = ('USER ')
    username += input('Enter username:')
    username += ('\n')
    sendMsg(username)
    password = ('PASS ')
    password += input('Enter password:')
    password += ('\n')
    success = sendMsg(password)
    return success

def makePASV():
    pasvResp = PASV()
    dataPort = pasvParser(pasvResp)
    pasvSckt.connect((serverName,dataPort))

def pasvStrip(response, char):
    list = response.split(char)
    join = ''
    join = join.join(list)
    return join

def pasvParser(pasvResp):
    stripList = pasvResp.split(' ')
    addrElem = stripList[4]
    i1 = ''
    i1 = i1.join(addrElem)
    i2 = pasvStrip(i1, '(')
    i3 = pasvStrip(i2, ')')
    i4 = pasvStrip(i3, '.')
    i5 = i4.split(',')
    x1 = int(i5[4])
    x2 = int(i5[5])
    x3 = (x1*256)+x2
    return x3

#-------------------------------------------------------------------------------
# Functions defined above
#-------------------------------------------------------------------------------

serverName = ''
serverPort = 21

try:
    serverName = sys.argv[1]
except IndexError:
    while serverName == '':
        try:
            serverName = input('Enter the FTP servername:')
        except (OSError, socket.gaierror) as err:
            raise ValueError("Failed to connect to '%s': %s" % (serverName, str(err)))
    #todo tweaking
    #Handle gaia error
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as err_msg:
    print ('Socket Error, code:' + str(err_msg[0]) + ' , Error message : ' + err_msg[1])
    sys.exit()

s.connect((serverName,serverPort))

#TODO: connection handling

#-------------------------------------------------------------------------------
# Login module
#-------------------------------------------------------------------------------

cmd = ('')
sendMsg(cmd)
logOk = login()
logSucess = logOk.split(' ')
while logSucess[0] != '230':
    logOk = login()
    logSucess = logOk.split(' ')


#-------------------------------------------------------------------------------
# Client module
#-------------------------------------------------------------------------------

sent = 0
#sentinel value for while loop
while sent == 0:
    pasvSckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cmd = input('myftp>')
    cmdList = cmd.split(' ')
    makePASV()


    if cmdList[0] == 'ls':
      cmd = ('LIST\n')
      sendMsg(cmd)
      data = pasvSckt.recv(4096).decode()
      print(data)


    elif cmdList[0]== 'cd':
      cmd = ('CWD ')
      cmd += input('Remote directory:')
      cmd += ('\n')
      sendMsg(cmd)
      continue

#-------------------------------------------------------------------------------
    elif cmdList[0] == 'get':
      cmd = ('RETR ')
      cmd += input('Enter pathname:')
      cmd += ('\n')
      sendMsg(cmd)

      with open(filePath, 'wb') as f:
          bytes_read = f.read(4096)
          pasvSckt.sendall(bytes_read)

#-------------------------------------------------------------------------------
    elif cmdList[0] == 'put':
      cmd = ('STOR ')
      filePath = input('Enter pathname:')
      exists = os.path.exists(filePath)
      #check if file exists

      if exists == True:
          cmd += filePath
          cmd += ('\n')
          sendMsg(cmd)

          # server listening for client to connect and send a file
          with open(filePath, 'rb') as f:
              bytes_read = f.read(4096)
              pasvSckt.sendall(bytes_read)

      else:
          print('Unable to find file')
          continue


#-------------------------------------------------------------------------------
    elif cmdList[0] == 'delete':
      cmd = ('DELE ')
      cmd += input('Enter pathname:')
      cmd += ('\n')
      sendMsg(cmd)
      continue

    elif cmdList[0] == 'quit':
      sent = 1
      cmd = ('QUIT\n')
      sendMsg(cmd)
      sys.exit()

    else:
      print('Invalid input, Available commands:')
      print('ls, cd, put, get, delete, quit')
      continue

    pasvSckt.close()
    cmd = ('')
    sendMsg(cmd)




s.close()
