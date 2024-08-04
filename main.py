import uiautomator2 as u2
import subprocess
import time
import re
import requests
import random

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

# Função para salvar a hierarquia da interface em um arquivo XML
def save_xml(d, filename="hierarchy_dump.xml"):
    print("Hierarquia da interface salva em 'hierarchy_dump.xml'. Verifique o arquivo para encontrar os elementos.")
    time.sleep(5)
    xml_dump = d.dump_hierarchy()
    with open(filename, "w", encoding="utf-8") as f:
        f.write(xml_dump)
    return filename

# Função para esperar o emulador iniciar
def wait_for_emulator(emulator_id='emulator-5554'):
    while True:
        result = subprocess.run(['adb', '-s', emulator_id, 'get-state'], capture_output=True, text=True)
        if 'device' in result.stdout:
            print("Emulador pronto!")
            time.sleep(10)
            break
        print("Esperando o emulador iniciar...")
        time.sleep(15)

# Função para extrair coordenadas e resource-id usando regex
def extract_coordinates(xml_file, pattern):
    time.sleep(5)
    with open(xml_file, "r", encoding="utf-8") as f:
        xml_content = f.read()
    
    match = re.search(pattern, xml_content)
    if match:
        x1, y1, x2, y2 = map(int, match.groups())
        return x1, y1, x2, y2
    return None

# Função para iniciar o emulador
def start_emulator(emulator_path, avd_name):
    subprocess.Popen([emulator_path, '-avd', avd_name, '-snapshot', 'avdsave'])
    wait_for_emulator()

# Função para conectar ao emulador
def connect_emulator(emulator_id='emulator-5554'):
    d = u2.connect(emulator_id)
    try:
        d.info
        print("Conectado ao emulador")
    except u2.exceptions.ConnectionError:
        print("Não foi possível conectar ao emulador")
        exit(1)
    return d

# Função para realizar pesquisas no Bing
def perform_searches(d, coordinates, queries, search_times=25):
    x1, y1, x2, y2 = coordinates
    for _ in range(search_times):
        random.shuffle(queries)
        query = " ".join(random.sample(queries, random.randint(2, 3)))
        d.click(x1 + (x2 - x1) / 2, y1 + (y2 - y1) / 2)
        time.sleep(3)
        d.send_keys(query)
        d.press("enter")
        time.sleep(5)
        d.press("back")
        time.sleep(2)

# Função principal para executar o fluxo de trabalho
def main():
    avd_name = "Pixel_8_Edited_API_34"
    emulator_path = "emulator"
    start_emulator(emulator_path, avd_name)
    
    d = connect_emulator()
    
    try:
        d.app_stop_all()
        d.app_stop("com.microsoft.bing")
    except:
        pass
    
    d.app_start("com.microsoft.bing")
    
    while d.app_current()['activity'] != "com.microsoft.sapphire.app.main.MainSapphireActivity":
        time.sleep(1)
    
    time.sleep(4)
    
    search_box_pattern = r'<node[^>]*resource-id="com\.microsoft\.bing:id/placeholder_search_box"[^>]*bounds="\[([0-9]+),([0-9]+)\]\[([0-9]+),([0-9]+)\]"[^>]*>'
    search_box_coords = None
    while not search_box_coords:
        search_box_coords = extract_coordinates(save_xml(d), search_box_pattern)
    print(f"Coordenadas do search_box: {search_box_coords}")
    
    seed_words = ['car', 'price', 'man', 'new']
    queries = get_keywords(seed_words)
    
    perform_searches(d, search_box_coords, queries)
    
    # Processo de logout e login no Bing
    logout_patterns = [
        r'<node[^>]*resource-id="com\.microsoft\.bing:id/sa_profile_button"[^>]*bounds="\[([0-9]+),([0-9]+)\]\[([0-9]+),([0-9]+)\]"[^>]*>',
        r'<node[^>]*text="[^"]*Victor Amarilha[^"]*"[^>]*bounds="\[([0-9]+),([0-9]+)\]\[([0-9]+),([0-9]+)\]"[^>]*>',
        r'<node[^>]*text="Sign out"[^>]*bounds="\[([0-9]+),([0-9]+)\]\[([0-9]+),([0-9]+)\]"[^>]*>',
        r'<node[^>]*text="Sign in"[^>]*bounds="\[([0-9]+),([0-9]+)\]\[([0-9]+),([0-9]+)\]"[^>]*>',
        r'<node[^>]*text="victor_amarilha@outlook.com"[^>]*bounds="\[([0-9]+),([0-9]+)\]\[([0-9]+),([0-9]+)\]"[^>]*>'
    ]
    
    for pattern in logout_patterns:
        while True:
            coords = extract_coordinates(save_xml(d), pattern)
            if coords != None:
                break
        d.click(coords[0] + (coords[2] - coords[0]) / 2, coords[1] + (coords[3] - coords[1]) / 2)
    
    time.sleep(5)
    d.app_stop("com.microsoft.bing")
    time.sleep(2)
    d.app_start("com.microsoft.bing")
    
    while not search_box_coords:
        search_box_coords = extract_coordinates(save_xml(d), search_box_pattern)
    print(f"Coordenadas do search_box: {search_box_coords}")

    perform_searches(d, search_box_coords, queries)
    
    logout_patterns = [
        r'<node[^>]*resource-id="com\.microsoft\.bing:id/sa_profile_button"[^>]*bounds="\[([0-9]+),([0-9]+)\]\[([0-9]+),([0-9]+)\]"[^>]*>',
        r'<node[^>]*text="Victor Amarilha"[^>]*bounds="\[([0-9]+),([0-9]+)\]\[([0-9]+),([0-9]+)\]"[^>]*>',
        r'<node[^>]*text="Sign out"[^>]*bounds="\[([0-9]+),([0-9]+)\]\[([0-9]+),([0-9]+)\]"[^>]*>',
        r'<node[^>]*text="Sign in"[^>]*bounds="\[([0-9]+),([0-9]+)\]\[([0-9]+),([0-9]+)\]"[^>]*>',
        r'<node[^>]*text="victor_amarilha@hotmail.com"[^>]*bounds="\[([0-9]+),([0-9]+)\]\[([0-9]+),([0-9]+)\]"[^>]*>'
    ]

    for pattern in logout_patterns:
        while True:
            coords = extract_coordinates(save_xml(d), pattern)
            if coords != None:
                break
        d.click(coords[0] + (coords[2] - coords[0]) / 2, coords[1] + (coords[3] - coords[1]) / 2)


    d.app_stop("com.microsoft.bing")
    subprocess.run(['adb', '-s', 'emulator-5554', 'emu', 'avd', 'snapshot', 'save', 'avdsave'])
    subprocess.run(['adb', '-s', 'emulator-5554', 'emu', 'kill'])


if __name__ == "__main__":
    main()
