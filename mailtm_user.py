from colorama import init, Fore as c
import random as r
import requests
import json
import os
init()

def get_address():
    adrsFile = open("addresses.txt", "r")
    addresses = adrsFile.read().split("\n")
    adrsFile.close()
    return addresses[r.randint(0, len(addresses)-1)]

def init_program():
    try:
        print("\n[0] Salir\n[1] Agregar cuenta      [2] Mostrar cuenta"+('s' if get_accounts('len') > 1 else '')+"\n[3] Mostrar mensajes    [4] Eliminar cuenta")
        action = int(input("Action >> "))
        if action == 0:
            print(c.GREEN+"Cerrando..."+c.WHITE)
            exit()
        elif action == 1:
            print("[0] Atras\n[1] Iniciar sesión   [2] Crear cuenta")
            option = int(input("Action >> "))
            if option == 1:
                email = input("Address (include domain)>> ")
                password = input("Password >> ")
                ret_code = add_account('login', email, password) 
                if ret_code == 422: print(c.GREEN+"[+] "+c.WHITE+"Cuenta añadida con éxito")
                else: print(c.YELLOW+"[*] "+c.WHITE+"La cuenta no existia, se ha creado y agregado con éxito")
            elif option == 2:
                email = input("Address (not include domain)>> ")
                password = input("Password >> ")
                ret_code, address = add_account('register', email, password)
                if ret_code == 422: 
                    print(c.RED+"[!] "+c.WHITE+"La cuenta que quieres crear ya existe.\nSi conoces las credenciales inicia sesión, o selecciona otro dominio")
                    # Read Addresses
                    adrsFile = open("addresses.txt", "r")
                    addresses = adrsFile.read().split("\n")
                    addresses.remove(address)
                    adrsFile.close()
                    # Display Addresses option
                    print("[0] Atras")
                    for addr in range(0, len(addresses), 2):
                        opcion_1 = f"[{addr+1}] {addresses[addr]}"
                        if addr+1 < len(addresses): opcion_2 = f"[{addr+2}] {addresses[addr+1]}"
                        else: opcion_2 = ""
                        print(f"{opcion_1:<30} {opcion_2}")
                    selAcc = input("Domain >> ")
        elif action == 2:
            show_account()
        elif action == 3:
            print("Revisando mensajes...")
            show_msg()
        elif action == 4:
            delete_account()
        else:
            print(c.RED+"[-] Err : Action not found..."+c.WHITE)
        init_program()
    except KeyboardInterrupt:
        print(c.RED+"\n\nCtrl+C Detectado... Cerrando programa... Bye (~.v)\n")

def add_account(action, email, password):
    if action != 'login': 
        address = get_address()
        email = email+address
    # Create account in server
    url = "https://api.mail.gw/accounts"
    payload = {
        "address": email,
        "password": password
    }
    headers = { 'Content-Type': 'application/json' }
    r = requests.post(url, headers=headers, json=payload)
    data = r.text
    if r.status_code == 422 and action == 'register': return r.status_code, address
    if r.status_code == 400: return r.status_code
    data = json.loads(data)
    # Detect Account file
    if os.path.exists('acc_info.json'):
        accFile = open('acc_info.json', 'r')
        accData = accFile.read()
        accData = accData[:-1][1:].replace('},', '}},').split('},') if len(accData) > 3 else []
        accFile.close()
    else: accData = []
    # Write new account in file
    accData.append('{'+f'"email":"{email}", "password":"{password}", "id":"{data["id"]}", "token":"{get_token(email, password)}"'+'}')
    accFile = open('acc_info.json', 'w')
    accFile.write('[')
    for acc in accData:
        accItem = json.loads(acc)
        if accData.index(acc) < len(accData)-1: accFile.write('\n    {\n        "email":"'+accItem["email"]+'",\n        "password":"'+accItem["password"]+'",\n        "id":"'+accItem["id"]+'",\n        "token":"'+accItem["token"]+'"\n    },')
        else: accFile.write('\n    {\n        "email":"'+accItem["email"]+'",\n        "password":"'+accItem["password"]+'",\n        "id":"'+accItem["id"]+'",\n        "token":"'+accItem["token"]+'"\n    }\n]')
    accFile.close()
    return r.status_code

