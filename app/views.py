import os
from app import app
from app import db
from app.forms import SignUpForm, LoginForm, RecipeForm, RecipesForm, IngredientForm
from flask import render_template, request, redirect, url_for, jsonify, Response
import validators
from sqlalchemy import text
from sqlalchemy import create_engine
from werkzeug import secure_filename
import json
import time
import random

engine = create_engine('mysql://project:project@localhost:3306/epicmealplan')

ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'gif','png'])

@app.route('/')
def launch():
    return render_template("index.html")

@app.route('/home')
def home():
    return render_template("home.html")


@app.route('/signup',methods=["GET","POST"])
def register():
    form = SignUpForm(request.form)
    if request.method=="POST":
        uploadedfile = request.files['uploadedfile']
        if uploadedfile and allowed_file(uploadedfile.filename):
            uploadedfilename = form.email.data + '_' + secure_filename(uploadedfile.filename)
            filepath = os.path.join(os.getcwd() + '/app/static/useruploads/',uploadedfilename)
            uploadedfile.save(filepath)
        connection = engine.raw_connection()
        cursor = connection.cursor()
        cursor.callproc("RegisterUser", [str(form.firstname.data),str(form.lastname.data),str(form.address.data),str(form.email.data),str(form.password.data),str(form.phonenumber.data),str(uploadedfilename),str(form.dob.data)])
        cursor.close()
        connection.commit()
        return redirect(url_for('home'))
    else:
        return render_template("signup.html",form=form)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method=="POST":
        connection = engine.raw_connection()
        cursor = connection.cursor()
        cursor.callproc("LoginUser", [str(form.email.data),str(form.password.data)])
        cursor.close()
        connection.commit()
        return redirect(url_for('home'))
    else:
        return render_template("login.html",form=form)

@app.route('/generate_mealplan',methods=["GET"])
def newMealPlan():
    firstconnection = engine.connect()
    result = firstconnection.execute("select mealplanday.mealplanday_id from mealplanday")
    mealplandays = []
    for row in result:
        mealplandays.append(row['mealplanday_id'])
    firstconnection.close()
    # connection = engine.raw_connection()
    # cursor = connection.cursor()
    # # cursor.callproc("GetMealPlanForWeek", [random.choice(mealplandays)])
    # cursor.close()
    # connection.commit()
    return render_template("mealplan.html")

@app.route('/create_recipe',methods=["GET","POST"])
def newRecipe():
    form = RecipeForm(request.form)
    if request.method=="POST":
        uploadedfile = request.files['uploadedfile']
        if uploadedfile and allowed_file(uploadedfile.filename):
            uploadedfilename = form.name.data + '_' + str(time.strftime("%Y-%m-%d-%H-%M-%S")) + "_" + secure_filename(uploadedfile.filename)
            filepath = os.path.join(os.getcwd() + '/app/static/recipeuploads/',uploadedfilename)
            uploadedfile.save(filepath)
        connection = engine.raw_connection()
        cursor = connection.cursor()
        cursor.callproc("AddRecipe", [str(form.name.data),str(form.recipetype.data),str(uploadedfilename),str(form.serving.data),str(form.preptime.data),str(time.strftime("%Y/%m/%d")),str(form.caloriecount.data)])
        result = cursor.fetchall()
        cursor.close()
        connection.commit()
        firstconnection = engine.connect()
        result = firstconnection.execute("SELECT MAX(recipe_id) FROM recipe LIMIT 1;")
        for row in result:
            iidd = row['MAX(recipe_id)']
        print iidd
        firstconnection.close()
        return redirect(url_for('recipes'))
    else:
        return render_template("recipe.html",form=form)

# @app.route('/users',methods=["GET"])
# def users():
#     connection = engine.connect()
#     result = connection.execute("select * from user")
#     users = []
#     for row in result:
#         users.append(row)
#     connection.close()
#     return render_template("users.html",users=users)

