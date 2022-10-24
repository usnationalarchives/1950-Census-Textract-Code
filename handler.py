import json
import os
from src.process import *

def textract(event, context):
    items=[]
    try:
        
        records = event.get('Records')
        for item in records:        
            items.append(item['body'])        
        process(items,event)

    except Exception as e:                
        if event.get('debug'):                                                                
            raise
    