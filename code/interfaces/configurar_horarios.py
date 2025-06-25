import sys
import json
import os
from PyQt6 import QtCore, QtGui, QtWidgets
from datetime import datetime, timedelta


class ConfigurarHorarios(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.config_path = "config/horarios_semanal.json"
        self.horarios_data = {
            'Lunes': [],
            'Martes': [],
            'Miércoles': [],
            'Jueves': [],
            'Viernes': []
        }
        self.laboratorios_disponibles = []
        self.setupUi()
        self.cargar_configuracion()

    def setupUi(self):
        self.setObjectName("ConfigurarHorarios")
        self.resize(1000, 700)
        self.setMinimumSize(QtCore.QSize(1000, 700))
        self.setMaximumSize(QtCore.QSize(1000, 700))
        self.setWindowTitle("OPTIM - Configurar Horarios Semanales")

        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        # ========= TÍTULO =========
        self.titulo = QtWidgets.QLabel(self.centralwidget)
        self.titulo.setGeometry(QtCore.QRect(50, 10, 900, 35))
        self.titulo.setText("Configuración de Horarios Semanales de Laboratorio")
        self.titulo.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.titulo.setStyleSheet("""
            QLabel {
                color: rgb(42,130,218);
                font-size: 16px;
                font-weight: bold;
                background-color: rgb(35,35,35);
                border: 1px solid rgb(42,130,218);
                border-radius: 5px;
                padding: 8px;
            }
        """)

        # ========= INSTRUCCIONES =========
        self.instrucciones = QtWidgets.QLabel(self.centralwidget)
        self.instrucciones.setGeometry(QtCore.QRect(50, 60, 900, 40))
        self.instrucciones.setText(
            "Define los horarios de laboratorio para cada día de la semana. Añade franjas horarias y selecciona qué laboratorios están disponibles.")
        self.instrucciones.setWordWrap(True)
        self.instrucciones.setStyleSheet("color: white; font-size: 11px;")

        # ========= PANEL IZQUIERDO - LISTA DÍAS =========
        self.setup_panel_dias()

        # ========= PANEL CENTRO - CONFIGURACIÓN DÍA ACTUAL =========
        self.setup_panel_configuracion()

        # ========= PANEL DERECHO - VISTA PREVIA =========
        self.setup_panel_vista_previa()

        # ========= BOTONES INFERIORES =========
        self.setup_botones()

        # ========= APLICAR TEMA OSCURO =========
        self.apply_dark_theme()

        # Seleccionar Lunes por defecto
        self.lista_dias.setCurrentRow(0)
        self.cargar_dia_actual()

    def setup_panel_dias(self):
        """Panel izquierdo con lista de días"""
        self.label_dias = QtWidgets.QLabel(self.centralwidget)
        self.label_dias.setGeometry(QtCore.QRect(50, 120, 200, 20))
        self.label_dias.setText("Días de la Semana:")
        self.label_dias.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")

        self.lista_dias = QtWidgets.QListWidget(self.centralwidget)
        self.lista_dias.setGeometry(QtCore.QRect(50, 150, 200, 150))
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        for dia in dias:
            item = QtWidgets.QListWidgetItem(dia)
            item.setIcon(self.get_day_icon(dia))
            self.lista_dias.addItem(item)

        self.lista_dias.currentRowChanged.connect(self.cargar_dia_actual)

        # Laboratorios disponibles
        self.label_labs = QtWidgets.QLabel(self.centralwidget)
        self.label_labs.setGeometry(QtCore.QRect(50, 320, 200, 20))
        self.label_labs.setText("Laboratorios del Sistema:")
        self.label_labs.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")

        self.lista_laboratorios = QtWidgets.QTextEdit(self.centralwidget)
        self.lista_laboratorios.setGeometry(QtCore.QRect(50, 350, 200, 200))
        self.lista_laboratorios.setPlaceholderText("Lab_Fisica_A\nLab_Fisica_B\nLab_Quimica_A\n...")
        self.lista_laboratorios.textChanged.connect(self.actualizar_laboratorios_disponibles)

    def setup_panel_configuracion(self):
        """Panel central para configurar día actual"""
        self.dia_actual_label = QtWidgets.QLabel(self.centralwidget)
        self.dia_actual_label.setGeometry(QtCore.QRect(280, 120, 350, 25))
        self.dia_actual_label.setText("LUNES - Configuración")
        self.dia_actual_label.setStyleSheet("color: rgb(42,130,218); font-weight: bold; font-size: 14px;")

        # Tabla de horarios del día
        self.tabla_horarios = QtWidgets.QTableWidget(self.centralwidget)
        self.tabla_horarios.setGeometry(QtCore.QRect(280, 160, 350, 300))
        self.tabla_horarios.setColumnCount(3)
        self.tabla_horarios.setHorizontalHeaderLabels(['Inicio', 'Fin', 'Laboratorios'])
        self.tabla_horarios.horizontalHeader().setStretchLastSection(True)
        self.tabla_horarios.setColumnWidth(0, 80)
        self.tabla_horarios.setColumnWidth(1, 80)

        # Controles para añadir horario
        self.label_nuevo = QtWidgets.QLabel(self.centralwidget)
        self.label_nuevo.setGeometry(QtCore.QRect(280, 480, 350, 20))
        self.label_nuevo.setText("Añadir Nueva Franja Horaria:")
        self.label_nuevo.setStyleSheet("color: white; font-weight: bold; font-size: 11px;")

        # Hora inicio
        self.label_inicio = QtWidgets.QLabel(self.centralwidget)
        self.label_inicio.setGeometry(QtCore.QRect(280, 510, 80, 20))
        self.label_inicio.setText("Hora Inicio:")

        self.time_inicio = QtWidgets.QTimeEdit(self.centralwidget)
        self.time_inicio.setGeometry(QtCore.QRect(280, 535, 80, 25))
        self.time_inicio.setTime(QtCore.QTime(8, 0))
        self.time_inicio.setDisplayFormat("HH:mm")

        # Hora fin
        self.label_fin = QtWidgets.QLabel(self.centralwidget)
        self.label_fin.setGeometry(QtCore.QRect(370, 510, 80, 20))
        self.label_fin.setText("Hora Fin:")

        self.time_fin = QtWidgets.QTimeEdit(self.centralwidget)
        self.time_fin.setGeometry(QtCore.QRect(370, 535, 80, 25))
        self.time_fin.setTime(QtCore.QTime(10, 0))
        self.time_fin.setDisplayFormat("HH:mm")

        # Laboratorios para esta franja
        self.label_labs_franja = QtWidgets.QLabel(self.centralwidget)
        self.label_labs_franja.setGeometry(QtCore.QRect(460, 510, 170, 20))
        self.label_labs_franja.setText("Laboratorios disponibles:")

        self.combo_laboratorios = QtWidgets.QComboBox(self.centralwidget)
        self.combo_laboratorios.setGeometry(QtCore.QRect(460, 535, 170, 25))
        self.combo_laboratorios.setEditable(True)

        # Botones
        self.btn_anadir = QtWidgets.QPushButton(self.centralwidget)
        self.btn_anadir.setGeometry(QtCore.QRect(280, 575, 80, 30))
        self.btn_anadir.setText("➕ Añadir")
        self.btn_anadir.clicked.connect(self.anadir_horario)

        self.btn_eliminar = QtWidgets.QPushButton(self.centralwidget)
        self.btn_eliminar.setGeometry(QtCore.QRect(370, 575, 80, 30))
        self.btn_eliminar.setText("🗑️ Eliminar")
        self.btn_eliminar.clicked.connect(self.eliminar_horario)

        self.btn_limpiar = QtWidgets.QPushButton(self.centralwidget)
        self.btn_limpiar.setGeometry(QtCore.QRect(460, 575, 80, 30))
        self.btn_limpiar.setText("🧹 Limpiar")
        self.btn_limpiar.clicked.connect(self.limpiar_dia)

    def setup_panel_vista_previa(self):
        """Panel derecho con vista previa"""
        self.label_preview = QtWidgets.QLabel(self.centralwidget)
        self.label_preview.setGeometry(QtCore.QRect(660, 120, 290, 20))
        self.label_preview.setText("Vista Previa Semanal:")
        self.label_preview.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")

        self.vista_previa = QtWidgets.QTextEdit(self.centralwidget)
        self.vista_previa.setGeometry(QtCore.QRect(660, 150, 290, 400))
        self.vista_previa.setReadOnly(True)
        self.vista_previa.setStyleSheet("""
            QTextEdit {
                background-color: rgb(35,35,35);
                color: white;
                border: 1px solid rgb(42,130,218);
                font-family: 'Consolas', monospace;
                font-size: 10px;
            }
        """)

    def setup_botones(self):
        """Botones principales"""
        self.btn_guardar = QtWidgets.QPushButton(self.centralwidget)
        self.btn_guardar.setGeometry(QtCore.QRect(300, 630, 120, 40))
        self.btn_guardar.setText("💾 Guardar")
        self.btn_guardar.clicked.connect(self.guardar_configuracion)

        self.btn_cargar = QtWidgets.QPushButton(self.centralwidget)
        self.btn_cargar.setGeometry(QtCore.QRect(430, 630, 120, 40))
        self.btn_cargar.setText("📂 Cargar")
        self.btn_cargar.clicked.connect(self.cargar_configuracion)

        self.btn_cerrar = QtWidgets.QPushButton(self.centralwidget)
        self.btn_cerrar.setGeometry(QtCore.QRect(560, 630, 120, 40))
        self.btn_cerrar.setText("✅ Cerrar")
        self.btn_cerrar.clicked.connect(self.close)

    def get_day_icon(self, dia):
        """Iconos para días de la semana"""
        iconos = {
            'Lunes': '📅',
            'Martes': '📋',
            'Miércoles': '📊',
            'Jueves': '📈',
            'Viernes': '🎯'
        }
        # En PyQt6, creamos un QIcon simple
        return QtGui.QIcon()

    def actualizar_laboratorios_disponibles(self):
        """Actualizar lista de laboratorios disponibles"""
        texto = self.lista_laboratorios.toPlainText()
        self.laboratorios_disponibles = [lab.strip() for lab in texto.split('\n') if lab.strip()]

        # Actualizar combo
        self.combo_laboratorios.clear()
        self.combo_laboratorios.addItems(self.laboratorios_disponibles)

    def cargar_dia_actual(self):
        """Cargar configuración del día seleccionado"""
        if self.lista_dias.currentRow() == -1:
            return

        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        dia_actual = dias[self.lista_dias.currentRow()]

        self.dia_actual_label.setText(f"{dia_actual.upper()} - Configuración")

        # Limpiar tabla
        self.tabla_horarios.setRowCount(0)

        # Cargar horarios del día
        if dia_actual in self.horarios_data:
            for horario in self.horarios_data[dia_actual]:
                self.agregar_fila_tabla(horario['inicio'], horario['fin'], horario['laboratorios'])

        self.actualizar_vista_previa()

    def agregar_fila_tabla(self, inicio, fin, laboratorios):
        """Agregar fila a la tabla de horarios"""
        row = self.tabla_horarios.rowCount()
        self.tabla_horarios.insertRow(row)

        self.tabla_horarios.setItem(row, 0, QtWidgets.QTableWidgetItem(inicio))
        self.tabla_horarios.setItem(row, 1, QtWidgets.QTableWidgetItem(fin))
        self.tabla_horarios.setItem(row, 2, QtWidgets.QTableWidgetItem(', '.join(laboratorios)))

    def anadir_horario(self):
        """Añadir nueva franja horaria"""
        inicio = self.time_inicio.time().toString("HH:mm")
        fin = self.time_fin.time().toString("HH:mm")
        labs_texto = self.combo_laboratorios.currentText()

        if not labs_texto:
            self.mostrar_mensaje("⚠️ Aviso", "Selecciona al menos un laboratorio")
            return

        # Validar horarios
        if inicio >= fin:
            self.mostrar_mensaje("❌ Error", "La hora de inicio debe ser anterior a la hora de fin")
            return

        # Procesar laboratorios (puede ser lista separada por comas)
        laboratorios = [lab.strip() for lab in labs_texto.split(',')]

        # Añadir a tabla
        self.agregar_fila_tabla(inicio, fin, laboratorios)

        # Guardar en datos
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        dia_actual = dias[self.lista_dias.currentRow()]

        self.horarios_data[dia_actual].append({
            'inicio': inicio,
            'fin': fin,
            'laboratorios': laboratorios
        })

        # Actualizar vista previa
        self.actualizar_vista_previa()

        # Limpiar campos
        self.time_inicio.setTime(QtCore.QTime.fromString(fin, "HH:mm"))
        nueva_hora_fin = QtCore.QTime.fromString(fin, "HH:mm").addSecs(2 * 3600)  # +2 horas
        self.time_fin.setTime(nueva_hora_fin)

    def eliminar_horario(self):
        """Eliminar horario seleccionado"""
        fila_actual = self.tabla_horarios.currentRow()
        if fila_actual == -1:
            self.mostrar_mensaje("⚠️ Aviso", "Selecciona una fila para eliminar")
            return

        # Eliminar de tabla
        self.tabla_horarios.removeRow(fila_actual)

        # Eliminar de datos
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        dia_actual = dias[self.lista_dias.currentRow()]

        if fila_actual < len(self.horarios_data[dia_actual]):
            del self.horarios_data[dia_actual][fila_actual]

        self.actualizar_vista_previa()

    def limpiar_dia(self):
        """Limpiar todos los horarios del día actual"""
        reply = QtWidgets.QMessageBox.question(
            self,
            "Confirmar",
            "¿Estás seguro de que quieres limpiar todos los horarios de este día?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self.tabla_horarios.setRowCount(0)

            dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
            dia_actual = dias[self.lista_dias.currentRow()]
            self.horarios_data[dia_actual] = []

            self.actualizar_vista_previa()

    def actualizar_vista_previa(self):
        """Actualizar vista previa semanal"""
        preview_text = "HORARIOS SEMANALES DE LABORATORIO\n"
        preview_text += "=" * 40 + "\n\n"

        for dia, horarios in self.horarios_data.items():
            preview_text += f"📅 {dia.upper()}\n"
            if not horarios:
                preview_text += "   Sin horarios configurados\n"
            else:
                for horario in horarios:
                    labs = ", ".join(horario['laboratorios'][:2])  # Max 2 para preview
                    if len(horario['laboratorios']) > 2:
                        labs += f" (+{len(horario['laboratorios']) - 2})"
                    preview_text += f"   {horario['inicio']}-{horario['fin']} → {labs}\n"
            preview_text += "\n"

        # Estadísticas
        total_franjas = sum(len(horarios) for horarios in self.horarios_data.values())
        labs_usados = set()
        for horarios in self.horarios_data.values():
            for horario in horarios:
                labs_usados.update(horario['laboratorios'])

        preview_text += f"📊 ESTADÍSTICAS\n"
        preview_text += f"• Total franjas: {total_franjas}\n"
        preview_text += f"• Laboratorios usados: {len(labs_usados)}\n"
        preview_text += f"• Días configurados: {sum(1 for h in self.horarios_data.values() if h)}\n"

        self.vista_previa.setText(preview_text)

    def guardar_configuracion(self):
        """Guardar configuración en JSON"""
        try:
            # Crear directorio si no existe
            os.makedirs("config", exist_ok=True)

            # Datos a guardar
            config_data = {
                'horarios_semanal': self.horarios_data,
                'laboratorios_disponibles': self.laboratorios_disponibles,
                'fecha_creacion': datetime.now().isoformat(),
                'version': '1.0'
            }

            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            self.mostrar_mensaje("✅ Éxito", f"Configuración guardada en:\n{self.config_path}")

        except Exception as e:
            self.mostrar_mensaje("❌ Error", f"Error guardando configuración:\n{str(e)}")

    def cargar_configuracion(self):
        """Cargar configuración desde JSON"""
        try:
            if not os.path.exists(self.config_path):
                # Cargar configuración por defecto
                self.cargar_configuracion_defecto()
                return

            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            self.horarios_data = config_data.get('horarios_semanal', self.horarios_data)
            labs_guardados = config_data.get('laboratorios_disponibles', [])

            if labs_guardados:
                self.lista_laboratorios.setText('\n'.join(labs_guardados))

            # Recargar día actual
            self.cargar_dia_actual()

            self.mostrar_mensaje("✅ Éxito", "Configuración cargada correctamente")

        except Exception as e:
            self.mostrar_mensaje("❌ Error", f"Error cargando configuración:\n{str(e)}")
            self.cargar_configuracion_defecto()

    def cargar_configuracion_defecto(self):
        """Cargar configuración por defecto"""
        self.lista_laboratorios.setText("""Lab_Fisica_A
Lab_Fisica_B
Lab_Quimica_A
Lab_Quimica_B
Lab_Informatica_A
Lab_Informatica_B
Lab_Electronica_A
Lab_Electronica_B""")

        # Horario ejemplo para Lunes
        self.horarios_data['Lunes'] = [
            {'inicio': '08:00', 'fin': '10:00', 'laboratorios': ['Lab_Fisica_A', 'Lab_Quimica_A']},
            {'inicio': '10:00', 'fin': '12:00', 'laboratorios': ['Lab_Informatica_A']},
            {'inicio': '14:00', 'fin': '16:00', 'laboratorios': ['Lab_Electronica_A']}
        ]

        self.cargar_dia_actual()

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
            QTimeEdit, QComboBox {
                background-color: rgb(42,42,42);
                color: white;
                border: 1px solid rgb(127,127,127);
                padding: 5px;
            }
            QComboBox::drop-down {
                background-color: rgb(53,53,53);
            }
            QComboBox QAbstractItemView {
                background-color: rgb(42,42,42);
                color: white;
                selection-background-color: rgb(42,130,218);
            }
        """)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')

    window = ConfigurarHorarios()
    window.show()
    sys.exit(app.exec())