#!/usr/bin/env python
# coding=utf-8
import os
import re
import urllib
import urllib2
from threading import Thread
from filelock  import FileLock
import sys 
reload(sys) 
sys.setdefaultencoding('utf-8') 


ROOTFOLDER = os.getcwd()
SAVEFOLDER = '%s/song'%(ROOTFOLDER)
SongListFile = '%s/songfile/log.txt'%(ROOTFOLDER)
LockFile   = '%s/songfile/log.lock'%(ROOTFOLDER)


ARITST = {
	"a1" : ["/fanAll?area=ML&property=Boy","内地男歌手"],	
	"a2" : ["/fanAll?area=ML&property=Girl","内地女歌手"],
	"a3" : ["/fanAll?area=ML&property=Combo","内地乐队/组合"],
	"a4" : ["/fanAll?area=HT&property=Boy","港台男歌手"],
	"a5" : ["/fanAll?area=HT&property=Girl","港台女歌手"],
	"a6" : ["/fanAll?area=HT&property=Combo","港台乐队/组合"],
	"a7" : ["/fanAll?area=US&property=Boy","欧美男歌手"],
	"a8" : ["/fanAll?area=US&property=Girl","欧美女歌手"],
	"a9" : ["/fanAll?area=US&property=Combo","欧美乐队/组合"],
	"a10" : ["/fanAll?area=KR&property=Boy","韩语男歌手"],
	"a11" : ["/fanAll?area=KR&property=Girl","韩语女歌手"],
	"a12" : ["/fanAll?area=KR&property=Combo","韩语乐队/组合"],
	"a13" : ["/fanAll?area=JP&property=Boy","日语男歌手"],
	"a14" : ["/fanAll?area=JP&property=Girl","日语女歌手"],
	"a15" : ["/fanAll?area=JP&property=Combo","日语乐队/组合"]
}
AreaDataMap={}

def main():
	f=open(SongListFile,'w')
	f.write('')
	f.close()
	for key in ARITST:
		kclass=ARITST[key][1]
		val = ARITST[key][0]
		GsDataMap={}
		kclass=kclass.decode('utf-8')
		AreaDataMap[kclass]=GsDataMap
		url = 'http://www.yinyuetai.com%s'%val
		dir = '%s/%s'%(SAVEFOLDER,kclass)
		t = Agent(url,GsDataMap,dir)
		t.start()
		
