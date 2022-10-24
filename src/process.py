import os,boto3,re
from PIL import Image
from io import BytesIO
from pathlib import Path
import datetime
import time

from src.textract import *

def process(items,event):
    debug = event.get('debug')
    b=0

    startTime = time.time()
    total = len(items)
    for key in items:  
        imageStartTime = time.time()
        b += 1
        if event and event.get('file'):
            print(f"\n* Processing  (batch {b}/{total}): local file {key}")   
            localfile=key                             
            key=re.sub(r'^/','',key)
        else: 
            print(f"\n* Processing (batch {b}/{total}): s3://{src_bucket}/{key}")        

        dirname=os.path.dirname(key)
        filename=os.path.basename(key)
        fname=os.path.splitext(filename)[0]

        if s3_prefix:
            prefix = f"{s3_prefix}/{dirname}/{fname}"            
        else:
            prefix=f"{dirname}/{fname}"

        if debug:
            prefix=f'debug/{prefix}'

        dkey = f"{prefix}.csv"        
        ekey=f"{prefix}.txt"
        path = os.path.dirname(dkey)

        
        
        
        try:
            status='loading'                       
            if event and event.get('file'):                  
                image,size = read_image_file(localfile)
                print(f"Loaded {key} ({size})")     
                
            else:
                image,size = read_image_from_s3(src_bucket,key)        
                print(f"Loaded s3://{src_bucket}/{key} ({size})")     

            if debug:                    
                os.makedirs(path,exist_ok=True)
                if not event.get('file') and debug and not os.path.exists(f"{prefix}.jpg"):
                    os.makedirs(path,exist_ok=True)
                    print(f"Save image to {prefix}.jpg")                
                    image.save(f"{prefix}.jpg", format="JPEG")                  
            status='preprocess'
            image = PreProcessSchedule(image,event)    

            if debug:
                print(f"Save stage image to {prefix}.jpg")                
                image.save(f"{prefix}-stage.jpg", format="JPEG")

            xy_text = GetFullResponseFormatted_Text_CLI_PIL( image )
                                    
            status='process'   
            data = ProcessSchedule(xy_text)            

            if data is not None:
                if debug:
                    print(f"Save result to{dkey}")                
                    data.to_csv(dkey,index = False )
                status='save result'
                print(f'Save CSV result to s3://{dst_bucket}/{dkey}')
                write_csv_s3(data, dst_bucket, dkey)            

        except Exception as e:                
            if debug:                                                                
                raise
            else:
                print(f'Error: {str(e)}')
                if status != 'loading':
                    write_text_s3(f'Error: {str(e)}',dst_bucket,ekey)
        finally:
            # don't need image data anymore and delete it
            if image:
                image.close()
                image=None
            executionTime = round(time.time() - imageStartTime,2)
            
            if status == 'loading':
                print(f'* Skipped {key} processing')
            else:
                print(f'* Completed {key} processing')
            print(f'Processed the image in {executionTime} seconds')

    executionTime = (time.time() - startTime)
    print(f"{total} image(s) in the batch completed {round(executionTime,2)} seconds ({round(executionTime/total,2)} seconds per image)")
    print(f'End process')
            