def get_token(email, password):
    url = "https://api.mail.gw/token"
    payload = {
        "address": email,
        "password": password
    }
    headers = { 'Content-Type': 'application/json' }
    r = requests.post(url, headers=headers, json=payload)
    data = r.text
    data = json.loads(data)
    return data["token"]

def delete_account():
    with open("acc_info.json", "r") as accFile:
        data = json.loads(accFile.read())
        id = data["id"]
        token = data["token"]
    accFile.close()
    header = {"authorization":f"Bearer {token}"}
    r = requests.delete(f"https://api.mail.gw/accounts/{id}", headers=header)
    with open("acc_info.json", "w") as accFile:
        accFile.write(" [!] NO Account Exists !!!")
    accFile.close()
    print(c.GREEN+"[+] Account Deleted"+c.WHITE)

def get_accounts(req=""):
    if not os.path.exists('acc_info.json'): return []
    accFile = open('acc_info.json', 'r')
    accData = accFile.read()
    accData = accData[:-1][1:].replace('},', '}},').split('},') if len(accData) > 3 else []
    accFile.close()
    accData = [acc for acc in accData if len(acc) > 5]
    # Request Check
    if req == "len": return len(accData)
    return accData

def show_account():
    # File Verification
    if not os.path.exists('acc_info.json'):
        print(c.RED+"[!] "+c.WHITE+"No existen cuentas. Porfavor añade una primero.")
        return 0
    # Account Read and Display
    accData = get_accounts()
    if len(accData) >= 2:
        print("[0] Atras")
        for acc in range(0, len(accData), 2):
            opcion_1 = f"[{acc+1}] {json.loads(accData[acc])["email"]}"
            if acc+1 < len(accData): opcion_2 = f"[{acc+2}] {json.loads(accData[acc+1])["email"]}"
            else: opcion_2 = ""
            print(f"{opcion_1:<30} {opcion_2}")
        selAcc = input("Account >> ")
        try: 
            if int(selAcc) == 0: return 0
            selAcc = int(selAcc)-1
            if selAcc > len(accData)-1 or selAcc < 0:
                print(c.RED+f"[!] Valor incorrecto, el {selAcc+1} no se encuentra en la lista"+c.WHITE)
                return 0
        except:
            print(c.RED+"[!] Valor incorrecto, porfavor ingresa un número"+c.WHITE)
            return 0
        account = json.loads(accData[selAcc])
        print(c.GREEN+"\nDireccion / Address : "+c.WHITE+account["email"]+c.GREEN+"\nContraseña / Password : "+c.WHITE+account["password"]+c.GREEN+"\nId : "+c.WHITE+account["id"]+c.GREEN+"\nToken : "+c.WHITE+account["token"])

def show_msg():
    with open("acc_info.json", "r") as accFile:
        data = json.loads(accFile.read())
        token = data["token"]
    accFile.close()
    header = {"authorization":f"Bearer {token}"}
    r = requests.get("https://api.mail.gw/messages", headers=header)
    mail_sayisi = r.text
    mail_sayisi = json.loads(mail_sayisi)
    if str(mail_sayisi["hydra:member"]) != "[]":
        id = mail_sayisi["hydra:member"][0]["id"]
        r  = requests.get(f"https://api.mail.gw/messages/{id}", headers=header)
        mail = r.text
        mail = json.loads(mail)
        
        mailS = mail["from"]["address"]
        title = mail["subject"]
        content = mail["text"]

        print("\n------------------------------")
        print(c.GREEN+" Remitente / From : "+c.WHITE+mailS+c.GREEN+"\n Asunto / Subject : "+c.WHITE+title+c.GREEN+"\n Contenido / Content : "+c.WHITE+content)
    else:
        print(c.RED+"[!] NO TIENES NINGUN MENSAJE"+c.WHITE)


print("Bienvenido a MailTm API... v.V")
init_program()