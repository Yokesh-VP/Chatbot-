from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
app = FastAPI()
import database_helper
import other_functions
global inprogess_order
inprogress_order = {}

@app.post("/webhook")
async def handle_request(request:Request):
    payload = await request.json()
    intent = payload["queryResult"]["intent"]["displayName"]
    parameters = payload["queryResult"]["parameters"]
    output_contexts = payload["queryResult"]["outputContexts"]
    session_id = other_functions.extract_session_id(output_contexts)

    if intent == "order.track.id":
        return track_order(parameters)
    elif intent == "order.add-ongoing-order":
        return add_order(parameters, session_id, inprogress_order)
    elif intent == "order.remove":
        return remove_order(parameters,session_id,inprogress_order)
    elif intent == "order.complete":
        return complete_order(session_id,inprogress_order)
def track_order(parameters:dict):
    order_id = int(parameters["order_id"])
    order_status = database_helper.get_status_order(order_id)
    if order_status:
        return JSONResponse(content={"fulfillmentText": "The order status for order id {} is {}".format(order_id,order_status)})
    else:
        return JSONResponse(content={"fulfillmentText": "No Order found with ID {}".format(order_id)})

def add_order(parameters:dict,session_id:str,inprogress_order:dict):
    quantity = parameters["number"]
    food_item = parameters["food-item"]
    if len(quantity)!= len(food_item):
        return JSONResponse(content={"fulfillmentText":"Please Provide Correct quantities along with food item"})

    else:
        food_order = dict(zip(food_item,quantity))
        if session_id in inprogress_order:
            cur_food_order = inprogress_order[session_id]
            cur_food_order.update(food_order)
            inprogress_order[session_id] = cur_food_order
        else:
            inprogress_order[session_id] = food_order
        print(session_id,":",inprogress_order[session_id])
        food_str = ""
        for i,j in inprogress_order[session_id].items():
            food_str += str(int(j)) + " " + i + ","
        return JSONResponse(content={"fulfillmentText":"Order added successfully, So far your order is {} ,Do you need anything else?".format(food_str)})
def remove_order(parameters:dict,session_id:str,inprogress_order:dict):
    if session_id not in inprogress_order:
        return JSONResponse(content={ "fulfillmentText":"You have not order anything else.Please order something from the menu " })
    else:
        food_item = parameters["food-item"]
        cur_food_order = inprogress_order[session_id]
        for i in food_item:
            if i in cur_food_order:
                del cur_food_order[i]
            else:
                return JSONResponse(content={"fulfillmentText": "{} is not in your order".format(i)})
        inprogress_order[session_id] = cur_food_order
        food_str = ""
        for i, j in inprogress_order[session_id].items():
            food_str += str(int(j)) + " " + i + ","
        remove_food_str = ""
        for i in food_item:
            remove_food_str+=i
        return JSONResponse(content={"fulfillmentText":"{} removed from the order successfully.Now your order is {}.Do you need any other favor?".format(remove_food_str,food_str)})
def complete_order(session_id,inprogress_order):
    if session_id not in inprogress_order:
        return JSONResponse(content={"fulfillmentText":"Sorry can't place the order.Can you please place a new order?"})
    else:
        food_order = inprogress_order[session_id]
        order_id = database_helper.update_to_database(food_order)
        if order_id == -1:
            return JSONResponse(content={"fulfillmentText": "Sorry can't place the order due to backend error.Can you please place a new order?"})
        else:
            order_total = database_helper.get_total_order_price(order_id)
            database_helper.update_order_id(order_id)
            del inprogress_order[session_id]
            return JSONResponse(content={"fulfillmentText": "Awesome Your order is placed. Here is your Order ID # {}.Your Total Price for the Order is Rs.{}".format(order_id,order_total)})


























