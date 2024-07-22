from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from auth.jwtbearer import JWTBearer
from ..config.database import connection
from ..models.persistence import contacts
from ..schemas.Contact import ContactResponse
from sqlalchemy import text
from decouple import config
from bs4 import BeautifulSoup
import requests
import re

contact = APIRouter(tags=['contact'])

API_KEY = config("api_key")
CSE_ID = config("cse_id")

def google_search(query, api_key, cse_id, num_results=10, **kwargs):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cse_id}"
    params = {'num': num_results, **kwargs}
    response = requests.get(url, params=params)
    return response.json()

def extract_contact_info(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Encuentra todos los elementos de texto en la página
        text_elements = soup.find_all(text=True)
        text = ' '.join(text_elements)  # Concatena todo el texto encontrado
        
        # Buscar correos electrónicos
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        
        # Buscar números de teléfono
        phones = re.findall(r'(\+\d{1,3}\s?\d[\d\s.-]{8,}|\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b)', text)

        # Inferir el nombre de la empresa basado en el dominio
        domain = re.findall(r'https?://(www\.)?([a-zA-Z0-9-]+)\.[a-zA-Z]+', url)
        if domain:
            company_name = domain[0][1]
        else:
            company_name = "Not Found - 0"
        
        return {
            "url": url,
            "emails": emails if emails else ["Not Found - 0"],
            "phones": phones if phones else ["Not Found - 0"],
            "company_name": company_name
        }
    except requests.exceptions.RequestException:
        return None

def is_social_media(url):
    social_media_domains = ['facebook.com', 'instagram.com', 'twitter.com', 'linkedin.com', 'pinterest.com', 'tiktok.com']
    for domain in social_media_domains:
        if domain in url:
            return True
    return False

def save_to_database(contact_info):
    try:
        if (contact_info['emails'] != ["Not Found - 0"]):

            # Verificar si la URL ya existe en la base de datos
            check_url_query = "SELECT COUNT(*) FROM contacts WHERE url = %s"
            (count,) = connection.execute(check_url_query, (contact_info['url'],)).first()

            if count == 0:
                # Insertar la información de contacto en la base de datos
                add_contact_query = "INSERT INTO contacts (url, emails, phones, company_name) VALUES (%s, %s, %s, %s)"
                connection.execute(add_contact_query, (
                    contact_info['url'],
                    ', '.join(contact_info['emails']),
                    ', '.join(contact_info['phones']),
                    contact_info['company_name']
                ))
                print(f"Contact info saved to DB for URL: {contact_info['url']}")
            else:
                print(f"URL ya existe en la base de datos: {contact_info['url']}")

            connection.close()
        else:
            print(f"No se guardó en la base de datos debido a información incompleta para URL: {contact_info['url']}")
    except Exception as err:
        print(f"Error: {err}")
        
@contact.post('/search_contact', dependencies=[Depends(JWTBearer())])
async def search_contact(request: ContactResponse):
    keyword = request.keyword
    number_of_pages = request.number_of_pages
    search_results = google_search(keyword, API_KEY, CSE_ID, num_results=number_of_pages)
    
    for item in search_results['items']:
        url = item['link']
        if not is_social_media(url):
            contact_info = extract_contact_info(url)
            if contact_info:
                save_to_database(contact_info)
    
    return {"msg": "Contact info saved to DB"}