from flask_wtf import Form
from wtforms import TextField, PasswordField, BooleanField, SelectField, FileField, SubmitField, validators
from wtforms.validators import Required

class SignUpForm(Form):
    uploadedfile = FileField("Upload A Picture")
    firstname = TextField("First Name",[validators.Required()])
    lastname = TextField("Last Name",[validators.Required()])
    address = TextField("Address",[validators.Required()])
    email = TextField("Email",[validators.Required()])
    password = PasswordField("Password",[validators.Required()])
    phonenumber = TextField("Phone Number",[validators.Required()])
    dob = TextField("Date Of Birth",[validators.Required()])
    submit = SubmitField("Submit")

class LoginForm(Form):
    email = TextField("Email",[validators.Required()])
    password = PasswordField("Password",[validators.Required()])
    submit = SubmitField("Submit")

class RecipeForm(Form):
    uploadedfile = FileField("Upload A Picture")
    name = TextField("Recipe Name",[validators.Required()])
    recipetype = SelectField("Type",choices=[("Breakfast","Breakfast"),("Lunch","Lunch"),("Dinner","Dinner"),("Snack","Snack")])
    serving = TextField("Serving",[validators.Required()])
    preptime = TextField("Preparation Time",[validators.Required()])
    caloriecount = TextField("Calorie Count",[validators.Required()])
    submit = SubmitField("Submit")

class RecipesForm(Form):
    name = TextField("Enter a recipe name")
    submit = SubmitField("Submit")

class IngredientForm(Form):
    submit = SubmitField("Submit")
