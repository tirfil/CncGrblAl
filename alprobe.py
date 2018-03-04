import serial
import sys
import os
import os.path
import time
import re
import marshal
import string



re_probe = re.compile("PRB:([^,]+),([^,]+),([^:]+):1")

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
		#time.sleep(0.2)
		return self.receive()
		#out=self.ser.readline()
		#while (len(out) < 2) or (out[-1]!='\n'):
			#out += self.ser.readline()
		#return out.strip()
		
	def receive(self):
		out=self.ser.readline()
		while (len(out) < 2) or (out[-1]!='\n'):
			out += self.ser.readline()
		out = out.strip()
		print ">"+ out +"<"
		return out
		
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
				out.append(result)
		return out		
	def	__del__(self):
		self.ser.close()
		
if __name__ == "__main__":
		
	if len(sys.argv) != 4:
		print "Usage: %s <xmax> <ymax> <increment>" % sys.argv[0]
		exit()
		
	xmax = float(sys.argv[1])
	ymax = float(sys.argv[2])
	incr = float(sys.argv[3])
	
	print "x: %f - y: %f - incr: %f" % (xmax,ymax,incr)
	
	if (xmax == 0) or (ymax == 0) or (incr == 0):
		exit()
		
	str_setup="""
G94 ( Millimeters per minute feed rate. )
G21 ( Units == Millimeters. )
G90 ( Absolute coordinates. )
F120.00000 ( Feedrate. )
G00 Z2.000 ( Move Z to safe height )
G00 X0 Y0 ( Move XY to start point )
G00 Z2.000 ( Move Z to probe height )
G38.2 Z-3 F80 ( Z-probe )
"""
	str_setup2="""
G10 L20 P0 Z0 ( Set the current Z as zero-value )
G01 Z2.000
G04 P0 ( dwell for no time -- G64 should not smooth over this point )
"""
	
	str_end = """
G00 Z2.000
G00 X0Y0
G38.2 Z-3 F80 ( Z-probe )
"""
	
	c = cnc()
	
	probe=[]
	
	c.sendbuf(str_setup.split('\n'))
	c.receive() #G38.2 extra
	c.sendbuf(str_setup2.split('\n'))
	
	y = 0.0;
	while(y <= ymax):
		x = 0.0
		while(x <= xmax):
			s = "G00 X%f Y%f" % (x,y)
			probe.extend(c.sendbuf([s]))
			s = "G38.2 Z-3 F80 ( Z-probe )"
			probe.extend(c.sendbuf([s]))
			probe.extend([c.receive()]) #G38.2 extra
			s = "G01 Z2.000"
			probe.extend(c.sendbuf([s]))
			s = "G04 P0 ( dwell for no time -- G64 should not smooth over this point )"
			probe.extend(c.sendbuf([s]))
			x += incr
		y += incr
			
	c.sendbuf(str_end.split('\n'))
	
	obj = []

	for line in probe:
		#print string.join(line).replace(' ','')
		#md = re_probe.search(string.join(line).replace(' ',''))
		#print "_"+line+"_"
		md = re_probe.search(line)
		if md:
			t = tuple([	round(25.4*float(md.group(1)),2),
					    round(25.4*float(md.group(2)),2),
					    round(25.4*float(md.group(3)),2)
					    ])
			print t
			obj.append(t)
			
	ouf = open('aldata.dat', 'wb')
	data = marshal.dump(obj,ouf)
	ouf.close()			
			
			
			
