from flask import Flask, render_template
from routes.seguridad import seguridad_bp
from routes.reportes import reportes_bp
from routes.incidencias import incidencias_bp

app = Flask(__name__)

# Registrar blueprints
app.register_blueprint(seguridad_bp)
app.register_blueprint(reportes_bp)
app.register_blueprint(incidencias_bp)

""" RUTA DEL HOME """
@app.route("/")
def home():
    return render_template('home.html')

"""------------------------------------------------------------------"""
""" RUTAS KARELLY"""
@app.route('/gestionCatalogoServicio')
@app.route('/gestionCatalogoServicio.html')
def gestion_catalogo_servicio():
    return render_template('gestionCatalogoServicio.html')

@app.route('/consultaAgendaMedica')
@app.route('/consultaAgendaMedica.html')
def consulta_agenda_medica():
    return render_template('consultaAgendaMedica.html')  

@app.route('/gestionRecursosFisicos')
@app.route('/gestionRecursosFisicos.html')
def gestion_recursos_fisicos():
    return render_template('gestionRecursosFisicos.html') 

@app.route('/gestionHorariosLaborables')
@app.route('/gestionHorariosLaborables.html')
def gestion_horarios_laborables():
    return render_template('gestionHorariosLaborables.html')

@app.route('/consultarIncidencia')
@app.route('/consultarIncidencia.html')
def consultarIncidencia():
    return render_template('consultarIncidencia.html') 

@app.route('/gestionarBloqueo')
@app.route('/gestionarBloqueo.html')
def gestionarBloqueo():
    return render_template('gestionarBloqueo.html') 


"""------------------------------------------------------------------"""

if __name__ == "__main__":
    app.run(debug=True)
