from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from flask_mail import Mail, Message

# Inicializaciones
app = Flask(__name__)

# Mysql 
app.config['MYSQL_HOST'] = 'localhost' 
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flaskcontacts'
mysql = MySQL(app)

# SMPT
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'antaresbar140@gmail.com'
app.config['MAIL_PASSWORD'] = 'Antar3s_B4r'
app.config['MAIL_DEFAULT_SERVER'] = 'antaresbar140@gmail.com'

mail = Mail(app)


# Configuraciones
app.secret_key = "mysecretkey"

# routes


@app.route('/reservas')
def Index():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contacts')
    data = cur.fetchall()
    cur.close()
    return render_template('index.html', contacts = data)




@app.route('/', methods = ['GET','POST'])   
def login():
    msg = ''
    if request.method == 'POST':                                #pedido de usuario a la DB
        username = request.form['username']
        password = request.form['password']
        cr = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cr.execute(
            'SELECT * FROM USERS WHERE username = % s AND password = % s',(username, password, )
        )
        user = cr.fetchone()                 
        if user:                                               #Verificacion de usuario
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username'] 
            success_message = 'Bienvenido {}'.format(username)
            flash(success_message)
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM contacts')
            data = cur.fetchall()
            cur.close()
            return render_template('index.html',contacts = data) 
        else:
            msg = 'Nombre de usuario o password incorrecto'
    return render_template('login.html', msg = msg)

@app.route('/logout')                                          # logout del usuario
def logout():
    # session.pop('loggedin', None)
    # session.pop('id', None)
    # if 'username' in session:
        
    #     session.pop('username',None)
    session.clear()
    return redirect(url_for('login.html'))

@app.route('/register', methods =['GET', 'POST'])              #Registro de nuevo usuario
def register():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cr = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cr.execute('SELECT * FROM users WHERE username = % s',(username, )) 
        user = cr.fetchone()
        if user:
            msg = 'Usuario ya existente'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email): 
            msg = 'Email invalido'
        elif not username or not password or not email: 
            msg = 'Por favor complete los campos'
        else: 
            cr.execute('INSERT INTO users VALUES(NULL, % s, % s, % s)',(username, password, email, )) 
            mysql.connection.commit() 
            msg = 'Se registro correctamente'
    elif request.method == 'POST': 
        msg = 'Por favor complete el formulario'
    return render_template('register.html', msg = msg) 


@app.route('/add_contact', methods=['POST'])        #Agregado de reservas 
def add_contact():
    if request.method == 'POST':
        fullname = request.form['fullname']
        phone = request.form['phone']
        email = request.form['email']
        hours = request.form['hours']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO contacts (fullname, phone, email, hours) VALUES (%s,%s,%s, %s)", (fullname, phone, email, hours))
        mysql.connection.commit()
        flash('Reserva confirmada')
        msg = Message('Reserva confirmada',
                                        sender ='abeld.correa@gmail.com',
                                        body='{} su reserva ha sido confirmada en el horario {}'.format(fullname,hours) ,
                                        recipients= [request.form['email']])
        mail.send(msg)
        return redirect(url_for('Index'))

@app.route('/edit/<id>', methods = ['POST', 'GET'])       # busqueda de la reserva para edicion
def get_contact(id): 
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contacts WHERE id = {0}'.format(id))
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('edit-contact.html', contact = data[0])

@app.route('/update/<id>', methods=['POST'])              #Edicion de la reserva
def update_contact(id): 
    if request.method == 'POST':
        fullname = request.form['fullname']
        phone = request.form['phone']
        email = request.form['email']
        hours = request.form['hours']
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE contacts
            SET fullname = %s,
                email = %s,
                phone = %s,
                hours = %s
            WHERE id = %s
            """, (fullname, email, phone, hours, id))
        flash('Contact Updated Successfully')
        mysql.connection.commit()
        return redirect(url_for('Index'))

@app.route('/delete/<string:id>', methods = ['POST','GET'])    # Borrar la reserva
def delete_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM contacts WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Contact Removed Successfully')
    return redirect(url_for('Index'))

# arrancar la app

if __name__ == "__main__":
    app.run(port=3000, debug=True)