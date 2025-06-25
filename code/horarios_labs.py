import pandas as pd
import xml.etree.ElementTree as ET
import multiprocessing as mp
from random import choice, shuffle
from copy import deepcopy
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path


def leer_configuracion():
    """Leer configuración desde XML"""
    config_dict = {}
    try:
        config = ET.parse('configuracion_labs.xml')
        root = config.getroot()

        for i in root:
            for j in i:
                config_dict[j.attrib['name']] = j.text
    except:
        # Configuración por defecto si no existe el archivo
        config_dict = {
            'hora_inicio': '8:00',
            'hora_fin': '20:00',
            'duracion_clase': '02:00',
            'peso_grupos_pares': '10',
            'peso_conflictos_alumnos': '20',
            'peso_disponibilidad_profesor': '15',
            'peso_capacidad_laboratorio': '25',
            'peso_compatibilidad_asignatura': '30'
        }

    return config_dict


def cargar_datos(path_alumnos, path_asignaturas, path_laboratorios, path_profesores, path_restricciones=None):
    """Cargar todos los archivos de datos"""
    try:
        # Cargar alumnos
        if path_alumnos.endswith('.csv'):
            df_alumnos = pd.read_csv(path_alumnos)
        else:
            df_alumnos = pd.read_excel(path_alumnos)

        # Cargar asignaturas
        if path_asignaturas.endswith('.csv'):
            df_asignaturas = pd.read_csv(path_asignaturas)
        else:
            df_asignaturas = pd.read_excel(path_asignaturas)

        # Cargar laboratorios
        if path_laboratorios.endswith('.csv'):
            df_laboratorios = pd.read_csv(path_laboratorios)
        else:
            df_laboratorios = pd.read_excel(path_laboratorios)

        # Cargar profesores
        if path_profesores.endswith('.csv'):
            df_profesores = pd.read_csv(path_profesores)
        else:
            df_profesores = pd.read_excel(path_profesores)

        # Cargar restricciones (opcional)
        df_restricciones = None
        if path_restricciones:
            if path_restricciones.endswith('.csv'):
                df_restricciones = pd.read_csv(path_restricciones)
            else:
                df_restricciones = pd.read_excel(path_restricciones)

        return df_alumnos, df_asignaturas, df_laboratorios, df_profesores, df_restricciones, 0, "Datos cargados correctamente"

    except Exception as e:
        return None, None, None, None, None, 2, f"Error cargando datos: {str(e)}"


def generar_grupos_optimizados(df_alumnos, capacidad_maxima, preferir_pares=True):
    """Generar grupos optimizados por asignatura"""
    grupos_dict = {}

    # Agrupar alumnos por asignatura
    asignaturas = df_alumnos['asignatura'].unique()

    for asignatura in asignaturas:
        alumnos_asignatura = df_alumnos[df_alumnos['asignatura'] == asignatura]
        total_alumnos = len(alumnos_asignatura)

        # Calcular número de grupos
        num_grupos = (total_alumnos + capacidad_maxima - 1) // capacidad_maxima

        if preferir_pares and num_grupos > 1:
            # Intentar división en grupos pares
            alumnos_por_grupo = total_alumnos // num_grupos
            resto = total_alumnos % num_grupos

            grupos = []
            inicio = 0

            for i in range(num_grupos):
                tamaño_grupo = alumnos_por_grupo + (1 if i < resto else 0)
                grupo_alumnos = alumnos_asignatura.iloc[inicio:inicio + tamaño_grupo]
                grupos.append({
                    'grupo_id': f"{asignatura}_G{i + 1}",
                    'asignatura': asignatura,
                    'alumnos': grupo_alumnos.to_dict('records'),
                    'num_alumnos': tamaño_grupo
                })
                inicio += tamaño_grupo
        else:
            # División simple
            grupos = []
            for i in range(0, total_alumnos, capacidad_maxima):
                grupo_alumnos = alumnos_asignatura.iloc[i:i + capacidad_maxima]
                grupos.append({
                    'grupo_id': f"{asignatura}_G{len(grupos) + 1}",
                    'asignatura': asignatura,
                    'alumnos': grupo_alumnos.to_dict('records'),
                    'num_alumnos': len(grupo_alumnos)
                })

        grupos_dict[asignatura] = grupos

    return grupos_dict


