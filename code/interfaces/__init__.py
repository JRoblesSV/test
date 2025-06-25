"""
Paquete de interfaces gráficas para OPTIM - Sistema de Programación de Laboratorios

Este paquete contiene todas las ventanas y diálogos de configuración del sistema:
- Configuración de calendario académico
- Configuración de horarios semanales
- Visualización de resultados
- Sistema de ayuda (opcional)

Desarrollado para ETSIDI - UPM
Stack: Python + PyQt6 + Pandas
"""

# Importaciones principales
try:
    from .configurar_calendario import ConfigurarCalendario
    from .configurar_horarios import ConfigurarHorarios
    from .ver_resultados import VerResultados
    # from .ayuda import AyudaSistema  # Comentado por ahora - demasiado extenso

except ImportError as e:
    print(f"Error importando interfaces: {e}")

    # Definir clases dummy en caso de error
    class ConfigurarCalendario:
        def __init__(self, parent=None):
            print("⚠️ ConfigurarCalendario no disponible")


    class ConfigurarHorarios:
        def __init__(self, parent=None):
            print("⚠️ ConfigurarHorarios no disponible")


    class VerResultados:
        def __init__(self, parent=None):
            print("⚠️ VerResultados no disponible")

# Versión del paquete
__version__ = "1.0.0"
__author__ = "Javier Robles Molina"
__description__ = "Interfaces gráficas para OPTIM - Sistema de Programación de Laboratorios"

# Exportaciones públicas
__all__ = [
    'ConfigurarCalendario',
    'ConfigurarHorarios',
    'VerResultados',
    # 'AyudaSistema'  # Comentado por ahora
]

# Metadatos para integración con gui_labs.py
INTERFACES_DISPONIBLES = {
    'calendario': ConfigurarCalendario,
    'horarios': ConfigurarHorarios,
    'resultados': VerResultados,
    # 'ayuda': AyudaSistema  # Comentado por ahora
}


def get_interface(nombre):
    """
    Obtener una clase de interfaz por nombre

    Args:
        nombre (str): Nombre de la interfaz ('calendario', 'horarios', 'resultados')

    Returns:
        class: Clase de la interfaz solicitada o None si no existe
    """
    return INTERFACES_DISPONIBLES.get(nombre.lower())


def listar_interfaces():
    """
    Listar todas las interfaces disponibles

    Returns:
        list: Lista de nombres de interfaces disponibles
    """
    return list(INTERFACES_DISPONIBLES.keys())


# Inicialización del paquete
print("📦 Paquete 'interfaces' cargado correctamente")
print(f"✅ {len(INTERFACES_DISPONIBLES)} interfaces disponibles: {', '.join(INTERFACES_DISPONIBLES.keys())}")