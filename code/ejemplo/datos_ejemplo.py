#!/usr/bin/env python3
"""
Script para crear archivos CSV de ejemplo
SIN DEPENDENCIAS - solo usa librerías estándar de Python
"""

import csv
import os


def crear_directorio_datos():
    """Crear directorio para datos de ejemplo"""
    if not os.path.exists('datos_ejemplo'):
        os.makedirs('datos_ejemplo')
        print("📁 Directorio 'datos_ejemplo' creado")


def crear_alumnos_csv():
    """Crear archivo de alumnos (versión realista: alumnos en varias asignaturas)"""
    datos_alumnos = [
        ['dni', 'nombre', 'apellidos', 'asignatura', 'email'],
        # Juan está en Física I y Programación
        ['12345678A', 'Juan', 'Pérez García', 'Física I', 'juan.perez@upm.es'],
        ['12345678A', 'Juan', 'Pérez García', 'Programación', 'juan.perez@upm.es'],

        # María en Física I y Química Orgánica
        ['23456789B', 'María', 'López Ruiz', 'Física I', 'maria.lopez@upm.es'],
        ['23456789B', 'María', 'López Ruiz', 'Química Orgánica', 'maria.lopez@upm.es'],

        # Carlos en Electrónica y Programación
        ['34567890C', 'Carlos', 'González Díaz', 'Electrónica Digital', 'carlos.gonzalez@upm.es'],
        ['34567890C', 'Carlos', 'González Díaz', 'Programación', 'carlos.gonzalez@upm.es'],

        # Ana en Química y Física
        ['45678901D', 'Ana', 'Martín Sánchez', 'Química Orgánica', 'ana.martin@upm.es'],
        ['45678901D', 'Ana', 'Martín Sánchez', 'Física I', 'ana.martin@upm.es'],

        # Pedro solo en Programación
        ['56789012E', 'Pedro', 'Fernández López', 'Programación', 'pedro.fernandez@upm.es'],

        # Laura en Química y Electrónica
        ['67890123F', 'Laura', 'Rodríguez García', 'Química Orgánica', 'laura.rodriguez@upm.es'],
        ['67890123F', 'Laura', 'Rodríguez García', 'Electrónica Digital', 'laura.rodriguez@upm.es'],

        # Miguel solo en Física I
        ['78901234G', 'Miguel', 'Jiménez Pérez', 'Física I', 'miguel.jimenez@upm.es'],

        # Carmen en todas
        ['89012345H', 'Carmen', 'Moreno López', 'Física I', 'carmen.moreno@upm.es'],
        ['89012345H', 'Carmen', 'Moreno López', 'Química Orgánica', 'carmen.moreno@upm.es'],
        ['89012345H', 'Carmen', 'Moreno López', 'Electrónica Digital', 'carmen.moreno@upm.es'],
        ['89012345H', 'Carmen', 'Moreno López', 'Programación', 'carmen.moreno@upm.es'],
    ]

    with open('datos_ejemplo/alumnos.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(datos_alumnos)

    print(f"✅ alumnos.csv creado ({len(datos_alumnos)-1} registros de asignatura)")


def crear_asignaturas_csv():
    """Crear archivo de asignaturas"""
    datos_asignaturas = [
        ['asignatura', 'laboratorio', 'equipamiento_requerido', 'duracion_horas', 'semestre'],
        ['Física I', 'Lab_Fisica_A', 'Equipos de medición', '2', '1'],
        ['Física I', 'Lab_Fisica_B', 'Equipos de medición', '2', '1'],
        ['Química Orgánica', 'Lab_Quimica_A', 'Campana extractora', '3', '1'],
        ['Química Orgánica', 'Lab_Quimica_B', 'Campana extractora', '3', '1'],
        ['Electrónica Digital', 'Lab_Electronica_A', 'Osciloscopios', '2', '2'],
        ['Electrónica Digital', 'Lab_Electronica_B', 'Osciloscopios', '2', '2'],
        ['Programación', 'Lab_Informatica_A', 'Ordenadores', '2', '1'],
        ['Programación', 'Lab_Informatica_B', 'Ordenadores', '2', '1'],
        ['Programación', 'Lab_Informatica_C', 'Ordenadores', '2', '1'],
    ]

    with open('datos_ejemplo/asignaturas.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(datos_asignaturas)

    print("✅ asignaturas.csv creado (4 asignaturas, 9 compatibilidades)")


def crear_laboratorios_csv():
    """Crear archivo de laboratorios"""
    datos_laboratorios = [
        ['nombre', 'capacidad', 'equipamiento', 'disponible', 'edificio', 'planta'],
        ['Lab_Fisica_A', '20', 'Equipos de medición básicos', 'Si', 'Edificio A', 'Planta 1'],
        ['Lab_Fisica_B', '24', 'Equipos de medición avanzados', 'Si', 'Edificio A', 'Planta 2'],
        ['Lab_Quimica_A', '18', 'Campana extractora + Material químico', 'Si', 'Edificio B', 'Planta 1'],
        ['Lab_Quimica_B', '22', 'Campana extractora + Material químico', 'Si', 'Edificio B', 'Planta 2'],
        ['Lab_Electronica_A', '16', 'Osciloscopios + Fuentes alimentación', 'Si', 'Edificio C', 'Planta 1'],
        ['Lab_Electronica_B', '20', 'Osciloscopios + Generadores', 'Si', 'Edificio C', 'Planta 2'],
        ['Lab_Informatica_A', '30', '30 Ordenadores + Proyector', 'Si', 'Edificio D', 'Planta 1'],
        ['Lab_Informatica_B', '25', '25 Ordenadores + Pizarra digital', 'Si', 'Edificio D', 'Planta 2'],
        ['Lab_Informatica_C', '28', '28 Ordenadores + Software especializado', 'Si', 'Edificio D', 'Planta 3'],
    ]

    with open('datos_ejemplo/laboratorios.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(datos_laboratorios)

    print("✅ laboratorios.csv creado (9 laboratorios)")


def crear_profesores_csv():
    """Crear archivo de profesores"""
    datos_profesores = [
        ['nombre', 'asignatura', 'disponibilidad_lunes', 'disponibilidad_martes', 'disponibilidad_miercoles',
         'disponibilidad_jueves', 'disponibilidad_viernes', 'email'],
        ['Dr. García López', 'Física I', '08:00-12:00;14:00-18:00', '10:00-14:00', '08:00-12:00;16:00-20:00',
         '10:00-14:00', '08:00-12:00', 'garcia.lopez@upm.es'],
        ['Dra. Martín Ruiz', 'Química Orgánica', '09:00-13:00', '09:00-13:00;15:00-19:00', '10:00-14:00',
         '09:00-13:00;15:00-19:00', '10:00-14:00', 'martin.ruiz@upm.es'],
        ['Prof. González Díaz', 'Electrónica Digital', '08:00-14:00', '08:00-12:00', '08:00-14:00', '10:00-16:00',
         '08:00-12:00', 'gonzalez.diaz@upm.es'],
        ['Dr. Fernández Pérez', 'Programación', '10:00-14:00;16:00-20:00', '08:00-12:00', '10:00-14:00;16:00-20:00',
         '08:00-12:00', '10:00-14:00', 'fernandez.perez@upm.es'],
    ]

    with open('datos_ejemplo/profesores.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(datos_profesores)

    print("✅ profesores.csv creado (4 profesores)")


def mostrar_resumen():
    """Mostrar resumen de archivos creados"""
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE DATOS CREADOS")
    print("=" * 50)

    archivos = [
        ('alumnos.csv', '15 estudiantes en 4 asignaturas'),
        ('asignaturas.csv', '4 asignaturas con 9 laboratorios compatibles'),
        ('laboratorios.csv', '9 laboratorios en 4 edificios'),
        ('profesores.csv', '4 profesores con disponibilidad horaria')
    ]

    for archivo, descripcion in archivos:
        ruta = f'datos_ejemplo/{archivo}'
        if os.path.exists(ruta):
            tamaño = os.path.getsize(ruta)
            print(f"✅ {archivo:20} - {descripcion} ({tamaño} bytes)")
        else:
            print(f"❌ {archivo:20} - NO CREADO")

    print("\n🎯 PRÓXIMOS PASOS:")
    print("1. Ejecutar: python gui_labs_simple.py")
    print("2. Cargar los 4 archivos CSV desde 'datos_ejemplo/'")
    print("3. Probar la generación de horarios")
    print("\n💡 Los archivos están en: ./datos_ejemplo/")


def main():
    """Función principal"""
    print("🔬 CREANDO DATOS DE EJEMPLO PARA LAB SCHEDULING")
    print("=" * 50)

    try:
        crear_directorio_datos()
        crear_alumnos_csv()
        crear_asignaturas_csv()
        crear_laboratorios_csv()
        crear_profesores_csv()
        mostrar_resumen()

    except Exception as e:
        print(f"❌ Error creando datos: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())