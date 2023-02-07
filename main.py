import requests.cookies
from flask import Flask, render_template, redirect, url_for, request, flash,send_from_directory
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor, CKEditorField
from datetime import datetime
from forms import BookForm, RegisterForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from fpdf import FPDF
from pathlib import Path

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.app_context().push()


# Table for books
class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    author = db.Column(db.String(250))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Integer)
    rating = db.Column(db.Integer)
    url = db.Column(db.String(250))
    description = db.Column(db.String(250))

#Table for users
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    email = db.Column(db.String(250), unique=True)
    password = db.Column(db.String(250))

#Table for user cart
class ShoppingCart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_cart=db.Column(db.Integer)
    book_name=db.Column(db.String(250))

db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    print(f'User id to load: {User.query.get(int(user_id))}')
    return User.query.get(int(user_id))


#################################################                         ################################################################
#################################################                         ################################################################
#################################################                         ################################################################

@app.route('/', methods=['GET', 'POST'])
def get_all_posts():
    if request.method == 'GET':
        preview = db.session.query(Books).all()[:3]  # ca sa vad doar primele cateva carti
    print(f'Logged in user ? {current_user.is_authenticated}')
    print(f'Current user: {current_user},{current_user.name}')
    return render_template("index.html", content=preview, date=datetime.now().strftime("%d/%m/%Y"))


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    error = None
    register_user_form = RegisterForm()
    if request.method == 'POST':
        # checking for email if already exists
        if User.query.filter_by(email=register_user_form.email.data).first():
            error = 'Email already used. Try a new email address.'
            return render_template('register.html', form=register_user_form, error=error)

        elif register_user_form.validate_on_submit() and \
                register_user_form.password.data == register_user_form.password_confirmation.data:  # match both passwords
            # hash password
            print(register_user_form.password.data)

            hash_password = generate_password_hash(password=register_user_form.password.data, method='pbkdf2:sha256',
                                                   salt_length=8)
            # print(hash_password)
            new_user = User(name=register_user_form.name.data,
                            email=register_user_form.email.data,
                            password=hash_password)
            db.session.add(new_user)
            db.session.commit()

            # Log in and authenticate user after adding details to database
            login_user(new_user)
            return redirect(url_for('catalogue'))

    return render_template('register.html', form=register_user_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if request.method == "POST":
        # search for the account
        if User.query.filter_by(email=str(login_form.email.data)).first():
            # if the account is registered
            user_to_login = User.query.filter_by(email=login_form.email.data).first()

            # checking for password
            if check_password_hash(pwhash=user_to_login.password, password=login_form.password.data):
                flash('You were successfully logged in!')

                # Log in and authenticate user
                login_user(user_to_login)
                print(f"Current user: {current_user, current_user.id, current_user.name}")
                return redirect(url_for('catalogue'))
            else:
                error = 'Invalid password,please try again.'
                return render_template('login.html', error=error, form=login_form)
        else:
            error = "That email does not exist, please try again."
            return render_template('login.html', error=error, form=login_form)

    return render_template('login.html', form=login_form)


@app.route('/edit/<int:id>', methods=["GET", "POST"])
@login_required
def edit(id):
    edit_form = BookForm()
    if request.method == 'GET':
        ###aici identific cartea din db si ii preiau caracteristicile pt editare
        book_to_edit = Books.query.filter_by(id=id).first()
        # print('GET')
        edit_form.name.data = book_to_edit.name
        edit_form.author.data = book_to_edit.author
        edit_form.quantity.data = book_to_edit.quantity
        edit_form.price.data = book_to_edit.price
        edit_form.rating.data = book_to_edit.rating
        edit_form.url.data = book_to_edit.url
        edit_form.description.data = book_to_edit.description
        return render_template('edit.html', form=edit_form)

    # Submit changes to db
    elif request.method == 'POST':
        if edit_form.validate_on_submit():
            # print('POST')
            # print(edit_form.name.data)
            # print(edit_form.author.data)
            # print(edit_form.quantity.data)
            # print(edit_form.price.data)
            # print(edit_form.rating.data)
            # print(edit_form.description.data)

            # Enter new data in db
            edited_book = Books.query.filter_by(id=id).first()
            edited_book.name = edit_form.name.data
            edited_book.author = edit_form.author.data
            edited_book.quantity = edit_form.quantity.data
            edited_book.price = edit_form.price.data
            edited_book.rating = edit_form.rating.data
            edited_book.url = edit_form.url.data
            edited_book.description = edit_form.description.data
            db.session.commit()
            return redirect(url_for('catalogue'))
        else:
            return render_template('edit.html', form=edit_form)

@app.route('/add_books', methods=['POST', "GET"])
def add_books():
    add_book_form = BookForm()
    if request.method == 'POST':
        # aici bag noua carte in db
        if add_book_form.validate_on_submit():
            print('AAAAAAAAAAAAAAAAAAAAAAAAAA')
            new_book = Books(name=add_book_form.name.data,
                             author=add_book_form.author.data,
                             quantity=add_book_form.quantity.data,
                             price=add_book_form.price.data,
                             rating=add_book_form.rating.data,
                             url=add_book_form.url.data,
                             description=add_book_form.description.data
                             )
            db.session.add(new_book)
            db.session.commit()

            return redirect(url_for('get_all_posts'))
        return render_template('add_books.html',form=add_book_form)
    else:
        return render_template('add_books.html',form=add_book_form)

@app.route('/delete/<int:id>', methods=["GET", "POST"])
def delete_book(id):
    book_to_delete = Books.query.get(id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

@app.route("/catalogue")
def catalogue():
    requested_post = None
    all_books = db.session.query(Books).all()
    return render_template("catalogue.html", content=all_books, date=datetime.now().strftime("%d/%m/%Y"))

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/finish order")
@login_required
def finish_order():
    cart = ShoppingCart.query.filter_by(user_cart=int(current_user.id)).all()
    # when the order is finished, substract the items quantity from the db
    for item in cart:
        book=Books.query.filter_by(name=item.book_name).first()
        book.quantity=book.quantity-1
        db.session.commit()

    #when the order is finished, clear the cart
    print(cart)
    for item in cart:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('get_all_posts'))

@app.route('/add_item/<int:id>')
def add_to_cart(id):
    print('Item added to cart')
    if current_user.is_authenticated:
        lista=ShoppingCart.query.filter_by(user_cart=int(current_user.id)).all()
        print(f'Lista ta de carti e: {lista,type(lista)}')

    item_to_add=ShoppingCart(user_cart=int(current_user.id),
                             book_name=Books.query.filter_by(id=id).first().name)
    db.session.add(item_to_add)
    db.session.commit()


    return redirect(url_for('catalogue'))


@app.route('/cart')
@login_required
def cart_page():
    # get all the titles added by a user , but in a list structure
    lst = ShoppingCart.query.filter_by(user_cart=int(current_user.id)).all()
    #search for every title from the list above in the Books table and add them in a list
    shop_cart = [Books.query.filter_by(name=item.book_name).first() for item in lst]

    print(f'Asta este shopping cart-ul: {shop_cart}')
    total_sum=0
    for item in shop_cart:
        print(item.name)
        total_sum+=item.price

    return render_template('cart_page.html',cart=shop_cart,total_sum=total_sum,num_of_products=len(shop_cart))


@app.route('/invoice-pdf')
def invoice_pdf():
    # get all the titles added by a user , but in a list structure
    lst = ShoppingCart.query.filter_by(user_cart=int(current_user.id)).all()
    #search for every title from the list above in the Books table and add them in a list
    shop_cart = [Books.query.filter_by(name=item.book_name).first() for item in lst]


    pdf = FPDF(format='A4', orientation='p', unit='mm')

    # Create the page
    pdf.add_page()
    # Header content
    pdf.set_font(family='Times', size=30, style='B')
    pdf.cell(w=20, h=12, txt=f'INVOICE ', align='L', ln=1, border=0)
    pdf.ln(4)
    pdf.set_font(family='Times', size=16, style='B')
    pdf.cell(w=20, h=12, txt=f'Date: {datetime.now().strftime("%m/%d/%Y")}', align='L', ln=1, border=0)
    pdf.set_font(family='Times', size=18, style='I')
    pdf.cell(w=20, h=12, txt=f'Thank you, {current_user.name.title()}. '
                             f'We have received your order, and it is really lovely.', align='L', ln=1, border=0)
    pdf.ln(12)



    #Columns hdr
    pdf.set_font(family='Times', size=14, style='B')
    pdf.cell(w=100, h=12, txt='Book Title', align='C', ln=0, border=1)
    pdf.cell(w=40, h=12, txt='Book Author', align='C', ln=0, border=1)
    pdf.cell(w=40, h=12, txt='Book Price (Eur)', align='C', ln=1, border=1)

    total_sum=0
    for book in shop_cart:
        # Table content
        pdf.set_font(family='Times', size=12)
        pdf.cell(w=100, h=12, txt=book.name, align='C', ln=0, border=1)
        pdf.cell(w=40, h=12, txt=book.author, align='C', ln=0, border=1)
        pdf.cell(w=40, h=12, txt=str(book.price), align='C', ln=0, border=1)
        pdf.ln(12)
        total_sum+=book.price

    # Adding the total
    pdf.set_font(family='Times', size=12, style='B')
    pdf.cell(w=100, h=12, txt='', align='C', ln=0, border=1)
    pdf.cell(w=40, h=12, txt='', align='C', ln=0, border=1)
    pdf.cell(w=40, h=12, txt=str(total_sum), align='C', ln=0, border=1)
    pdf.ln(20)
    #
    # Creating the sum sentence
    pdf.set_font(family='Times', size=18, style='B')
    pdf.cell(w=0, h=12, txt=f'The total due amont is {total_sum} Eur', align='L', ln=1, border=0)

    # Creating the name of the file
    pdf.output('static/files/invoice.pdf')

    return send_from_directory(directory=app.static_folder, path='files/invoice.pdf',as_attachment=True)

@app.route('/search', methods=["GET", "POST"])
def search():
    if request.method=='POST':
        print(request.form['searchbox'])
    search=request.form['searchbox']
    all_books = db.session.query(Books).all()
    for book in all_books:
        if search.lower() in book.name.lower():
            print('Da, cartea e in lista')
            result=book
            break
        else:
            result='Searched book is no available'
    return render_template('search.html',item=result)
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))
if __name__ == "__main__":
    app.run(debug=True)









