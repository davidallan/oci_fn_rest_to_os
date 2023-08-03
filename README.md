# oci_fn_rest_to_os

Examples

Pattern 1 - OCI API using opc next page

echo '{"url":"https://identity.us-ashburn-1.oraclecloud.com/20160918/policies/?compartmentId=ocid1.tenancy.oc1..tbd&limit=25&sortBy=timeCreated&sortOrder=DESC", "target_bucket":"a_cmd_bucket", "target_objectname":"allpolicies.json", "pattern":1}' | fn invoke distools rest_to_os

echo '{"url":"https://idhev4koz6gf.objectstorage.us-ashburn-1.oci.customer-oci.com/n/idhev4koz6gf/b/?compartmentId=ocid1.compartment.oc1..tbd&limit=2&fields=tags", "target_bucket":"a_cmd_bucket", "target_objectname":"allbuckets.json", "pattern":1}' | fn invoke distools rest_to_os

Pattern 2 - Link in body
echo '{"url":"https://api.punkapi.com/v2/beers", "target_bucket":"a_cmd_bucket", "target_objectname":"allbeers.json", "pattern":2, "page_prop":"?page=", "page_limit":"&per_page=", "start_page_no":1, "page_limit_cnt":20}' | fn invoke distools rest_to_os

