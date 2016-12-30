# import the necessary packages
import exiftool
from imutils import paths
import argparse
import cv2
import json
def variance_of_laplacian(image):
	# compute the Laplacian of the image and then return the focus
	# measure, which is simply the variance of the Laplacian
	return cv2.Laplacian(image, cv2.CV_64F).var()
 
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--images", required=True,
	help="path to input directory of images")
ap.add_argument("-t", "--threshold", type=float, default=100.0,
	help="focus measures that fall below this value will be considered 'blurry'")
args = vars(ap.parse_args())

ec = exiftool.ExifTool()
ec.start()

f = open('workfile','w')

class MetaData:
	def __init__(self, filesrc):
		self.filesrc = filesrc

	def setData(self,focal35, shutterspeed, flash, fnumber, iso, varlaplace):
		self.iso = iso
		self.invshutterspeed=1/shutterspeed
		self.flash=flash
		self.focal35 = focal35
		self.fnumber=fnumber
		self.varlaplace = varlaplace


	def setLabel(self, label):
		print "Labelled as : " + label
		self.label = label


DataList = []

# loop over the input images
for imagePath in paths.list_images(args["images"]):
	# load the image, convert it to grayscale, and compute the
	# focus measure of the image using the Variance of Laplacian
	# method
    

	metadata = ec.get_metadata(imagePath)

	
	iso = metadata['EXIF:ISO']
	focal35  = metadata['Composite:FocalLength35efl']
	sourceFile = metadata['SourceFile']
	shutterspeed = metadata['Composite:ShutterSpeed']
	fnumber = metadata['EXIF:FNumber']	
	#print metadata
	try:
		flash = metadata['MakerNotes:FlashBias']
	except KeyError:
		flash = metadata['EXIF:Flash']




	image = cv2.imread(imagePath)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	fm = variance_of_laplacian(gray)


	text = "Not Blurry"

	# if the focus measure is less than the supplied threshold,
	# then the image should be considered "blurry"
	if fm < args["threshold"]:
		text = "Blurry"
 
	# show the image
	cv2.putText(image, "{} FACTOR={:.2f}, ISO={:d}, Focal35mmEquivalent={:1.2f}, 1/ShutterSpeed={:1.2f}, FNumber={:1.2f}, Flash={:1.2f}".format(text, fm, iso, focal35,1/shutterspeed,fnumber, flash), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 0, 255), 3)

	cv2.namedWindow(sourceFile,cv2.WINDOW_NORMAL)
	cv2.resizeWindow(sourceFile,1200,800)
	cv2.imshow(sourceFile, image)
	
	key = cv2.waitKey(0)
	
	print key
	label = 'S'
	if key==98:
		label='B'


	DataList.append(['ImagePath:'+imagePath, 'Focal35mm:'+str(focal35), 'InvShutterSpeed:'+str(1/shutterspeed), 'Flash:'+str(flash), 'FNumber:'+str(fnumber), 'ISO:'+str(iso), 'FM:'+str(fm), 'Class:'+label])

	if key==27:
		break
	cv2.destroyAllWindows()

json.dump(DataList,f)

cv2.destroyAllWindows()
ec.terminate()