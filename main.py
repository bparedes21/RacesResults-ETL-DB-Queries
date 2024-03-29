#importo librerias
import pandas as pd
import sqlite3

from fastapi import FastAPI
import os
from starlette.responses import  RedirectResponse
tags_metadata = [
    {
        "name": "Races",
        "description": "Consultas datos tablas: de Races"
    },
    {
        "name": "Driver, Result",
        "description": "Consultas datos de tablas: Drivers, Results"
    },
    {
        "name": "Races, Circuit",
        "description": "Consultas datos de tablas: Races, Circuits"
    }

]

description = """
🚥Races API 🚗 El objetivo del proyecto es mostrar informacion extraida de archivos en formato CSV. Para ello primero hice un procesamiento de los datos garantizando la calidad de los mismos.

## Consultas a csv's en Pandas 🐼
* **El año con más carreras**
* **El nombre del corredor con mayor cantidad de primeros puestos**
* **El nombre del circuito con mas recorrido**
* **El nombre del corredor con mayor cantidad de puntos en total**

"""

app=FastAPI(description=description,openapi_tags=tags_metadata) 

@app.get("/")
def index():

    return RedirectResponse ("/docs/")

#no recibe parametros
#abre un csv: races_.csv, cada registro es una carrera, cuenta la cantidad de registros por cada año
#devuelve el Año con más carreras
@app.get("/get_anio_con_mas_carreras/",tags=["Races"])
def get_anio_con_mayor_cantidad_de_carreras_():
    
    name_db="Racing_BB.db"
    conn=sqlite3.connect(name_db)
    cursor = conn.cursor()
    query = """SELECT r."year", COUNT(r.raceId) as cantidad_de_carreras FROM races as r
    GROUP BY r."year"
    ORDER BY   cantidad_de_carreras DESC   ,r."year"  ASC
    LIMIT 1 """
    #almaceno en df
    df_query= pd.read_sql(query, conn)
    
    anios=df_query["year"].iloc[0]
    converted_anio=str(anios)

    cantidad_del_anio=df_query["cantidad_de_carreras"].iloc[0]
    converted_cantidad_del_anio=str(cantidad_del_anio)
    cursor.close()
    conn.close()

    mensaje="El Año " + converted_anio +" tuvo la cantidad de "+converted_cantidad_del_anio + " carreras. Fue el año con más carreras!" 
    return {"mensaje":mensaje}

#no recibe parametros
#abre un csv: result_.csv, cada registro es una resultado, agrupa los corredores y compara almacenadno el ganador con mas resultados en primer puesto
#luego abre un csv: drivers_.csv, y busca el nombre del corredor en primer puesto
#devuelve el nombre del corredor en primer puesto
@app.get("/get_Piloto_con_mayor_cantidad_de_primeros_puestos/",tags=["Driver, Result"])
def get_Piloto_con_mayor_cantidad_de_primeros_puestos():
    
    name_db="Racing_BB.db"
    conn=sqlite3.connect(name_db)
    cursor = conn.cursor()
    query = """
    SELECT d.forename, d.surname,results.cant_de_primeros_puestos  FROM drivers d 
    INNER JOIN
    (
    SELECT res.driverId  , res."rank"  , COUNT(res."rank") as cant_de_primeros_puestos  FROM results  as res
    WHERE res."rank"  ="1"
    GROUP BY res.driverId
    ORDER BY   cant_de_primeros_puestos DESC   
    LIMIT 1
    ) as results 
    ON results.driverId  = d.driverId 
    LIMIT 1 """
    #almaceno en df
    df_query= pd.read_sql(query, conn)
    
    forename=df_query["forename"].iloc[0]
    
    surname=df_query["surname"].iloc[0]

    cantidad_del_anio=df_query["cant_de_primeros_puestos"].iloc[0]
    converted_auxiliar=str(cantidad_del_anio)

    cursor.close()
    conn.close()

    return {'El nombre del corredor con mayor cantidad de primeros puestos: ' + forename +' '+ surname + ' con la cantidad de '+converted_auxiliar+' primeros puestos.'}

#no recibe parametros
#abre un csv: races_.csv, cada registro es una circuito corrido, cuenta la cantidad de circuitId por cada circuito
#luego abre un csv: circuit_.csv, y busca el circuitId con mas recorridos
#devuelve el nombre del circuito con mas recorrido
@app.get("/get_busca_circuito_con_mas_corridos/",tags=["Races, Circuit"])
async  def get_busca_circuito_con_mas_corrido():

    name_db="Racing_BB.db"
    conn=sqlite3.connect(name_db)
    cursor = conn.cursor()
    query = """SELECT  races.name as nombre_de_la_carrera , circuits.name as nombre_de_circuito , SUM( r.laps)  as cantidad_de_recorrido_vueltas FROM results r 
    INNER JOIN 
    races on races.raceId = r.raceId
    INNER JOIN 
    circuits ON circuits.circuitId  = races.circuitId 
    GROUP BY nombre_de_circuito
    ORDER BY  cantidad_de_recorrido_vueltas  DESC
    LIMIT 1 """
    #almaceno en df
    df_query= pd.read_sql(query, conn)
    nombre_de_circuitor=df_query["nombre_de_circuito"].iloc[0]
    veces_recorrido=df_query["cantidad_de_recorrido_vueltas"].iloc[0]
    cursor.close()
    conn.close()

    veces_recorrido_str=str(veces_recorrido)

    return {'El nombre del circuito con mas recorrido es: ' + nombre_de_circuitor + ' con la cantidad recorrida de '+veces_recorrido_str+' veces.'}

#Piloto con mayor cantidad de puntos en total, cuyo constructor sea de nacionalidad sea American o British
#no recibe parametros
#abre un csv: drivers_.csv, cada registro es corredor, busca los corredores con   american o british
#luego abre un csv: result_.csv, y busca el nombre del corredor de esa nacionalidad con mayor puntaje
#devuelve el nombre del corredor con mayor cantidad de puntos en total
@app.get("/get_buscar_conductor_con_mas_puntaje/",tags=["Driver, Result"])
async  def get_buscar_conductor_con_mas_puntaje():
    name_db="Racing_BB.db"
    conn=sqlite3.connect(name_db)
    cursor = conn.cursor()
    query = """
    SELECT  d.forename ,d.surname , SUM(points) AS cantidad_de_puntos_en_total FROM results r 
    INNER JOIN
    drivers d on d.driverId = r.driverId 
    LIMIT 1 """
    #almaceno en df
    df_query= pd.read_sql(query, conn)
    
    forename=df_query["forename"].iloc[0]

    surname=df_query["surname"].iloc[0]

    cantidad_de_puntos_en_total=df_query["cantidad_de_puntos_en_total"].iloc[0]

    converted_auxiliar=str(cantidad_de_puntos_en_total)

    cursor.close()
    conn.close()
    
    return {'El nombre del corredor con mayor cantidad de puntos en total: ' +forename+' '+ surname+' con la cantidad de '+converted_auxiliar+' puntos.'}



def create_app():
    from waitress import serve
    PORT = int(os.environ.get("PORT",8000))
    serve(app, host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    create_app()
