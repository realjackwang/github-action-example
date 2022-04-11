# -*- coding: utf-8 -*-

import json
from PIL import Image
import sys
import os
import requests
from obs import *
current_file_path = os.path.dirname(os.path.realpath(__file__))
# append current path to search paths, so that we can import some third party libraries.
sys.path.append(current_file_path)

TEMP_ROOT_PATH = "/tmp/"
secure = True
signature = 'v4'
port = 443
path_style = True

def newObsClient(context, obs_server):
    ak = context.getAccessKey()
    sk = context.getSecretKey()
    return ObsClient(access_key_id=ak, secret_access_key=sk, server=obs_server,
                     path_style=True, ssl_verify=False, max_retry_count=5, timeout=20)

def downloadFile(obsClient, bucket, objName, localFile):
    resp = obsClient.getObject(bucket, objName, localFile)
    if resp.status < 300:
        print('download file ', objName, 'succeed')
    else:
        print('download failed, errorCode: %s, errorMessage: %s, requestId: %s' %(resp.errorCode, resp.errorMessage,
              resp.requestId))

def getObjInfoFromObsEvent(event):
    if 's3' in event['Records'][0]:
        s3 = event['Records'][0]['s3']
        eventName = event['Records'][0]['eventName']
        bucket = s3['bucket']['name']
        objName = s3['object']['key']
    else:
        obsInfo = event['Records'][0]['obs']
        eventName = event['Records'][0]['eventName']
        bucket = obsInfo['bucket']['name']
        objName = obsInfo['object']['key']
    print("*** obsEventName: %s, srcBucketName: %s, objName: %s" %(eventName, bucket, objName))
    return bucket, objName

def PostObject(obsAddr, bucket, objName, ak, sk):
    TestObs = ObsClient(access_key_id=ak, secret_access_key=sk,
                        is_secure=secure, server=obsAddr, signature=signature, path_style=path_style,ssl_verify=False, port=port,
                        max_retry_count=5, timeout=20)


    Lheaders = PutObjectHeader(md5=None, acl='private', location=None, contentType='text/plain')

    Lheaders.sseHeader = SseKmsHeader.getInstance()
    h = PutObjectHeader()
    Lmetadata = {'key': 'value'}

    objPath = TEMP_ROOT_PATH + objName
    resp = TestObs.postObject(bucketName=bucket, objectKey=objName, file_path=objPath,
                              metadata=Lmetadata, headers=h)
    if isinstance(resp, list):
        for k, v in resp:
            print('PostObject, objectKey',k, 'common msg:status:', v.status, ',errorCode:', v.errorCode, ',errorMessage:', v.errorMessage)
    else:
        print('PostObject, common msg: status:', resp.status, ',errorCode:', resp.errorCode, ',errorMessage:', resp.errorMessage)


def handler(event, context):
    srcBucket, srcObjName = getObjInfoFromObsEvent(event)
    obs_address = context.getUserData('obs_address')
    pluginId = context.getUserData('plugin_id')
    pluginToken = context.getUserData('plugin_token')
    if obs_address is None:
        obs_address = '100.125.15.200'

    print("*** srcBucketName: " + srcBucket)
    print("*** srcObjName:" + srcObjName)
    print("*** obs_address: " + obs_address)
    
    print("------------------------------------ update by function local file -------------------------------------")
    client = newObsClient(context, obs_address)
    # download file uploaded by user from obs
    localFile = TEMP_ROOT_PATH + srcObjName
    downloadFile(client, srcBucket, srcObjName, localFile)
    print("*** localFile: " + localFile)
 
    url = 'https://plugins.jetbrains.com/plugin/uploadPlugin'
    data = {'pluginId': pluginId}
    headers = {'Authorization': 'Bearer '+pluginToken,}
    files = {
        "file": (srcObjName, open(localFile, "rb"))
    }
    response = requests.post(url=url, files=files, data=data,headers=headers)
    print(response)
    return 'OK'


