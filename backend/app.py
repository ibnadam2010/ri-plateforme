from flask import Flask, request, jsonify, session, make_response, send_file
from flask_restx import Api, Resource, fields
from flask_swagger_ui import get_swaggerui_blueprint
from config import DevConfig
from models.model import User
from models.exts import db
from flask_marshmallow import Marshmallow
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask_cors import CORS, cross_origin
import os
import json
import pdftotext
from docx import Document #use by FilesDataExtraction
import glob #use by FilesDataExtraction
from tqdm import tqdm
import re #use by RemoveSpecialCharacters FilesDataExtraction
import numpy as np
from haystack.nodes import PreProcessor
import SmartResearchModel


"""
API SCRIPT DECLARATIONS
"""
app = Flask(__name__)
app.app_context().push()
app.config.from_object(DevConfig)
CORS(app)
CORS(app, origins="http://localhost:3000")
#file current path
db.init_app(app)
ma = Marshmallow(app)
JWTManager(app)

"""
API SCRIPT SWAGGER
"""
SWAGGER_URL='/swagger'
API_URL='/static/swagger.json'
SWAGGER_BLUEPRINT=get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name':'Recherche Intelligente'})
app.register_blueprint(SWAGGER_BLUEPRINT, url_prefix=SWAGGER_URL)
app.config.from_object(DevConfig)

class UserSchema(ma.Schema):
     class Meta:
          fields =('id', 'username', 'email', 'role', 'password')

user_schema = UserSchema(many=True)

cur_path = os.getcwd()

"""
API SCRIPT INDEX ROUTE
"""
@app.get("/administrator")
def admin():
    return {"msg": "hello world"}

"""
API SCRIPT USER ROUTE
"""
@app.post("/adduser")
@cross_origin()
@jwt_required
def add_user():
    username = request.json['username']
    email = request.json['email']
    role = request.json['role']
    if role.strip() == "":
         role = "user"
    password = request.json['password']
    db_user = User.query.filter_by(username=username).first()
    if db_user is not None:
         return {"response":"failed","detail":f"username {username} already exists"},409
    else:

        if email.strip() !="" and username.strip() !="" and password.strip() !="" and role.strip() !="":
          password = generate_password_hash(request.json['password'])
          new_user = User(username=username, email=email, role=role, password=password)
          new_user.save()
          return {"response":"success", "detail":f"user {new_user.username} successful created"},201
        else:
             return {"response":"failed", "detail":"some inputs are blank"},400

@app.get("/users")
@cross_origin()
@jwt_required()
def users_list():
    users =[]
    all_users = User.query.all()
    for user in all_users:
         data = {
              "id":user.id,
              "username":user.username,
              "email":user.email,
              "role":user.role,
              "password":user.password
         }
         users.append(data)
    return users

@app.get("/user/<iduser>")
@cross_origin()
@jwt_required()
def user_detail(iduser):
    user = User.query.filter_by(id=iduser).first()
    if user is not None:
         user_detail = {
              "id":user.id,
              "username":user.username,
              "email":user.email,
              "password":user.password
         }
    return user_detail,200


@app.put("/user/update/<iduser>")
@cross_origin()
@jwt_required()
def user_update(iduser):
        user_to_update = User.query.get_or_404(iduser)
        data = request.get_json()
        if data.get("username").strip() =="" or data.get("email").strip() =="":
             return {"response":"failed", "detail":"some inputs are blank"},400
        else:     
          if data.get("password").strip() =="": 
               user_to_update.update(data.get("username"), data.get("email"), data.get("role"), user_to_update.password)
               return {"response":"success", "detail":"user successfuly updated"},200
          else :
               user_to_update.update(data.get("username"), data.get("email"), data.get("role"), generate_password_hash(data.get("password")))
          return {"response":"success", "detail":"user successfuly updated"},200
   

@app.delete("/user/delete/<iduser>")
@cross_origin()
@jwt_required()
def user_delete(iduser):
        user_to_delete = User.query.get_or_404(iduser)
        user_to_delete.delete()
        return f"{user_to_delete}"


@app.post("/login")
@cross_origin()
def login():
     username = request.json['username']
     password = request.json['password']
     db_user = User.query.filter_by(username=username).first()
     
     global p 
     if db_user is not None and check_password_hash(db_user.password,password):
          access_token = create_access_token(identity=db_user.username)
          refresh_token = create_refresh_token(identity=db_user.username)
          p = get_pipeline()
          return {"response":"success", "access_token":access_token, "refresh_token":refresh_token, "role":db_user.role}


@app.post('/logout')
@cross_origin()
@jwt_required()
def logout():
	session.pop('username', None)
	return jsonify({"response":"success", 'detail' : 'You have been successfully logged out'})


@app.post("/refresh")
@cross_origin()
@jwt_required(refresh=True)
def token_refresh():   
     current_user = get_jwt_identity()
     new_access_token = create_access_token(identity=current_user)
     return make_response(jsonify({"access_token": new_access_token}), 200)

def get_pipeline():
     pipeline = SmartResearchModel.init_smart_research(True)
     return pipeline

@app.route('/getdocument/<path:filepath>', methods=['GET'])
@cross_origin()
#@jwt_required()
def download(filepath):
    filepath = '/'+filepath
    return send_file(filepath, as_attachment=True)

@app.post("/research")
@cross_origin()
@jwt_required()
def question_answer():
     requete = request.json['requete']
     output = SmartResearchModel.process_query(requete,p)
     #Si question de compréhension 
     if "QAReader" in list(output['_debug'].keys()):
          #output_retriever = output['_debug']['RetrieverBM25']['output']
          output_reader_retriever = output['_debug']['QAReader']['output']
          output_GPT = output['_debug']['GPTanswer']['output']['answers']

          return_back_end = {"output_gen":output_GPT, "output_answers_paragraphs":output_reader_retriever}#, "output_retriever":output_retriever}
     #Si requete
     else :
          output_doc = []
          for doc in output["documents"]:
              output_doc.append(doc.meta["document_absolute_path"])  

          return_back_end = {"output_docs":output_doc}

     return return_back_end


@app.shell_context_processor
def make_shell_context():
     return {"db":db, "User":User}

if __name__ == '__main__':
         app.run(debug=True, port=5003)