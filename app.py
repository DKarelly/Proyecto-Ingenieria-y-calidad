from flask import Flask, render_template
from routes.seguridad import seguridad_bp
from routes.reportes import reportes_bp
from routes.incidencias import incidencias_bp

app = Flask(__name__)

# Registrar blueprints
app.register_blueprint(seguridad_bp)
app.register_blueprint(reportes_bp)
app.register_blueprint(incidencias_bp)

@app.route("/")
def home():
    return render_template('home.html')

if __name__ == "__main__":
    app.run(debug=True)


