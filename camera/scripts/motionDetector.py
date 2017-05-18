# -*- coding: utf-8 -*-
import sys
import urllib2
import os
import tempfile
from datetime import datetime


class MotionDetector:
    def __init__(self):
        self.facesUrl = "https://gateway-a.watsonplatform.net/visual-recognition/api/v3/detect_faces?api_key=f6d03dcf2888d305b31804fdfcd6d9f9ce6697ad&version=2016-05-20"
        self.classifyUrl = "https://gateway-a.watsonplatform.net/visual-recognition/api/v3/classify?api_key=f6d03dcf2888d305b31804fdfcd6d9f9ce6697ad&version=2016-05-20"

    def sendImage(self, url, imagePath):
        image = open(imagePath, "rb").read()
        req = urllib2.Request(url, image)
        req.add_header('Content-Length', '%d' % len(image))
        req.add_header('Content-Type', 'application/octet-stream')
        res = urllib2.urlopen(req)
        return res.read()

    def writeWatsonResponse(self, watsonResponse, outputPath):
        fd, path = tempfile.mkstemp()
        os.write(fd, watsonResponse)
        now = datetime.now()
        name = '%s-%s-%s::%s:%s:%s.%s.txt'%(now.year,now.month,now.day,now.hour,now.minute,now.second,now.microsecond)
        os.system("scp " + path + " " + outputPath + "/" + name)
        os.remove(path)

    def analyse(self, imagePath, outputPath, isClassify):
        url = self.classifyUrl if isClassify else self.facesUrl
        watsonResponse = self.sendImage(url, imagePath)
        self.writeWatsonResponse(watsonResponse, outputPath)


if __name__ == "__main__":
    if len(sys.argv) < 4 or (sys.argv[3] != "detect_faces" and sys.argv[3] != "classify") :
        print "Error: no image input"
        print "syntax: python motionDetector.py path/to/image/input.jpg <account>@<ip-adress>:path/to/analyse/dir/ (detect_faces|classify)"

    md = MotionDetector()
    md.analyse(sys.argv[1], sys.argv[2], sys.argv[3] == "classify")

