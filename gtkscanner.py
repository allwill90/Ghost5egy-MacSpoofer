import gtk
import pango
import nmap
import sys
import os.path
from info import *
from spoofmac.version import __version__
from spoofmac.util import random_mac_address, MAC_ADDRESS_R, normalize_mac_address

from spoofmac.version import __version__
from spoofmac.util import random_mac_address, MAC_ADDRESS_R, normalize_mac_address
if sys.platform == 'win32':
    import ctypes


from spoofmac.interface import (
	wireless_port_names,
	find_interfaces,
	find_interface,
	set_interface_mac,
	get_os_spoofer
)


# Return Codes
SUCCESS = 0
INVALID_ARGS = 1001
UNSUPPORTED_PLATFORM = 1002
INVALID_TARGET = 1003
INVALID_MAC_ADDR = 1004
NON_ROOT_USER = 1005

devlist = []
portlist = []
nmask = ""
ipaddr = ""
gway = ""
tmac = ""

def get_intterfaces():

	spoofer = get_os_spoofer()
	targets = []
	line = []

	for port, device, address, current_address in spoofer.find_interfaces(targets=targets):
		devlist.append(device)
		portlist.append(port)

class mywindow(gtk.Window):

	def __init__(self):
		gtk.Window.__init__(self,gtk.WINDOW_TOPLEVEL)
		self.set_size_request(600, 400)
		self.Mainbox = gtk.HBox(spacing = 3)
		self.add(self.Mainbox)
		self.thirdbox = gtk.VBox(spacing = 3)
		self.Mainbox.pack_start(self.thirdbox,True,True,5)
		self.Ncard = gtk.HBox(spacing = 3)
		self.thirdbox.pack_start(self.Ncard,True,True,5)
		self.label = gtk.Label("Network Card")
		self.Ncard.pack_start(self.label,True,True,5)
		self.entry = gtk.Combo()
		self.entry.set_popdown_strings(devlist)
		self.entry.entry.connect("changed", self.getifinfo)
		self.entry.entry.set_text("Choose Network Card")
		self.Ncard.pack_start(self.entry,True,True,5)
		self.sbtn = gtk.Button(label="Use this")
		self.sbtn.connect("clicked",self.on_sbtn_click)
		self.Ncard.pack_start(self.sbtn,True,True,5)
		self.ifinfo = gtk.HBox(spacing = 3)
		self.thirdbox.pack_start(self.ifinfo,True,True,5)
		self.iplbl = gtk.Label("ip : 0.0.0.0")
		self.ifinfo.pack_start(self.iplbl,True,True,5)
		self.netmlbl = gtk.Label("netmask : 0.0.0.0")
		self.ifinfo.pack_start(self.netmlbl,True,True,5)
		self.glbl = gtk.Label("gateway : 0.0.0.0")
		self.ifinfo.pack_start(self.glbl,True,True,5)
		self.spbtn = gtk.Button(label="Act like selected")
		self.spbtn.connect("clicked",self.on_spbtn_click)
		self.ifinfo.pack_start(self.spbtn,True,True,5)
		self.table = gtk.ScrolledWindow()
		self.table.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.thirdbox.pack_start(self.table,True,True,5)
		self.treestore = gtk.ListStore(int, str, str)
		self.treeview = gtk.TreeView(self.treestore)
		self.cell = gtk.CellRendererText()
		self.tvcolumn = gtk.TreeViewColumn('Num',self.cell ,text=0)
		self.treeview.append_column(self.tvcolumn)
		self.tvcolumn.set_sort_column_id(0)
		self.cell1 = gtk.CellRendererText()
		self.tvcolumn1 = gtk.TreeViewColumn('IP Address',self.cell1 ,text=1)
		self.treeview.append_column(self.tvcolumn1)
		self.tvcolumn1.set_sort_column_id(1)
		self.cell2 = gtk.CellRendererText()
		self.tvcolumn2 = gtk.TreeViewColumn('Mac Address',self.cell2 ,text=2)
		self.treeview.append_column(self.tvcolumn2)
		self.tvcolumn2.set_sort_column_id(2)
		self.table.add(self.treeview)
		self.statelbl = gtk.Label("Choose Network Card")
		self.thirdbox.pack_start(self.statelbl,True,True,5)
		
	def on_sbtn_click(self, widget):
		global nmask
		global ipaddr
		global gway
		self.treestore.clear()
		hlist = []
		netmask = sum([bin(int(x)).count('1') for x in nmask.split(".")])
		nm = nmap.PortScanner()
		nres = nm.scan(hosts=ipaddr+'/'+str(netmask), arguments='-sP -PR')
		print nres 
		nmaps = nres['nmap']
		scan  = nres['scan']
		print nmaps['command_line']
		print nmaps['scanstats']['uphosts']
		print nmaps['scanstats']['downhosts']
		print nmaps['scanstats']['totalhosts']
		
		for x in scan:
			hlist.append(x)
		
		c = 0
		
		for i in hlist:
			if "mac" not in scan[i]['addresses'].keys():
				c = c + 1
				print c,"ip : "+scan[i]['addresses']['ipv4']+" on mac : None "
				self.treestore.append((c,(scan[i]['addresses']['ipv4']),(None)))
				continue
			else:
				c = c + 1
				print c,"ip : "+scan[i]['addresses']['ipv4']+" on mac : "+scan[i]['addresses']['mac']
				self.treestore.append((c,(scan[i]['addresses']['ipv4']),(scan[i]['addresses']['mac'])))
		self.statelbl.set_text("Scan Done Choose Device to act like")
	
	def on_spbtn_click(self, widget):
		global tmac
		selection = self.treeview.get_selection()
		(model , selrow) = selection.get_selected()
		if selrow != None :
			if gway != model.get_value(selrow,1):
				print model.get_value(selrow,0)
				print model.get_value(selrow,1)
				print model.get_value(selrow,2)
				tmac = model.get_value(selrow,2)
				self.changemac()
			else:
				self.statelbl.set_text("You must select any other device not your gateway")
				print "You must select any other device not your gateway"
		else:
			self.statelbl.set_text("You Must select something")
			print "You Must select something"
	
	def getifinfo(self, widget):
		global nmask
		global ipaddr
		global gway
		if sys.platform == 'win32':
			ipaddr = win_getinfo(self.entry.entry.get_text(), "IPv4 Address")
			if ipaddr != None:
				self.iplbl.set_text("ip : "+ipaddr)
			else:
				self.iplbl.set_text("ip : 0.0.0.0")	
				
			nmask = win_getinfo(self.entry.entry.get_text(), "Subnet Mask")
			if nmask != None:
				self.netmlbl.set_text("netmask : "+nmask)
			else:
				self.netmlbl.set_text("netmask : 0.0.0.0")
				
			gway = win_getinfo(self.entry.entry.get_text(), "Default Gateway")
			if gway != None:
				self.glbl.set_text("gateway : "+gway)
			else:
				self.glbl.set_text("gateway : 0.0.0.0")
		else:
			ipaddr = nix_getinfo(self.entry.entry.get_text(), "inet addr")
			if ipaddr != None:
				self.iplbl.set_text("ip : "+ipaddr)
			else:
				self.iplbl.set_text("ip : 0.0.0.0")	
				
			nmask = nix_getinfo(self.entry.entry.get_text(), "Mask")
			if nmask != None:
				self.netmlbl.set_text("netmask : "+nmask)
			else:
				self.netmlbl.set_text("netmask : 0.0.0.0")
				
			gway = nix_getinfo(self.entry.entry.get_text(), "gateway")
			if gway != None:
				self.glbl.set_text("gateway : "+gway)
			else:
				self.glbl.set_text("gateway : 0.0.0.0")
		
		self.statelbl.set_text("Press Use this")
	
	def changemac(self):
		global tmac
		try:
			root_or_admin = os.geteuid() == 0
		except AttributeError:
			root_or_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
		
		else:
			spoofer = None

			try:
				spoofer = get_os_spoofer()
			except NotImplementedError:
				return UNSUPPORTED_PLATFORM
			result = find_interface(self.entry.entry.get_text())
			if result is None:
				print('- couldn\'t find the device for {target}'.format(
					target=target
				))
				self.statelbl.set_text("Couldn't find device ")
				return INVALID_TARGET
				
			port, device, address, current_address = result			
			target_mac = tmac
			if int(target_mac[1], 16) % 2:
				self.label3.set_text("It's Multicast Address")
				print('Warning: The address you supplied is a multicast address and thus can not be used as a host address.')
			
			if not MAC_ADDRESS_R.match(target_mac):
				print('- {mac} is not a valid MAC address'.format(
					mac=target_mac
				))
				return INVALID_MAC_ADDR

			if not root_or_admin:
				if sys.platform == 'win32':
					print('Error: Must run this with administrative privileges to set MAC addresses')
					self.statelbl.set_text("You Need to run as admin")
					return NON_ROOT_USER
				else:
					print('Error: Must run this as root (or with sudo) to set MAC addresses')
					self.statelbl.set_text("You Need to run as root")
					return NON_ROOT_USER
			asd = set_interface_mac(device, target_mac, port)
			self.statelbl.set_text("Mac Spoofed")
			self.getifinfo()
			
get_intterfaces()
win = mywindow()
win.set_title("Ghost5egy MacSpoofer")
win.connect("delete-event",gtk.main_quit)
win.show_all()
gtk.main()