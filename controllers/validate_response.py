from fastapi import HTTPException
from fastapi.responses import JSONResponse,Response
import aiohttp

async def validate_response(response:aiohttp.ClientResponse):
    
    if response.status!= 200:
        raise HTTPException(status_code=response.status, detail=aiohttp.ClientResponseError)
    if response.headers.get('Content-Type').startswith('application/json'):
        response_json = await response.json()
        return JSONResponse(content=response_json)     
    else:
        response_xml = await response.text()
        return Response(content= response_xml,media_type="application/xml") 
        
            