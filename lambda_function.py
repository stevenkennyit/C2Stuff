import requests
import base64
import json
requests.packages.urllib3.disable_warnings() 

def lambda_handler(event, context):

    # Setup forwarding URL
    cs = "<REPLACE_WITH_TS_PRIVATE_IP>"   #CS
    red = "google.com"   #redirect unwanted traffic 
    
    #Debug
    print("Calling path:", event["path"])
    
    #CS short redirect#######################################
    #profiles/amz_evts_mod.profile
    if "js" in event["path"]:
        url = "https://" + cs + event["path"]
        print("Short:", url)
        print("HEADERS:", event["headers"])
        if "api" in event["headers"] or "stg" in event["headers"] :
            print('Proceed')
            if "body" in event.keys():
                if event["isBase64Encoded"]:
                    body = base64.b64decode(event["body"])
                else:
                    body = event["body"]
                    
                try:
                    queryStrings = {}
                    if "queryStringParameters" in event.keys():
                        for key, value in event["queryStringParameters"].items():
                            queryStrings[key] = value
                except:
                    pass
                
                if event["httpMethod"] == "GET":
                    resp = requests.get(url, params=queryStrings, verify=False, headers=event["headers"])
                elif event["httpMethod"] == "POST":
                    resp = requests.post(url, data=body.encode('utf-8'), params=queryStrings, verify=False, headers=event["headers"])
            
                outboundHeaders = {}
                
                for head, val in resp.headers.items():
                    if head.lower() != 'content-encoding':
                        outboundHeaders[head] = val
                        
                outboundHeaders['Content-Encoding'] = 'application/octet-stream'
                
                response = {
                    "headers": outboundHeaders,
                    "statusCode": resp.status_code,
                    "body":  base64.b64encode(resp.content).decode('utf-8'),
                    "isBase64Encoded": True
                }
        else:
            print('HEADER not matched! - Doing HTTP redirect')
            response = {
            "statusCode": 302,
            "headers": {
                "Location": "https://" + red
            },
            "body": json.dumps({
                "message": "Redirecting to " + "https://" + red
            })
        }
    
    #redirect#######################################
    else:
        # Perform 302 redirect 
        print("URI not matched! - Doing HTTP redirect")
        print(event["path"])
        response = {
            "statusCode": 302,
            "headers": {
                "Location": "https://" + red
            },
            "body": json.dumps({
                "message": "Redirecting to " + "https://" + red
            })
        }
    
    
    return response
