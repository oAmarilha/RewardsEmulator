import threading
from airtest.core.api import *
from airtest.core.android.android import ADB
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
import random
import requests
import time

# Função para obter palavras relacionadas usando a API Datamuse
def get_related_words(seed_word, max_words=10):
    response = requests.get(f'https://api.datamuse.com/words?ml={seed_word}&max={max_words}')
    if response.status_code == 200:
        words = [word['word'] for word in response.json()]
        return words
    else:
        print('Erro ao obter palavras da API')
        return []

# Função para obter palavras-chave relacionadas a partir de palavras-semente
def get_keywords(seed_words):
    keywords = []
    for seed in seed_words:
        related_words = get_related_words(seed)
        keywords.extend(related_words)
    return keywords

def start_bing(poco, device):
    try:
        device.stop_app('com.microsoft.bing')
        device.start_app('com.microsoft.bing')
    except:
        device.start_app('com.microsoft.bing')
    
    search = poco(name="com.microsoft.bing:id/sa_hp_header_search_box")
    search.wait_for_appearance()
    search.click()
    shuffle_search(device)
    time.sleep(2)

def shuffle_search(device):
    seed_words = ['car', 'price', 'man', 'new']  # Palavras-semente
    searches = get_keywords(seed_words)  # Obter palavras-chave relacionadas
    random.shuffle(searches)
    query = " ".join(random.sample(searches, random.randint(2, 3)))
    device.text(query)

def start_bing_searches(device, poco, serial, email):
    email = email
    start_bing(poco, device)
    time.sleep(3)
    for _ in range(1):
        print(f"\nAndroid: {serial}, pesquisa bing n : {_ + 1}\n")
        poco("com.microsoft.bing:id/iab_address_bar_text_view").click()
        poco("com.microsoft.bing:id/clear").click()
        shuffle_search(device)
        time.sleep(2)
    logout_login(poco, device, email)
    device.stop_app('com.microsoft.bing')

def start_chrome(poco, device):
    try:
        device.stop_app('com.android.chrome')
        device.start_app('com.android.chrome')
    except:
        device.start_app('com.android.chrome')
    
    searchInput = poco(name="com.android.chrome:id/search_box_text")
    searchInput.wait_for_appearance()
    searchInput.click()
    shuffle_search(device)
    time.sleep(2)

def start_chrome_searches(poco, device, serial):
    start_chrome(poco, device)
    for _ in range(1):
        print(f"\nAndroid: {serial}, pesquisa chrome n : {_ + 1}\n")
        poco(name="com.android.chrome:id/url_bar").click()
        time.sleep(1)
        poco(name="com.android.chrome:id/url_bar").set_text("")  # Limpar o texto da barra de pesquisa
        time.sleep(1)
        shuffle_search(device)
    device.stop_app('com.android.chrome')

def logout_login(poco, device,email):
    # Logout e login no Bing usando o Poco
    poco(text="Home").click()
    poco(name="com.microsoft.bing:id/sa_profile_button").click()
    poco(text="Settings").click()
    time.sleep(1)
    poco(text="Sign out").click()  # Desfazer o login
    time.sleep(5)
    
    # Realizar o login
    poco(text="Sign in").click()
    poco(text=email).click()
    time.sleep(5)
    
    start_bing(poco, device)
    time.sleep(3)

def init_searches(serial):
    adb = ADB(serialno=serial)
    device = init_device("Android", uuid=serial)
    poco = AndroidUiautomationPoco(device=device)
    start_bing_searches(device, poco, serial, "victor_amarilha@outlook.com")
    start_bing_searches(device, poco, serial, "victor_amarilha@hotmail.com")
    start_chrome_searches(poco, device, serial)
    return adb, device, poco

# t1 = threading.Thread(target=init_searches, args=('R3CT6044BPE',)) # Fold 4
t1 = threading.Thread(target=init_searches, args=('emulator-5554',)) # Flip 5
# t2 = threading.Thread(target=init_searches, args=('RQCT601N17W',)) # S22 Ultra
t1.start()
# t2.start()
t1.join()
# t2.join()
