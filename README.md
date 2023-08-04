## Copy data from REST endpoint to OCI Object Storage

# Introduction

A number of simple patterns are defined;
1. Query param for page and prop in headers for next page pattern (next page is in header)
2. Paginate through pages in numeric order
3. Next page link is in body

You will need to have permissions to create an OCI Function and also for the function to access resources like OCI Object Storage.
* allow any-user to use object-family in compartment <compartment-name> where ALL {request.principal.type = 'fnfunc'}

If you use this from another service like OCI Data Integration you will also need the workspace resource principal to have access to execute the function and use OCI Object Storage.

* allow any-user to use object-family in compartment <compartment-name> where ALL {request.principal.type = 'disworkspace', request.principal.id = '<workspace-ocid>'}
* allow any-user to manage function-family in compartment <compartment-name> where ALL {request.principal.type = 'disworkspace', request.principal.id = '<workspace-ocid>'}

# Description

Description of properties that are supported in the patterns.

Property | Description | Example
--- | --- | ---
url | URL to call GET on | https://api.punkapi.com/v2/beers
auth | Value can be RESOURCE_PRINCIPAL or omit. Use to call API with OCI resource principal | RESOURCE_PRINCIPAL
target_bucket | Bucket name to write results into. | mybucket
target_object | Object name to write results into. | myobject.json
pattern | Pattern 1 using response headers and request query param. 2 use query param page count. 3 use link in body | 1
query_param_page | query parameter name to add to URL | ?page= or &page= if first query parameter
query_param_page_limit | query parameter name to add to URL | &per_page=
start_page_no | Page number to start with, generally 1, may be 0 | 1
page_limit_cnt | Number of items per page to retrieve | 20
dataProperty | The property in the response body that has the data (array of results) | results
pagingLinkProperty | An array representing the property with the next page link. | ["paging","next","link"]
request_interval | Interval in seconds to delay requests | 0.5

# Examples

## Pattern 1 - Query param and next page in header

This is the pattern that OCI APIs use, the opc-next-page header property is in response and the page query parameter defines the page to read. To try this replace the compartment with the compartment you have access to, this will list the buckets in a compartment and result it stored in the desired bucket and object;

echo '{"auth":"RESOURCE_PRINCIPAL","url":"https://idhev4koz6gf.objectstorage.us-ashburn-1.oci.customer-oci.com/n/idhev4koz6gf/b/?compartmentId=ocid1.compartment.oc1..tbd&limit=2&fields=tags", "target_bucket":"a_cmd_bucket", "target_objectname":"allbuckets.json", "pattern":1, "query_param_page":"&page=", "header_prop_name":"opc-next-page"}' | fn invoke distools rest_to_os

## Pattern 2 - Page through response pages numerically

This should work ootb;

echo '{"url":"https://api.punkapi.com/v2/beers", "target_bucket":"a_cmd_bucket", "target_objectname":"allbeers.json", "pattern":2, "query_param_page":"?page=", "query_param_page_limit":"&per_page=", "start_page_no":1, "page_limit_cnt":20}' | fn invoke distools rest_to_os

IF you need to execute the API behind API Gateway, then you will need to authenticate against OCI, so you need to specify an additional property to identify you want to use RESOURCE_PRINCIPAL, like this;

echo '{"auth":"RESOURCE_PRINCIPAL", "url":"https://api.punkapi.com/v2/beers", "target_bucket":"a_cmd_bucket", "target_objectname":"allbeers.json", "pattern":2, "query_param_page":"?page=", "query_param_page_limit":"&per_page=", "start_page_no":1, "page_limit_cnt":20}' | fn invoke distools rest_to_os


## Pattern 3 - Link in body

This example gets the next page link from a property value where the property is identified in pagingLinkProperty which is an array representing nested properties so for property $.paging.next.link, specify ["paging","next","link"]. The data needs to be extracted, so a property name will identify which property has the data.

#echo '{"url":"https://api.tbd.com/v1/stuff", "target_bucket":"a_cmd_bucket", "target_objectname":"allstuff.json", "pattern":3, "dataProperty":"data", "pagingLinkProperty":["paging","next","link"]}' | fn invoke distools rest_to_os

Again IF you need to execute the API behind API Gateway, then you will need to authenticate against OCI, so you need to specify an additional property to identify you want to use RESOURCE_PRINCIPAL, like above using "auth":"RESOURCE_PRINCIPAL" in payload.


