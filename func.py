import io
import json
import oci
import requests
from fdk import response
from oci.signer import Signer
import concurrent
from concurrent.futures import ThreadPoolExecutor

# OCI paginated REST Example
def get_pages_opc_next_page(url, headers, auth):
    params={}
    first_page = requests.get(url, headers=headers, auth=auth, params=params)
    yield first_page.json()
    nxt=first_page.headers.get('opc-next-page')

    while nxt is not None:
        xurl=url+"&page="+nxt
        next_page = requests.get(xurl, headers=headers, auth=auth)
        nxt=next_page.headers.get('opc-next-page')
        yield next_page.json()

# Paginated REST Example with Page query parameter and Limit query parameter
def get_pages_by_page_no(url, headers, auth, page_prop, page_limit, start_page_no, page_limit_cnt):
    pageno = start_page_no
    per_page = page_limit_cnt
    xurl = url + page_prop + str(pageno) + page_limit + str(per_page)
    session = requests.Session()
    first_page = session.get(xurl, stream=True, headers=headers)
    #first_page = requests.get(xurl, headers=headers, auth=auth)
    yield first_page.json()

    while True:
        pageno = pageno + 1
        xurl = url + page_prop + str(pageno) + page_limit + str(per_page)
        #next_page = requests.get(xurl, auth=auth)
        next_page = session.get(xurl, stream=True, headers=headers)
        if len(next_page.json()) == 0: break
        yield next_page.json()

# Paginated REST Example with page link in body along with data
def get_pages_next_page_url(url, headers, auth, dataProperty, pagingLinkProperty):
    params={}
    session = requests.Session()
    #first_page = requests.get(url, headers=headers, auth=auth, params=params)
    first_page = session.get(url, stream=True, headers=headers)
    yield first_page.json()[dataProperty]
    nxtUrl=''
    if (len(pagingLinkProperty) == 3):
      nxtUrl = first_page.json()[pagingLinkProperty[0]][pagingLinkProperty[1]][pagingLinkProperty[2]]
    elif (len(pagingLinkProperty) == 2):
      nxtUrl = first_page.json()[pagingLinkProperty[0]][pagingLinkProperty[1]]
    else:
      nxtUrl = first_page.json()[pagingLinkProperty[0]]

    while nxtUrl is not None:
        #next_page = requests.get(nxtUrl, headers=headers, auth=auth)
        next_page = session.get(nxtUrl, stream=True, headers=headers)
        nxtUrl=next_page.headers.get('opc-next-page')
        if (len(pagingLinkProperty) == 3):
          nxtUrl = next_page.json()[pagingLinkProperty[0]][pagingLinkProperty[1]][pagingLinkProperty[2]]
        elif (len(pagingLinkProperty) == 2):
          nxtUrl = next_page.json()[pagingLinkProperty[0]][pagingLinkProperty[1]]
        else:
          nxtUrl = next_page.json()[pagingLinkProperty[0]]
        yield next_page.json()[dataProperty]

def task(data,object_storage_client, namespace,target_bucket,target_object,uploadid,upload_part_num):
   jsonStrings = [json.dumps(obj) for obj in data]
   jsonStrings = [el + "\n" for el in jsonStrings]
   jsonString = ''.join(jsonStrings)
   upload_part_body = jsonString.encode()
   resp = object_storage_client.upload_part(namespace, target_bucket, target_object, uploadid, upload_part_num, upload_part_body)
   return [resp,upload_part_num]

def upload_from_rest(ctx, signer, url, headers, target_bucket, target_object, restType, page_prop=None, page_limit=None, start_page_no=None, page_limit_cnt=None, dataProperty=None,pagingLinkProperty=None):
    object_storage_client = oci.object_storage.ObjectStorageClient(config={}, signer=signer)
    namespace = object_storage_client.get_namespace().data
    cmpd = oci.object_storage.models.CreateMultipartUploadDetails(object=target_object)
    resp = object_storage_client.create_multipart_upload(namespace, target_bucket, cmpd)
    parts=[]
    uploadid = resp.data.upload_id
    upload_part_num=0

    # create a pool
    executor = ThreadPoolExecutor(5)

    try:
      futures = []
      pages=[]
      if (restType == 1):
        pages = get_pages_opc_next_page(url, headers, signer)
      elif (restType == 2):
        pages = get_pages_by_page_no(url, headers, None, page_prop, page_limit, start_page_no, page_limit_cnt)
      elif (restType == 3):
        pages = get_pages_next_page_url(url, headers, None, dataProperty, pagingLinkProperty)
      for page in pages:
        # execute this via the pool
        upload_part_num=upload_part_num+1
        arr=[page,object_storage_client, namespace, target_bucket, target_object, uploadid, upload_part_num]
        fut=executor.submit(lambda p: task(*p), arr)
        futures.append(fut)

      for future in concurrent.futures.as_completed(futures):
        respnum = future.result()
        parts.append(oci.object_storage.models.CommitMultipartUploadPartDetails(etag=respnum[0].headers['etag'], part_num=respnum[1]))


      commit_multipart_upload_details = oci.object_storage.models.CommitMultipartUploadDetails(parts_to_commit=parts)
      object_storage_client.commit_multipart_upload(namespace, target_bucket, target_object, uploadid, commit_multipart_upload_details)
    except oci.exceptions.ServiceError as inst:
      return response.Response( ctx, response_data=inst, headers={"Content-Type": "application/json"})

def handler(ctx, data: io.BytesIO = None):
    signer = oci.auth.signers.get_resource_principals_signer()
    body = json.loads(data.getvalue())
    url = body.get("url")
    pattern = body.get("pattern")
    headers = body.get("headers")
    target_objectname = body.get("target_objectname")
    target_bucket = body.get("target_bucket")
    page_prop = body.get("page_prop")
    page_limit = body.get("page_limit")
    start_page_no = body.get("start_page_no")
    page_limit_cnt = body.get("page_limit_cnt")
    dataProperty = body.get("dataProperty")
    pagingLinkProperty = body.get("pagingLinkProperty")
    if (target_bucket == None or target_objectname == None or url == None):
      resp_data = {"status":"400", "info":"Required parameters have not been supplied - target_objectname, target_bucket, url need to be supplied"}
      return response.Response(
            ctx, response_data=resp_data, headers={"Content-Type": "application/json"}
      )

    try:
      upload_from_rest(ctx, signer, url, headers, target_bucket, target_objectname, pattern, page_prop, page_limit, start_page_no, page_limit_cnt, dataProperty,pagingLinkProperty)
      resp_data = {"status":"200"}
      return response.Response( ctx, response_data=resp_data, headers={"Content-Type": "application/json"})
    except oci.exceptions.ServiceError as inst:
      return response.Response( ctx, response_data=inst, headers={"Content-Type": "application/json"})