@app.route('/getmealplanrecipes/<mtype>', methods=["GET","POST"])
def getmealplanrecipes(mtype):
    form = RecipesForm(request.form)
    if request.method=="GET":
        connection = engine.raw_connection()
        cursor = connection.cursor()

        cursor.callproc("GetWeekRecipesByType",[str(mtype)])
        result = cursor.fetchall()
        print result

        cursor.close()
        connection.commit()
        recipes = []
        for row in result:
            recipes.append(row)
        print recipes
        return jsonify({"recipes":recipes})


@app.route('/recipes', methods=["GET","POST"])
def recipes():
    form = RecipesForm(request.form)
    if request.method=="POST":
        connection = engine.raw_connection()
        cursor = connection.cursor()
        cursor.callproc("GetRecipesLike",[str(form.name.data)])
        result = cursor.fetchall()
        print result

        cursor.close()
        connection.commit()
        recipes = []
        for row in result:
            recipes.append(row)
        print recipes
    # connection = engine.connect()
    # result = connection.execute("select * from recipe order by recipe_creationdate desc")
    # recipes = []
    # for row in result:
    #     recipes.append(row)
    # connection.close()
        return render_template("recipes.html",form=form,recipes=recipes)
    else:
        return render_template("recipes.html",form=form)

@app.route('/filteredrecipes',methods=["GET","POST"])
def filteredrecipes():
    form = RecipesForm(request.form)
    connection = engine.raw_connection()
    cursor = connection.cursor()
    cursor.callproc("GetUnderSpecficCalorieCount",[str(request.form['calories'])])
    result = cursor.fetchall()
    cursor.close()
    connection.commit()
    recipes = []
    for row in result:
        recipes.append(row)
    print recipes
    return render_template("recipes.html",form=form,recipes=recipes)

@app.route('/recipedetails/<recipeid>',methods=["GET"])
def recipedetails(recipeid):
    connection = engine.raw_connection()
    cursor = connection.cursor()
    cursor.callproc("GetRecipeById",[str(recipeid)])
    result = cursor.fetchall()
    cursor.close()
    cursor = connection.cursor()
    cursor.callproc("recipeinstruction",[str(recipeid)])
    result_instr = cursor.fetchall()
    cursor.close()
    connection.commit()
    recipes = []
    instr = []
    for row in result:
        recipes.append(row)
    for row in result_instr:
        instr.append(row)
    return render_template("recipedetails.html",recipes=recipes, instrs=instr )

@app.route('/seecredenials/<recipeid>',methods=["GET"])
def seecredentials(recipeid):
    connection = engine.raw_connection()
    cursor = connection.cursor()
    cursor.callproc("GetIngrMeasurFromRecipe",[str(recipeid)])
    result = cursor.fetchall()
    cursor.close()
    connection.commit()
    results = []
    for row in result:
        results.append(row['ingrient_name'] + row['ingr'])

@app.route('/measurements',methods=["GET"])
def measurements():
    connection = engine.connect()
    result = connection.execute("select measurement.measurement_name from measurement")
    measurements = []
    for row in result:
        measurements.append(row['measurement_name'])
    connection.close()
    return jsonify({"measurements":measurements})

@app.route('/ingredients',methods=["GET"])
def ingredients():
    connection = engine.connect()
    result = connection.execute("select * from ingredient")
    ingredients = []
    for row in result:
        if row['ingredient_id'] != 96:
            ingredients.append(row['ingredient_name'])
    connection.close()
    return jsonify({"ingredients":ingredients})

@app.route('/restrictions',methods=["GET"])
def restrictions():
    connection = engine.connect()
    result = connection.execute("select userrestriction.restriction_name from userrestriction")
    restrictions = []
    for row in result:
        restrictions.append(row['restriction_name'])
    connection.close()
    return restrictions

@app.route('/kitchen',methods=[""])
def kitchen():
    return render_template("")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port="8888")
