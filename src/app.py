"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, send_from_directory
from flask_migrate import Migrate
from flask_swagger import swagger
from api.utils import APIException, generate_sitemap
from api.models import db, User, Customer, Address, Provider, Products, CategoryProduct, Sales, DetailSales,ProductEntry,States
from api.routes import api
from api.admin import setup_admin
from api.commands import setup_commands
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from datetime import datetime
from sqlalchemy.orm import relationship, join, sessionmaker
from sqlalchemy import create_engine, engine, join, and_, or_
import json
from sqlalchemy.sql import func
from werkzeug.security import check_password_hash



# from models import Person

ENV = "development" if os.getenv("FLASK_DEBUG") == "1" else "production"
static_file_dir = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), '../public/')
app = Flask(__name__)
app.url_map.strict_slashes = False

# database configuration
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db, compare_type=True)
db.init_app(app)

# Initialize JWT
jwt = JWTManager(app)

# Add the admin
setup_admin(app)

# Add the admin
setup_commands(app)

# Add all endpoints form the API with a "api" prefix
app.register_blueprint(api, url_prefix='/api')

# Handle/serialize errors like a JSON object

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# Generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    if ENV == "development":
        return generate_sitemap(app)
    return send_from_directory(static_file_dir, 'index.html')

# Function to approve a user and assign a role
def approveUser(userId, role):
    user = User.query.get(userId)
    if user:
        user.profile = role
        user.is_active = True
        db.session.commit()
        return {"message": "User approved successfully"}
    else:
        return {"message": "User not found"}

# Function to get all pending users (users with profile 0)
def getPendingUsers():
    users = User.query.filter_by(profile=0).all()
    return [user.serialize() for user in users]

# Function to handle user signup and return a message
def Signup(datau):
    print("datau recibida de register-user", datau)
    newUser = User()
    newUser.email = datau.get("email")
    newUser.name = datau.get("name")
    newUser.lastName = datau.get("lastname")
    newUser.password = datau.get("password")
    newUser.is_active = False  
    newUser.profile = 0  
    print("GET GET  ",datau.get("email"),datau.get("name"), datau.get("lastname"),datau.get("password") )
    print(newUser.email,newUser.name, newUser.lastName,newUser.password )
    if newUser.email == "" or newUser.password == "":
        response_body = {"message": "email and password are required"}
        return response_body
    else:
        user_result = db.session.execute(db.select(User).filter_by(email=newUser.email)).one_or_none()
        if user_result is not None and user_result[0].email == newUser.email:
            response_body = {"message": "user already exists"}
            return response_body
        else:
            db.session.add(newUser)
            db.session.commit()
             
            response_body = {"message": "User created successfully"}
            return response_body
        
def register_user(data):
    user_response = Signup(data)
    print("user_responseuser_response", user_response)
    if user_response.get("message") == "User created successfully":

        user_result = db.session.execute(db.select(User).filter_by(email=data.get("email"))).one_or_none()
               
        customer_data = {
            "nit": data.get("nit"),
            "phone": data.get("phone"),
            "idUser": user_response.get("id"),
            "address": data.get("address"),
            "city": data.get("city"),
            "country": data.get("country"),
            "idUser" :  user_result[0].id
        }

        customer_response = addCustomer(customer_data)
        return customer_response
    else:
        return user_response


# Function to handle user login and return token, id, and email
def Login(data):
    newUser = User()
    print("Newuser dentro de Login",data.get("email"), data.get("password"))
    newUser.email = data.get("email")
    newUser.password = data.get("password")

    if newUser.email == "" or newUser.password == "":
        response_body = {"Error": "email and password are required"}
        return response_body
    else:
        user_result = db.session.execute(db.select(User).filter_by(email=data.get("email"))).one_or_none()
        if user_result is None:
            response_body = {"Error": "user doesn't exist please create user first"}
            return response_body
        else:
            user_result = user_result[0]
            print("Newuser PASSWORD",user_result.password, newUser.password, "ID es: ", user_result.id)
            passwd_is_ok = user_result.password == newUser.password
            if not passwd_is_ok:
                response_body = {"Error": "Password incorrect"}
                return response_body
            token = create_access_token(identity=user_result.id)
            response_body = {
                "token": token,
                "id": user_result.id,
                "email": user_result.email,
                "name": user_result.name,
                "lastName": user_result.lastName, 
                "isActive": user_result.is_active,
                "profile": user_result.profile
            }
            return response_body
        
def get_user_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user:
        return user.serialize()
    else:
        return {"message": "User not found"}

#Funciones para Customers

