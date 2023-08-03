## OCI Function to Copy REST data to OCI Object Storage

# Introduction

A number of simple patterns are defined;
1 OCI API next page pattern (next page is in header)
2 Next page info in body
3. Next page link is in body

You will need to have permissions to create an OCI Function and also for the function to access resources like OCI Object Storage.
allow any-user to use object-family in compartment <compartment-name> where ALL {request.principal.type = 'fnfunc'}

If you use this from another service like OCI Data Integration you will also need the workspace resource principal to have access to execute the function and use OCI Object Storage.

allow any-user to use object-family in compartment <compartment-name> where ALL {request.principal.type = 'disworkspace', request.principal.id = '<workspace-ocid>'}
allow any-user to manage function-family in compartment <compartment-name> where ALL {request.principal.type = 'disworkspace', request.principal.id = '<workspace-ocid>'}

# Pattern Examples

Pattern 1 - OCI API using opc next page

To try this repalce the compartment with the compartment you have access to, this will list the buckets in a compartment and result it stored in the desired bucket and object;

echo '{"url":"https://idhev4koz6gf.objectstorage.us-ashburn-1.oci.customer-oci.com/n/idhev4koz6gf/b/?compartmentId=ocid1.compartment.oc1..tbd&limit=2&fields=tags", "target_bucket":"a_cmd_bucket", "target_objectname":"allbuckets.json", "pattern":1}' | fn invoke distools rest_to_os

Pattern 2 - Next page info in body

This should work ootb;

echo '{"url":"https://api.punkapi.com/v2/beers", "target_bucket":"a_cmd_bucket", "target_objectname":"allbeers.json", "pattern":2, "page_prop":"?page=", "page_limit":"&per_page=", "start_page_no":1, "page_limit_cnt":20}' | fn invoke distools rest_to_os


Pattern 3 - Link in body

This example gets the next page link from a property value where the property is identified in pagingLinkProperty which is an array representing nested properties so for property $.paging.next.link, specify ["paging","next","link"]. The data needs to be extracted, so a property name will identify which property has the data.

#echo '{"url":"https://api.tbd.com/v1/stuff", "target_bucket":"a_cmd_bucket", "target_objectname":"allstuff.json", "pattern":3, "dataProperty":"data", "pagingLinkProperty":["paging","next","link"]}' | fn invoke distools rest_to_os
