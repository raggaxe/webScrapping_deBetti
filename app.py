from flask import Flask, session, Response
from flask import request, render_template, url_for, redirect, flash, send_from_directory, send_file
from dbconnect import connection
from functools import wraps
from passlib.hash import sha256_crypt
import gc
from datetime import datetime
from Web_Scrapping import list_content
from bs4 import BeautifulSoup
import requests

from werkzeug.utils import secure_filename
import os
import json

app = Flask(__name__,static_url_path='/static')
dia = str(datetime.now().strftime("%d-%m-%Y"))

UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Precisa fazer o Login")
            return redirect(url_for('login'))
    return wrap

@app.route('/transfer/<filename>', methods=['GET', 'POST'])
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route('/transfer_images/<filename>', methods=['GET', 'POST'])
def memory_images(filename):
    return send_from_directory(app.config['MEMORY_GAME_FOLDER'],
                               filename)


@app.route("/")
def home():
    return render_template("index.html")

@app.route('/logout/')
@login_required
def logout():
    session.clear()
    flash('Voce esta saindo do APP! Obrigado')
    return redirect(url_for('home'))

@app.route('/login/', methods=['POST'])
def login():
    error = ''
    try:
        c, conn = connection()
        print('connect')
        if request.method == 'POST':
            email = request.form['email']
            print(email)
            x = c.execute("""
                            SELECT
                                *
                            FROM
                                usuarios
                            WHERE
                               email=%s""", [email])
            print(x)

            if int(x) > 0:
                data = c.fetchone()[3]
                print(data)

                # if int(x) > 0:
                if sha256_crypt.verify(request.form['password'], data):
                    session['logged_in'] = True
                    session['username'] = email
                    flash("Bem-Vindo")
                    return redirect(url_for('home'))

                else:
                    flash("SENHA INVALIDA")
            if int(x) == 0:
                email = request.form['email']
                print(email)

                password_admin = "figueiradafoz"
                data = sha256_crypt.encrypt((str(password_admin)))


                if sha256_crypt.verify(request.form['password'], data):
                    session['admin'] = True
                    session['email'] = email

                    return redirect(url_for('dashboard'))
                else:
                    flash("USUARIO NAO EXISTE, FACA CADASTRO ")

            # if int(x) > 0:
            #     myresult = c.fetchall()
            #     for x in myresult:
            #         id_usuario = x[0]
            #         nome = x[1]
            #         senha = x[2]
            #         email = x[3]
            #         pontos = x[7]
            #     print(myresult)
            #     session['logged_in'] = True
            #     # session['id_user'] = id_user
            #     session['username'] = nome
            #     # session['endereco'] = endereco
            #     # session['telefone'] = telefone
            #     session['email'] = email
            #     session['user_pontos'] = pontos
            #     session['notificacoes'] = 0
            #
            #     c.close()
            #     flash("Bem Vindo " + nome)
            #     return redirect(url_for('home'))



            # if request.form['email'] == "admin@admin.com" and request.form['password'] == "123456":
            #     session['admin'] = True
            #     session['email'] = email
            #
            #     return redirect(url_for('dashboard'))


        return render_template("teste.html", error=error)
    except Exception as e:
        flash(e)
        return render_template('teste.html', error=error)

@app.route('/register/', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

@app.route('/insert_usuario', methods=['GET', 'POST'])
def insert_usuario():
    try:
        if request.method == "POST":
            c, conn = connection()
            nome = request.form['nome']
            email = request.form['email']
            password = sha256_crypt.encrypt((str(request.form['password'])))
            print(nome)
            print(email)
            print(password)
            #print(confirme_password)
            x = c.execute("""
                            SELECT
                                *
                            FROM
                                usuarios
                            WHERE
                               email=%s""", [email])
            if int(x) > 0:
                flash("E-mail já está cadastrado. Verifique se está correto o email.")
                return render_template('register.html')
            if int(x) == 0:
                if sha256_crypt.verify(request.form['confirme_password'],password):
                    pontos = 0
                    c.execute("""
                    INSERT INTO
                          portifolio.usuarios
                             (nome,email,password,pontos)
                             VALUES
                              (%s,%s,%s,%s)""",
                          [nome, email, password, pontos])
                    flash("Obrigado por Registrar")
                    session['logged_in'] = True
                    session['username'] = nome
                    session['email'] = email
                    session['notificacoes'] = 0
                    session['pontos'] = 0
                    conn.commit()
                    c.close()
                    conn.close()
                    gc.collect()
                    flash("Cliente Cadastrado com Sucesso")
                    return render_template('teste.html')
                else:
                    flash("Passwords diferentes, insira novamente")
                    return render_template('register.html')
            return render_template('register.html')
    except Exception as e:
        return (str(e))

@app.route('/scrapping/', methods=['POST'])
def scrapping():
    url = request.form['url']
    paginas = request.form['paginas']
    data = list_content(url, int(paginas))
    return render_template('index.html', data=data[0], filename=data[1])

@app.route('/uploads/<path:filename>', methods = ['GET'])
def downloads(filename):
    return send_file(filename, as_attachment=True)





def main ():
    app.secret_key = 'debetti'
    port = int(os.environ.get("PORT", 5002))
    app.run (host="0.0.0.0", port=port)

if __name__ == "__main__":
   main()