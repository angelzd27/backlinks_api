import smtplib
import time
import random
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from email_validator import validate_email, EmailNotValidError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from auth.jwtbearer import JWTBearer
from ..config.database import connection
from ..models.persistence import contacts
from ..schemas.Contact import ContactResponse, EmailSender
from sqlalchemy import text
from decouple import config
from bs4 import BeautifulSoup
import requests
import re

contact = APIRouter(tags=['contact'])

API_KEY = config("api_key")
CSE_ID = config("cse_id")
proxies = [
    'http://104.248.63.17:80',
    'http://167.71.5.83:8080',
    'http://138.68.24.145:8080',
    'http://178.62.193.19:8080',
    'http://159.89.132.35:8080',
]

def google_search(query, api_key, cse_id, num_results=10, **kwargs):
    results = []
    start_index = 1  # Índice inicial para las búsquedas, Google Custom Search API usa 1-based indexing
    
    while len(results) < num_results:
        num = min(10, num_results - len(results))  # Limita la cantidad de resultados a 10 por solicitud
        url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cse_id}&start={start_index}&num={num}"
        params = kwargs
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'items' in data:
            results.extend(data['items'])
        else:
            break  # Si no hay más resultados, salir del bucle
        
        start_index += 10  # Incrementar el índice inicial para la siguiente solicitud
    
    return {'items': results}

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
        
        # Validar correos electrónicos
        valid_emails = []
        for email in emails:
            try:
                validate_email(email)
                valid_emails.append(email)
                break
            except EmailNotValidError:
                continue

        # Buscar números de teléfono
        phones = re.findall(r'(\+\d{1,3}\s?\d[\d\s.-]{8,}|\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b)', text)

        # Inferir el nombre de la empresa basado en el dominio
        domain = re.findall(r'https?://(www\.)?([a-zA-Z0-9-]+)\.[a-zA-Z]+', url)
        if domain:
            company_name = domain[0][1]
        else:
            company_name = "Not Found"
        
        return {
            "url": url,
            "emails": valid_emails if valid_emails else ["Not Found"],
            "phones": phones if phones else ["Not Found"],
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
        if (contact_info['emails'] != ["Not Found"]):

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
    
    return {"error": False, "msg": "Contacts info saved to DB"}

def get_random_proxy():
    return random.choice(proxies)

def send_email(sendto, subject, text, credentials):
    for i in range(3):
        try:
            for credential in credentials:
                proxy = get_random_proxy()
                print(f"Changing IP using proxy {proxy}...")

                # Configura el proxy en el servidor SMTP
                proxy_dict = {
                    "http": proxy,
                    "https": proxy,
                }

                username, password = credential.email, credential.password
                print(f"Sending Email to {sendto} using {username} (trial {i+1})...")

                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = username
                msg['To'] = sendto

                part1 = MIMEText(text, 'plain')
                part2 = MIMEText(text, 'html')

                msg.attach(part1)
                msg.attach(part2)

                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()

                # Configura el proxy para el servidor SMTP
                server.ehlo()
                server.esmtp_features['proxy'] = 'on'
                server.esmtp_features['proxy_host'] = proxy

                server.login(username, password)
                server.sendmail(username, sendto, msg.as_string())
                server.quit()

                print("Email sent!")
                time.sleep(10)
                return
        except Exception as e:
            print("Failed to send email due to Exception:")
            print(e)
            
def get_emails_from_db():
    try:
        emails = connection.execute("SELECT emails FROM contacts")
        return [email[0] for email in emails]
    except Exception as err:
        print(f"Error: {err}")
        
@contact.post('/send_email', dependencies=[Depends(JWTBearer())])
async def send_email_to_contacts(request: EmailSender):
    subject = request.subject
    message = request.message
    credentials = request.credentials
    print(credentials)
    emails = get_emails_from_db()
    
    for index, email in enumerate(emails):
        credential_index = index % len(credentials)
        print([credentials[credential_index]])
        send_email(email, subject, message, [credentials[credential_index]])
    
    return {"error": False, "msg": "Emails sent successfully"}

@contact.get('/get_contacts', dependencies=[Depends(JWTBearer())])
async def get_contacts():
    result = connection.execute("SELECT * FROM contacts").fetchall()
    if result == None:
        return {'error': True, 'msg': 'There are not contacts'}
    return {"error": False, 'msg':result}

@contact.get('/get_contact_by_id/{id}', dependencies=[Depends(JWTBearer())])
async def get_contact_by_id(id):
    result = connection.execute(contacts.select().where(contacts.c.id == id)).first()
    if result != None:
        _status = status.HTTP_200_OK
        return {"error":False,"msg":result}
    _status = status.HTTP_404_NOT_FOUND

    result = {"error":True,"msg":"contact not found"}
    return JSONResponse(status_code=_status, content=result)

@contact.delete('/delete_contact/{id}', dependencies=[Depends(JWTBearer())])
async def delete_contact(id):
    connection.execute(contacts.delete().where(contacts.c.id == id))
    return {"error": False, "msg": "Contact deleted successfully"}

@contact.delete('/delete_contacts', dependencies=[Depends(JWTBearer())])
async def delete_contacts():
    connection.execute("TRUNCATE TABLE contacts")
    return {"error": False, "msg": "All contacts deleted successfully"}