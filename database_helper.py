import mysql.connector
global connection
connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="seasonal_tastes_db" )
def get_status_order(order_id:int):
    cursor = connection.cursor()
    query = "SELECT Status FROM order_tracking WHERE OrderID = %s"
    cursor.execute(query,(order_id,))
    result = cursor.fetchone()
    cursor.close()
    if result is not None:
        return result[0]
    else:
        return None
def update_to_database(food_order):
    try:
        cursor = connection.cursor()
        order_id = generate_order_id() + 1
        for food_name,quantity in food_order.items():
            cursor.callproc("insert_order_item",(food_name,quantity,order_id))
        connection.commit()
        cursor.close()
        return order_id
    except mysql.connector.Error as err:
        connection.rollback()
        return -1
    except Exception as err:
        connection.rollback()
        return -1

def generate_order_id():
    cursor = connection.cursor()
    query = "SELECT MAX(OrderId) FROM orders"
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    if result is not None:
        return result[0]
    else:
        return 1

def get_total_order_price(order_id):
    cursor = connection.cursor()
    query = "SELECT get_total_order_price(%s)"
    cursor.execute(query,(order_id,))
    result = cursor.fetchone()
    cursor.close()
    if result is not None:
        return result[0]
    else:
        return None

def update_order_id(order_id):
    cursor = connection.cursor()
    query = "INSERT INTO `seasonal_tastes_db`.`order_tracking` (`OrderID`, `Status`) VALUES (%s, %s);"
    cursor.execute(query,(order_id,"In Progress"))
    connection.commit()
    cursor.close()
