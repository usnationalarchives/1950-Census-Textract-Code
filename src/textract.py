import sys
from time import sleep
import os,io,boto3,re
from botocore.config import Config
from botocore.exceptions import ClientError
from PIL import Image as Image, ImageDraw , ImageOps
import pandas as pd
from math import degrees,ceil
import numpy as np
from statistics import median
from fuzzywuzzy import fuzz
from random import randrange


src_bucket = os.getenv('BUCKET_SRC','1950census-desc')
dst_bucket = os.getenv('BUCKET_DST','nara-textract')
s3_prefix = os.getenv('DS3_PREFIX')
region = os.getenv('REGION','us-east-1')
debug = os.getenv('DEBUG')

s3_timeout=5
textract_timeout = 80
textract_connect_timeout=15
textract_max_attempts=1
textract_throttling_exception_retry=10
#textract_throttling_exception_sleep=20

s3_config = Config(
        connect_timeout=3, read_timeout=10,
        retries={'max_attempts': 2})

textract_config = Config(
        connect_timeout=textract_connect_timeout, read_timeout=textract_timeout,
        retries={
            'max_attempts': textract_max_attempts
            })
client = boto3.client('textract', region_name=region, config=textract_config)

#create textract client connection and handle ThrottlingException
'''
i=0    
while True:
    i+=1
    try:
        client = boto3.client('textract', region_name=region, config=textract_config)          
    except Exception as e:
        print(f'client error: {str(e)}')
        if i <= textract_throttling_exception_retry:            
            sleep(textract_throttling_exception_sleep)
            continue        
        raise

    break    
'''




def GetFullResponseFormatted_Text_CLI_PIL( documentName):
    response_text = GetTexract_CLI_PIL( documentName)

    xy_Text = GetBoxesFromResponse( response_text )
    xy_Text.sort_values(by=['Y1'], inplace=True)
    xy_Text = xy_Text.dropna().reset_index(drop=True)
    return xy_Text 


def GetTexract_CLI_PIL( image):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    
    #print(f'**** detect_document_text {randrange(4, textract_throttling_exception_sleep)}')
    #response = client.detect_document_text(Document={'Bytes':img_byte_arr})        

    
    c=0
    while True:
        c+=1
        try:
            print("Info: Running document text detection")            
            response = client.detect_document_text(Document={'Bytes':img_byte_arr})                
        except Exception as e:
            
            print(f"* Error code: {e.response['Error']['Code']}")
            if e.response['Error']['Code'] in ('Throttling','ThrottlingException','ThrottledException','RequestThrottledException','ProvisionedThroughputExceededException'):
                if c <= textract_throttling_exception_retry:   # retry 30 times 
                    #sleep_time=randrange(10, textract_throttling_exception_sleep)
                    sleep_time = ceil( 1 + 2 ** c / 2)
                    print(f"* Sleeping {sleep_time} seconds for retry {c}")
                    sleep(sleep_time) 
                    continue
                else:
                    print(f"*** Tried {textract_throttling_exception_retry} times and terminating the process.")
                    sys.exit(str(e)) # terminate the function after max retry and return unprocessed image to queue
            elif c <= 2:
                sleep(2)
                continue
            raise                          
            
        break
    return response

def GetBoxesFromResponse( response ):    
    xy_df = pd.DataFrame(columns = ['BlockType', 'Text']+['X1', 'Y1', 'X2', 'Y2', 'X3', 'Y3', 'X4', 'Y4'])
    for idx, block in enumerate(response['Blocks']):
        if 'Confidence' in block:
            xy_df.loc[idx, 'Confidence'] = block['Confidence']
        blockType = block['BlockType']
        xy_df.loc[idx, 'BlockType'] = blockType
    #     if blockType in ['LINE', 'WORD']:
        if blockType in ['LINE']:
            xy_df.loc[idx, 'Text'] = block['Text']
        xy_coords = block['Geometry']['Polygon']
        assert len(xy_coords) == 4
        for i, xy_coord in enumerate(xy_coords):
            xy_df.loc[idx, 'X{}'.format(i+1)] = xy_coord['X']
            xy_df.loc[idx, 'Y{}'.format(i+1)] = xy_coord['Y']
    xy_df = xy_df.dropna().reset_index(drop=True)
    return xy_df

