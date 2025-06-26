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
        """Configurar interfaz con mejor legibilidad"""
        # ========= VENTANA MÁS GRANDE =========
        self.setObjectName("ConfigurarHorarios")
        self.resize(1500, 900)  # Aumentado considerablemente
        self.setMinimumSize(QtCore.QSize(1500, 900))
        self.setWindowTitle("OPTIM - Configurar Horarios Semanales")

        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        # ========= TÍTULO MÁS GRANDE =========
        self.titulo = QtWidgets.QLabel(self.centralwidget)
        self.titulo.setGeometry(QtCore.QRect(50, 10, 1400, 50))
        self.titulo.setText("Configuración de Horarios Semanales de Laboratorio")
        self.titulo.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # ========= INSTRUCCIONES =========
        self.instrucciones = QtWidgets.QLabel(self.centralwidget)
        self.instrucciones.setGeometry(QtCore.QRect(50, 70, 1400, 40))
        self.instrucciones.setText(
            "Define los horarios de laboratorio para cada día de la semana. Añade franjas horarias y selecciona qué laboratorios están disponibles.")
        self.instrucciones.setWordWrap(True)

        # ========= CONFIGURACIÓN CON MEJOR ESPACIADO =========
        self.setup_panel_dias()
        self.setup_panel_configuracion()
        self.setup_panel_vista_previa()
        self.setup_botones()
        self.apply_dark_theme_legible()

        # Seleccionar Lunes por defecto
        self.lista_dias.setCurrentRow(0)
        self.cargar_dia_actual()

    def setup_panel_dias(self):
        """Panel izquierdo con lista de días - MÁS GRANDE"""
        y_start = 130

        self.label_dias = QtWidgets.QLabel(self.centralwidget)
        self.label_dias.setGeometry(QtCore.QRect(50, y_start, 250, 30))
        self.label_dias.setText("Días de la Semana:")

        self.lista_dias = QtWidgets.QListWidget(self.centralwidget)
        self.lista_dias.setGeometry(QtCore.QRect(50, y_start + 40, 250, 200))  # Más grande
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        for dia in dias:
            item = QtWidgets.QListWidgetItem(f"📅 {dia}")
            self.lista_dias.addItem(item)

        self.lista_dias.currentRowChanged.connect(self.cargar_dia_actual)

        # Laboratorios disponibles - MÁS GRANDE
        lab_y = y_start + 260
        self.label_labs = QtWidgets.QLabel(self.centralwidget)
        self.label_labs.setGeometry(QtCore.QRect(50, lab_y, 250, 30))
        self.label_labs.setText("Laboratorios del Sistema:")

        self.lista_laboratorios = QtWidgets.QTextEdit(self.centralwidget)
        self.lista_laboratorios.setGeometry(QtCore.QRect(50, lab_y + 40, 250, 250))  # Más grande
        self.lista_laboratorios.setPlaceholderText("Lab_Fisica_A\nLab_Fisica_B\nLab_Quimica_A\nLab_Informatica_A\n...")
        self.lista_laboratorios.textChanged.connect(self.actualizar_laboratorios_disponibles)

    def setup_panel_configuracion(self):
        """Panel central para configurar día actual - MÁS GRANDE"""
        x_panel = 330
        y_start = 130

        self.dia_actual_label = QtWidgets.QLabel(self.centralwidget)
        self.dia_actual_label.setGeometry(QtCore.QRect(x_panel, y_start, 500, 35))
        self.dia_actual_label.setText("LUNES - Configuración")

        # Tabla de horarios del día - MÁS GRANDE
        self.tabla_horarios = QtWidgets.QTableWidget(self.centralwidget)
        self.tabla_horarios.setGeometry(QtCore.QRect(x_panel, y_start + 50, 500, 350))  # Mucho más grande
        self.tabla_horarios.setColumnCount(3)
        self.tabla_horarios.setHorizontalHeaderLabels(['Inicio', 'Fin', 'Laboratorios'])
        self.tabla_horarios.horizontalHeader().setStretchLastSection(True)
        self.tabla_horarios.setColumnWidth(0, 100)
        self.tabla_horarios.setColumnWidth(1, 100)

        # Controles para añadir horario - MEJOR ESPACIADO
        control_y = y_start + 420
        self.label_nuevo = QtWidgets.QLabel(self.centralwidget)
        self.label_nuevo.setGeometry(QtCore.QRect(x_panel, control_y, 500, 25))
        self.label_nuevo.setText("Añadir Nueva Franja Horaria:")

        # Fila de controles con mejor espaciado
        row_y = control_y + 35

        # Hora inicio
        self.label_inicio = QtWidgets.QLabel(self.centralwidget)
        self.label_inicio.setGeometry(QtCore.QRect(x_panel, row_y, 80, 25))
        self.label_inicio.setText("Hora Inicio:")

        self.time_inicio = QtWidgets.QTimeEdit(self.centralwidget)
        self.time_inicio.setGeometry(QtCore.QRect(x_panel, row_y + 30, 100, 30))  # Más grande
        self.time_inicio.setTime(QtCore.QTime(8, 0))
        self.time_inicio.setDisplayFormat("HH:mm")

        # Hora fin
        self.label_fin = QtWidgets.QLabel(self.centralwidget)
        self.label_fin.setGeometry(QtCore.QRect(x_panel + 120, row_y, 80, 25))
        self.label_fin.setText("Hora Fin:")

        self.time_fin = QtWidgets.QTimeEdit(self.centralwidget)
        self.time_fin.setGeometry(QtCore.QRect(x_panel + 120, row_y + 30, 100, 30))  # Más grande
        self.time_fin.setTime(QtCore.QTime(10, 0))
        self.time_fin.setDisplayFormat("HH:mm")

        # Laboratorios para esta franja
        self.label_labs_franja = QtWidgets.QLabel(self.centralwidget)
        self.label_labs_franja.setGeometry(QtCore.QRect(x_panel + 240, row_y, 200, 25))
        self.label_labs_franja.setText("Laboratorios disponibles:")

        self.combo_laboratorios = QtWidgets.QComboBox(self.centralwidget)
        self.combo_laboratorios.setGeometry(QtCore.QRect(x_panel + 240, row_y + 30, 200, 30))  # Más grande
        self.combo_laboratorios.setEditable(True)

        # Botones - MÁS GRANDES
        button_y = row_y + 80
        self.btn_anadir = QtWidgets.QPushButton(self.centralwidget)
        self.btn_anadir.setGeometry(QtCore.QRect(x_panel, button_y, 100, 35))
        self.btn_anadir.setText("➕ Añadir")
        self.btn_anadir.clicked.connect(self.anadir_horario)

        self.btn_eliminar = QtWidgets.QPushButton(self.centralwidget)
        self.btn_eliminar.setGeometry(QtCore.QRect(x_panel + 120, button_y, 100, 35))
        self.btn_eliminar.setText("🗑️ Eliminar")
        self.btn_eliminar.clicked.connect(self.eliminar_horario)

        self.btn_limpiar = QtWidgets.QPushButton(self.centralwidget)
        self.btn_limpiar.setGeometry(QtCore.QRect(x_panel + 240, button_y, 100, 35))
        self.btn_limpiar.setText("🧹 Limpiar")
        self.btn_limpiar.clicked.connect(self.limpiar_dia)

    def setup_panel_vista_previa(self):
        """Panel derecho con vista previa - MÁS GRANDE"""
        x_preview = 860
        y_start = 130

        self.label_preview = QtWidgets.QLabel(self.centralwidget)
        self.label_preview.setGeometry(QtCore.QRect(x_preview, y_start, 580, 30))
        self.label_preview.setText("Vista Previa Semanal:")

        self.vista_previa = QtWidgets.QTextEdit(self.centralwidget)
        self.vista_previa.setGeometry(QtCore.QRect(x_preview, y_start + 40, 580, 600))  # Mucho más grande
        self.vista_previa.setReadOnly(True)

    def setup_botones(self):
        """Botones principales - MÁS GRANDES"""
        y_buttons = 800
        x_center = 650

        self.btn_guardar = QtWidgets.QPushButton(self.centralwidget)
        self.btn_guardar.setGeometry(QtCore.QRect(x_center, y_buttons, 140, 50))  # Más grandes
        self.btn_guardar.setText("💾 Guardar")
        self.btn_guardar.clicked.connect(self.guardar_configuracion)

        self.btn_cargar = QtWidgets.QPushButton(self.centralwidget)
        self.btn_cargar.setGeometry(QtCore.QRect(x_center + 160, y_buttons, 140, 50))
        self.btn_cargar.setText("📂 Cargar")
        self.btn_cargar.clicked.connect(self.cargar_configuracion)

        self.btn_cerrar = QtWidgets.QPushButton(self.centralwidget)
        self.btn_cerrar.setGeometry(QtCore.QRect(x_center + 320, y_buttons, 140, 50))
        self.btn_cerrar.setText("✅ Cerrar")
        self.btn_cerrar.clicked.connect(self.close)

    # ========= MÉTODOS FUNCIONALES =========

    def actualizar_laboratorios_disponibles(self):
        """Actualizar lista de laboratorios disponibles"""
        texto = self.lista_laboratorios.toPlainText()
        self.laboratorios_disponibles = [lab.strip() for lab in texto.split('\n') if lab.strip()]

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

        if inicio >= fin:
            self.mostrar_mensaje("❌ Error", "La hora de inicio debe ser anterior a la hora de fin")
            return

        laboratorios = [lab.strip() for lab in labs_texto.split(',')]

        self.agregar_fila_tabla(inicio, fin, laboratorios)

        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        dia_actual = dias[self.lista_dias.currentRow()]

        self.horarios_data[dia_actual].append({
            'inicio': inicio,
            'fin': fin,
            'laboratorios': laboratorios
        })

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

        self.tabla_horarios.removeRow(fila_actual)

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
        preview_text += "=" * 50 + "\n\n"

        for dia, horarios in self.horarios_data.items():
            preview_text += f"📅 {dia.upper()}\n"
            if not horarios:
                preview_text += "   Sin horarios configurados\n"
            else:
                for horario in horarios:
                    labs = ", ".join(horario['laboratorios'][:2])
                    if len(horario['laboratorios']) > 2:
                        labs += f" (+{len(horario['laboratorios']) - 2})"
                    preview_text += f"   {horario['inicio']}-{horario['fin']} → {labs}\n"
            preview_text += "\n"

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
            os.makedirs("config", exist_ok=True)

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
                self.cargar_configuracion_defecto()
                return

            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            self.horarios_data = config_data.get('horarios_semanal', self.horarios_data)
            labs_guardados = config_data.get('laboratorios_disponibles', [])

            if labs_guardados:
                self.lista_laboratorios.setText('\n'.join(labs_guardados))

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

    def apply_dark_theme_legible(self):
        """Aplicar tema oscuro con fuentes legibles"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: rgb(53,53,53);
                color: white;
            }
            QWidget {
                background-color: rgb(53,53,53);
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }
            QLabel {
                color: white;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton {
                background-color: rgb(53,53,53);
                color: white;
                border: 1px solid rgb(127,127,127);
                padding: 10px;
                font-size: 12px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgb(66,66,66);
                border: 1px solid rgb(42,130,218);
            }
            QListWidget {
                background-color: rgb(42,42,42);
                color: white;
                border: 1px solid rgb(127,127,127);
                font-size: 12px;
                selection-background-color: rgb(42,130,218);
                border-radius: 3px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid rgb(60,60,60);
            }
            QTableWidget {
                background-color: rgb(42,42,42);
                color: white;
                border: 1px solid rgb(127,127,127);
                gridline-color: rgb(127,127,127);
                font-size: 11px;
                border-radius: 3px;
            }
            QTableWidget::item {
                border-bottom: 1px solid rgb(127,127,127);
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: rgb(42,130,218);
            }
            QHeaderView::section {
                background-color: rgb(35,35,35);
                color: white;
                border: 1px solid rgb(127,127,127);
                padding: 8px;
                font-weight: bold;
                font-size: 11px;
            }
            QTextEdit {
                background-color: rgb(42,42,42);
                color: white;
                border: 1px solid rgb(127,127,127);
                font-family: 'Consolas', monospace;
                font-size: 11px;
                line-height: 1.4;
                padding: 8px;
                border-radius: 3px;
            }
            QTimeEdit, QComboBox {
                background-color: rgb(42,42,42);
                color: white;
                border: 1px solid rgb(127,127,127);
                padding: 8px;
                font-size: 12px;
                border-radius: 3px;
            }
            QComboBox::drop-down {
                background-color: rgb(53,53,53);
            }
            QComboBox QAbstractItemView {
                background-color: rgb(42,42,42);
                color: white;
                selection-background-color: rgb(42,130,218);
                font-size: 12px;
            }
            QMessageBox {
                background-color: rgb(53,53,53);
                color: white;
                font-size: 12px;
            }
        """)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')

    window = ConfigurarHorarios()
    window.show()
    sys.exit(app.exec())