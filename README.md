# PyMocker

PyMocker can build several mock server by proxy, and every mock server can customize the response of rest api.

PyMocker includes a management rest server and several rest mock server processes which have its own rest api.

The API spec can follow the postman json file py-mock.postman_collection.json



Examples:

1. Create a new mock server:

curl --location --request POST 'localhost:5000/mock_servers' \
--header 'Content-Type: application/json' \
--data-raw '{
    "mock_server_id": "001",
    "mock_url": "https://www.httpbin.org",
    "mock_rules": [
        {
            "method": "PUT",
            "path": ".*put.*",
            "response_status": 201,
            "response_data": {
                "error": "Rewrite put response!!!"
            },
            "response_headers": {
                "HHH": "Mock header"
            }
        },
        {
            "method": "POST",
            "path": ".*/post.*",
            "response_status": 201,
            "response_data": {
                "info": "hit post!!"
            }
        },
        {
            "method": "GET",
            "path": ".*/script.*",
            "response_status": 201,
            "response_data": {
                "info": "hit script!!"
            },
            "python_script": "response.headers['\''new'\'']='\''python script'\''; response.data['\''new'\'']='\''python script'\''"
        }
    ]
}'


2. List all mock servers

curl --location --request GET 'localhost:5000/mock_servers'


3. Update mock rules for one mock server:

curl --location --request PUT 'localhost:5000/mock_servers/001' \
--header 'Content-Type: application/json' \
--data-raw '{
    "mock_rules": [
        {
            "method": "PUT",
            "path": ".*put.*",
            "response_status": 202,
            "response_data": {
                "error": "Updated put response!!!"
            },
            "response_headers": {
                "HHH": "Mock header updated"
            }
        }
    ]
}'