def mavg(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w






def Slope(x1, y1, x2, y2):
    if x2 != x1:        
        m = (y2-y1)/(x2-x1)        
        return m
    return 0
def FindRotateDegree(xy_text):        
    line_length = indx = 0
    
    # fine the longest text line
    #for x in xy_text.Text:
    
    for index, row in xy_text.iterrows():
        size=len(row.Text)
        if size > line_length:
            indx = index
            line_length = size
    #print(f'***** {xy_text.iloc[indx]}')
    slope = Slope(xy_text.iloc[indx].X4,xy_text.iloc[indx].Y4,xy_text.iloc[indx].X3,xy_text.iloc[indx].Y3)      
    return degrees(slope)    

def FindTag(xy_text,regex,x1=None,y1=None,x2=None,y2=None):
                
    for index, row in xy_text.iterrows():
        #print(row.Text)           
        if re.search(regex,row.Text,re.IGNORECASE):            
            
            if y1 is not None and (row.Y1 < y1 or row.Y2 > y2):
                #print(f'no in range {y1} < {row.Y1} < {y2} : {row.Text}')
                continue
            if x1 is not None and (row.X1 < x1 or row.X2 > x2):
                #print(f'no in range {x1} < {row.X1} < {x2} : {row.Text}')
                continue            
            return row
    return None

def FindTagFuzzy(xy_text,search,x1=None,y1=None,x2=None,y2=None,ratio=85):
                
    for index, row in xy_text.iterrows():
        #print(f'* {row.Text}')
        if y1 is not None and (row.Y1 < y1 or row.Y2 > y2):
            #print(f'no in range {y1} < {row.Y1} < {y2} : {row.Text}')
            continue
        if x1 is not None and (row.X1 < x1 or row.X2 > x2):
            #print(f'no in range {x1} < {row.X1} < {x2} : {row.Text}')
            continue
        text = row.Text.lower()
        if isinstance(search,list):
            for sword in search:
                if fuzz.partial_ratio(text,sword.lower()) > ratio:                       
                    return row
        else:
            if fuzz.partial_ratio(text,search.lower()) > ratio:                            
                return row
    return None

def StringFilter(data):
    #data = re.sub(r'[\r\n]',' ',data)
    if re.search('(PRINTING|OFFICE)', data, re.IGNORECASE):
        return ''
    return data


def RecordColumnMappingByGap(xy_text,ed_indexs,description_indexs):     
    prev_y=0
    gaps={}    
    ed_list_size = len(ed_indexs)     
    des_list_size = len(description_indexs)
    data=[]
    
    #find avg text height
    height=0
    for index in description_indexs:
        height+=xy_text.loc[index].Y4 - xy_text.loc[index].Y1
    avg_text_height = height /  des_list_size

    
    for index in description_indexs:   
        if prev_y == 0:
            prev_y = xy_text.loc[index].Y4           
            continue        
        elif re.search('(printing|office)', xy_text.loc[index].Text, re.IGNORECASE):
            continue                
        gap = xy_text.loc[index].Y4 - prev_y    
        
        gaps.update({index:gap})        
        prev_y = xy_text.loc[index].Y4
        #find last possible gap possition and break if bigger
        if xy_text.loc[ed_indexs[-1]].Y4  <= xy_text.loc[index].Y4 + avg_text_height:    
            break
    #sort by whitle space between lines
    gaps=dict(sorted(gaps.items(), key=lambda item: item[1],reverse=True))

    keys = list(gaps.keys())    
    big_gaps = keys[:ed_list_size - 1]

    #debug code
    '''
    last_y=0
    print('***********************')
    for index in description_indexs:        
        gap = xy_text.loc[index].Y3 - last_y
        if index in big_gaps:
            print(f'gap {gap}')    
        print(f"{index} {xy_text.loc[index].Text}")
        last_y = xy_text.loc[index].Y4 
    '''
    # end debug code

    ed=desc=''
    ed_indx=0
    ed = ' ' + xy_text.loc[ed_indexs[ed_indx]].Text
    for index in description_indexs:
        if index in big_gaps:
            if ed or desc:
                data.append((ed,desc.strip()))
            ed_indx += 1
            ed = ' ' + xy_text.loc[ed_indexs[ed_indx]].Text
            desc = StringFilter(xy_text.loc[index].Text)            
        else:
            desc += ' ' + StringFilter(xy_text.loc[index].Text)            
    
    if ed or desc:
        data.append((ed,desc.strip()))   
    return data

def RecordColumMappingByStartLine(xy_text,ed_indexs,description_indexs):
    ed_indx=-1
    ed_list_size = len(ed_indexs)     
    des_list_size = len(description_indexs)
    i=1    
    data=[]
    desc= ed = ''
    
    for index in description_indexs:       
        if ed_indx + 1 < ed_list_size and xy_text.loc[ed_indexs[ed_indx + 1]].Y1 < (xy_text.loc[index].Y1 + 0.01):                            
                if ed or desc:
                    data.append((ed,desc.strip()))                    
                ed_indx = ed_indx + 1            
                ed = xy_text.loc[ed_indexs[ed_indx]].Text
                if ed:
                    ed = ' ' + ed                
                desc = StringFilter(xy_text.loc[index].Text)
        else:   
            desc += ' ' + StringFilter(xy_text.loc[index].Text)            
        i=i+1
    if ed or desc:
        data.append((ed,desc.strip()))

    return data

def ProcessDescription(xy_text,debug=None):
    ed_list=[]
    desc_list=[]

    
    #print('------')
    #for index, row in xy_text.iterrows():
    #    print(row.Text)
    
    ed_raw=None
    desc_raw=None
    found = FindTag(xy_text, '(1?950.*E.*D|50.*E\..*D)')
    
    if found is None:
        raise Exception('ED column not found')

    
    if found.any():
        height = found.Y4 - found.Y1
        ed_padding=height
        
        width = found.X2 - found.X1                
        ed_indexs = xy_text[ (xy_text.X1 >= found.X1 - ed_padding) & (xy_text.X2 <= found.X2 + ed_padding) & ( xy_text.Y1 > found.Y1)].index

        # find locale value
        
        c=2
        while True:
            locale_y= found.Y1 - height * 5.6
            locale_x2 = found.X2 + width * c

            #locale_indexs = list(xy_text[ (xy_text.X1 >= found.X1 - locale_padding) & (xy_text.X2 <= locale_x2 + locale_padding) & ( xy_text.Y1 < found.Y1) & ( xy_text.Y1 > locale_y)].index)
            locale_indexs = list(xy_text[ (xy_text.X2 >= found.X1) & (xy_text.X2 <= locale_x2) & ( xy_text.Y1 < found.Y1) & ( xy_text.Y1 > locale_y)].index)
            locale=[]
            for indx in reversed(locale_indexs):            
                txt = xy_text.loc[indx].Text.strip()    
                #print(f'* {txt}')        
                if re.search('(name|geog|code)',txt,re.IGNORECASE) or txt.isnumeric():
                    continue
                txt = re.sub('^([fs]?[tl]?a?t?e|c?o?u?n?t?y) ','',txt,flags=re.I)
                txt = re.sub('^s?t?ate ?','',txt,flags=re.I)
                locale.append(txt)
            c+=2
            if c > 4 or len(locale) >= 2:                
                break

        #remove possible bad items if more than 2 array items
        '''
        if len(locale) > 2:
            tmp_locale = locale
            locale=[]
            for x in reversed(tmp_locale):                
                if not re.match('(state|tate|ate|ounty)',x,re.IGNORECASE):
                    locale.append(x)
        '''
    
    #print(f"* {', '.join(locale)}")

    # clean up non ED values    
    tmp_list=[]
    for indx in ed_indexs:               
        if not re.search('[0-9a-fA-F]+-[0-9a-fA-F]',xy_text.loc[indx].Text):
            continue
        tmp_list.append(indx)    
    ed_indexs = tmp_list
    
    
    #description column padding to get column width
    desc_padding = 0.1    
    found = FindTag(xy_text, "(DESCRIPTION.*ENUMERATION DISTRICT|RIPTION.*ENUMERATION DISTRICT|DESCRIP.*)")
    if found is None:
        raise Exception('Description column not found')
    description_list=[]
    if found.any():
        description_indexs = xy_text[ (xy_text.X1 >= found.X1 - desc_padding) & (xy_text.X2 <= found.X2 + desc_padding) & ( xy_text.Y1 > found.Y1)].index
        
    
    
   
    data = RecordColumnMappingByGap(xy_text,ed_indexs,description_indexs)
    #data = RecordColumMappingByStartLine(xy_text,ed_indexs,description_indexs)
   
    schema = { 'ED': str, 'Description': str, 'Locale': str}
    processed_data = pd.DataFrame(columns=schema.keys()).astype(schema)   
    
    if data:        
        i=1
        for row in data:                   
            processed_data.loc[i] = row + (', '.join(locale), )
            i += 1            
    #for i,d in processed_data.iterrows():
    #    print(d.Description)
    return processed_data
    

def PreProcessSchedule(image, event=None):
    
    
    
    xy_text = GetFullResponseFormatted_Text_CLI_PIL( image )
    
    degree = FindRotateDegree(xy_text)
    if abs(degree) > 0.1 :          
        image = image.rotate(degree)        
        xy_text = GetFullResponseFormatted_Text_CLI_PIL( image )
    
    #print(xy_text)
    imageRa1 = np.asarray(image)
   
    #width = imageRa1.shape[0]
    #height = imageRa1.shape[1]
    #print(imageRa1.shape)
    height, width, z = imageRa1.shape

    
    #for index, row in xy_text.iterrows():
    #    print(row.Text)

    y2=height
    
    c1_x1_pct = 0
    c1_x1 = 1
    c1_x2_pct = 1/6
    c1_x2 = int(c1_x2_pct * width)
    c1_y1_pct=0
    y1=0
    char_width = 0
    char_height = 0

    #find y2 for columns
    tag = FindTag(xy_text, '(NEXT.*SHEET|HOUSEDHOLD.*CONTINUED|QUESTIONS.*BELOW|CODES.*USED.*INDICATED)',y1=1/2,y2=1)    
    if tag is None:
        tag = FindTagFuzzy(xy_text, ['HOUSEHOLD CONTINUED','QUESTIONS BELOW'],y1=1/2,y2=1)    
    if tag is not None:
        y2=int( (tag.Y4 - (tag.Y4 - tag.Y1)) * height )
    

    #for index, row in xy_text.iterrows():
    #    print(row.Text) 

    # find x2 for first column
    tag = FindTag(xy_text, '(FOR.*HEAD.*OF.*HOUSEHOLD)',x1=0, x2=1/4)
    if tag is None:        
        #tag = FindTagFuzzy(xy_text, ['LOCATION','RESIDENCE'],x1=0, x2=1/8)        
        tag = FindTagFuzzy(xy_text, ['FOR HEAD','HEAD OF HOUSEHOLD'],x1=0, x2=1/4)

    if tag is not None:
        char_width=(tag.X2 - tag.X1)/len(tag.Text)
        char_height=tag.Y4 - tag.Y1   
        c1_y1_pct = tag.Y4 + char_height * 5
        c1_x1_pct= tag.X1 - char_width * 6
        #c1_x2_pct= tag.X1 + char_width
        c1_x2_pct= tag.X4 - char_width * 2.5
        
        c1_x1 = int(c1_x1_pct * width)
        c1_x2 = int( c1_x2_pct * width)
    '''
    else:        
        # alter tag for AS        
        
        tag = FindTag(xy_text, 'Village',x1=0, x2=1/4)   
        if tag is None:        
            tag = FindTagFuzzy(xy_text, ['Village'],x1=0,x2=1/4)
        if tag is not None:
            char_width=(tag.X2 - tag.X1)/len(tag.Text)
            char_height=tag.Y4 - tag.Y1
            c1_x1_pct= tag.X4
            c1_x2_pct= tag.X4 + char_width * 3
            c1_x1 = int(c1_x1_pct * width)
            c1_x2 = int( c1_x2_pct * width)
            c1_y1_pct = tag.Y4
    '''
    if tag is not None:
        
        y1=int( (tag.Y4 + char_height * 16) * height )
        skip_text = xy_text[(xy_text.X1 >= c1_x1_pct) & (xy_text.X2 <= c1_x2_pct) & (xy_text.Y1 > tag.Y4) ]
        for index, row in skip_text.iterrows():        
            if row.Text.isnumeric():
                y1=int( (row.Y4 - char_height * 3) * height )
                break
    
    
    
    
    
    # find x1 for name column
    tag = FindTag(xy_text, '(FOR.*HEAD.*OF.*HOUSEHOLD)',x1=0,x2=1/4)
    if tag is None:        
        tag = FindTagFuzzy(xy_text, ['FOR HEAD OF HOUEHOLD','HEAD OF HOUSEHOLD'],x1=0, x2=1/4)
    if tag is not None:
        #c2_x1_pct = tag.X3 + char_width
        c2_x1_pct = tag.X3
    else: #alter for AS
        c2_x1_pct = c1_x1_pct + char_width * 5
    c2_x1=int( c2_x1_pct * width)

    # finx x2 for name column    
    tag2 = FindTag(xy_text, 'RELATIONSHIP',x1=0,x2=1/2)
    if tag2 is not None:
        c2_x2_pct = tag2.X4 - char_width * 1
    else:
        tag2 = FindTag(xy_text, 'FOR.*ALL.*PERSONS',x1=0,x2=1/2)
        if tag2 is not None:
            c2_x2_pct = tag2.X4 - char_width * 3    
    #if tag2 is None:        
    #    tag2 = FindTagFuzzy(xy_text, ['RELATIONSHIP'],x1=0,x2=1/2)    

    # can't find any tags
    if tag is None and tag2 is None:
        raise Exception("Can't find any required tags in the image")

    #print(tag2)    
    c2_x2 = int( c2_x2_pct * width)
    
    if tag is None:        
        name_y1 = c1_y1_pct
    else:
        name_y1 = tag.Y1
    tag = FindTag(xy_text, 'NAME',y1=name_y1, y2=1/3, x1=c2_x1_pct, x2=c2_x2_pct)
    if tag is None:        
        tag = FindTagFuzzy(xy_text, ['NAME'],y1=name_y1, y2=1/3, x1=c2_x1_pct, x2=c2_x2_pct)

    name_x1 = tag.X4
    name_x2 = tag.X3
    skip_text = xy_text[(xy_text.X1 >= name_x1) & (xy_text.X2 <=name_x2) & (xy_text.Y1 >= tag2.Y4) & (xy_text.Y1 <= y2) ]
    for index, row in skip_text.iterrows():
        
        if re.search(r'^[0-7]$',row.Text.strip()): 
            y1 = int( (row.Y4 + char_height / 3 ) * height)
            break   

    

    I1 = imageRa1[y1:y2, c1_x1:c1_x2]
    I2 = imageRa1[y1:y2, c2_x1:c2_x2]        
    I3 = np.concatenate( (I1,I2) , axis =1)

    return Image.fromarray(I3)

def ProcessSchedule(xy_text):       
    
    #for index, row in xy_text.iterrows():
    #    print(row.Text)

    col1_x2_pct = 1/7
    schedule_col1_indexs = xy_text[(xy_text.X2 < col1_x2_pct ) ].index    
    col1_list=[]
    col1_values={}
    #for index in description_indexs:       
    #if ed_indx + 1 < ed_list_size and xy_text.loc[ed_indexs[ed_indx + 1]].Y1 < (xy_text.loc[index].Y1 + 0.01):                            
    
    for index in  schedule_col1_indexs:                               
        col1_list.append(xy_text.loc[index].X2)    
        #print(f'row number: {xy_text.loc[index].Text}')
    if col1_list:
        col1_x2 = median(col1_list)            
    else:
        col1_x2 = col1_x2_pct
      
    schedule_col2 = xy_text[(xy_text.X1 > col1_x2 ) ]

    schema = { 'Row Number': str, 'Name': str}
    processed_data = pd.DataFrame(columns=schema.keys()).astype(schema) 
    df_row=1
    col1_index=-1
    has_data = False
    for index,row in  schedule_col2.iterrows():   
        
        h=row.Y4 - row.Y1                    
        while col1_index < len(schedule_col1_indexs) - 1 and xy_text.loc[schedule_col1_indexs[col1_index+1]].Y3  < row.Y4:
            col1_index +=1
        name_str = re.sub(r'^[-\s0-9].*','',row.Text)
        name_str = re.sub(r'[@\/0-9,\'")(\*&#!+=]','',name_str)
        name_str = re.sub(r'^[@\/0-9,\s]*','',name_str)
        if len(name_str) > 2:
            if col1_list:
                row_number = re.sub(r'[^0-9]','',xy_text.loc[schedule_col1_indexs[col1_index]].Text)            
            else:
                row_number = ''
            processed_data.loc[df_row] = [row_number,name_str]
            has_data = True
            df_row += 1
    
    
    #print(processed_data)
    if has_data:
        return processed_data
    else:
        return None
    

################# misc functions #####################################
def human_size(bytes, units=[' bytes','KB','MB','GB','TB', 'PB', 'EB']):
    """ Returns a human readable string representation of bytes """
    #return str(bytes) + units[0] if bytes < 1024 else human_size(bytes>>10, units[1:])
    return "{:.2f}{}".format(float(bytes), units[0]) if bytes < 1024 else human_size(bytes / 1024, units[1:]) 

def read_image_from_s3(bucket, key):    
    s3 = boto3.resource('s3',config=s3_config)    
    object = s3.Object(bucket,key)  
    size = human_size(object.content_length)
    return (Image.open(object.get()['Body']),size)
    

def read_image_file(file):      
    image_file = Image.open(file)
    return image_file,len(image_file.fp.read())    
    

def write_image_to_s3(img, bucket, key):    
    s3 = boto3.resource('s3',config=s3_config)
    bucket = s3.Bucket(bucket)
    object = bucket.Object(key)
    file_stream = io.BytesIO()
    #im = Image.fromarray(img_array)
    im.save(file_stream, format='jpeg')
    object.put(Body=file_stream.getvalue())

def write_csv_s3(df, bucket, key):        
    #print(df)
    s3 = boto3.resource('s3',config=s3_config)
    bucket = s3.Bucket(bucket)
    object = bucket.Object(key)    
    object.put(Body=df.to_csv(index = False ))

def write_text_s3(data, bucket, key):    
    try:
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucket)
        object = bucket.Object(key)    
        object.put(Body=data)
    except Exception as e:
        print(f"Error: on writing text to {bucket} {key}{str(e)}")

def delete_error_file_s3(bucket, key):    
    s3 = boto3.resource('s3',config=s3_config)
    try:        
        s3.Object(bucket,key+'.error').delete()
    except Exception as e:
        print(f'Error: {str(e)}')
