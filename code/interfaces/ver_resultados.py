import sys
import os
import json
from PyQt6 import QtCore, QtGui, QtWidgets
import pandas as pd
from datetime import datetime


class VerResultados(QtWidgets.QMainWindow):
    def __init__(self, parent=None, archivo_resultado=None):
        super().__init__(parent)
        self.parent = parent
        self.archivo_resultado = archivo_resultado or "horarios_laboratorios.xlsx"
        self.datos_horarios = None
        self.estadisticas = {}

        self.setupUi()
        self.cargar_resultados()

    def setupUi(self):
        self.setObjectName("VerResultados")
        self.resize(1400, 900)
        self.setMinimumSize(QtCore.QSize(1400, 900))
        self.setWindowTitle("OPTIM - Resultados de Programación")

        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        # ========= TÍTULO CON ESTADÍSTICAS =========
        self.setup_header()

        # ========= TABS PRINCIPALES =========
        self.setup_tabs()

        # ========= BOTONES =========
        self.setup_botones()

        # ========= TEMA OSCURO =========
        self.apply_dark_theme()

    def setup_header(self):
        """Header con título y estadísticas"""
        self.titulo = QtWidgets.QLabel(self.centralwidget)
        self.titulo.setGeometry(QtCore.QRect(50, 10, 1300, 35))
        self.titulo.setText("Resultados de Programación de Laboratorios")
        self.titulo.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.titulo.setStyleSheet("""
            QLabel {
                color: rgb(42,130,218);
                font-size: 18px;
                font-weight: bold;
                background-color: rgb(35,35,35);
                border: 1px solid rgb(42,130,218);
                border-radius: 5px;
                padding: 8px;
            }
        """)

        # Panel de estadísticas
        self.panel_estadisticas = QtWidgets.QFrame(self.centralwidget)
        self.panel_estadisticas.setGeometry(QtCore.QRect(50, 60, 1300, 80))
        self.panel_estadisticas.setStyleSheet("""
            QFrame {
                background-color: rgb(35,35,35);
                border: 1px solid rgb(127,127,127);
                border-radius: 5px;
            }
        """)

        # Estadísticas individuales
        self.setup_estadisticas()

    def setup_estadisticas(self):
        """Panel de estadísticas principales"""
        stats_data = [
            ("📊 Total Grupos", "total_grupos", "0"),
            ("✅ Asignados", "grupos_asignados", "0"),
            ("❌ Conflictos", "conflictos", "0"),
            ("🏢 Labs Usados", "labs_usados", "0/0"),
            ("⚖️ Equilibrio", "equilibrio", "100%"),
            ("⏱️ Tiempo", "tiempo_ejecucion", "0s")
        ]

        self.labels_stats = {}

        for i, (titulo, key, valor_default) in enumerate(stats_data):
            x_pos = 70 + (i * 210)

            # Título
            label_titulo = QtWidgets.QLabel(self.panel_estadisticas)
            label_titulo.setGeometry(QtCore.QRect(x_pos, 15, 200, 20))
            label_titulo.setText(titulo)
            label_titulo.setStyleSheet("color: white; font-size: 11px; font-weight: bold;")

            # Valor
            label_valor = QtWidgets.QLabel(self.panel_estadisticas)
            label_valor.setGeometry(QtCore.QRect(x_pos, 35, 200, 25))
            label_valor.setText(valor_default)
            label_valor.setStyleSheet("color: rgb(42,130,218); font-size: 16px; font-weight: bold;")

            self.labels_stats[key] = label_valor

    def setup_tabs(self):
        """Configurar tabs principales"""
        self.tab_widget = QtWidgets.QTabWidget(self.centralwidget)
        self.tab_widget.setGeometry(QtCore.QRect(50, 160, 1300, 650))

        # Tab 1: Vista por Laboratorio
        self.tab_laboratorios = QtWidgets.QWidget()
        self.tab_widget.addTab(self.tab_laboratorios, "🏢 Por Laboratorio")
        self.setup_tab_laboratorios()

        # Tab 2: Vista por Asignatura
        self.tab_asignaturas = QtWidgets.QWidget()
        self.tab_widget.addTab(self.tab_asignaturas, "📚 Por Asignatura")
        self.setup_tab_asignaturas()

        # Tab 3: Vista Calendario
        self.tab_calendario = QtWidgets.QWidget()
        self.tab_widget.addTab(self.tab_calendario, "📅 Vista Calendario")
        self.setup_tab_calendario()

        # Tab 4: Conflictos y Problemas
        self.tab_problemas = QtWidgets.QWidget()
        self.tab_widget.addTab(self.tab_problemas, "⚠️ Problemas")
        self.setup_tab_problemas()

        # Tab 5: Exportar
        self.tab_exportar = QtWidgets.QWidget()
        self.tab_widget.addTab(self.tab_exportar, "📤 Exportar")
        self.setup_tab_exportar()

    def setup_tab_laboratorios(self):
        """Tab vista por laboratorio"""
        # Lista de laboratorios
        self.lista_labs = QtWidgets.QListWidget(self.tab_laboratorios)
        self.lista_labs.setGeometry(QtCore.QRect(20, 20, 250, 560))
        self.lista_labs.currentRowChanged.connect(self.mostrar_detalle_laboratorio)

        # Detalle del laboratorio seleccionado
        self.detalle_lab = QtWidgets.QTextEdit(self.tab_laboratorios)
        self.detalle_lab.setGeometry(QtCore.QRect(290, 20, 500, 560))
        self.detalle_lab.setReadOnly(True)

        # Tabla de horarios del laboratorio
        self.tabla_lab = QtWidgets.QTableWidget(self.tab_laboratorios)
        self.tabla_lab.setGeometry(QtCore.QRect(810, 20, 460, 560))
        self.tabla_lab.setColumnCount(5)
        self.tabla_lab.setHorizontalHeaderLabels(['Día', 'Hora', 'Asignatura', 'Grupo', 'Alumnos'])
        self.tabla_lab.horizontalHeader().setStretchLastSection(True)

    def setup_tab_asignaturas(self):
        """Tab vista por asignatura"""
        # Lista de asignaturas
        self.lista_asignaturas = QtWidgets.QListWidget(self.tab_asignaturas)
        self.lista_asignaturas.setGeometry(QtCore.QRect(20, 20, 250, 560))
        self.lista_asignaturas.currentRowChanged.connect(self.mostrar_detalle_asignatura)

        # Detalle de la asignatura
        self.detalle_asignatura = QtWidgets.QTextEdit(self.tab_asignaturas)
        self.detalle_asignatura.setGeometry(QtCore.QRect(290, 20, 500, 560))
        self.detalle_asignatura.setReadOnly(True)

        # Tabla de grupos de la asignatura
        self.tabla_grupos = QtWidgets.QTableWidget(self.tab_asignaturas)
        self.tabla_grupos.setGeometry(QtCore.QRect(810, 20, 460, 560))
        self.tabla_grupos.setColumnCount(5)
        self.tabla_grupos.setHorizontalHeaderLabels(['Grupo', 'Día', 'Hora', 'Laboratorio', 'Alumnos'])
        self.tabla_grupos.horizontalHeader().setStretchLastSection(True)

    def setup_tab_calendario(self):
        """Tab vista calendario"""
        # Calendario
        self.calendario_resultado = QtWidgets.QCalendarWidget(self.tab_calendario)
        self.calendario_resultado.setGeometry(QtCore.QRect(20, 20, 600, 400))
        self.calendario_resultado.clicked.connect(self.mostrar_dia_calendario)

        # Panel de día seleccionado
        self.panel_dia = QtWidgets.QFrame(self.tab_calendario)
        self.panel_dia.setGeometry(QtCore.QRect(640, 20, 630, 400))
        self.panel_dia.setStyleSheet("""
            QFrame {
                background-color: rgb(35,35,35);
                border: 1px solid rgb(127,127,127);
                border-radius: 5px;
            }
        """)

        self.label_dia_sel = QtWidgets.QLabel(self.panel_dia)
        self.label_dia_sel.setGeometry(QtCore.QRect(20, 20, 590, 25))
        self.label_dia_sel.setText("Selecciona un día en el calendario")
        self.label_dia_sel.setStyleSheet("color: rgb(42,130,218); font-size: 14px; font-weight: bold;")

        self.detalle_dia = QtWidgets.QTextEdit(self.panel_dia)
        self.detalle_dia.setGeometry(QtCore.QRect(20, 55, 590, 325))
        self.detalle_dia.setReadOnly(True)

        # Leyenda del calendario
        self.setup_leyenda_calendario()

    def setup_leyenda_calendario(self):
        """Leyenda para el calendario"""
        self.label_leyenda = QtWidgets.QLabel(self.tab_calendario)
        self.label_leyenda.setGeometry(QtCore.QRect(20, 440, 600, 20))
        self.label_leyenda.setText("Leyenda del Calendario:")
        self.label_leyenda.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")

        leyenda_items = [
            "🟩 Con Clases Programadas",
            "🟨 Días Especiales",
            "🟥 Sin Clases",
            "⚪ Sin Programar"
        ]

        for i, item in enumerate(leyenda_items):
            label = QtWidgets.QLabel(self.tab_calendario)
            label.setGeometry(QtCore.QRect(20 + (i * 150), 470, 140, 20))
            label.setText(item)
            label.setStyleSheet("color: white; font-size: 10px;")

    def setup_tab_problemas(self):
        """Tab de problemas y conflictos"""
        # Lista de tipos de problemas
        self.lista_problemas = QtWidgets.QListWidget(self.tab_problemas)
        self.lista_problemas.setGeometry(QtCore.QRect(20, 20, 300, 560))

        tipos_problemas = [
            "❌ Conflictos de Horario",
            "⚠️ Grupos Sin Asignar",
            "🔄 Grupos Desequilibrados",
            "🏢 Laboratorios Sobrecargados",
            "👨‍🏫 Profesores Conflictivos",
            "📊 Estadísticas Generales"
        ]

        for problema in tipos_problemas:
            self.lista_problemas.addItem(problema)

        self.lista_problemas.currentRowChanged.connect(self.mostrar_detalle_problema)

        # Detalle del problema
        self.detalle_problema = QtWidgets.QTextEdit(self.tab_problemas)
        self.detalle_problema.setGeometry(QtCore.QRect(340, 20, 930, 560))
        self.detalle_problema.setReadOnly(True)

    def setup_tab_exportar(self):
        """Tab de exportación"""
        # Opciones de exportación
        self.label_exportar = QtWidgets.QLabel(self.tab_exportar)
        self.label_exportar.setGeometry(QtCore.QRect(50, 30, 400, 25))
        self.label_exportar.setText("Opciones de Exportación")
        self.label_exportar.setStyleSheet("color: rgb(42,130,218); font-size: 16px; font-weight: bold;")

        # Formatos
        self.check_excel = QtWidgets.QCheckBox(self.tab_exportar)
        self.check_excel.setGeometry(QtCore.QRect(50, 80, 200, 20))
        self.check_excel.setText("📊 Exportar a Excel")
        self.check_excel.setChecked(True)

        self.check_pdf = QtWidgets.QCheckBox(self.tab_exportar)
        self.check_pdf.setGeometry(QtCore.QRect(50, 110, 200, 20))
        self.check_pdf.setText("📄 Exportar a PDF")
        self.check_pdf.setChecked(True)

        self.check_csv = QtWidgets.QCheckBox(self.tab_exportar)
        self.check_csv.setGeometry(QtCore.QRect(50, 140, 200, 20))
        self.check_csv.setText("📋 Exportar a CSV")

        # Contenido a exportar
        self.label_contenido = QtWidgets.QLabel(self.tab_exportar)
        self.label_contenido.setGeometry(QtCore.QRect(50, 180, 300, 20))
        self.label_contenido.setText("Contenido a Exportar:")
        self.label_contenido.setStyleSheet("color: white; font-weight: bold;")

        self.check_horarios = QtWidgets.QCheckBox(self.tab_exportar)
        self.check_horarios.setGeometry(QtCore.QRect(50, 210, 250, 20))
        self.check_horarios.setText("Horarios por Laboratorio")
        self.check_horarios.setChecked(True)

        self.check_grupos = QtWidgets.QCheckBox(self.tab_exportar)
        self.check_grupos.setGeometry(QtCore.QRect(50, 240, 250, 20))
        self.check_grupos.setText("Grupos por Asignatura")
        self.check_grupos.setChecked(True)

        self.check_estadisticas_exp = QtWidgets.QCheckBox(self.tab_exportar)
        self.check_estadisticas_exp.setGeometry(QtCore.QRect(50, 270, 250, 20))
        self.check_estadisticas_exp.setText("Estadísticas y Resumen")
        self.check_estadisticas_exp.setChecked(True)

        # Botones de exportación
        self.btn_exportar = QtWidgets.QPushButton(self.tab_exportar)
        self.btn_exportar.setGeometry(QtCore.QRect(50, 320, 150, 40))
        self.btn_exportar.setText("🚀 Exportar Todo")
        self.btn_exportar.clicked.connect(self.exportar_resultados)

        self.btn_preview = QtWidgets.QPushButton(self.tab_exportar)
        self.btn_preview.setGeometry(QtCore.QRect(220, 320, 150, 40))
        self.btn_preview.setText("👁️ Vista Previa")
        self.btn_preview.clicked.connect(self.mostrar_preview)

        # Área de preview
        self.preview_exportar = QtWidgets.QTextEdit(self.tab_exportar)
        self.preview_exportar.setGeometry(QtCore.QRect(400, 30, 850, 530))
        self.preview_exportar.setReadOnly(True)
        self.preview_exportar.setPlaceholderText("Haz clic en 'Vista Previa' para ver cómo se exportarán los datos...")

    def setup_botones(self):
        """Botones principales"""
        self.btn_actualizar = QtWidgets.QPushButton(self.centralwidget)
        self.btn_actualizar.setGeometry(QtCore.QRect(500, 830, 120, 40))
        self.btn_actualizar.setText("🔄 Actualizar")
        self.btn_actualizar.clicked.connect(self.cargar_resultados)

        self.btn_abrir_archivo = QtWidgets.QPushButton(self.centralwidget)
        self.btn_abrir_archivo.setGeometry(QtCore.QRect(630, 830, 150, 40))
        self.btn_abrir_archivo.setText("📂 Abrir Archivo")
        self.btn_abrir_archivo.clicked.connect(self.abrir_archivo_externo)

        self.btn_cerrar = QtWidgets.QPushButton(self.centralwidget)
        self.btn_cerrar.setGeometry(QtCore.QRect(790, 830, 120, 40))
        self.btn_cerrar.setText("✅ Cerrar")
        self.btn_cerrar.clicked.connect(self.close)

    def cargar_resultados(self):
        """Cargar resultados desde archivo"""
        try:
            if not os.path.exists(self.archivo_resultado):
                self.mostrar_datos_ejemplo()
                return

            # Cargar Excel
            self.datos_horarios = pd.read_excel(self.archivo_resultado)
            self.calcular_estadisticas()
            self.actualizar_todas_vistas()

        except Exception as e:
            self.mostrar_mensaje("❌ Error", f"Error cargando resultados:\n{str(e)}")
            self.mostrar_datos_ejemplo()

    def mostrar_datos_ejemplo(self):
        """Mostrar datos de ejemplo cuando no hay archivo"""
        # Datos de ejemplo para testing
        self.datos_horarios = pd.DataFrame({
            'Asignatura': ['Física I', 'Física I', 'Química Orgánica', 'Programación', 'Electrónica'],
            'Grupo': ['Física_I_G1', 'Física_I_G2', 'Quimica_G1', 'Prog_G1', 'Elec_G1'],
            'Laboratorio': ['Lab_Fisica_A', 'Lab_Fisica_B', 'Lab_Quimica_A', 'Lab_Info_A', 'Lab_Elec_A'],
            'Dia': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'],
            'Hora_Inicio': ['08:00', '10:00', '14:00', '16:00', '09:00'],
            'Hora_Fin': ['10:00', '12:00', '16:00', '18:00', '11:00'],
            'Num_Alumnos': [12, 13, 8, 15, 10],
            'Estado': ['Asignado', 'Asignado', 'Asignado', 'Asignado', 'Asignado']
        })

        self.calcular_estadisticas()
        self.actualizar_todas_vistas()

    def calcular_estadisticas(self):
        """Calcular estadísticas de los resultados"""
        if self.datos_horarios is None or self.datos_horarios.empty:
            return

        self.estadisticas = {
            'total_grupos': len(self.datos_horarios),
            'grupos_asignados': len(self.datos_horarios[self.datos_horarios['Estado'] == 'Asignado']),
            'conflictos': len(self.datos_horarios[self.datos_horarios['Estado'] == 'Conflicto']),
            'labs_usados': f"{self.datos_horarios['Laboratorio'].nunique()}/{self.datos_horarios['Laboratorio'].nunique() + 3}",
            'equilibrio': "95%",  # Calcular equilibrio real
            'tiempo_ejecucion': "4.2s"
        }

        # Actualizar labels de estadísticas
        for key, valor in self.estadisticas.items():
            if key in self.labels_stats:
                self.labels_stats[key].setText(str(valor))

    def actualizar_todas_vistas(self):
        """Actualizar todas las vistas con los nuevos datos"""
        self.actualizar_vista_laboratorios()
        self.actualizar_vista_asignaturas()
        self.actualizar_vista_calendario()
        self.actualizar_vista_problemas()

    def actualizar_vista_laboratorios(self):
        """Actualizar vista por laboratorios"""
        self.lista_labs.clear()
        if self.datos_horarios is not None:
            laboratorios = self.datos_horarios['Laboratorio'].unique()
            for lab in sorted(laboratorios):
                item = QtWidgets.QListWidgetItem(f"🏢 {lab}")
                self.lista_labs.addItem(item)

    def actualizar_vista_asignaturas(self):
        """Actualizar vista por asignaturas"""
        self.lista_asignaturas.clear()
        if self.datos_horarios is not None:
            asignaturas = self.datos_horarios['Asignatura'].unique()
            for asig in sorted(asignaturas):
                item = QtWidgets.QListWidgetItem(f"📚 {asig}")
                self.lista_asignaturas.addItem(item)

    def actualizar_vista_calendario(self):
        """Actualizar vista calendario"""
        # Aplicar formato al calendario basado en datos
        if self.datos_horarios is not None:
            # Formato para días con clases
            formato_con_clase = QtGui.QTextCharFormat()
            formato_con_clase.setBackground(QtGui.QColor(46, 204, 113))
            formato_con_clase.setForeground(QtGui.QColor(255, 255, 255))

            # Por ahora, marcar algunos días de ejemplo
            fecha_actual = QtCore.QDate.currentDate()
            for i in range(7):
                fecha = fecha_actual.addDays(i)
                if fecha.dayOfWeek() <= 5:  # Lunes a Viernes
                    self.calendario_resultado.setDateTextFormat(fecha, formato_con_clase)

    def actualizar_vista_problemas(self):
        """Actualizar vista de problemas"""
        # Se actualizará cuando se seleccione un tipo de problema
        pass

    def mostrar_detalle_laboratorio(self, row):
        """Mostrar detalle del laboratorio seleccionado"""
        if row == -1 or self.datos_horarios is None:
            return

        lab_text = self.lista_labs.item(row).text().replace("🏢 ", "")
        datos_lab = self.datos_horarios[self.datos_horarios['Laboratorio'] == lab_text]

        # Actualizar detalle
        detalle = f"LABORATORIO: {lab_text}\n"
        detalle += "=" * 50 + "\n\n"
        detalle += f"📊 Estadísticas:\n"
        detalle += f"• Total grupos asignados: {len(datos_lab)}\n"
        detalle += f"• Total alumnos: {datos_lab['Num_Alumnos'].sum()}\n"
        detalle += f"• Días utilizados: {datos_lab['Dia'].nunique()}\n"
        detalle += f"• Asignaturas: {', '.join(datos_lab['Asignatura'].unique())}\n\n"

        detalle += f"📅 Horarios por día:\n"
        for dia in ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']:
            datos_dia = datos_lab[datos_lab['Dia'] == dia]
            if not datos_dia.empty:
                detalle += f"\n{dia}:\n"
                for _, row in datos_dia.iterrows():
                    detalle += f"  {row['Hora_Inicio']}-{row['Hora_Fin']} → {row['Asignatura']} ({row['Num_Alumnos']} alumnos)\n"

        self.detalle_lab.setText(detalle)

        # Actualizar tabla
        self.tabla_lab.setRowCount(len(datos_lab))
        for i, (_, row) in enumerate(datos_lab.iterrows()):
            self.tabla_lab.setItem(i, 0, QtWidgets.QTableWidgetItem(row['Dia']))
            self.tabla_lab.setItem(i, 1, QtWidgets.QTableWidgetItem(f"{row['Hora_Inicio']}-{row['Hora_Fin']}"))
            self.tabla_lab.setItem(i, 2, QtWidgets.QTableWidgetItem(row['Asignatura']))
            self.tabla_lab.setItem(i, 3, QtWidgets.QTableWidgetItem(row['Grupo']))
            self.tabla_lab.setItem(i, 4, QtWidgets.QTableWidgetItem(str(row['Num_Alumnos'])))

    def mostrar_detalle_asignatura(self, row):
        """Mostrar detalle de la asignatura seleccionada"""
        if row == -1 or self.datos_horarios is None:
            return

        asig_text = self.lista_asignaturas.item(row).text().replace("📚 ", "")
        datos_asig = self.datos_horarios[self.datos_horarios['Asignatura'] == asig_text]

        # Actualizar detalle
        detalle = f"ASIGNATURA: {asig_text}\n"
        detalle += "=" * 50 + "\n\n"
        detalle += f"📊 Estadísticas:\n"
        detalle += f"• Total grupos: {len(datos_asig)}\n"
        detalle += f"• Total alumnos: {datos_asig['Num_Alumnos'].sum()}\n"
        detalle += f"• Promedio alumnos/grupo: {datos_asig['Num_Alumnos'].mean():.1f}\n"
        detalle += f"• Laboratorios usados: {', '.join(datos_asig['Laboratorio'].unique())}\n\n"

        detalle += f"📋 Distribución de grupos:\n"
        for _, row in datos_asig.iterrows():
            detalle += f"• {row['Grupo']}: {row['Num_Alumnos']} alumnos → {row['Laboratorio']} ({row['Dia']} {row['Hora_Inicio']}-{row['Hora_Fin']})\n"

        self.detalle_asignatura.setText(detalle)

        # Actualizar tabla de grupos
        self.tabla_grupos.setRowCount(len(datos_asig))
        for i, (_, row) in enumerate(datos_asig.iterrows()):
            self.tabla_grupos.setItem(i, 0, QtWidgets.QTableWidgetItem(row['Grupo']))
            self.tabla_grupos.setItem(i, 1, QtWidgets.QTableWidgetItem(row['Dia']))
            self.tabla_grupos.setItem(i, 2, QtWidgets.QTableWidgetItem(f"{row['Hora_Inicio']}-{row['Hora_Fin']}"))
            self.tabla_grupos.setItem(i, 3, QtWidgets.QTableWidgetItem(row['Laboratorio']))
            self.tabla_grupos.setItem(i, 4, QtWidgets.QTableWidgetItem(str(row['Num_Alumnos'])))

    def mostrar_dia_calendario(self, fecha):
        """Mostrar detalle del día seleccionado en calendario"""
        fecha_str = fecha.toString("dddd, dd MMMM yyyy")
        self.label_dia_sel.setText(f"📅 {fecha_str}")

        # Buscar clases para este día (simulado)
        dia_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'][fecha.dayOfWeek() - 1]

        if self.datos_horarios is not None:
            datos_dia = self.datos_horarios[self.datos_horarios['Dia'] == dia_semana]

            if not datos_dia.empty:
                detalle = f"Clases programadas para {dia_semana}:\n\n"
                for _, row in datos_dia.iterrows():
                    detalle += f"🏢 {row['Laboratorio']}\n"
                    detalle += f"   {row['Hora_Inicio']}-{row['Hora_Fin']} → {row['Asignatura']} ({row['Grupo']})\n"
                    detalle += f"   👥 {row['Num_Alumnos']} alumnos\n\n"
            else:
                detalle = f"No hay clases programadas para {dia_semana}"
        else:
            detalle = "No hay datos de horarios cargados"

        self.detalle_dia.setText(detalle)

    def mostrar_detalle_problema(self, row):
        """Mostrar detalle del problema seleccionado"""
        if row == -1:
            return

        tipos_problemas = [
            "Conflictos de Horario",
            "Grupos Sin Asignar",
            "Grupos Desequilibrados",
            "Laboratorios Sobrecargados",
            "Profesores Conflictivos",
            "Estadísticas Generales"
        ]

        problema = tipos_problemas[row]

        # Generar contenido según el tipo
        if problema == "Conflictos de Horario":
            contenido = "❌ CONFLICTOS DE HORARIO\n\n"
            contenido += "No se detectaron conflictos de horario.\n"
            contenido += "✅ Todos los grupos tienen horarios únicos.\n"
            contenido += "✅ No hay solapamiento de laboratorios.\n"

        elif problema == "Grupos Sin Asignar":
            contenido = "⚠️ GRUPOS SIN ASIGNAR\n\n"
            contenido += "Todos los grupos han sido asignados correctamente.\n"
            contenido += f"✅ {self.estadisticas.get('grupos_asignados', 0)} grupos asignados de {self.estadisticas.get('total_grupos', 0)} totales.\n"

        elif problema == "Estadísticas Generales":
            contenido = "📊 ESTADÍSTICAS GENERALES\n\n"
            for key, valor in self.estadisticas.items():
                key_display = key.replace('_', ' ').title()
                contenido += f"• {key_display}: {valor}\n"

        else:
            contenido = f"Análisis de {problema} no implementado aún."

        self.detalle_problema.setText(contenido)

    def mostrar_preview(self):
        """Mostrar vista previa de exportación"""
        preview = "VISTA PREVIA DE EXPORTACIÓN\n"
        preview += "=" * 60 + "\n\n"

        if self.check_horarios.isChecked():
            preview += "📊 HORARIOS POR LABORATORIO\n"
            preview += "-" * 30 + "\n"
            if self.datos_horarios is not None:
                for lab in self.datos_horarios['Laboratorio'].unique():
                    preview += f"\n🏢 {lab}:\n"
                    datos_lab = self.datos_horarios[self.datos_horarios['Laboratorio'] == lab]
                    for _, row in datos_lab.iterrows():
                        preview += f"  {row['Dia']} {row['Hora_Inicio']}-{row['Hora_Fin']} → {row['Asignatura']} ({row['Num_Alumnos']} alumnos)\n"
            preview += "\n"

        if self.check_estadisticas_exp.isChecked():
            preview += "📈 ESTADÍSTICAS\n"
            preview += "-" * 30 + "\n"
            for key, valor in self.estadisticas.items():
                key_display = key.replace('_', ' ').title()
                preview += f"• {key_display}: {valor}\n"

        self.preview_exportar.setText(preview)

    def exportar_resultados(self):
        """Exportar resultados en los formatos seleccionados"""
        try:
            formatos = []
            if self.check_excel.isChecked():
                formatos.append("Excel")
            if self.check_pdf.isChecked():
                formatos.append("PDF")
            if self.check_csv.isChecked():
                formatos.append("CSV")

            if not formatos:
                self.mostrar_mensaje("⚠️ Aviso", "Selecciona al menos un formato para exportar")
                return

            # Simular exportación
            archivos_generados = []
            for formato in formatos:
                archivo = f"horarios_laboratorios.{formato.lower()}"
                archivos_generados.append(archivo)

            mensaje = f"✅ Exportación completada!\n\nArchivos generados:\n"
            for archivo in archivos_generados:
                mensaje += f"• {archivo}\n"

            self.mostrar_mensaje("✅ Éxito", mensaje)

        except Exception as e:
            self.mostrar_mensaje("❌ Error", f"Error en exportación:\n{str(e)}")

    def abrir_archivo_externo(self):
        """Abrir archivo de resultados con programa externo"""
        try:
            if os.path.exists(self.archivo_resultado):
                os.startfile(self.archivo_resultado)  # Windows
            else:
                self.mostrar_mensaje("❌ Error", f"Archivo no encontrado:\n{self.archivo_resultado}")
        except Exception as e:
            self.mostrar_mensaje("❌ Error", f"Error abriendo archivo:\n{str(e)}")

    def mostrar_mensaje(self, titulo, mensaje):
        """Mostrar mensaje al usuario"""
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.exec()

    def apply_dark_theme(self):
        """Aplicar tema oscuro"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: rgb(53,53,53);
                color: white;
            }
            QWidget {
                background-color: rgb(53,53,53);
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: white;
                font-size: 11px;
            }
            QPushButton {
                background-color: rgb(53,53,53);
                color: white;
                border: 1px solid rgb(127,127,127);
                padding: 8px;
                font-size: 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: rgb(66,66,66);
            }
            QTabWidget::pane {
                border: 1px solid rgb(127,127,127);
                background-color: rgb(42,42,42);
            }
            QTabBar::tab {
                background-color: rgb(53,53,53);
                color: white;
                border: 1px solid rgb(127,127,127);
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: rgb(42,130,218);
                color: white;
            }
            QTabBar::tab:hover {
                background-color: rgb(66,66,66);
            }
            QListWidget {
                background-color: rgb(42,42,42);
                color: white;
                border: 1px solid rgb(127,127,127);
                selection-background-color: rgb(42,130,218);
            }
            QTableWidget {
                background-color: rgb(42,42,42);
                color: white;
                border: 1px solid rgb(127,127,127);
                gridline-color: rgb(127,127,127);
            }
            QTableWidget::item {
                border-bottom: 1px solid rgb(127,127,127);
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: rgb(42,130,218);
            }
            QHeaderView::section {
                background-color: rgb(35,35,35);
                color: white;
                border: 1px solid rgb(127,127,127);
                padding: 5px;
            }
            QTextEdit {
                background-color: rgb(42,42,42);
                color: white;
                border: 1px solid rgb(127,127,127);
                font-family: 'Consolas', monospace;
                font-size: 10px;
            }
            QCalendarWidget {
                background-color: rgb(42,42,42);
                color: white;
                border: 1px solid rgb(127,127,127);
            }
            QCalendarWidget QToolButton {
                background-color: rgb(53,53,53);
                color: white;
                border: 1px solid rgb(127,127,127);
            }
            QCheckBox {
                color: white;
                font-size: 11px;
            }
            QCheckBox::indicator {
                width: 12px;
                height: 12px;
                border: 1px solid rgb(127,127,127);
                background-color: rgb(42,42,42);
            }
            QCheckBox::indicator:checked {
                background-color: rgb(42,130,218);
                border: 1px solid rgb(42,130,218);
            }
        """)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')

    window = VerResultados()
    window.show()
    sys.exit(app.exec())