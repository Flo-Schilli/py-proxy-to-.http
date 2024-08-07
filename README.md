# py-proxy-to-.http

This project is for easily creating .http files from requests done by an application.

It can be used as a proxy for requests between frontend and backend. 
It will create .http files which can later be used for e2e tests.

It also creates a http-proxy.env.json which can be used in IntelliJ - IDEs

Additionally, it not only creates the http files for the requests, but also logs the responses in a separate file, 
so that it can be used for different assertations.

## Usage
To run the proxy you have to run the following command.
Flask then listens on all available interfaces on port 8080

```
flask run -h 0.0.0.0 -p 8080
```

To trigger the start of a logging you have to call the endpoint `http://{HOST}:{PORT}/config/start`
with a POST request. The application then stores all requests for the querying IP.
You have to provide the following body: 
```json
{
  "base_url": "{{BACKEND_URL}}",
  "ip": "OPTIONAL IP THE REQUEST COMES FROM"
}
```

To stop the logging you have to call the endpoint `http://{HOST}:{PORT}/config/stop` with stopping, you'll get a zip 
file back with the recorded data.

The endpoint for proxying all the data is: `http://{HOST}:{PORT}/proxy` everything following will be forwarded to the
endpoint you configured during calling `http://{HOST}:{PORT}/config/start`.


## Output

Output will be a file in the following schema
```http request
GET https://{{BACKEND_URL}}/applications/configuration

###
```
