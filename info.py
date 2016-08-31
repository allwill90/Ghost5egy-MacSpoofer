import re
import subprocess
import sys
import os
import os.path
import ctypes

def reqadminwin(argv=None, debug=False):
    shell32 = ctypes.windll.shell32
    if argv is None and shell32.IsUserAnAdmin():
        return True

    if argv is None:
        argv = sys.argv
    if hasattr(sys, '_MEIPASS'):
        # Support pyinstaller wrapped program.
        arguments = map(unicode, argv[1:])
    else:
        arguments = map(unicode, argv)
    argument_line = u' '.join(arguments)
    executable = unicode(sys.executable)
    if debug:
        print 'Command line: ', executable, argument_line
    ret = shell32.ShellExecuteW(None, u"runas", executable, argument_line, None, 1)
    if int(ret) <= 32:
        return False
    return None

def checkcon():
	if sys.platform == 'win32':
		parme = "www.google.com"
	else:
		parme = "-c 4 www.google.com"
	
	res = subprocess.check_output(["ping", parme], stderr=subprocess.STDOUT)
	res.decode('ascii')
	m = re.search("Reply from", res)
	if hasattr(m, "group") and m.group(0) != None:
		return True
	else:
		return False

def getintspeed():
	res = subprocess.check_output(["python", "speedtest_cli.py"], stderr=subprocess.STDOUT)
	res.decode('ascii')
	inttest = []
	# extract description then strip out value
	m = re.search("(?<=Download: )(.*)", res)
	if hasattr(m, "group") and m.group(0) != None:
		inttest.append(m.group(0))
	m = re.search("(?<=Upload: )(.*)", res)
	if hasattr(m, "group") and m.group(0) != None:
		inttest.append(m.group(0))
	
	return inttest

def nix_getipormask(deinfo, res):
  if deinfo == "inet addr":
    sstr = deinfo+":[0-9](.*) B"
  else:
    sstr = deinfo+":[0-9](.*)"
  m = re.search(sstr, res)
  if not hasattr(m, "group") or m.group(0) == None:
    return None
  else:
    sttr = m.group(0).strip()

  m2 = re.search("[0-9](.*)[0-9]", sttr)
  if not hasattr(m2, "group") or m2.group(0) == None:
    return None
  else:
    return m2.group(0).strip()

def nix_getdgateway(device):
  res = subprocess.check_output(["ip", "route"], stderr=subprocess.STDOUT, universal_newlines=True)
  m2 = re.search("[0-9](.*)[0-9] dev "+device, res)
  if not hasattr(m2, "group") or m2.group(0) == None:
    print None
  else:
    sttr = m2.group(0).strip()
    
  m2 = re.search("^[0-9](.*) d", sttr)
  if not hasattr(m2, "group") or m2.group(0) == None:
    return None
  else:
    sttr2 = m2.group(0).strip()
  
  m3 = re.search("[0-9](.*)[0-9]", sttr2)
  if not hasattr(m3, "group") or m3.group(0) == None:
    return None
  else:
    return m3.group(0).strip()
		
def nix_getinfo(device,deinfo, res=None):
	if (deinfo == "inet addr") or (deinfo == "Mask"):
		res = subprocess.check_output(["ifconfig", device], stderr=subprocess.STDOUT, universal_newlines=True)
		return nix_getipormask(deinfo, res)
	elif deinfo == "gateway":
		return nix_getdgateway(device)
	else:
		return None

def win_getinfo(device, deinfo):
	result = subprocess.check_output(["ipconfig", "/all"], stderr=subprocess.STDOUT)
	res = result.decode('ascii')
	sm8 = re.search("adapter "+device+":[\\n\\r]+(.*?)\\s*"+deinfo+"[^\\d]+(\\s\\S+)",res ,re.I | re.DOTALL)
	if hasattr(sm8, "group") and sm8.group(0) != None:
		sttr6 = sm8.group(0).strip()
	else:
		return None
		
	smtest = re.findall("Description",sttr6)
	if len(smtest) > 1:
		return None
		
	sm9 = re.search(deinfo+"[^\\d]+(\\s\\S+)", sttr6)
	if hasattr(sm9, "group") and sm9.group(0) != None:
		sttr7 = sm9.group(0)
	else:
		return None
	
	sm10 = re.search("(?<=:\\s)(.*)", sttr7)
	if hasattr(sm10, "group") and sm10.group(0) != None:
		ifip = sm10.group(0)
	else:
		return None
	if deinfo == "IPv4 Address" :
		sm11 = re.search("(.*)+[0-9]", ifip)
		if hasattr(sm11, "group") and sm11.group(0) != None:
			ifip2 = sm11.group(0)
			return ifip2
		else:
			return None
	else:
		return ifip