def addCustomer(data):

    print("VAO¿LORES DE DATA", data)
    newCustomer = Customer()
    newAddr = Address()
    newCustomer.nit = data.get("nit")
    newCustomer.phone = data.get("phone")
    newCustomer.idUser = data.get("idUser")

    newAddr.nit = data.get("nit")
    newAddr.address = data.get("address")
    newAddr.city = data.get("city")
    newAddr.country = data.get("country")
    
    if newCustomer.nit == "" :
        response_body = {"message": "Nit required"}
        return response_body
    else:
        user_result = db.session.execute(db.select(Customer).filter_by(nit=newCustomer.nit)).one_or_none()
        if user_result != None and user_result[0].nit == newCustomer.nit:
            response_body = {"message": "Customer already exists"}
            return response_body
        else:
            db.session.add(newCustomer)
            db.session.commit()
            db.session.add(newAddr)
            db.session.commit()
            response_body = {"message": "Customer created successfully"}
            return response_body

def delCustomer(data):
    delnit = db.session.execute(db.select(Customer).filter_by(nit=data)).one_or_none()
    
    if delnit != None:
        delnit = Customer.query.filter_by(nit=data).one()
        db.session.delete(delnit)
        db.session.commit()
        response_body = {"message": "Customer deleted successfully"}
        return response_body
    else:
        response_body = {"message": "Customer not found", "nit": data}
        return response_body

def getCustomer():
    customerList=[]
    query = db.select(Customer.nit,Customer.phone,Customer.date, Address.address,Address.country,Address.city).join(Address, Customer.nit == Address.nit)
    result = db.session.execute(query)

    for customer in result.fetchall():
        customerList.append(dict(customer._mapping))

    return tuple(customerList)


def getOneCustomer(data):
    customerList=[]
    query = db.select(Customer.nit,Customer.phone,Customer.date, Address.address,Address.country,Address.city).join(Address, Customer.nit == Address.nit).filter_by(nit=data)
    result = db.session.execute(query)

    for customer in result.fetchall():
        print(dict(customer._mapping))
        customerList.append(dict(customer._mapping))

    return tuple(customerList) if customerList else None

def getOneCustomerID(data):
    customerList=[]
    print("VALOR de DATA", data, type(data))
    query = db.select(User.id, User.name, User.lastName,Customer.nit,Customer.phone,Customer.date, Address.address,Address.country,Address.city)\
         .join(Customer, Customer.idUser == User.id)\
         .join(Address, Customer.nit == Address.nit)\
         .filter(User.id == data)
    result = db.session.execute(query)
    for customer in result.fetchall():
        print("DENTRO DE APP GETONE",dict(customer._mapping))
        customerList.append(dict(customer._mapping))

    return tuple(customerList) if customerList else None
# Funciones para Providers

def addProvider(data):
    newProvider = Provider()
    newAddr = Address()
    newProvider.nit = data.get("nit")
    newProvider.phone = data.get("phone")
    #newProvider.date = data.get("date")
    newProvider.idUser = data.get("idUser")
    #newProvider.addrNit = data.get("nit")

    # newAddr.id = data.get("id")
    newAddr.nit = data.get("nit")
    newAddr.address = data.get("address")
    newAddr.city = data.get("city")
    newAddr.country = data.get("country")
    
    if newProvider.nit == "" :
        response_body = {"message": "Nit required"}
        return response_body
    else:
        user_result = db.session.execute(db.select(Customer).filter_by(nit=newProvider.nit)).one_or_none()
        if user_result != None and user_result[0].nit == newProvider.nit:
            response_body = {"message": "Customer already exists"}
            return response_body
        else:
            db.session.add(newProvider)
            db.session.commit()
            db.session.add(newAddr)
            db.session.commit()
            response_body = {"message": "Customer created successfully"}
            return response_body

# Functions for Products

