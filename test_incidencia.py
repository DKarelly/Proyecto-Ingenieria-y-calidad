from models.incidencia import Incidencia

incidencias = Incidencia.obtener_todas()
print('Incidencias obtenidas:', len(incidencias))
if incidencias:
    print('Primera keys:', list(incidencias[0].keys()))
    print('Primera:', incidencias[0])
else:
    print('No hay incidencias')
