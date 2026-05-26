from database.DB_connect import DBConnect
from model.airport import Airport
from model.tratta import Tratta


class DAO():

    @staticmethod
    def getAllAirports():
        conn = DBConnect.get_connection()

        result = []

        cursor = conn.cursor(dictionary=True)
        query = """SELECT * from airports a order by a.AIRPORT asc"""

        cursor.execute(query)

        for row in cursor:
            result.append(Airport(**row))

        cursor.close()
        conn.close()

        return result


    @staticmethod
    def getAllNodes(nMin, idMapAeroporti):
        conn = DBConnect.get_connection()

        result = []

        cursor = conn.cursor(dictionary=True)
        query = """SELECT t.ID, t.IATA_CODE, count(*) as N 
                    FROM (select a.ID, a.IATA_CODE, f.AIRLINE_ID, count(*) 
                    from airports a, flights f 
                    where a.ID = f.ORIGIN_AIRPORT_ID 
                    or a.ID = f.DESTINATION_AIRPORT_ID 
                    GROUP BY a.ID, a.IATA_CODE, f.AIRLINE_ID ) t 
                    GROUP BY t.ID, t.IATA_CODE 
                    having N >= %s 
                    order by N asc"""

        cursor.execute(query, (nMin,))

        for row in cursor:
            result.append(idMapAeroporti[row["ID"]]) # recupero l'oggetto attraerso la sua chiave nella id map

        cursor.close()
        conn.close()

        return result


    @staticmethod
    def getAllEdgesV1(idMapAeroporti):
        conn = DBConnect.get_connection()

        result = []

        # con questa però ho archi ad andare e a tornare che devono essere sommati e non sono filtrati per i
        # voli che voglio io
        cursor = conn.cursor(dictionary=True)
        query = """SELECT f.ORIGIN_AIRPORT_ID as id1, f.DESTINATION_AIRPORT_ID as id2, COUNT(*) as peso 
                    FROM flights f 
                    GROUP BY f.ORIGIN_AIRPORT_ID, f.DESTINATION_AIRPORT_ID 
                    ORDER BY f.ORIGIN_AIRPORT_ID, f.DESTINATION_AIRPORT_ID """

        cursor.execute(query)

        for row in cursor:
            result.append(Tratta(idMapAeroporti[row["id1"]],
                                 idMapAeroporti[row["id2"]],
                                 row["peso"]))

        cursor.close()
        conn.close()

        return result


    @staticmethod
    def getAllEdgesV2(idMapAeroporti):
        conn = DBConnect.get_connection()

        result = []

        # coalesce mi restituisce 0 se non trova un peso, mi permette di non avere valori null
        cursor = conn.cursor(dictionary=True)
        query = """SELECT t1.ORIGIN_AIRPORT_ID as id1, t1.DESTINATION_AIRPORT_ID as id2, (COALESCE(t1.n, 0) + COALESCE(t2.n, 0)) as peso 
                    FROM (SELECT f.ORIGIN_AIRPORT_ID, f.DESTINATION_AIRPORT_ID, COUNT(*) AS n 
                    FROM flights f 
                    GROUP BY f.ORIGIN_AIRPORT_ID, f.DESTINATION_AIRPORT_ID 
                    ORDER BY f.ORIGIN_AIRPORT_ID, f.DESTINATION_AIRPORT_ID) t1 
                    LEFT JOIN (SELECT f.ORIGIN_AIRPORT_ID, f.DESTINATION_AIRPORT_ID, COUNT(*) AS n 
                    FROM flights f 
                    GROUP BY f.ORIGIN_AIRPORT_ID, f.DESTINATION_AIRPORT_ID 
                    ORDER BY f.ORIGIN_AIRPORT_ID, f.DESTINATION_AIRPORT_ID) t2 
                    ON t1.ORIGIN_AIRPORT_ID = t2.DESTINATION_AIRPORT_ID AND t1.DESTINATION_AIRPORT_ID = t2.ORIGIN_AIRPORT_ID 
                    WHERE t1.ORIGIN_AIRPORT_ID < t1.DESTINATION_AIRPORT_ID OR t2.ORIGIN_AIRPORT_ID = Null"""

        cursor.execute(query)

        for row in cursor:
            result.append(Tratta(idMapAeroporti[row["id1"]],
                                 idMapAeroporti[row["id2"]],
                                 row["peso"]))

        cursor.close()
        conn.close()

        return result