def addProducts(data):
    newProducts = Products()
    newEntry = ProductEntry()
    category_name = data.get("category").upper()
    print("category_name :*****",category_name)
    Category_result = db.session.execute(db.select(CategoryProduct).filter_by(category=category_name)).one_or_none()
    
    if not Category_result:
        response_body = {"message": "Category doesn't exist"}
        return response_body
    
    newProducts.id_prod = data.get("id_prod")
    newProducts.prodname = data.get("prodname").upper()
    newProducts.brand = data.get("brand").upper()
    newProducts.salesPrice = data.get("salesPrice")
    newProducts.stock = data.get("amount")
    newProducts.idCatProd = Category_result[0].idCatProd

    # campos en la tabla ProductEntry para tener el detalle de las entradas
    newEntry.cost_price = data.get("costPrice")
    newEntry.amount = data.get("amount")
    newEntry.id_prod = data.get("id_prod")
    newEntry.amount_Prev = 0  # se asigna en "cero" porque el producto es nuevo, no exite cantidad anterior
    newEntry.salesPrice_prev = 0 # se asigna en "cero" porque el producto es nuevo, no exite precio de venta anterior
    # Verificar si el producto ya existe
    Product_result = db.session.execute(db.select(Products).filter_by(id_prod=newProducts.id_prod)).one_or_none()
    if Product_result is not None:
        response_body = {"message": "PRODUCT already exists"}
        return response_body

    # Guardar el nuevo producto
    db.session.add(newProducts)
    db.session.commit()
    db.session.add(newEntry)
    db.session.commit()

    response_body = {"message": "PRODUCT created successfully"}
    return response_body

def addProdEntry(data):
    print("VALORES DE DATA EN productsentry ****", data)

    newEntry = ProductEntry()
    newEntry.cost_price = data.get("costPrice")
    newEntry.amount = data.get("amount")
    newEntry.id_prod = data.get("id_prod")
    # Guardar el nuevo producto
    product = db.session.execute(db.select(Products).filter_by(id_prod=data.get("id_prod"))).one_or_none()
    product = product[0]
    #entry = db.session.execute(db.select(ProductEntry).filter_by(id_prod=data.get("id_prod"))).order_by(Products.id_prod.desc()).first()

    entry = db.session.execute(db.select(ProductEntry).order_by(ProductEntry.date.desc()).filter_by(id_prod=data.get("id_prod"))).first()

     # campos en la tabla ProductEntry para tener el detalle de las entradas
    if entry == None:
        newEntry.amount_Prev = 0
    else:
        newEntry.amount_Prev = entry[0].amount
    
    newEntry.salesPrice_prev = product.salesPrice

    product.stock = product.stock + int(data.get("amount"))
    product.salesPrice = int(data.get("salesPrice"))
    db.session.add(newEntry)
    db.session.commit()

    response_body = {"message": "PRODUCT created successfully"}
    return response_body

 

def getProducts():
    productsList=[]
    prueba = []
    
    query = db.select(Products.id_prod,Products.prodname,Products.brand, Products.salesPrice, Products.stock, Products.Catproducts, CategoryProduct.category,CategoryProduct.description,ProductEntry.cost_price,ProductEntry.amount )\
        .join(CategoryProduct, Products.idCatProd == CategoryProduct.idCatProd)\
        .join(ProductEntry, Products.id_prod == ProductEntry.id_prod).order_by(ProductEntry.id.desc())
    
    result = db.session.execute(query)

    for products in result.fetchall():
        if products._mapping.id_prod not in prueba:
            prueba.append(products._mapping.id_prod)
            productsList.append(dict(products._mapping))
    return tuple(productsList)

def getOneProducts(data):
    productsList=[]
    query = db.select(Products.id_prod,Products.prodname,Products.brand, Products.salesPrice, Products.stock, Products.Catproducts, CategoryProduct.category,CategoryProduct.description).filter_by(id_prod=data).join(CategoryProduct, Products.idCatProd == CategoryProduct.idCatProd)
    result = db.session.execute(query)

    for products in result.fetchall():
        # print(products._mapping, type())
        productsList.append(dict(products._mapping))

    return tuple(productsList)

def delProducts(data):
    delIdProd = db.session.execute(db.select(Products).filter_by(id_prod=data)).one_or_none()
    
    if delIdProd != None:
        delIdProd = Products.query.filter_by(id_prod=data).one()
        db.session.delete(delIdProd)
        db.session.commit()
        response_body = {"message": "Products deleted successfully"}
        return response_body
    else:
        response_body = {"message": "Products not found", "nit": data}
        return response_body



def updateProduct(id, data):
    product = db.session.execute(db.select(Products).filter_by(id_prod=id)).one_or_none()

    if product is None:
        return {"message": "Product not found"}

    product = product[0]  # Accede al objeto Products

    product.prodname = data.get("prodname").upper()
    product.brand = data.get("brand").upper()
    product.salesPrice = data.get("salesPrice")
    # product.stock = data.get("stock")
    
    # No permitir cambiar el id_prod
    # product.id_prod = data.get("id_prod")

    db.session.commit()

    return {"message": "Product updated successfully"}