def readhead(url):
	try:
		req = urllib2.Request(url)
		req.add_header("User-Agent", "Mozilla/5.0 (X11; U; Linux i686; zh-CN; rv:1.9.2.13) Gecko/20101206 Ubuntu/8.04 (hardy) Firefox/3.6.13")
		req.add_header("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
		req.add_header("Accept-Language", "zh-cn,en;q=0.5")
		req.add_header("Connection", "Keep-Alive")
		f = urllib2.urlopen(req)
		head = f.head()
		return head
	except:
		print '%s error'%url
		return ''
	
def readhtml(url):
	try:
		req = urllib2.Request(url)
		req.add_header("User-Agent", "Mozilla/5.0 (X11; U; Linux i686; zh-CN; rv:1.9.2.13) Gecko/20101206 Ubuntu/8.04 (hardy) Firefox/3.6.13")
		req.add_header("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
		req.add_header("Accept-Language", "zh-cn,en;q=0.5")
		req.add_header("Connection", "Keep-Alive")
		f = urllib2.urlopen(req)
		html = f.read()
		return html
	except:
		print '%s error'%url
		return ''
	
class Agent(Thread):
	def __init__(self,url,gsdatamap,dir):
		Thread.__init__(self)
		self.url = url
		self.gsdatamap=gsdatamap
		self.dir = dir
	def run(self):	
		#self.LoadPlayListPage(1)
		
		html = readhtml(self.url)
		#<a href="/fanAll?area=ML&page=2&property=Boy">2</a>
		
		matches = re.findall('<a\s*href=\"/fanAll\?area=[\s\S]*?&page=(\d*?)&property=[\s\S]*?">\d*?</a>',html)
		
		
		for ma in matches:
			self.LoadPlayListPage(ma)
			
	def LoadPlayListPage(self,page):
		murl = '%s&page=%s'%(self.url,page)
		html = readhtml(murl)
		#<a href="/fanclub/35" target="_blank" class="song" title="张杰">张杰</a>
		matches = re.findall('<a\s*\s*href=\"/fanclub/\d+\"\s*target=\"_blank\"\s*class=\"song\"\s*title=\"[\s\S]*?\"',html)
		
		
		for ma in matches:
			playid     = re.search("/fanclub/(\d+)",ma).group(1)
			playname   = re.search("title=\"([\s\S]*?)\"",ma).group(1)
			playname = playname.decode('utf-8')
			#print playname,playid
			playdatamap={}
			self.gsdatamap[playname]=playdatamap
			fanf = FanClubFiddler(playdatamap)
			fanf.LoadSognPage(playname,playid,self.dir)
			
class FanClubFiddler():
	def __init__(self,playdatamap):
		self.playdatamap=playdatamap
		
	def LoadSognPage(self,playname,playerid,dir):
		murl = 'http://www.yinyuetai.com/fanclub/mv-all/%s/toNew'%playerid
		self.url = murl
		self.playerid = playerid
		self.playname = playname
		self.dir      = dir
		
			
		#下载第一页
		self.LoadSongListPage(1)
		html = readhtml(self.url)
		matches = re.findall('<a\s*\s*href=\"/fanclub/mv-all/\d+/toNew/(\d+)\"',html)
		for ma in matches:
			self.LoadSongListPage(ma)
			return
			
	def LoadSongListPage(self,page):
		#<a target="_blank" title="这就是爱 北京演唱会" href="/video/393148">
		murl = '%s/%s'%(self.url,page)
		html = readhtml(murl)
		matches = re.findall('<a\s*target=\"_blank\"\s*title=\"[\s\S]*?\"\s*href=\"/video/\d+\"',html)
		
		
		for ma in matches:
			mvid = re.search("/video/(\d+)",ma).group(1)
			mvname   = re.search("title=\"([\s\S]*?)\"",ma).group(1)
			mvname   = mvname.decode('utf-8')
			#print mvname,mvid
			mvdatamap={}
			mvdatamap[mvname]=mvid
			self.playdatamap[mvname]=mvdatamap
			
			#http://www.yinyuetai.com/insite/get-video-info?flex=true&videoId=155936
			dlurl = 'http://www.yinyuetai.com/insite/get-video-info?flex=true&videoId=%s'%mvid
			dldir = '%s/%s/'%(self.dir,self.playname)
			with FileLock(LockFile):
				f=open(SongListFile,'aw')
				line = '%s,%s,%s\n'%(dldir,mvname,mvid)
				print line
				f.write(line)
				f.close()
			t = DownLoadAgent(dldir,dlurl,mvid)
			t.run()
		
		
class DownLoadAgent():#(Thread):
	def __init__(self,dldir,url,file):
		#Thread.__init__(self)
		self.dir = dldir
		self.url = url
		self.file = file
	def run(self):
		filepath = "%s/%s.flv" % (self.dir,self.file)
		if os.path.exists(filepath):
			return
			
		if not os.path.exists(self.dir):
			os.makedirs(self.dir)
			
		html = readhtml(self.url)
		#print self.url
		#http://hc.yinyuetai.com/uploads/videos/common/69DD0136AC635993418A82907929C6E2.flv
		matches = re.search('http:\/\/hc\.yinyuetai\.com/uploads/videos/common/([\s\S]*?)\.flv',html)
		
		if matches is not None:
			flv= matches.group(0)
			
			try:
				urllib.urlretrieve(flv, filepath, self.process)
			except:
				print '%s,error'%flv
				
	def process(self, block, block_size, total_size):
		block_numbers=block
		block_size=block_size
		file_total_size=total_size
		temp_file_total_size=block_numbers*block_size
		if temp_file_total_size>file_total_size:
			print "%s/%s,Download Successful!"%(self.dir,self.file)
		#else:
			#print str(float(temp_file_total_size)/file_total_size*100)[0:5]+"%"
	

if __name__ == '__main__':
	main()