def generar_franjas_horarias(hora_inicio, hora_fin, duracion_clase):
    """Generar franjas horarias disponibles"""
    franjas = []
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']

    inicio = datetime.strptime(hora_inicio, '%H:%M')
    fin = datetime.strptime(hora_fin, '%H:%M')
    duracion = datetime.strptime(duracion_clase, '%H:%M')
    time_zero = datetime.strptime('00:00', '%H:%M')

    for dia in dias_semana:
        hora_actual = inicio
        while hora_actual + (duracion - time_zero) <= fin:
            hora_fin_franja = hora_actual + (duracion - time_zero)
            franjas.append({
                'dia': dia,
                'hora_inicio': hora_actual.strftime('%H:%M'),
                'hora_fin': hora_fin_franja.strftime('%H:%M'),
                'disponible': True
            })
            hora_actual = hora_fin_franja

    return franjas


def verificar_compatibilidad_laboratorio(asignatura, laboratorio, df_asignaturas):
    """Verificar si una asignatura es compatible con un laboratorio"""
    compatibilidad = df_asignaturas[
        (df_asignaturas['asignatura'] == asignatura) &
        (df_asignaturas['laboratorio'] == laboratorio)
        ]
    return len(compatibilidad) > 0


def detectar_conflictos_alumnos(grupo1, grupo2, horario_propuesto):
    """Detectar si dos grupos tienen alumnos en común"""
    alumnos_g1 = {alumno['dni'] for alumno in grupo1['alumnos']}
    alumnos_g2 = {alumno['dni'] for alumno in grupo2['alumnos']}

    # Si hay alumnos comunes y mismo horario, hay conflicto
    if alumnos_g1.intersection(alumnos_g2) and horario_propuesto['dia'] == horario_propuesto['dia']:
        return True
    return False


def funcion_objetivo(asignacion, grupos_dict, df_profesores, df_laboratorios, config):
    """Función objetivo para optimizar asignaciones"""
    peso_grupos_pares = int(config['peso_grupos_pares'])
    peso_conflictos_alumnos = int(config['peso_conflictos_alumnos'])
    peso_disponibilidad_profesor = int(config['peso_disponibilidad_profesor'])
    peso_capacidad_laboratorio = int(config['peso_capacidad_laboratorio'])
    peso_compatibilidad_asignatura = int(config['peso_compatibilidad_asignatura'])

    penalizacion = 0

    # Penalización por grupos impares
    for asignatura in grupos_dict:
        if len(grupos_dict[asignatura]) % 2 != 0:
            penalizacion += peso_grupos_pares

    # Penalización por conflictos de alumnos
    for i, asig1 in enumerate(asignacion):
        for j, asig2 in enumerate(asignacion):
            if i != j and asig1['dia'] == asig2['dia'] and asig1['hora_inicio'] == asig2['hora_inicio']:
                if detectar_conflictos_alumnos(asig1, asig2, asig1):
                    penalizacion += peso_conflictos_alumnos

    # Penalización por capacidad de laboratorio
    for asig in asignacion:
        capacidad_lab = df_laboratorios[df_laboratorios['nombre'] == asig['laboratorio']]['capacidad'].iloc[0]
        if asig['num_alumnos'] > capacidad_lab:
            penalizacion += peso_capacidad_laboratorio * (asig['num_alumnos'] - capacidad_lab)

    return penalizacion


