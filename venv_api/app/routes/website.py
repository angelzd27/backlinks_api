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
import time

website = APIRouter(tags=['website'])

def check_url_in_db(url):
    query = "SELECT id FROM website WHERE url = %s"
    result = connection.execute(query, (url,)).first()
    return result is not None

def add_url_to_db(url, status):
    query = "INSERT INTO website (url, status) VALUES (%s, %s)"
    connection.execute(query, (url, status))
    
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

                    # Busca el formulario de comentarios por clase, id o nombre
                    try:
                        comment_form = driver.find_element(By.CLASS_NAME, "comment-form")
                    except:
                        try:
                            comment_form = driver.find_element(By.ID, "commentform")
                        except:
                            try:
                                comment_form = driver.find_element(By.CLASS_NAME, "c-form")
                            except:
                                comment_form = None

                    if comment_form:
                        # Encuentra todos los campos dentro del formulario de comentarios
                        input_fields = comment_form.find_elements(By.TAG_NAME, "input")
                        textarea_fields = comment_form.find_elements(By.TAG_NAME, "textarea")
                        submit_button = None

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

                        if not submit_button:
                            try:
                                # submit_button = comment_form.find_element(By.CSS_SELECTOR, 'button[name="submit"], button[id="submit"], button.submit')
                                submit_button = True
                            except:
                                submit_button = None

                        if submit_button:
                            # submit_button.click()
                            print(f"Comentario enviado en la página: {driver.current_url}")
                            add_url_to_db(url, 1)
                        else:
                            print("No se encontró un botón de submit en la página actual.")
                            add_url_to_db(url, 0)
                    else:
                        print("No se encontró un formulario de comentarios en la página actual.")
                        add_url_to_db(url, 0)

                    driver.back()  # Volver a los resultados de búsqueda
                    time.sleep(2)  # Esperar que se cargue la página de resultados
                except Exception as e:
                    print("Error al acceder al link:", str(e))
            else:
                print("El resultado no es un enlace, se omitirá.")
        else:
            print("No hay más resultados para mostrar.")
            break

    driver.quit()

    return {"error": False, "msg": "Proceso completado"}