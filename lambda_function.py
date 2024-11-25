import requests
import base64
import json
requests.packages.urllib3.disable_warnings()

def lambda_handler(event, context):
    # Setup forwarding URL
    cs = "<REPLACE_WITH_TS_PRIVATE_IP>"  # CS
    red = "google.com"  # redirect unwanted traffic

    # Debug
    print("Calling path:", event["path"])

    response = None  # Ensure response is always defined
    
    # CS short redirect #######################################
    if "js" in event["path"]:
        url = "https://" + cs + event["path"]
        print("Short:", url)
        print("HEADERS:", event["headers"])
        if "api" in event["headers"] or "stg" in event["headers"]:
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
                except Exception as e:
                    print("Error parsing query strings:", e)
                    queryStrings = {}

                # Initialize resp as None to handle unexpected methods
                resp = None
                try:
                    if event["httpMethod"] == "GET":
                        resp = requests.get(url, params=queryStrings, verify=False, headers=event["headers"])
                    elif event["httpMethod"] == "POST":
                        resp = requests.post(url, data=body.encode('utf-8'), params=queryStrings, verify=False, headers=event["headers"])

                    if resp:
                        outboundHeaders = {}
                        for head, val in resp.headers.items():
                            if head.lower() != 'content-encoding':
                                outboundHeaders[head] = val
                        outboundHeaders['Content-Encoding'] = 'application/octet-stream'

                        response = {
                            "headers": outboundHeaders,
                            "statusCode": resp.status_code,
                            "body": base64.b64encode(resp.content).decode('utf-8'),
                            "isBase64Encoded": True
                        }
                except Exception as e:
                    print("Error during request:", e)
            else:
                print('No body provided for POST/GET')
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

    # Ensure response is not None to avoid runtime errors
    if response is None:
        response = {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal Server Error"})
        }

    return response
