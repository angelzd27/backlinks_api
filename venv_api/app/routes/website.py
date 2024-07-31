from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from auth.jwtbearer import JWTBearer
from ..config.database import connection
from ..models.persistence import websites
from ..schemas.Website import Website, CommentRequest
from sqlalchemy import text
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import xml.etree.ElementTree as ET
import requests
import time

website = APIRouter(tags=['website'])

def check_url_in_db(url):
    query = "SELECT id FROM website WHERE url = %s"
    result = connection.execute(query, (url,)).first()
    return result is not None

def add_url_to_db(url, status):
    query = "INSERT INTO website (url, status) VALUES (%s, %s)"
    connection.execute(query, (url, status))
    
def extract_comments_from_feed(url):
    # Obtener el contenido de la URL
    response = requests.get(url)
    
    # Comprobar si la solicitud fue exitosa
    if response.status_code == 200:
        # Obtener el contenido XML
        xml_data = response.text

        # Parsear el XML
        root = ET.fromstring(xml_data)

        # Lista para almacenar las URLs de comentarios
        comments_list = []

        # Encontrar todos los elementos <item> y extraer el texto de <comments>
        for item in root.findall('.//item'):
            comments = item.find('comments')
            if comments is not None:
                comments_text = comments.text
                if comments_text and '/feed' not in comments_text:
                    comments_list.append(comments_text)

        # Retornar la lista de URLs de comentarios
        return comments_list
    else:
        print(f'Error al acceder a la URL: {response.status_code}')
        return []
    
def find_submit_button(comment_form):
    try:
        # Intentar encontrar el botón de submit por los atributos especificados
        submit_button = comment_form.find_element(By.XPATH, '//input[@type="submit" and (@name="submit" or @id="submit" or @class="submit")]')
        return submit_button
    except:
        return None

@website.post('/create_comment', dependencies=[Depends(JWTBearer())])
async def make_contacts(request: CommentRequest):
    keyword = request.keyword
    pages_to_search = request.number_of_pages
    author = request.author
    email = request.email
    website_url = request.url
    comment_text = request.comment
    driver = webdriver.Chrome()
    search_url = "https://www.google.com"
    driver.get(search_url)
    pageCommented = False

    # Buscar la palabra clave en Google
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(keyword)
    search_box.send_keys(Keys.RETURN)

    time.sleep(2)  # Esperar que se carguen los resultados

    for page in range(pages_to_search):
        # Iterar sobre los resultados de búsqueda
        results = driver.find_elements(By.CSS_SELECTOR, 'h3')
        if page < len(results):
            # Verificar si el resultado es un enlace
            parent = results[page].find_element(By.XPATH, '..')  # Obtener el elemento padre
            if parent.tag_name == 'a':  # Comprobar si el padre es un enlace
                url = parent.get_attribute('href')
                if check_url_in_db(url):
                    print("URL ya existente:", url)
                    continue

                try:
                    parent.click()  # Hacer clic en el enlace
                    time.sleep(2)  # Esperar que se cargue la página
                    current_url = driver.current_url

                    # Navegar a la URL + /feed
                    feed_url = current_url + "/feed"
                    driver.get(feed_url)
                    time.sleep(5)  # Esperar que se cargue la página

                    # Buscar la etiqueta <comments>
                    comment_urls = extract_comments_from_feed(feed_url)
                    
                    for comment_url in comment_urls[:2]:  # Solo las primeras 3 URLs
                        try:
                            # Navegar a la URL extraída
                            driver.get(comment_url)
                            time.sleep(2)  # Esperar que se cargue la página

                            # Busca el formulario de comentarios por clase, id o nombre
                            comment_form = None

                            selectors = [
                                (By.CLASS_NAME, "comment-form"),
                                (By.ID, "commentform"),
                                (By.ID, "comments"),
                                (By.CLASS_NAME, "c-form"),
                                (By.CLASS_NAME, "comments"),
                                (By.CLASS_NAME, "comments-area")
                            ]

                            for selector in selectors:
                                try:
                                    comment_form = driver.find_element(*selector)
                                    break
                                except:
                                    continue

                            if comment_form:
                                # Encuentra todos los campos dentro del formulario de comentarios
                                input_fields = comment_form.find_elements(By.TAG_NAME, "input")
                                textarea_fields = comment_form.find_elements(By.TAG_NAME, "textarea")

                                # Rellenar los campos del formulario
                                for field in input_fields:
                                    field_name = field.get_attribute('name')
                                    if field_name == "author":
                                        field.send_keys(author)
                                    elif field_name == "email":
                                        field.send_keys(email)
                                    elif field_name == "url":
                                        field.send_keys(website_url)

                                for field in textarea_fields:
                                    if field.get_attribute('name') == "comment":
                                        field.send_keys(comment_text)

                                submit_button = find_submit_button(comment_form)

                                if submit_button:
                                    # submit_button.click()
                                    print(f"Comentario enviado en la página: {driver.current_url}")
                                    add_url_to_db(comment_url, 1)
                                    pageCommented = True
                                else:
                                    print("No se encontró un botón de submit en la página actual.")
                                    add_url_to_db(comment_url, 0)
                                    pageCommented = True
                            else:
                                print("No se encontró un formulario de comentarios en la página actual.")
                                add_url_to_db(comment_url, 0)
                        except Exception as e:
                            print(f"Error al acceder a la URL de comentarios: {comment_url} - {str(e)}")

                    # Volver a la página de resultados de búsqueda
                    driver.back()
                    driver.back()
                    driver.back()
                    if pageCommented == True:
                        driver.back()
                        
                    time.sleep(2)  # Esperar que se cargue la página de resultados
                    pageCommented = False

                except Exception as e:
                    print("Error al acceder al link:", str(e))
            else:
                print("El resultado no es un enlace, se omitirá.")
        else:
            print("No hay más resultados para mostrar.")
            break

    driver.quit()

    return {"error": False, "msg": "Proceso completado"}

@website.get('/get_websites', dependencies=[Depends(JWTBearer())])
async def get_websites():
    result = connection.execute("SELECT * FROM website").fetchall()
    if result == None:
        return {'error': True, 'msg': 'There are not websites'}
    return {"error": False, 'msg':result}

@website.get('/get_website_by_id/{id}', dependencies=[Depends(JWTBearer())])
async def get_website_by_id(id):
    result = connection.execute(websites.select().where(websites.c.id == id)).first()
    if result != None:
        _status = status.HTTP_200_OK
        return {"error":False,"msg":result}
    _status = status.HTTP_404_NOT_FOUND

    result = {"error":True,"msg":"Website not found"}
    return JSONResponse(status_code=_status, content=result)

@website.delete('/delete_website/{id}', dependencies=[Depends(JWTBearer())])
async def delete_website(id):
    connection.execute(websites.delete().where(websites.c.id == id))
    return {"error": False, "msg": "Website deleted successfully"}

@website.delete('/delete_websites', dependencies=[Depends(JWTBearer())])
async def delete_websites():
    connection.execute("TRUNCATE TABLE website")
    return {"error": False, "msg": "All websites deleted successfully"}