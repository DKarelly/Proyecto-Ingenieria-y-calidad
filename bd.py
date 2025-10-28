import pymysql

def obtener_conexion():
    return pymysql.connect(host='trolley.proxy.rlwy.net',
                                port=40902,
                                user='root',
                                password='EOFxUnNipaqUHGATGeTGjiOzlcdEvKwL',
                                db='CLINICA',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)