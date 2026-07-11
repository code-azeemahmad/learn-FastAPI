from fastapi import FastAPI
from routers import users, products

app =FastAPI()

app.include_router(users.router)
app.include_router(products.router)






'''app.include_router(users.router)
Take all the routes from users.py and 
add them to this application'''
