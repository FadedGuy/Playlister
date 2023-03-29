import os, requests

def token(access_token):
    if not access_token:
        return None, ("missing credentials", 401)
    
    session = requests.Session()
    session.verify = False
    response = session.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/verify",
        headers={"Authorization": "Bearer " + access_token},
        verify=False, 
    )

    if response.status_code == 200:
        return response.text, None
    else:
        return None, (response.text, response.status_code)