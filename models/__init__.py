# Configuración de la BD y modelos
from .empleado import Empleado
from .registro_actividad import RegistroActividad
from .categoria import Categoria
from .reporte import Reporte
from .recurso import Recurso
from .tipo_recurso import TipoRecurso
from .reporte_ocupacion import ReporteOcupacion
from .incidencia import Incidencia

__all__ = ['Empleado', 'RegistroActividad', 'Categoria', 'Reporte', 
           'Recurso', 'TipoRecurso', 'ReporteOcupacion', 'Incidencia']