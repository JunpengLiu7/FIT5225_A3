import json
import base64
import boto3
import os
import numpy as np
import cv2
import uuid

#from os import listdir

#{"user_name":"ID_token","image_file": "base 64","image_name":"name.jpg" }
print('test')
FOLDER = "images/"
FOLDER_RESIZE = "images_resized/"
s3 = boto3.client('s3')
BUCKET="5225-a3-images-demo"
WIDTH = 3
def lambda_handler(event, context):
    
    #print(listdir("/opt/python/lib/python3.9/site-packages/"))
    #print(cv2.__version__)

    # get the data
    data = json.loads(event['body'])
    username = data['user_name']
    image_name = data['image_name']
    image_file = data['image_file']
    
    print(username)
    print('lalal')
    
    # set the key
    # unused name
    _, suffix = os.path.splitext(image_name)
    id = uuid.uuid1()
    
    # image name
    img_name = FOLDER + username + "/" + str(id.hex) + suffix
    
    # read the image
    decod_image = base64.b64decode(image_file)
    
    # resize the image .shape->(height, width) to thumbnail
    image_arrary = np.asarray(bytearray(decod_image), np.uint8)
    upload_image = cv2.imdecode(image_arrary, cv2.IMREAD_COLOR)

    height = int(upload_image.shape[0] * (WIDTH / upload_image.shape[1]))
    resize_image = cv2.resize(upload_image, (WIDTH, height), interpolation=cv2.INTER_AREA)
    
    # get the idea from https://stackoverflow.com/questions/17967320/python-opencv-convert-image-to-byte-string
    resize_image_bytes = cv2.imencode(suffix, resize_image)[1].tobytes()
    
    # resized image name
    img_name_resized = FOLDER_RESIZE + username + "/" + str(id.hex) + suffix
    
    # save image in s3
    s3.put_object(Bucket=BUCKET, Key=img_name, Body=decod_image, ContentType='mimetype', ContentDisposition='inline')
    s3.put_object(Bucket=BUCKET, Key=img_name_resized, Body=resize_image_bytes, ContentType='mimetype', ContentDisposition='inline')
    
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda! image uoloaded'),
        'headers': {
            'Access-Control_Allow_Origin': '*',
            'Access-Control_Allow_Methods': '*',
            'Access-Control_Allow_Headers': '*'
        }
    }