def delProducts(data):
    delIdProd = db.session.execute(db.select(Products).filter_by(id_prod=data)).one_or_none()
    if delIdProd != None:
        delIdProd = Products.query.filter_by(id_prod=data).one()
        db.session.delete(delIdProd)
        db.session.commit()
        response_body = {"message": "Products deleted successfully"}
        return response_body
    else:
        response_body = {"message": "Products not found", "nit": data}
        return response_body
    
def getNextProdId():
     obj = db.session.query(Products).order_by(Products.id_prod.desc()).first()
     nextId = obj.id_prod + 1 if obj else 1
    #  print("Nex ID: ",obj, type(obj.idSales), nextId+1) 
     response_body = {"ID": nextId}
     return response_body

# Functions for CategoryProduct

def addCategoryProduct(data):
    newCatProd = CategoryProduct()
   
    newCatProd.category = data.get("category").upper()
    newCatProd.description = data.get("description", "").upper()

    if not newCatProd.category:
        response_body = {"message": "Category is necessary"}
        return response_body
    else:
        Category_result = db.session.execute(db.select(CategoryProduct).filter_by(category=newCatProd.category)).one_or_none()
        if Category_result:
            response_body = {"message": "Category already exists"}
            return response_body
        else:
            db.session.add(newCatProd)
            db.session.commit()
            response_body = {"message": "Category created successfully"}
            return response_body



def getCategories():
    categoriesList = []
    query = db.select(CategoryProduct).order_by(CategoryProduct.category)
    result = db.session.execute(query)

    for category in result.fetchall():
        categoriesList.append(category[0].serialize())

    return categoriesList


# Functions for Sales

def addSales(data):
    print("DATA dentro de ******* Sales! ", data)
    sales_list = data.get("salesList", [])
    
    for sale_data in sales_list:
        newSales = Sales()
    
        # Sales
        newSales.idSales  = sale_data.get("idsales")
        newSales.iduser  = sale_data.get("iduser")
        newSales.totalPrice  = int(sale_data.get("unitPrice")) * int(sale_data.get("amount"))
        newSales.nit  = sale_data.get("nit")
        
        print("DATA dentro de ******* Sales! ", newSales.idSales, '\n', newSales.iduser, '\n', newSales.totalPrice, '\n', newSales.nit )
        sales_exists = db.session.execute(db.select(Sales).filter_by(idSales=newSales.idSales)).one_or_none()
        if sales_exists == None:
            db.session.add(newSales)
            db.session.commit()
            response_body = addDetailSales(sale_data)
            if response_body.get("message") != "Sales created successfully":
                return response_body
        else:
            response_body = {"message": "Sales receipts already exists"}
            response_body = addDetailSales(sale_data)
            if response_body.get("message") != "Sales created successfully":
                return response_body
    
    return {"message": "Sales created successfully"}

# Function to validate product existence and stock availability before processing a sale
def validate_product_and_stock(data):
    stock_available = db.session.execute(db.select(Products.stock).filter((Products.id_prod == data.get("id_prod")))).one_or_none()
    if stock_available[0] < int(data.get("amount")):
        return False, {"message": "Stock not available", "Stock": stock_available[0]}
    return True, {}

def addDetailSales(data):
    newDtSales = DetailSales()
    print("DATA dentro de addDetailSales! ", data)
    
    valid, error_response = validate_product_and_stock(data)
    if not valid:
        return error_response

    # DetailSales
    newDtSales.amount  = data.get("amount")
    newDtSales.unitPrice =  data.get("unitPrice")
    newDtSales.idSales = data.get("idsales")
    newDtSales.id_prod  = data.get("id_prod")

    db.session.add(newDtSales)
    
    # Actualizar el stock
    stock_available = db.session.execute(db.select(Products.stock).filter((Products.id_prod == newDtSales.id_prod))).one_or_none()
    newstock = stock_available[0] - int(newDtSales.amount)
    print("**** DETAILSALES :",newstock, '\n', stock_available[0], '\n', int(newDtSales.amount),'\n','\n' )
    db.session.query(Products).filter(Products.id_prod == newDtSales.id_prod).update({Products.stock : newstock})
    
    db.session.commit()
    return {"message": "Sales created successfully"}


def getNextId():
     obj = db.session.query(Sales).order_by(Sales.idSales.desc()).first()
     print(obj)
     if obj != None: 
         nextId = obj.idSales + 1
     else: 
         nextId = 1
    
     response_body = {"ID": nextId}
     return response_body

