import serial
import sys
import os
import os.path
import time

class cnc:
	def __init__(self):
		self.ser = serial.Serial(
			port='/dev/ttyUSB0',\
			baudrate=115200,\
			parity=serial.PARITY_NONE,\
			stopbits=serial.STOPBITS_ONE,\
			bytesize=serial.EIGHTBITS,\
			rtscts=0,\
			xonxoff=True,\
			timeout=0)
		print self.transaction("\r\n\r")
		
	def transaction(self,line):
		self.ser.write(line+"\n")
		dummy=self.ser.readline()
		while (len(dummy) < 2) or (dummy[-1]!='\n'):
			dummy += self.ser.readline()
		return dummy.strip()
		
	def check(self,line):
		if line.startswith('M2 '):
			return False
		if line.startswith('M0 '):
			return False
		if (len(line)>3 and line[0]!='('):
			return True
		return False
		
	def sendbuf(self,buf):
		out=[]
		for line in buf:
			if self.check(line):
				print line
				result = self.transaction(line)
				print ">"+ result
				out.append(result)
		return out		
	def	__del__(self):
		self.ser.close()
		
		
if __name__ == "__main__":		
		
	filename = sys.argv[1]

	if not(os.path.isfile(filename)):
		print("File %s doesn't exist -> exit" % filename)
		exit()
		
	c = cnc()
	buf = []
	nline = 0 
	   
	with open(filename,'r') as f: 
		for line in f:
			buf.append(line.strip())
			nline += 1
			
	print("Found: %d line(s)" % nline)
			   
	c.sendbuf(buf)
	buf = ["G0 X0Y0Z25","M2"]
	c.sendbuf(buf)

	

	



