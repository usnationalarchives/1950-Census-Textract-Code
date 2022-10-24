import sys,boto3,uuid

# Get the service resource
sqs = boto3.resource('sqs')

# Get the queue
queue = sqs.get_queue_by_name(QueueName='TextractQueue')

batch_size=10   #max number is 10
if len(sys.argv) == 2:
    listfile=sys.argv[1]    
    with open(listfile) as f:
        messages=[]        
        i=0
        for line in f:
            msg = line.strip()
            if msg:                
                i=i+1
                # Create a new message
                print(msg)                
                #messageGroupId is only needed for fifo SQS
                #messages.append({'MessageGroupId':'tiffimg', 'MessageBody':msg})
                #messages.append({'MessageGroupId':'tiffimg','Id':f'{uuid.uuid4()}-{i}', 'MessageBody':msg})
                #print(f"{uuid.uuid4()}-{i}")
                messages.append({'Id':f'{uuid.uuid4()}-{i}', 'MessageBody':msg})
                
                if len(messages) >= batch_size:                    
                    #print(messages)
                    response = queue.send_messages(Entries=messages)
                    messages=[]
        if messages:            
            response = queue.send_messages(Entries=messages)