#!/usr/bin/env python3
import subprocess
from subprocess import check_output, CalledProcessError
import time
import argparse
import os, sys
sys.path.append(os.path.join(sys.path[0], os.path.dirname(os.getcwd())))
sys.path.append(os.path.join(sys.path[0], os.getcwd()))
import sql
import signal

class GracefulKiller:
	kill_now = False
	def __init__(self):
		signal.signal(signal.SIGINT, self.exit_gracefully)
		signal.signal(signal.SIGTERM, self.exit_gracefully)
	
	def exit_gracefully(self,signum, frame):
		self.kill_now = True

def main(serv, port):
	port = str(port)
	firstrun = True
	currentstat = []
	readstats = ""
	killer = GracefulKiller()
	old_stat_service = ""
	
	while True:
		try:			
			cmd = "echo show info | nc "+serv+" "+port+" |grep -e 'Curr\|MaxSessRate:\|SessRate:'|awk '{print $2}'"
			readstats = subprocess.check_output([cmd], shell=True)
		except CalledProcessError as e:
			print("Command error")
		except OSError as e:
			print(e)
			sys.exit()
		readstats = readstats.decode(encoding='UTF-8')	
		metric = readstats.splitlines()
		metrics = []
		for i in range(0,len(metric)):
			metrics.append(metric[i])
			
		sql.insert_mentrics(serv, metrics[0], metrics[1], metrics[2], metrics[3])
	
		time.sleep(30)	
				
		if killer.kill_now:
			break

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Metrics HAProxy service.', prog='check_haproxy.py', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	
	parser.add_argument('IP', help='Start get metrics from HAProxy service at this ip', nargs='?', type=str)
	parser.add_argument('--port', help='Start get metrics from HAProxy service at this port', nargs='?', default=1999, type=int)
					
	args = parser.parse_args()
	if args.IP is None:
		parser.print_help()
		import sys
		sys.exit()
	else: 
		try:
			main(args.IP, args.port)
		except KeyboardInterrupt:
			pass