def asignar_horarios_optimizado(grupos_dict, df_profesores, df_laboratorios, df_asignaturas, config,
                                progress_callback=None):
    """Algoritmo principal de asignación de horarios"""
    franjas_disponibles = generar_franjas_horarias(
        config['hora_inicio'],
        config['hora_fin'],
        config['duracion_clase']
    )

    asignaciones = []
    franjas_ocupadas = {}

    # Ordenar grupos por número de alumnos (descendente)
    todos_grupos = []
    for asignatura, grupos in grupos_dict.items():
        todos_grupos.extend(grupos)

    todos_grupos.sort(key=lambda x: x['num_alumnos'], reverse=True)

    total_grupos = len(todos_grupos)
    progreso_actual = 0

    for grupo in todos_grupos:
        mejor_asignacion = None
        mejor_penalizacion = float('inf')

        # Buscar mejor laboratorio y horario para este grupo
        laboratorios_compatibles = df_asignaturas[
            df_asignaturas['asignatura'] == grupo['asignatura']
            ]['laboratorio'].unique()

        for laboratorio in laboratorios_compatibles:
            capacidad_lab = df_laboratorios[df_laboratorios['nombre'] == laboratorio]['capacidad'].iloc[0]

            if grupo['num_alumnos'] <= capacidad_lab:
                for franja in franjas_disponibles:
                    key_franja = f"{laboratorio}_{franja['dia']}_{franja['hora_inicio']}"

                    if key_franja not in franjas_ocupadas:
                        # Crear asignación temporal
                        asignacion_temp = asignaciones + [{
                            'grupo_id': grupo['grupo_id'],
                            'asignatura': grupo['asignatura'],
                            'laboratorio': laboratorio,
                            'dia': franja['dia'],
                            'hora_inicio': franja['hora_inicio'],
                            'hora_fin': franja['hora_fin'],
                            'num_alumnos': grupo['num_alumnos'],
                            'alumnos': grupo['alumnos']
                        }]

                        # Calcular penalización
                        penalizacion = funcion_objetivo(asignacion_temp, grupos_dict, df_profesores, df_laboratorios,
                                                        config)

                        if penalizacion < mejor_penalizacion:
                            mejor_penalizacion = penalizacion
                            mejor_asignacion = {
                                'grupo_id': grupo['grupo_id'],
                                'asignatura': grupo['asignatura'],
                                'laboratorio': laboratorio,
                                'dia': franja['dia'],
                                'hora_inicio': franja['hora_inicio'],
                                'hora_fin': franja['hora_fin'],
                                'num_alumnos': grupo['num_alumnos'],
                                'alumnos': grupo['alumnos']
                            }

        if mejor_asignacion:
            asignaciones.append(mejor_asignacion)
            key_franja = f"{mejor_asignacion['laboratorio']}_{mejor_asignacion['dia']}_{mejor_asignacion['hora_inicio']}"
            franjas_ocupadas[key_franja] = True

        # Actualizar progreso
        progreso_actual += 1
        if progress_callback:
            progress_callback(int((progreso_actual / total_grupos) * 100))

    return asignaciones


def exportar_horarios(asignaciones, formato='excel'):
    """Exportar horarios a Excel/CSV"""
    df_horarios = pd.DataFrame(asignaciones)

    if formato == 'excel':
        output_path = 'horarios_laboratorios.xlsx'
        df_horarios.to_excel(output_path, index=False)
    else:
        output_path = 'horarios_laboratorios.csv'
        df_horarios.to_csv(output_path, index=False)

    return output_path


def programar_laboratorios(path_alumnos, path_asignaturas, path_laboratorios, path_profesores,
                           path_restricciones=None, parametros=None, progress_callback=None):
    """Función principal de programación de laboratorios"""

    try:
        # Leer configuración
        config = leer_configuracion()

        if progress_callback:
            progress_callback(10)

        # Cargar datos
        df_alumnos, df_asignaturas, df_laboratorios, df_profesores, df_restricciones, cod_error, msje_error = cargar_datos(
            path_alumnos, path_asignaturas, path_laboratorios, path_profesores, path_restricciones
        )

        if cod_error != 0:
            return cod_error, msje_error

        if progress_callback:
            progress_callback(25)

        # Generar grupos optimizados
        grupos_dict = generar_grupos_optimizados(
            df_alumnos,
            parametros.get('capacidad_maxima', 24),
            parametros.get('grupos_pares', True)
        )

        if progress_callback:
            progress_callback(40)

        # Asignar horarios
        asignaciones = asignar_horarios_optimizado(
            grupos_dict, df_profesores, df_laboratorios, df_asignaturas, config, progress_callback
        )

        if progress_callback:
            progress_callback(80)

        # Exportar resultados
        output_path = exportar_horarios(asignaciones)

        if progress_callback:
            progress_callback(100)

        # Estadísticas finales
        total_grupos = sum(len(grupos) for grupos in grupos_dict.values())
        grupos_asignados = len(asignaciones)

        mensaje_resultado = f"""
        ✅ PROGRAMACIÓN COMPLETADA

        📊 Estadísticas:
        • Total de grupos generados: {total_grupos}
        • Grupos con horario asignado: {grupos_asignados}
        • Porcentaje de éxito: {(grupos_asignados / total_grupos) * 100:.1f}%

        📁 Archivo generado: {output_path}

        {f"⚠️ {total_grupos - grupos_asignados} grupos sin asignar" if grupos_asignados < total_grupos else ""}
        """

        return 0, mensaje_resultado

    except Exception as e:
        return 2, f"Error en la programación de laboratorios: {str(e)}"


if __name__ == "__main__":
    # Test básico
    print("Motor de scheduling de laboratorios - Test")
    config = leer_configuracion()
    print(f"Configuración cargada: {len(config)} parámetros")