def getSales():
    customerList=[]
    # query = db.select(Sales.iduser, Sales.nit, DetailSales.amount, DetailSales.unitPrice, DetailSales.idSales, DetailSales.id_prod).join(Sales, Sales.idSales == DetailSales.idSales).filter_by(idSales=data)
    query = db.select(User.name, User.lastName, Products.prodname, Sales.iduser, Sales.nit, Sales.date, DetailSales.amount, DetailSales.unitPrice, DetailSales.idSales, DetailSales.id_prod).join(Sales, Sales.idSales == DetailSales.idSales)\
        .join(User, User.id == Sales.iduser)\
        .join(Products, Products.id_prod == DetailSales.id_prod)
    result = db.session.execute(query)

    for customer in result.fetchall():
        print(dict(customer._mapping))
        customerList.append(dict(customer._mapping))

    return tuple(customerList)

def getOneSales(data):
    customerList=[]
    # query = db.select(Sales.iduser, Sales.nit, DetailSales.amount, DetailSales.unitPrice, DetailSales.idSales, DetailSales.id_prod).join(Sales, Sales.idSales == DetailSales.idSales).filter_by(idSales=data)
    query = db.select(User.name, User.lastName, Products.prodname, Sales.iduser, Sales.nit, DetailSales.amount, DetailSales.unitPrice, DetailSales.idSales, DetailSales.id_prod).join(Sales, Sales.idSales == DetailSales.idSales)\
        .filter_by(idSales=data)\
        .join(User, User.id == Sales.iduser)\
        .join(Products, Products.id_prod == DetailSales.id_prod)
    result = db.session.execute(query)

    for customer in result.fetchall():
        print(dict(customer._mapping))
        customerList.append(dict(customer._mapping))

    return tuple(customerList) if customerList else None

def delSales(data):
    delSales = db.session.execute(db.select(Sales).filter_by(idSales=data)).one_or_none()
    
    if delSales != None:
        delSales = Sales.query.filter_by(idSales=data).one()
        db.session.delete(delSales)
        db.session.commit()
        response_body = {"message": "Sale deleted successfully"}
        return response_body
    else:
        response_body = {"message": "Sale not found", "ID": data}
        return response_body


def addStates(statesList):
    # valid, error_response = validate_product_and_stock(statesList)
    # if not valid:
    #     return error_response

    # DetailSales
    db.session.execute('''TRUNCATE TABLE States''')
    db.session.commit()
    count = 1
    listStates = []

    for states1 in statesList:
        newStates = States(id= count,state_name=states1.get("state_name"))
        listStates.append(newStates)
        count = count + 1

    db.session.add_all(listStates)
    db.session.commit()
    return {"message": "States created successfully"}

def getStates():
    print("ENTREEEEE!!! a getStates en APP.py")
    stateList=[]
    # query = db.select(States)
    result = States.query.all()

    for state in result:
        print(state.state_name)
        stateList.append(state.state_name)

    return tuple(stateList)

def getAmountSold():
    amountSoldList=[]
    query = db.select(Products.prodname, func.sum(DetailSales.amount).label("Amounts Sold"), func.avg(Sales.totalPrice).label("Avg Selling Price"),DetailSales.id_prod)\
        .join(Sales, Sales.idSales == DetailSales.idSales)\
        .join(Products, Products.id_prod == DetailSales.id_prod)\
        .group_by(Products.prodname, DetailSales.id_prod)\
        .order_by(func.sum(DetailSales.amount).desc())
    
    result = db.session.execute(query)

    for sales in result.fetchall():
        print(dict(sales._mapping))
        amountSoldList.append(dict(sales._mapping))

    return tuple(amountSoldList) if amountSoldList else None

def getProductXClient(data):
    amountSoldList=[]
    query = db.select(Products.prodname, Sales.date, DetailSales.amount, Sales.totalPrice)\
        .join(Sales, Sales.idSales == DetailSales.idSales)\
        .filter_by(nit=data)\
        .join(Products, Products.id_prod == DetailSales.id_prod)\
        .group_by(Products.prodname, DetailSales.id_prod, Sales.date, DetailSales.amount, Sales.totalPrice)\
        .order_by(Sales.date.desc())
    
    result = db.session.execute(query)

    for sales in result.fetchall():
        print(dict(sales._mapping))
        amountSoldList.append(dict(sales._mapping))

    return tuple(amountSoldList) if amountSoldList else None

######## 

@app.route('/<path:path>', methods=['GET'])
def serve_any_other_file(path):
    if not os.path.isfile(os.path.join(static_file_dir, path)):
        path = 'index.html'
    response = send_from_directory(static_file_dir, path)
    response.cache_control.max_age = 0  # avoid cache memory
    return response






# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=True)


