# arquivo com as rotas  (links) do site
from flask import render_template, url_for, redirect
from fakepinterest import app, database, bcrypt
from flask_login import login_required, login_user, logout_user, current_user
from fakepinterest.models import Usuario, Foto
from fakepinterest.forms import FormLogin, FormCriarConta, FormFoto
import os
from werkzeug.utils import secure_filename


@app.route("/", methods=["GET", "POST"])
def homepage():
    form_login = FormLogin()
    if form_login.validate_on_submit():
         usuario = Usuario.query.filter_by(email=form_login.email.data).first()
         if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=True)
            return redirect(url_for("perfil", id_usuario=usuario.id))
         
    return render_template("homepage.html", form=form_login)

@app.route("/criarconta", methods=["GET", "POST"])
def criarconta():
    form_criarconta = FormCriarConta()
    if form_criarconta.validate_on_submit():
        senhacri = bcrypt.generate_password_hash(form_criarconta.senha.data)
        usuario = Usuario(username= form_criarconta.username.data, 
                          senha=senhacri, 
                          email=form_criarconta.email.data)
        database.session.add(usuario)
        database.session.commit()
        login_user(usuario, remember=True)

        return redirect(url_for("perfil", id_usuario=usuario.id))
    return render_template("criarconta.html", form=form_criarconta)

@app.route("/perfil/<id_usuario>", methods=["GET", "POST"])
@login_required
def perfil(id_usuario):
    if int(id_usuario) == int(current_user.id):
        # o ususário esta acessando o proprio perfil
        form_foto = FormFoto()
        if form_foto.validate_on_submit():
            arquivofoto = form_foto.foto.data
            nome_seguro = secure_filename (arquivofoto.filename)
            #salvar aqruivona pasta fotos_post 
            caminho = os.path.join(os.path.abspath(os.path.dirname(__file__)), #pasta do projeto
                            app.config["UPLOAD_FOLDER"], #constante com o nome da pasta dos arquivos de fotos
                            nome_seguro) #nome do arquivo
            
            arquivofoto.save(caminho)
            
            #registrar o arquivo no banco de dados
            foto = Foto(imagem=nome_seguro, id_usuario=int(current_user.id))
            database.session.add(foto)
            database.session.commit()

        return render_template("perfil.html", usuario=current_user, form=form_foto) 
    else:
        #Usuario acessando o perfil de outro usuario
        usuario = Usuario.query.get(int(id_usuario))    
    return render_template("perfil.html", usuario=usuario, form=None)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))

@app.route("/feed")
@login_required
def feed():
    fotos = Foto.query.order_by(Foto.data_criacao.desc()).all()
    return render_template("feed.html", fotos=fotos)