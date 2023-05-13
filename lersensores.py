import os
import glob
import time
import mysql.connector
from mysql.connector import errorcode
import requests

from flask import Flask, jsonify, render_template

cmd = ['python', 'site.py']

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'

device_folder = glob.glob(base_dir + '28*')[0]
device_folder1 = glob.glob(base_dir + '28*')[1]

device_file = device_folder + '/w1_slave'
device_file1 = device_folder1 + '/w1_slave'


def read_rom():
    name_file = device_folder+'/name'
    f = open(name_file,'r')
    return f.readline()

def read_rom1():
    name_file1 = device_folder1+'/name'
    g = open(name_file1,'r')
    return g.readline()

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp_raw1():
    g = open(device_file1, 'r')
    lines1 = g.readlines()
    g.close()
    return lines1

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0

        return temp_c
    
def read_temp1():
    lines1 = read_temp_raw1()
    while lines1[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines1 = read_temp_raw1()
    equals_pos1 = lines1[1].find('t=')
    if equals_pos1 != -1:
        temp_string1 = lines1[1][equals_pos1+2:]
        temp_c1 = float(temp_string1) / 1000.0
        temp_f1 = temp_c1 * 9.0 / 5.0 + 32.0
        
        return temp_c1 

app = Flask(__name__)
@app.route('/dados', methods=['GET', 'POST'])

def get_dados(): 
    dados = {}
    temp_c = read_temp()
    temp_c1 = read_temp1()

    dados['temperatura_1'] = temp_c
    dados['temperatura_2'] = temp_c1

    return render_template('index.html', jsonify(dados))

# Configurar a conexão com o banco de dados
connection = {
  'host':'bancodedados.ch30kvh0gicl.sa-east-1.rds.amazonaws.com',
  'user':'alex',
  'password':'Lhm260768',
  'database':'sensordetemperatura'
}

while True:
    c1, f1 = read_temp()
    c2, f2 = read_temp1()
    print(f' C1={c1:.3f}  F1={f1:.3f}')
    print(f' C2={c2:.3f}  F2={f2:.3f}')
    
    try:
        conn = mysql.connector.connect(**connection)
        print("Connection estabelecida")

        with conn.cursor() as cursor:
            # criar tabela se não existir
            table_name = 'tabela_sensores'  
            create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} (id INT AUTO_INCREMENT PRIMARY KEY, temperatura_c1 FLOAT, temperatura_f1 FLOAT, temperatura_c2 FLOAT, temperatura_f2 FLOAT, data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
            cursor.execute(create_table_query)

            # inserir dados na tabela
            insert_query = "INSERT INTO tabela_sensores (temperatura_c1, temperatura_f1, temperatura_c2, temperatura_f2) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_query, (c1, f1, c2, f2))
            conn.commit()
            
             # exibir dados da tabela
            select_query = "SELECT * FROM tabela_sensores ORDER BY id DESC LIMIT 1"
            cursor.execute(select_query)
            rows = cursor.fetchall()
            for row in rows:
                print(row)

    except mysql.connector.Error as error:
        print("Erro ao se conectar ao MySql:", error)

    finally:
        if (conn.is_connected()):
            cursor.close()
            conn.close()
            print("Connection finalizada")   
        
    time.sleep(4)