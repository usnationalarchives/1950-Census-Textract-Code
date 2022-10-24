import json,sys,os
from optparse import OptionParser


currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

batchsize=10

from handler import textract
records=[]
event={
   "Records":records
}

parser = OptionParser()
parser.add_option("-f", "--file", action="store_true", dest="file", help="process local file")
parser.add_option("-s", "--s3", action="store_true", dest="s3", help="process s3 file")
parser.add_option("-d", "--debug", action="store_true", dest="debug", help="debug")
(options, args) = parser.parse_args()


context=None
local = True
debug = False
if options.debug:
   debug = True


if options.file and len(args) == 1 and args[0]:   
   event.update({'local':local,'debug':debug,'file':'localfile'})
   records.append( {"body":args[0]})   
   textract(event,context)

elif options.s3 and len(args) == 1 and args[0]:
   event.update({'local':local,'debug':debug})
   records.append( {"body":args[0]})
   textract(event,context)
elif len(args) == 1 and args[0]:
   filename = args[0]
   c=0
   for line in open(filename):  
      event.update({'local':local,'debug':debug})    
      records.append( {"body":line.strip(),'local':local,'debug':debug})   
      if c != 0 and c % batchsize == 0:
         #print(event)
         textract(event,context)
         records=[]
         event={            
            "Records":records
         }
      c = c + 1
   if len(records) > 0:
      textract(event,context)

else:
   event.update({'local':local,'debug':debug})
   records.append( {"body":"census/census-1940/T627/AK/m-t0627-04581/m-t0627-04581-00913.jpg"})
   records.append( {"body":"census/census-1940/T627/AK/m-t0627-04581/m-t0627-04581-00914.jpg"})
   textract(event,context)


