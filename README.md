# API Reference
## Get Stated
Base Url - At present, this application runs locally and is not hosted at a base URL. The backend app is hosted at the default htttp://127.0.0.1:5000/, which is set as proxy for the frontend configuration.

Authentication: This version of this application doesn't require documentation

##Error Handling
Error are returned as JSON objects in the following formats:

```
{
  'success': False
  'error': 400,
  'message'; 'bad request'
}

```
The API could return following error:
- 400: Bad Request
- 404: Resource not found
- 422: Unprocessable

## Endpoints
### Get /books
- General:
Returns a list of book objects, success values, and total number of books.
The results are paginated in groups of 4. Include a request argument to choose page number, starting from 1.

Sample: 'curl http://127.0.0.1:5000/books'

'''
"books":[{

  }
  ]
'''
