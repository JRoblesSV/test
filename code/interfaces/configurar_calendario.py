import sys
import json
import os
from PyQt6 import QtCore, QtGui, QtWidgets
from datetime import datetime, date, timedelta
import calendar


class ConfigurarCalendario(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.config_path = "config/calendario_academico.json"
        self.year_actual = datetime.now().year
        self.calendario_data = {
            'year': self.year_actual,
            'cuatrimestre_1': {'inicio': None, 'fin': None},
            'cuatrimestre_2': {'inicio': None, 'fin': None},
            'dias_especiales': [],  # [{'fecha': 'YYYY-MM-DD', 'tipo': 'horario_lunes', 'descripcion': ''}]
            'dias_sin_clase': [],  # ['YYYY-MM-DD', ...]
            'fecha_creacion': datetime.now().isoformat()
        }

        self.setupUi()
        self.cargar_configuracion()

    def setupUi(self):
        self.setObjectName("ConfigurarCalendario")
        self.resize(1200, 800)
        self.setMinimumSize(QtCore.QSize(1200, 800))
        self.setMaximumSize(QtCore.QSize(1200, 800))
        self.setWindowTitle("OPTIM - Configurar Calendario Académico")

        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        # ========= TÍTULO =========
        self.titulo = QtWidgets.QLabel(self.centralwidget)
        self.titulo.setGeometry(QtCore.QRect(50, 10, 1100, 35))
        self.titulo.setText(f"Configuración de Calendario Académico {self.year_actual}-{self.year_actual + 1}")
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

        # ========= CONTROLES SUPERIORES =========
        self.setup_controles_superiores()

        # ========= CALENDARIO VISUAL =========
        self.setup_calendario()

        # ========= PANEL CONFIGURACIÓN =========
        self.setup_panel_configuracion()

        # ========= VISTA PREVIA =========
        self.setup_vista_previa()

        # ========= BOTONES =========
        self.setup_botones()

        # ========= TEMA OSCURO =========
        self.apply_dark_theme()

        # Cargar mes actual
        self.actualizar_calendario()

    def setup_controles_superiores(self):
        """Controles para navegar por el calendario"""
        # Año
        self.label_year = QtWidgets.QLabel(self.centralwidget)
        self.label_year.setGeometry(QtCore.QRect(50, 60, 50, 20))
        self.label_year.setText("Año:")

        self.spin_year = QtWidgets.QSpinBox(self.centralwidget)
        self.spin_year.setGeometry(QtCore.QRect(110, 60, 80, 25))
        self.spin_year.setMinimum(2020)
        self.spin_year.setMaximum(2030)
        self.spin_year.setValue(self.year_actual)
        self.spin_year.valueChanged.connect(self.cambiar_año)

        # Mes
        self.label_mes = QtWidgets.QLabel(self.centralwidget)
        self.label_mes.setGeometry(QtCore.QRect(220, 60, 50, 20))
        self.label_mes.setText("Mes:")

        self.combo_mes = QtWidgets.QComboBox(self.centralwidget)
        self.combo_mes.setGeometry(QtCore.QRect(280, 60, 120, 25))
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        self.combo_mes.addItems(meses)
        self.combo_mes.setCurrentIndex(datetime.now().month - 1)
        self.combo_mes.currentIndexChanged.connect(self.actualizar_calendario)

        # Botones navegación
        self.btn_anterior = QtWidgets.QPushButton(self.centralwidget)
        self.btn_anterior.setGeometry(QtCore.QRect(420, 60, 80, 25))
        self.btn_anterior.setText("◀ Anterior")
        self.btn_anterior.clicked.connect(self.mes_anterior)

        self.btn_siguiente = QtWidgets.QPushButton(self.centralwidget)
        self.btn_siguiente.setGeometry(QtCore.QRect(510, 60, 80, 25))
        self.btn_siguiente.setText("Siguiente ▶")
        self.btn_siguiente.clicked.connect(self.mes_siguiente)

        # Leyenda
        self.setup_leyenda()

    def setup_leyenda(self):
        """Leyenda de colores"""
        x_base = 650
        y_base = 60

        leyenda_items = [
            ("🟦 1º Cuatrimestre", "rgb(42,130,218)"),
            ("🟩 2º Cuatrimestre", "rgb(46,204,113)"),
            ("🟨 Día Especial", "rgb(241,196,15)"),
            ("🟥 Sin Clase", "rgb(231,76,60)")
        ]

        for i, (texto, color) in enumerate(leyenda_items):
            label = QtWidgets.QLabel(self.centralwidget)
            label.setGeometry(QtCore.QRect(x_base + (i * 130), y_base, 120, 20))
            label.setText(texto)
            label.setStyleSheet(f"color: {color}; font-size: 10px; font-weight: bold;")

    def setup_calendario(self):
        """Calendario visual"""
        self.calendario_widget = QtWidgets.QCalendarWidget(self.centralwidget)
        self.calendario_widget.setGeometry(QtCore.QRect(50, 100, 550, 400))
        self.calendario_widget.clicked.connect(self.dia_seleccionado)

        # Configurar formato de fechas
        formato = QtGui.QTextCharFormat()
        formato.setBackground(QtGui.QColor(42, 42, 42))
        formato.setForeground(QtGui.QColor(255, 255, 255))
        self.calendario_widget.setWeekdayTextFormat(QtCore.Qt.DayOfWeek.Monday, formato)

    def setup_panel_configuracion(self):
        """Panel de configuración de fechas"""
        self.label_config = QtWidgets.QLabel(self.centralwidget)
        self.label_config.setGeometry(QtCore.QRect(630, 100, 520, 25))
        self.label_config.setText("Configuración de Períodos Académicos")
        self.label_config.setStyleSheet("color: rgb(42,130,218); font-weight: bold; font-size: 14px;")

        # 1º Cuatrimestre
        self.setup_cuatrimestre_controls(1, 140)

        # 2º Cuatrimestre
        self.setup_cuatrimestre_controls(2, 220)

        # Día seleccionado
        self.label_dia_sel = QtWidgets.QLabel(self.centralwidget)
        self.label_dia_sel.setGeometry(QtCore.QRect(630, 300, 520, 25))
        self.label_dia_sel.setText("Configurar Día Seleccionado:")
        self.label_dia_sel.setStyleSheet("color: rgb(42,130,218); font-weight: bold; font-size: 12px;")

        self.fecha_seleccionada = QtWidgets.QLabel(self.centralwidget)
        self.fecha_seleccionada.setGeometry(QtCore.QRect(630, 330, 520, 20))
        self.fecha_seleccionada.setText("Haz clic en una fecha del calendario")

        # Opciones para día seleccionado
        self.radio_normal = QtWidgets.QRadioButton(self.centralwidget)
        self.radio_normal.setGeometry(QtCore.QRect(630, 360, 150, 20))
        self.radio_normal.setText("Día normal")
        self.radio_normal.setChecked(True)

        self.radio_sin_clase = QtWidgets.QRadioButton(self.centralwidget)
        self.radio_sin_clase.setGeometry(QtCore.QRect(630, 385, 150, 20))
        self.radio_sin_clase.setText("Sin clase")

        self.radio_especial = QtWidgets.QRadioButton(self.centralwidget)
        self.radio_especial.setGeometry(QtCore.QRect(630, 410, 150, 20))
        self.radio_especial.setText("Día especial:")

        self.combo_tipo_especial = QtWidgets.QComboBox(self.centralwidget)
        self.combo_tipo_especial.setGeometry(QtCore.QRect(790, 410, 120, 25))
        tipos = ["Horario Lunes", "Horario Martes", "Horario Miércoles", "Horario Jueves", "Horario Viernes"]
        self.combo_tipo_especial.addItems(tipos)
        self.combo_tipo_especial.setEnabled(False)

        self.radio_especial.toggled.connect(lambda checked: self.combo_tipo_especial.setEnabled(checked))

        # Descripción
        self.label_desc = QtWidgets.QLabel(self.centralwidget)
        self.label_desc.setGeometry(QtCore.QRect(630, 445, 100, 20))
        self.label_desc.setText("Descripción:")

        self.line_descripcion = QtWidgets.QLineEdit(self.centralwidget)
        self.line_descripcion.setGeometry(QtCore.QRect(740, 445, 170, 25))
        self.line_descripcion.setPlaceholderText("Ej: Día del Pilar")

        # Botón aplicar
        self.btn_aplicar_dia = QtWidgets.QPushButton(self.centralwidget)
        self.btn_aplicar_dia.setGeometry(QtCore.QRect(930, 445, 80, 25))
        self.btn_aplicar_dia.setText("Aplicar")
        self.btn_aplicar_dia.clicked.connect(self.aplicar_configuracion_dia)

    def setup_cuatrimestre_controls(self, numero, y_pos):
        """Controles para configurar cuatrimestre"""
        label = QtWidgets.QLabel(self.centralwidget)
        label.setGeometry(QtCore.QRect(630, y_pos, 120, 20))
        label.setText(f"{numero}º Cuatrimestre:")
        label.setStyleSheet("color: white; font-weight: bold;")

        # Fecha inicio
        label_inicio = QtWidgets.QLabel(self.centralwidget)
        label_inicio.setGeometry(QtCore.QRect(750, y_pos, 50, 20))
        label_inicio.setText("Inicio:")

        date_inicio = QtWidgets.QDateEdit(self.centralwidget)
        date_inicio.setGeometry(QtCore.QRect(800, y_pos, 100, 25))
        date_inicio.setCalendarPopup(True)
        date_inicio.setDate(QtCore.QDate.currentDate())

        # Fecha fin
        label_fin = QtWidgets.QLabel(self.centralwidget)
        label_fin.setGeometry(QtCore.QRect(750, y_pos + 30, 50, 20))
        label_fin.setText("Fin:")

        date_fin = QtWidgets.QDateEdit(self.centralwidget)
        date_fin.setGeometry(QtCore.QRect(800, y_pos + 30, 100, 25))
        date_fin.setCalendarPopup(True)
        date_fin.setDate(QtCore.QDate.currentDate())

        # Botón establecer
        btn_establecer = QtWidgets.QPushButton(self.centralwidget)
        btn_establecer.setGeometry(QtCore.QRect(920, y_pos + 15, 90, 25))
        btn_establecer.setText("Establecer")

        # Guardar referencias
        if numero == 1:
            self.date_inicio_1 = date_inicio
            self.date_fin_1 = date_fin
            self.btn_establecer_1 = btn_establecer
            btn_establecer.clicked.connect(lambda: self.establecer_cuatrimestre(1))
        else:
            self.date_inicio_2 = date_inicio
            self.date_fin_2 = date_fin
            self.btn_establecer_2 = btn_establecer
            btn_establecer.clicked.connect(lambda: self.establecer_cuatrimestre(2))

    def setup_vista_previa(self):
        """Vista previa de la configuración"""
        self.label_vista = QtWidgets.QLabel(self.centralwidget)
        self.label_vista.setGeometry(QtCore.QRect(50, 520, 550, 20))
        self.label_vista.setText("Vista Previa de Configuración:")
        self.label_vista.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")

        self.vista_previa = QtWidgets.QTextEdit(self.centralwidget)
        self.vista_previa.setGeometry(QtCore.QRect(50, 550, 550, 180))
        self.vista_previa.setReadOnly(True)

    def setup_botones(self):
        """Botones principales"""
        self.btn_guardar = QtWidgets.QPushButton(self.centralwidget)
        self.btn_guardar.setGeometry(QtCore.QRect(700, 680, 120, 40))
        self.btn_guardar.setText("💾 Guardar")
        self.btn_guardar.clicked.connect(self.guardar_configuracion)

        self.btn_cargar = QtWidgets.QPushButton(self.centralwidget)
        self.btn_cargar.setGeometry(QtCore.QRect(830, 680, 120, 40))
        self.btn_cargar.setText("📂 Cargar")
        self.btn_cargar.clicked.connect(self.cargar_configuracion)

        self.btn_cerrar = QtWidgets.QPushButton(self.centralwidget)
        self.btn_cerrar.setGeometry(QtCore.QRect(960, 680, 120, 40))
        self.btn_cerrar.setText("✅ Cerrar")
        self.btn_cerrar.clicked.connect(self.close)

    def cambiar_año(self, año):
        """Cambiar año del calendario"""
        self.year_actual = año
        self.calendario_data['year'] = año
        self.actualizar_calendario()
        self.titulo.setText(f"Configuración de Calendario Académico {año}-{año + 1}")

    def actualizar_calendario(self):
        """Actualizar vista del calendario"""
        año = self.spin_year.value()
        mes = self.combo_mes.currentIndex() + 1

        self.calendario_widget.setCurrentPage(año, mes)
        self.aplicar_formato_calendario()
        self.actualizar_vista_previa()

    def mes_anterior(self):
        """Ir al mes anterior"""
        if self.combo_mes.currentIndex() == 0:
            self.combo_mes.setCurrentIndex(11)
            self.spin_year.setValue(self.spin_year.value() - 1)
        else:
            self.combo_mes.setCurrentIndex(self.combo_mes.currentIndex() - 1)

    def mes_siguiente(self):
        """Ir al mes siguiente"""
        if self.combo_mes.currentIndex() == 11:
            self.combo_mes.setCurrentIndex(0)
            self.spin_year.setValue(self.spin_year.value() + 1)
        else:
            self.combo_mes.setCurrentIndex(self.combo_mes.currentIndex() + 1)

    def aplicar_formato_calendario(self):
        """Aplicar colores al calendario según configuración"""
        # Limpiar formatos
        formato_normal = QtGui.QTextCharFormat()
        formato_normal.setBackground(QtGui.QColor(42, 42, 42))
        formato_normal.setForeground(QtGui.QColor(255, 255, 255))

        # Aplicar formato por defecto a todas las fechas
        año = self.spin_year.value()
        mes = self.combo_mes.currentIndex() + 1

        for dia in range(1, 32):
            try:
                fecha = QtCore.QDate(año, mes, dia)
                if fecha.isValid():
                    self.calendario_widget.setDateTextFormat(fecha, formato_normal)
            except:
                break

        # Aplicar formatos especiales
        self.aplicar_formato_cuatrimestres()
        self.aplicar_formato_dias_especiales()

    def aplicar_formato_cuatrimestres(self):
        """Aplicar formato a los cuatrimestres"""
        # 1º Cuatrimestre - Azul
        if self.calendario_data['cuatrimestre_1']['inicio'] and self.calendario_data['cuatrimestre_1']['fin']:
            formato_1 = QtGui.QTextCharFormat()
            formato_1.setBackground(QtGui.QColor(42, 130, 218))
            formato_1.setForeground(QtGui.QColor(255, 255, 255))

            inicio = datetime.fromisoformat(self.calendario_data['cuatrimestre_1']['inicio']).date()
            fin = datetime.fromisoformat(self.calendario_data['cuatrimestre_1']['fin']).date()

            fecha_actual = inicio
            while fecha_actual <= fin:
                qdate = QtCore.QDate(fecha_actual.year, fecha_actual.month, fecha_actual.day)
                self.calendario_widget.setDateTextFormat(qdate, formato_1)
                fecha_actual += timedelta(days=1)

        # 2º Cuatrimestre - Verde
        if self.calendario_data['cuatrimestre_2']['inicio'] and self.calendario_data['cuatrimestre_2']['fin']:
            formato_2 = QtGui.QTextCharFormat()
            formato_2.setBackground(QtGui.QColor(46, 204, 113))
            formato_2.setForeground(QtGui.QColor(255, 255, 255))

            inicio = datetime.fromisoformat(self.calendario_data['cuatrimestre_2']['inicio']).date()
            fin = datetime.fromisoformat(self.calendario_data['cuatrimestre_2']['fin']).date()

            fecha_actual = inicio
            while fecha_actual <= fin:
                qdate = QtCore.QDate(fecha_actual.year, fecha_actual.month, fecha_actual.day)
                self.calendario_widget.setDateTextFormat(qdate, formato_2)
                fecha_actual += timedelta(days=1)

    def aplicar_formato_dias_especiales(self):
        """Aplicar formato a días especiales y sin clase"""
        # Días especiales - Amarillo
        formato_especial = QtGui.QTextCharFormat()
        formato_especial.setBackground(QtGui.QColor(241, 196, 15))
        formato_especial.setForeground(QtGui.QColor(0, 0, 0))

        for dia_especial in self.calendario_data['dias_especiales']:
            fecha = datetime.fromisoformat(dia_especial['fecha']).date()
            qdate = QtCore.QDate(fecha.year, fecha.month, fecha.day)
            self.calendario_widget.setDateTextFormat(qdate, formato_especial)

        # Días sin clase - Rojo
        formato_sin_clase = QtGui.QTextCharFormat()
        formato_sin_clase.setBackground(QtGui.QColor(231, 76, 60))
        formato_sin_clase.setForeground(QtGui.QColor(255, 255, 255))

        for fecha_str in self.calendario_data['dias_sin_clase']:
            fecha = datetime.fromisoformat(fecha_str).date()
            qdate = QtCore.QDate(fecha.year, fecha.month, fecha.day)
            self.calendario_widget.setDateTextFormat(qdate, formato_sin_clase)

    def dia_seleccionado(self, fecha):
        """Manejar selección de día"""
        fecha_str = fecha.toString("yyyy-MM-dd")
        self.fecha_seleccionada.setText(f"Fecha seleccionada: {fecha.toString('dddd, dd MMMM yyyy')}")

        # Determinar estado actual del día
        if fecha_str in self.calendario_data['dias_sin_clase']:
            self.radio_sin_clase.setChecked(True)
        elif any(d['fecha'] == fecha_str for d in self.calendario_data['dias_especiales']):
            self.radio_especial.setChecked(True)
            # Encontrar tipo
            for dia in self.calendario_data['dias_especiales']:
                if dia['fecha'] == fecha_str:
                    tipo_map = {
                        'horario_lunes': 0, 'horario_martes': 1, 'horario_miercoles': 2,
                        'horario_jueves': 3, 'horario_viernes': 4
                    }
                    self.combo_tipo_especial.setCurrentIndex(tipo_map.get(dia['tipo'], 0))
                    self.line_descripcion.setText(dia.get('descripcion', ''))
                    break
        else:
            self.radio_normal.setChecked(True)

    def establecer_cuatrimestre(self, numero):
        """Establecer fechas de cuatrimestre"""
        if numero == 1:
            inicio = self.date_inicio_1.date().toString("yyyy-MM-dd")
            fin = self.date_fin_1.date().toString("yyyy-MM-dd")
            self.calendario_data['cuatrimestre_1'] = {'inicio': inicio, 'fin': fin}
        else:
            inicio = self.date_inicio_2.date().toString("yyyy-MM-dd")
            fin = self.date_fin_2.date().toString("yyyy-MM-dd")
            self.calendario_data['cuatrimestre_2'] = {'inicio': inicio, 'fin': fin}

        self.aplicar_formato_calendario()
        self.actualizar_vista_previa()
        self.mostrar_mensaje("✅ Éxito", f"{numero}º Cuatrimestre configurado correctamente")

    def aplicar_configuracion_dia(self):
        """Aplicar configuración al día seleccionado"""
        fecha_seleccionada = self.calendario_widget.selectedDate()
        fecha_str = fecha_seleccionada.toString("yyyy-MM-dd")

        # Limpiar configuraciones previas de este día
        self.calendario_data['dias_sin_clase'] = [d for d in self.calendario_data['dias_sin_clase'] if d != fecha_str]
        self.calendario_data['dias_especiales'] = [d for d in self.calendario_data['dias_especiales'] if
                                                   d['fecha'] != fecha_str]

        if self.radio_sin_clase.isChecked():
            self.calendario_data['dias_sin_clase'].append(fecha_str)
        elif self.radio_especial.isChecked():
            tipos = ['horario_lunes', 'horario_martes', 'horario_miercoles', 'horario_jueves', 'horario_viernes']
            tipo = tipos[self.combo_tipo_especial.currentIndex()]

            self.calendario_data['dias_especiales'].append({
                'fecha': fecha_str,
                'tipo': tipo,
                'descripcion': self.line_descripcion.text()
            })

        self.aplicar_formato_calendario()
        self.actualizar_vista_previa()
        self.mostrar_mensaje("✅ Éxito", "Configuración del día aplicada")

    def actualizar_vista_previa(self):
        """Actualizar vista previa"""
        preview = f"CONFIGURACIÓN CALENDARIO ACADÉMICO {self.calendario_data['year']}-{self.calendario_data['year'] + 1}\n"
        preview += "=" * 60 + "\n\n"

        # Cuatrimestres
        preview += "📅 PERÍODOS ACADÉMICOS:\n"
        if self.calendario_data['cuatrimestre_1']['inicio']:
            preview += f"  1º Cuatrimestre: {self.calendario_data['cuatrimestre_1']['inicio']} → {self.calendario_data['cuatrimestre_1']['fin']}\n"
        else:
            preview += "  1º Cuatrimestre: Sin configurar\n"

        if self.calendario_data['cuatrimestre_2']['inicio']:
            preview += f"  2º Cuatrimestre: {self.calendario_data['cuatrimestre_2']['inicio']} → {self.calendario_data['cuatrimestre_2']['fin']}\n"
        else:
            preview += "  2º Cuatrimestre: Sin configurar\n"

        # Días especiales
        preview += f"\n🟨 DÍAS ESPECIALES ({len(self.calendario_data['dias_especiales'])}):\n"
        for dia in self.calendario_data['dias_especiales']:
            tipo_display = dia['tipo'].replace('horario_', 'Horario ').title()
            desc = f" - {dia['descripcion']}" if dia['descripcion'] else ""
            preview += f"  • {dia['fecha']} → {tipo_display}{desc}\n"

        # Días sin clase
        preview += f"\n🟥 DÍAS SIN CLASE ({len(self.calendario_data['dias_sin_clase'])}):\n"
        for fecha in sorted(self.calendario_data['dias_sin_clase']):
            preview += f"  • {fecha}\n"

        # Estadísticas
        total_especiales = len(self.calendario_data['dias_especiales']) + len(self.calendario_data['dias_sin_clase'])
        preview += f"\n📊 ESTADÍSTICAS:\n"
        preview += f"  • Total días especiales/sin clase: {total_especiales}\n"

        cuatrimestres_config = sum(
            1 for c in [self.calendario_data['cuatrimestre_1'], self.calendario_data['cuatrimestre_2']] if c['inicio'])
        preview += f"  • Cuatrimestres configurados: {cuatrimestres_config}/2\n"

        self.vista_previa.setText(preview)

    def guardar_configuracion(self):
        """Guardar configuración"""
        try:
            os.makedirs("config", exist_ok=True)

            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.calendario_data, f, indent=2, ensure_ascii=False)

            self.mostrar_mensaje("✅ Éxito", f"Configuración guardada en:\n{self.config_path}")

        except Exception as e:
            self.mostrar_mensaje("❌ Error", f"Error guardando:\n{str(e)}")

    def cargar_configuracion(self):
        """Cargar configuración"""
        try:
            if not os.path.exists(self.config_path):
                self.cargar_configuracion_defecto()
                return

            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.calendario_data = json.load(f)

            # Actualizar controles
            if self.calendario_data['cuatrimestre_1']['inicio']:
                fecha = QtCore.QDate.fromString(self.calendario_data['cuatrimestre_1']['inicio'], "yyyy-MM-dd")
                self.date_inicio_1.setDate(fecha)
                fecha = QtCore.QDate.fromString(self.calendario_data['cuatrimestre_1']['fin'], "yyyy-MM-dd")
                self.date_fin_1.setDate(fecha)

            if self.calendario_data['cuatrimestre_2']['inicio']:
                fecha = QtCore.QDate.fromString(self.calendario_data['cuatrimestre_2']['inicio'], "yyyy-MM-dd")
                self.date_inicio_2.setDate(fecha)
                fecha = QtCore.QDate.fromString(self.calendario_data['cuatrimestre_2']['fin'], "yyyy-MM-dd")
                self.date_fin_2.setDate(fecha)

            self.actualizar_calendario()
            self.mostrar_mensaje("✅ Éxito", "Configuración cargada")

        except Exception as e:
            self.mostrar_mensaje("❌ Error", f"Error cargando:\n{str(e)}")
            self.cargar_configuracion_defecto()

    def cargar_configuracion_defecto(self):
        """Cargar configuración por defecto"""
        year = self.year_actual

        # Fechas típicas académicas
        self.calendario_data = {
            'year': year,
            'cuatrimestre_1': {
                'inicio': f"{year}-09-16",  # Septiembre
                'fin': f"{year + 1}-01-20"  # Enero
            },
            'cuatrimestre_2': {
                'inicio': f"{year + 1}-02-03",  # Febrero
                'fin': f"{year + 1}-06-06"  # Junio
            },
            'dias_especiales': [
                {'fecha': f"{year}-10-12", 'tipo': 'horario_lunes', 'descripcion': 'Día del Pilar'},
                {'fecha': f"{year}-12-06", 'tipo': 'horario_martes', 'descripcion': 'Día de la Constitución'}
            ],
            'dias_sin_clase': [
                f"{year}-11-01",  # Todos los Santos
                f"{year}-12-25",  # Navidad
                f"{year + 1}-01-01"  # Año Nuevo
            ],
            'fecha_creacion': datetime.now().isoformat()
        }

        # Actualizar controles con valores por defecto
        self.date_inicio_1.setDate(QtCore.QDate(year, 9, 16))
        self.date_fin_1.setDate(QtCore.QDate(year + 1, 1, 20))
        self.date_inicio_2.setDate(QtCore.QDate(year + 1, 2, 3))
        self.date_fin_2.setDate(QtCore.QDate(year + 1, 6, 6))

        self.actualizar_calendario()

    def mostrar_mensaje(self, titulo, mensaje):
        """Mostrar mensaje"""
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
            QCalendarWidget QMenu {
                background-color: rgb(42,42,42);
                color: white;
            }
            QCalendarWidget QSpinBox {
                background-color: rgb(42,42,42);
                color: white;
                border: 1px solid rgb(127,127,127);
            }
            QComboBox, QSpinBox, QDateEdit {
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
            QTextEdit {
                background-color: rgb(42,42,42);
                color: white;
                border: 1px solid rgb(127,127,127);
                font-family: 'Consolas', monospace;
                font-size: 10px;
            }
            QLineEdit {
                background-color: rgb(42,42,42);
                color: white;
                border: 1px solid rgb(127,127,127);
                padding: 5px;
            }
            QRadioButton {
                color: white;
                font-size: 11px;
            }
            QRadioButton::indicator {
                width: 12px;
                height: 12px;
                border-radius: 6px;
                border: 1px solid rgb(127,127,127);
                background-color: rgb(42,42,42);
            }
            QRadioButton::indicator:checked {
                background-color: rgb(42,130,218);
                border: 1px solid rgb(42,130,218);
            }
        """)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')

    window = ConfigurarCalendario()
    window.show()
    sys.exit(app.exec())