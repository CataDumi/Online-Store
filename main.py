import requests.cookies
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm,Form
from wtforms import StringField, SubmitField,TextField,TextAreaField,IntegerField
from wtforms import SubmitField, BooleanField, StringField, PasswordField, validators
from wtforms.validators import DataRequired, URL,InputRequired,NumberRange
from flask_ckeditor import CKEditor, CKEditorField
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.app_context().push()

# Creez form pt carti


# ramane de testat


# Creez database pt carti

class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    author = db.Column(db.String(250))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Integer)
    rating = db.Column(db.Integer)
    description = db.Column(db.String(250))
db.create_all()

# Form pt edit
class Edit(FlaskForm):
    name = StringField('Edit book name', validators=[DataRequired(),InputRequired()])
    author = StringField('Edit author name', validators=[DataRequired()])
    quantity = IntegerField('Edit quantity available ', validators=[DataRequired()])
    price = IntegerField('Edit book price', validators=[DataRequired()])
    rating = IntegerField('Edit book rating', validators=[DataRequired(),validators.NumberRange(min=0,max=5)])
    description = TextAreaField('Edit book description', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/', methods=['GET', 'POST'])
def get_all_posts():
    if request.method=='GET':
        preview=db.session.query(Books).all()[:1]  # ca sa vad doar primele cateva carti
    return render_template("index.html",content=preview,date=datetime.now().strftime("%d/%m/%Y"))

@app.route('/edit/<int:id>',methods=["GET","POST"])
def edit(id):
    edit_form=Edit()

    if request.method=='GET':
    ###aici identific cartea din db si ii preiau caracteristicile pt editare
        book_to_edit=Books.query.filter_by(id=id).first()
        print('GET')
        edit_form.name.data=book_to_edit.name
        edit_form.author.data = book_to_edit.author
        edit_form.quantity.data = book_to_edit.quantity
        edit_form.price.data = book_to_edit.price
        edit_form.rating.data = book_to_edit.rating
        edit_form.description.data = book_to_edit.description
        return render_template('edit.html', form=edit_form)

    #Submit changes to db
    elif request.method=='POST':
        print('POST')
        print(edit_form.name.data)
        print(edit_form.author.data)
        print(edit_form.quantity.data)
        print(edit_form.price.data)
        print(edit_form.rating.data)
        print(edit_form.description.data)

        #Enter new data
        edited_book=Books.query.filter_by(id=id).first()
        print(edited_book.name)
        print(edit_form.name.data)
        edited_book.name=edit_form.name.data
        edited_book.author=edit_form.author.data
        edited_book.quantity=edit_form.quantity.data
        edited_book.price=edit_form.price.data
        edited_book.rating=edit_form.rating.data
        edited_book.description=edit_form.description.data
        db.session.commit()

        return redirect(url_for('catalogue'))


@app.route('/delete/<int:id>',methods=["GET","POST"])
def delete_book(id):
    book_to_delete=Books.query.get(id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

@app.route("/catalogue")
def catalogue():
    requested_post = None
    all_books=db.session.query(Books).all()
    return render_template("catalogue.html",content=all_books,date=datetime.now().strftime("%d/%m/%Y"))


@app.route('/add_books', methods=['POST', "GET"])
def add_books():
    if request.method == 'POST':
        print('yas')

        # aici vad tot ce se da add din add books
        print(request.form['name'])
        print(request.form['author'])
        print(request.form['quantity'])
        print(request.form['price'])
        print(request.form['rating'])
        print(request.form['description'])

        # aici bag noua carte in db
        new_book = Books(name=request.form['name'],
                         author=request.form['author'],
                         quantity=request.form['quantity'],
                         price=request.form['price'],
                         rating=request.form['rating'],
                         description=request.form['description']
                         )
        db.session.add(new_book)
        db.session.commit()

        return redirect(url_for('get_all_posts'))
    else:
        return render_template('add_books.html')


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True)
