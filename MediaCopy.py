import exiftool #requried package
import os
import datetime
import hashlib
import argparse
import re
import shutil

#Where to save pictures and videos
targetLocation=['/home/meng/Pictures', '/home/meng/Videos']

MD5SUMBYTES = 20000;

#Input processing / checking
parser = argparse.ArgumentParser(description='Safe copy of images and videos to predefined location on harddrive. This programs has the following dependencies: exiftool and dateutil which must be installed before the program will run.')
parser.add_argument('source', type=str, help='Where to copy the source files from')

args = parser.parse_args()

sourcefolder=args.source #"/home/meng/work/mediaGetter/test/data";#No end /


def getFileExtension(filesource):
	filesource, ext = os.path.splitext(filesource)
	extL=ext.lower()
        lookup = {'.jpg':0, '.cr2':0, '.mov':1, '.mts':1, '.avi':1, '.mp4':1,'.mpg':1};
        try:
                key = lookup[extL]
        except KeyError:
                key = -1;
        
        print key

	return key



#MediaObject class 
class MediaObject:
        """ MediaObject contains the necessary functionality for extracting metadata from
            the files and other necessary information """
        
        mediaCounter=0
        existCounter=0
	def __init__(self, stype, filesrc, metadata):
		self.typeid = stype
		self.filedir, self.filename = os.path.split(filesrc)
                self.filesrc = filesrc
            	self.metadata = metadata
                print metadata
               	if metadata:
                        #2015:07:16 15:41:26+01:00
                        cleanDateInfo = re.split('\+',metadata)
                        metadata = cleanDateInfo[0]
                        supportedDateList = ['%Y:%m:%d %H:%M:%S']
                        for dl in supportedDateList:
                                try:
                                        dt = datetime.datetime.strptime(metadata,dl)
                                except ValueError:
                                        dt = datetime.datetime(1977,1,1,0,0)
 

                                        
                                
                                        
           
                else:
                        print 'No Metadata found in ',self.filesrc
                        dt = datetime.datetime(1977,1,1,0,0)
                                   
		self.year = dt.year
		self.month = dt.month
		self.day = dt.day
		self.md5 = self.getMd5(filesrc) 

	def getMd5(self, filesrc):
		hasher = hashlib.md5()
		with open(filesrc,'rb') as afile:
                        afile.seek(-MD5SUMBYTES,2) #read from the end of the file
			buf = afile.read(MD5SUMBYTES)
			hasher.update(buf)
		return hasher.hexdigest()

       	def copy(self):
                targetSrc = os.path.join(targetLocation[self.typeid],str(self.year),str(self.month).zfill(2),str(self.day).zfill(2))
                targetFilename = os.path.join(targetSrc, self.filename)
                if not os.path.isfile(targetFilename): #file does note exist
                        if not os.path.exists(targetSrc):
                                os.makedirs(targetSrc,0755)
                        print "Copying ",self.filesrc," to ",targetFilename
                        try:
                                shutil.copy2(self.filesrc, targetFilename)
                                MediaObject.mediaCounter += 1
                        except IOerror,e:
                                print 'Unable to copy file. %s',e
                                
                elif self.getMd5(targetFilename)==self.md5:
                        #File exist at target do not copy
                        print self.filename,"exist at target location!"
                        MediaObject.existCounter += 1
                else:
                        #Rename file at try again
                        print "Make a unique filename and copy again!"
                        filename, ext = os.path.splitext(self.filename)
                        self.filename = filename+'_'+self.md5+ext;
                        self.copy()
                        
                
class FileCrawler:
	""" Find the necessary image and movie files to be copied to disk """
	def __init__(self, source):
		self.source = source
                self.prog = re.compile('(jpg|JPG|mts|MTS|mov|MOV|avi|AVI|mp4|MP4|MPG|mpg|cr2|CR2)')
                
	def run(self):
                print "Crawling source folder", self.source
		newList = list()
		for dirName, subdirList, fileList in os.walk(self.source):
			#print dirName
			for fname in fileList:
                                #Only append the right files
                                if self.prog.search(fname):
                                        filesize = os.stat(os.path.join(dirName,fname)).st_size
                                        if filesize > 30000:
                                                newList.append(os.path.join(dirName,fname))		
		return newList			

# Mainline for code execution
fc = FileCrawler(sourcefolder) 
filelist=fc.run() 

#Startup the exiftool
ec = exiftool.ExifTool()
ec.start()

#Scan the file list for metadata and copy the correct files.
for et in filelist:
    dataType = getFileExtension(et)
    if dataType > -1:
        metadata = ec.get_tag('DateTimeOriginal', et)
        if not(metadata):
                metadata = ec.get_tag('MediaCreateDate',et)
        if not(metadata):
                metadata = ec.get_tag('CreateDate',et)
        if not(metadata):
                metadata = ec.get_tag('FileModifyDate', et)
        do = MediaObject(dataType, et, metadata)
        do.copy()



#Remember to close the exiftool
ec.terminate()

#Print final information
print 'MediaCopy copied \n ' + str(MediaObject.mediaCounter) + ' files to media location. \n '+ str(MediaObject.existCounter) + ' files exist at location'

