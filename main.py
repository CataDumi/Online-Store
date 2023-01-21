import requests.cookies
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
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

# class BookForm(FlaskForm):
#     book_id=StringField('Enter book id',validators=[DataRequired()])
#     name = StringField('Enter book name', validators=[DataRequired()])
#     author = StringField('Enter author name', validators=[DataRequired()])
#     quantity = StringField('Enter quantity available ', validators=[DataRequired()])
#     price = StringField('Enter book price', validators=[DataRequired()])
#     rating = StringField('Enter book rating out of 5', validators=[DataRequired()])
#     description = StringField('Enter book description', validators=[DataRequired()])
#     submit=SubmitField('Submit')
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



@app.route('/', methods=['GET', 'POST'])
def get_all_posts():
    if request.method=='GET':
        all_books=db.session.query(Books).all()[:1]  # ca sa vad doar primele cateva carti

    return render_template("index.html",content=all_books,date=datetime.now().strftime("%d/%m/%Y"))


@app.route('/delete',methods=["GET","POST"])
def delete_book():
    print('sall CFFFFF')
    return render_template('index.html')

@app.route("/catalogue")
def show_post():
    requested_post = None
    all_books=db.session.query(Books).all()
    return render_template("catalogue.html",content=all_books)


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
