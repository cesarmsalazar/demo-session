from flask import Flask
from flask import render_template, session
from flask import request, redirect #recibe post y redirige 
from flaskext.mysql import MySQL #importamos Mysql
from datetime import datetime #control de tiempo para casos de adjuntar archivos con el mismo nombre 
from flask import send_from_directory #permite obtener informacion de un archivo de imagen 
import os

app = Flask(__name__)
app.secret_key = "develoteca"

mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '123456'
app.config['MYSQL_DATABASE_DB'] = 'sitio'
mysql.init_app(app)



@app.route('/')
def inicio():
    return render_template('sitio/index.html')

@app.route('/img/<imagen>') #ruta que devuelve una imagen 
def imagenes(imagen):
    print(imagen)
    return send_from_directory(os.path.join('templates/sitio/img'), imagen)

@app.route('/css/<archivocss>') #ruta que devuelve una imagen 
def css_link(archivocss):
    return send_from_directory(os.path.join('templates/sitio/css'), archivocss)


@app.route('/libros')
def libros():
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute('select * from libros')
    libros = cursor.fetchall()
    conexion.commit()
    return render_template('sitio/libros.html', libros = libros)

@app.route('/nosotros')
def nosotros():
    return render_template('sitio/nosotros.html')

@app.route('/admin/')
def admin_index():
    if not 'login' in session:
        return redirect('/admin/login')

    return render_template('admin/index.html')

@app.route('/admin/login')
def admin_login():
    return render_template('admin/login.html')

@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    _usuario = request.form['txtUsuario']
    _password = request.form['txtPassword']
    print(_usuario)
    print(_password)

    if _usuario=='admin' and _password == '123':
        session['login'] = True
        session['usuario'] = 'Administrador Sist'
        return redirect('/admin')

    return render_template('admin/login.html', mensaje='Acceso Denegado')

@app.route('/admin/cerrar')
def admin_cerrar():
    session.clear()
    return redirect('/admin/login')


@app.route('/admin/libros')
def admin_libros():
    if not 'login' in session:
        return redirect('/admin/login')

    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute('select * from libros')
    libros = cursor.fetchall()
    conexion.commit()
    print(libros)
    return render_template('admin/libros.html', libros = libros)


@app.route('/admin/libros/guardar',methods=['POST'] )
def admin_libros_guardar():
    if not 'login' in session:
        return redirect('/admin/login')

    _nombre = request.form['txtNombre']
    _url =  request.form['txtURL']
    _archivo = request.files['txtImagen']
    tiempo = datetime.now()
    horaActual = tiempo.strftime('%Y%H%M%S')

    if _archivo.filename != "":
        nuevoNombre = horaActual+"_"+_archivo.filename
        _archivo.save("templates/sitio/img/"+nuevoNombre)

    sql = "insert into libros (id, nombre, imagen, url) values (null, %s, %s, %s);"
    datos = (_nombre, nuevoNombre, _url)
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(sql, datos)
    conexion.commit()
    return redirect('/admin/libros')

@app.route('/admin/libros/borrar',methods=['POST'] )
def admin_libros_borrar():
    if not 'login' in session:
        return redirect('/admin/login')

    _id = request.form['txtID']

    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("select imagen from libros where id=%s", (_id))
    libro = cursor.fetchall()
    conexion.commit()
    print(libro)

    #borra la imagen de la carpeta img, si existe
    if os.path.exists("templates/sitio/img/"+str(libro[0][0])):
        os.unlink("templates/sitio/img/"+str(libro[0][0]))
    
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("delete from libros where id=%s", (_id))
    conexion.commit()

    return redirect('/admin/libros')



if __name__ == '__main__':
    app.run(debug=True)

#minuto: 02:52:16 sitio web en python.mp4 
  
