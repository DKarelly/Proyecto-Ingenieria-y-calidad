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
""" RUTAS MAURICIO """
# Módulo de Reportes
@app.route('/reportes/consultar-por-categoria')
@app.route('/reportes/consultar-por-categoria.html')
def consultar_reportes_por_categoria():
    return render_template('reportes/consultar_por_categoria.html')

@app.route('/reportes/generar-reporte-actividad')
@app.route('/reportes/generar-reporte-actividad.html')
def generar_reporte_actividad():
    return render_template('reportes/generar_reporte_actividad.html')

@app.route('/reportes/generar-ocupacion-recursos')
@app.route('/reportes/generar-ocupacion-recursos.html')
def generar_ocupacion_recursos():
    return render_template('reportes/generar_ocupacion_recursos.html')

# Módulo de Incidencias
@app.route('/incidencias/generar-informe')
@app.route('/incidencias/generar-informe.html')
def generar_informe_incidencias():
    return render_template('incidencias/generar_informe.html')

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
    return render_template('incidencias/consultarIncidencia.html') 

@app.route('/gestionarBloqueo')
@app.route('/gestionarBloqueo.html')
def gestionarBloqueo():
    return render_template('gestionarBloqueo.html') 

"""------------------------------------------------------------------"""




if __name__ == "__main__":
    app.run(debug=True)
