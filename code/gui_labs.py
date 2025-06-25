import subprocess
import sys

# Instalar dependencias automáticamente
# subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

from PyQt6 import QtCore, QtGui, QtWidgets
import pandas as pd

# Importar las nuevas interfaces
try:
    from interfaces import ConfigurarCalendario, ConfigurarHorarios, VerResultados

    INTERFACES_DISPONIBLES = True
except ImportError as e:
    print(f"⚠️ Error importando interfaces: {e}")
    INTERFACES_DISPONIBLES = False


class CustomCheckBox(QtWidgets.QCheckBox):
    """CheckBox personalizado con X visible cuando está marcado"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QCheckBox {
                color: white;
                font-size: 11px;
                font-weight: bold;
            }

            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                background-color: rgb(42,42,42);
                border: 2px solid rgb(127,127,127);
                border-radius: 3px;
            }

            QCheckBox::indicator:checked {
                background-color: rgb(42,130,218);
                border: 2px solid rgb(42,130,218);
            }
        """)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.isChecked():
            # Dibujar X personalizada
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

            # Configurar pen para la X
            pen = QtGui.QPen(QtGui.QColor(255, 255, 255), 2)
            painter.setPen(pen)

            # Calcular posición del indicator
            option = QtWidgets.QStyleOptionButton()
            self.initStyleOption(option)
            rect = self.style().subElementRect(QtWidgets.QStyle.SubElement.SE_CheckBoxIndicator, option, self)

            # Dibujar X
            margin = 4
            painter.drawLine(
                rect.left() + margin, rect.top() + margin,
                rect.right() - margin, rect.bottom() - margin
            )
            painter.drawLine(
                rect.right() - margin, rect.top() + margin,
                rect.left() + margin, rect.bottom() - margin
            )


class Ui_MainWindow(object):
    def __init__(self):
        self.path_alumnos = None
        self.path_asignaturas = None
        self.path_laboratorios = None
        self.path_profesores = None
        self.path_restricciones = None
        self._validation_logged = False

        # Referencias a ventanas de configuración
        self.ventana_calendario = None
        self.ventana_horarios = None
        self.ventana_resultados = None

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1100, 750)  # Aumentar altura para nuevos botones
        MainWindow.setMinimumSize(QtCore.QSize(1100, 750))
        MainWindow.setMaximumSize(QtCore.QSize(1100, 750))
        MainWindow.setWindowTitle("OPTIM by SoftVier - ETSIDI")

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # ========= MENÚ SUPERIOR =========
        self.setup_menu_bar(MainWindow)

        # ========= TÍTULO PRINCIPAL =========
        self.titulo_principal = QtWidgets.QLabel(self.centralwidget)
        self.titulo_principal.setGeometry(QtCore.QRect(50, 10, 1000, 35))
        self.titulo_principal.setText("OPTIM by SoftVier - ETSIDI")
        self.titulo_principal.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.titulo_principal.setStyleSheet("""
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

        # ========= SECCIÓN CREDENCIALES WEB =========
        self.setup_credenciales_section()

        # ========= SECCIÓN ARCHIVOS DE DATOS =========
        self.setup_archivos_section()

        # ========= SECCIÓN CONFIGURACIÓN =========
        self.setup_configuracion_section()

        # ========= SECCIÓN OPCIONES AVANZADAS =========
        self.setup_opciones_section()

        # ========= BOTONES DE CONFIGURACIÓN AVANZADA =========
        self.setup_botones_configuracion()

        # ========= ÁREA DE LOG =========
        self.info_area = QtWidgets.QTextEdit(self.centralwidget)
        self.info_area.setGeometry(QtCore.QRect(580, 120, 470, 450))
        self.info_area.setReadOnly(True)
        self.info_area.setText("""OPTIM - Sistema de Programación de Laboratorios v1.0
Desarrollado por SoftVier para ETSIDI

INSTRUCCIONES:
1. Credenciales UPM (OPCIONALES - solo para web scraping)
2. Selecciona los 4 archivos CSV/Excel OBLIGATORIOS
3. Configura opciones adicionales si lo deseas
4. Haz clic en 'Generar Horarios' para comenzar

ARCHIVOS OBLIGATORIOS:
• Alumnos: Lista con DNI, nombre, asignatura
• Asignaturas: Compatibilidad con laboratorios  
• Laboratorios: Capacidad y equipamiento
• Profesores: Disponibilidad horaria

OPCIONES ADICIONALES:
• Grupos equilibrados: Mejor distribución de alumnos
• Web scraping: Datos automáticos del calendario
• Optimización avanzada: Mejor calidad (más lento)

CONFIGURACIÓN AVANZADA:
• Configurar Calendario: Períodos académicos y festivos
• Configurar Horarios: Franjas horarias por día
• Ver Resultados: Análisis detallado de horarios generados

Sistema listo para procesar datos...""")

        # ========= BOTONES PRINCIPALES =========
        self.setup_botones_principales()

        # ========= BARRA DE PROGRESO =========
        self.progress_bar = QtWidgets.QProgressBar(self.centralwidget)
        self.progress_bar.setGeometry(QtCore.QRect(50, 720, 1000, 20))
        self.progress_bar.setVisible(False)

        MainWindow.setCentralWidget(self.centralwidget)

        # ========= CONEXIONES DE SEÑALES =========
        self.connect_signals()

        # ========= APLICAR TEMA OSCURO COMO TFG =========
        self.apply_dark_theme_tfg()

    def setup_menu_bar(self, MainWindow):
        """Configurar barra de menú"""
        if not INTERFACES_DISPONIBLES:
            return

        menubar = MainWindow.menuBar()

        # Menú Configuración
        menu_config = menubar.addMenu('⚙️ Configuración')

        # Acción Configurar Calendario
        action_calendario = QtGui.QAction('📅 Configurar Calendario', MainWindow)
        action_calendario.setStatusTip('Configurar períodos académicos y días festivos')
        action_calendario.triggered.connect(self.abrir_configurar_calendario)
        menu_config.addAction(action_calendario)

        # Acción Configurar Horarios
        action_horarios = QtGui.QAction('⏰ Configurar Horarios', MainWindow)
        action_horarios.setStatusTip('Configurar horarios semanales de laboratorio')
        action_horarios.triggered.connect(self.abrir_configurar_horarios)
        menu_config.addAction(action_horarios)

        menu_config.addSeparator()

        # Acción Ver Resultados
        action_resultados = QtGui.QAction('📊 Ver Resultados', MainWindow)
        action_resultados.setStatusTip('Visualizar y analizar resultados de programación')
        action_resultados.triggered.connect(self.abrir_ver_resultados)
        menu_config.addAction(action_resultados)

        # Menú Ayuda
        menu_ayuda = menubar.addMenu('❓ Ayuda')

        action_acerca = QtGui.QAction('ℹ️ Acerca de OPTIM', MainWindow)
        action_acerca.triggered.connect(self.mostrar_acerca_de)
        menu_ayuda.addAction(action_acerca)

    def setup_credenciales_section(self):
        """Configurar sección de credenciales UPM"""
        # Título credenciales
        self.label_credenciales = QtWidgets.QLabel(self.centralwidget)
        self.label_credenciales.setGeometry(QtCore.QRect(50, 60, 500, 25))
        self.label_credenciales.setText(
            "Credenciales UPM (OPCIONALES - solo para obtener datos automáticamente de la web)")

        # Email UPM
        self.label_email = QtWidgets.QLabel(self.centralwidget)
        self.label_email.setGeometry(QtCore.QRect(50, 95, 100, 20))
        self.label_email.setText("Email UPM:")

        self.lineEdit_email = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_email.setGeometry(QtCore.QRect(160, 95, 370, 25))
        self.lineEdit_email.setPlaceholderText("usuario@upm.es")

        # Contraseña
        self.label_password = QtWidgets.QLabel(self.centralwidget)
        self.label_password.setGeometry(QtCore.QRect(50, 135, 100, 20))
        self.label_password.setText("Contraseña:")

        self.lineEdit_password = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_password.setGeometry(QtCore.QRect(160, 135, 370, 25))
        self.lineEdit_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.lineEdit_password.setPlaceholderText("Tu contraseña UPM")

    def setup_archivos_section(self):
        """Configurar sección de archivos de datos"""
        # Título sección
        self.label_archivos = QtWidgets.QLabel(self.centralwidget)
        self.label_archivos.setGeometry(QtCore.QRect(50, 180, 500, 25))
        self.label_archivos.setText("Seleccione los archivos con los datos del sistema")

        # Archivo Alumnos
        self.label_alumnos = QtWidgets.QLabel(self.centralwidget)
        self.label_alumnos.setGeometry(QtCore.QRect(50, 215, 350, 20))
        self.label_alumnos.setText("Lista de Alumnos por Asignatura (CSV/Excel)")

        self.btn_alumnos = QtWidgets.QPushButton(self.centralwidget)
        self.btn_alumnos.setGeometry(QtCore.QRect(450, 215, 80, 25))
        self.btn_alumnos.setText("Examinar")

        # Archivo Asignaturas
        self.label_asignaturas = QtWidgets.QLabel(self.centralwidget)
        self.label_asignaturas.setGeometry(QtCore.QRect(50, 255, 350, 20))
        self.label_asignaturas.setText("Asignaturas y Laboratorios Compatibles (CSV/Excel)")

        self.btn_asignaturas = QtWidgets.QPushButton(self.centralwidget)
        self.btn_asignaturas.setGeometry(QtCore.QRect(450, 255, 80, 25))
        self.btn_asignaturas.setText("Examinar")

        # Archivo Laboratorios
        self.label_laboratorios = QtWidgets.QLabel(self.centralwidget)
        self.label_laboratorios.setGeometry(QtCore.QRect(50, 295, 350, 20))
        self.label_laboratorios.setText("Laboratorios Disponibles y Capacidades (CSV/Excel)")

        self.btn_laboratorios = QtWidgets.QPushButton(self.centralwidget)
        self.btn_laboratorios.setGeometry(QtCore.QRect(450, 295, 80, 25))
        self.btn_laboratorios.setText("Examinar")

        # Archivo Profesores
        self.label_profesores = QtWidgets.QLabel(self.centralwidget)
        self.label_profesores.setGeometry(QtCore.QRect(50, 335, 350, 20))
        self.label_profesores.setText("Profesores y Disponibilidad Horaria (CSV/Excel)")

        self.btn_profesores = QtWidgets.QPushButton(self.centralwidget)
        self.btn_profesores.setGeometry(QtCore.QRect(450, 335, 80, 25))
        self.btn_profesores.setText("Examinar")

        # Archivo Restricciones (Opcional)
        self.label_restricciones = QtWidgets.QLabel(self.centralwidget)
        self.label_restricciones.setGeometry(QtCore.QRect(50, 375, 350, 20))
        self.label_restricciones.setText("Restricciones Adicionales (Opcional)")

        self.btn_restricciones = QtWidgets.QPushButton(self.centralwidget)
        self.btn_restricciones.setGeometry(QtCore.QRect(450, 375, 80, 25))
        self.btn_restricciones.setText("Examinar")

    def setup_configuracion_section(self):
        """Configurar sección de parámetros"""
        # Título sección
        self.label_config = QtWidgets.QLabel(self.centralwidget)
        self.label_config.setGeometry(QtCore.QRect(50, 420, 500, 25))
        self.label_config.setText("Seleccione las opciones con las que desea que se ejecute el programa")

        # Semestre
        self.label_semestre = QtWidgets.QLabel(self.centralwidget)
        self.label_semestre.setGeometry(QtCore.QRect(50, 455, 80, 20))
        self.label_semestre.setText("Semestre:")

        self.combo_semestre = QtWidgets.QComboBox(self.centralwidget)
        self.combo_semestre.setGeometry(QtCore.QRect(140, 455, 60, 25))
        self.combo_semestre.addItems(["1", "2"])

        # Capacidad por defecto
        self.label_capacidad = QtWidgets.QLabel(self.centralwidget)
        self.label_capacidad.setGeometry(QtCore.QRect(250, 455, 130, 20))
        self.label_capacidad.setText("Capacidad máxima:")

        self.spin_capacidad = QtWidgets.QSpinBox(self.centralwidget)
        self.spin_capacidad.setGeometry(QtCore.QRect(390, 455, 60, 25))
        self.spin_capacidad.setMinimum(10)
        self.spin_capacidad.setMaximum(50)
        self.spin_capacidad.setValue(24)

    def setup_opciones_section(self):
        """Configurar sección de opciones avanzadas"""
        # Título sección
        self.label_opciones = QtWidgets.QLabel(self.centralwidget)
        self.label_opciones.setGeometry(QtCore.QRect(50, 500, 500, 25))
        self.label_opciones.setText("Elija las opciones adicionales que desee:")

        # Checkbox Grupos Equilibrados
        self.check_grupos_pares = CustomCheckBox("Priorizar grupos equilibrados (12+12 vs 11+13)", self.centralwidget)
        self.check_grupos_pares.setGeometry(QtCore.QRect(50, 535, 500, 20))
        self.check_grupos_pares.setChecked(True)

        # Checkbox Web Scraping
        self.check_web_scraping = CustomCheckBox("Obtener datos automáticamente de la web (requiere credenciales UPM)",
                                                 self.centralwidget)
        self.check_web_scraping.setGeometry(QtCore.QRect(50, 560, 500, 20))
        self.check_web_scraping.setChecked(False)

        # Checkbox Optimización Avanzada
        self.check_optimizacion = CustomCheckBox("Activar optimización avanzada (puede tardar más tiempo)",
                                                 self.centralwidget)
        self.check_optimizacion.setGeometry(QtCore.QRect(50, 585, 500, 20))
        self.check_optimizacion.setChecked(False)

    def setup_botones_configuracion(self):
        """Configurar botones de configuración avanzada"""
        if not INTERFACES_DISPONIBLES:
            return

        # Título sección
        self.label_config_avanzada = QtWidgets.QLabel(self.centralwidget)
        self.label_config_avanzada.setGeometry(QtCore.QRect(50, 615, 500, 20))
        self.label_config_avanzada.setText("Configuración Avanzada:")
        self.label_config_avanzada.setStyleSheet("color: rgb(42,130,218); font-weight: bold;")

        # Botón Configurar Calendario
        self.btn_config_calendario = QtWidgets.QPushButton(self.centralwidget)
        self.btn_config_calendario.setGeometry(QtCore.QRect(50, 640, 140, 30))
        self.btn_config_calendario.setText("📅 Calendario")
        self.btn_config_calendario.setToolTip("Configurar períodos académicos y días festivos")

        # Botón Configurar Horarios
        self.btn_config_horarios = QtWidgets.QPushButton(self.centralwidget)
        self.btn_config_horarios.setGeometry(QtCore.QRect(200, 640, 140, 30))
        self.btn_config_horarios.setText("⏰ Horarios")
        self.btn_config_horarios.setToolTip("Configurar horarios semanales de laboratorio")

        # Botón Ver Resultados
        self.btn_ver_resultados = QtWidgets.QPushButton(self.centralwidget)
        self.btn_ver_resultados.setGeometry(QtCore.QRect(350, 640, 140, 30))
        self.btn_ver_resultados.setText("📊 Resultados")
        self.btn_ver_resultados.setToolTip("Ver y analizar resultados de programación")

    def setup_botones_principales(self):
        """Configurar botones principales de acción"""
        # Botón Ejecutar
        self.ejecutar = QtWidgets.QPushButton(self.centralwidget)
        self.ejecutar.setGeometry(QtCore.QRect(650, 580, 180, 40))
        self.ejecutar.setText("🚀 Generar Horarios")
        self.ejecutar.setEnabled(False)
        self.ejecutar.setStyleSheet("""
            QPushButton {
                background-color: rgb(42,130,218);
                color: white;
                border: none;
                font-size: 12px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: rgb(35,110,190);
            }
            QPushButton:disabled {
                background-color: rgb(60,60,60);
                color: rgb(140,140,140);
            }
        """)

        # Botón Limpiar Log
        self.btn_limpiar_log = QtWidgets.QPushButton(self.centralwidget)
        self.btn_limpiar_log.setGeometry(QtCore.QRect(850, 580, 100, 40))
        self.btn_limpiar_log.setText("🧹 Limpiar")
        self.btn_limpiar_log.setToolTip("Limpiar área de log")

        # Botón Salir
        self.btn_salir = QtWidgets.QPushButton(self.centralwidget)
        self.btn_salir.setGeometry(QtCore.QRect(960, 580, 90, 40))
        self.btn_salir.setText("❌ Salir")
        self.btn_salir.setToolTip("Cerrar aplicación")

    def connect_signals(self):
        """Conectar señales de botones"""
        # Botones de archivos
        self.btn_alumnos.clicked.connect(lambda: self.seleccionar_archivo('alumnos'))
        self.btn_asignaturas.clicked.connect(lambda: self.seleccionar_archivo('asignaturas'))
        self.btn_laboratorios.clicked.connect(lambda: self.seleccionar_archivo('laboratorios'))
        self.btn_profesores.clicked.connect(lambda: self.seleccionar_archivo('profesores'))
        self.btn_restricciones.clicked.connect(lambda: self.seleccionar_archivo('restricciones'))

        # Validar habilitación del botón ejecutar
        self.btn_alumnos.clicked.connect(self.validar_ejecucion)
        self.btn_asignaturas.clicked.connect(self.validar_ejecucion)
        self.btn_laboratorios.clicked.connect(self.validar_ejecucion)
        self.btn_profesores.clicked.connect(self.validar_ejecucion)

        # Botón principal
        self.ejecutar.clicked.connect(self.iniciar_programacion)

        # Botones de configuración (solo si las interfaces están disponibles)
        if INTERFACES_DISPONIBLES:
            self.btn_config_calendario.clicked.connect(self.abrir_configurar_calendario)
            self.btn_config_horarios.clicked.connect(self.abrir_configurar_horarios)
            self.btn_ver_resultados.clicked.connect(self.abrir_ver_resultados)

        # Botones de utilidad
        self.btn_limpiar_log.clicked.connect(self.limpiar_log)
        self.btn_salir.clicked.connect(self.salir_aplicacion)

    def seleccionar_archivo(self, tipo):
        """Seleccionar archivo CSV/Excel"""
        fname = QtWidgets.QFileDialog.getOpenFileName(
            None,
            f'Seleccionar archivo de {tipo}',
            '',
            'Archivos (*.csv *.xlsx *.xls)'
        )

        if fname[0] != '':
            setattr(self, f'path_{tipo}', fname[0])

            # Actualizar botón con estilo verde
            btn = getattr(self, f'btn_{tipo}')
            btn.setText("✓ Cargado")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2ecc71;
                    color: white;
                    border: none;
                    padding: 5px;
                    font-size: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #27ae60;
                }
            """)

            # Log en área de información
            filename = fname[0].split('/')[-1].split('\\')[-1]
            self.log_info(f"✓ {tipo.capitalize()} cargado: {filename}")

            # Preview básico
            self.preview_archivo(fname[0], tipo)

    def preview_archivo(self, fname, tipo):
        """Preview rápido del archivo"""
        try:
            if fname.endswith('.csv'):
                df = pd.read_csv(fname, nrows=3)
            else:
                df = pd.read_excel(fname, nrows=3)

            columnas = list(df.columns)
            filas = len(df)

            self.log_info(f"  • Columnas detectadas: {', '.join(columnas[:3])}{'...' if len(columnas) > 3 else ''}")
            self.log_info(f"  • Filas detectadas: {filas}+ registros")

        except Exception as e:
            self.log_info(f"  ⚠ Error leyendo archivo: {str(e)[:40]}...")

    def log_info(self, mensaje):
        """Añadir mensaje al log"""
        self.info_area.append(mensaje)
        # Auto-scroll al final
        scrollbar = self.info_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def limpiar_log(self):
        """Limpiar área de log"""
        self.info_area.clear()
        self.log_info("Log limpiado - Sistema listo para procesar datos...")

    def validar_ejecucion(self):
        """Validar si se pueden ejecutar los horarios"""
        # Solo verificar archivos obligatorios (credenciales son opcionales)
        archivos_ok = all([
            self.path_alumnos is not None,
            self.path_asignaturas is not None,
            self.path_laboratorios is not None,
            self.path_profesores is not None
        ])

        if archivos_ok:
            self.ejecutar.setEnabled(True)
            if hasattr(self, '_validation_logged') and not self._validation_logged:
                self.log_info("\n✓ Todos los archivos obligatorios cargados")
                self.log_info("✓ Sistema listo para generar horarios")

                # Informar sobre credenciales opcionales
                email_ok = len(self.lineEdit_email.text().strip()) > 0
                password_ok = len(self.lineEdit_password.text().strip()) > 0
                if email_ok and password_ok:
                    self.log_info("✓ Credenciales UPM detectadas - Web scraping habilitado")
                else:
                    self.log_info("ℹ Credenciales UPM opcionales para web scraping")

                self._validation_logged = True
        else:
            self.ejecutar.setEnabled(False)
            self._validation_logged = False

            faltantes = []
            if self.path_alumnos is None: faltantes.append("alumnos")
            if self.path_asignaturas is None: faltantes.append("asignaturas")
            if self.path_laboratorios is None: faltantes.append("laboratorios")
            if self.path_profesores is None: faltantes.append("profesores")

            if faltantes:
                self.log_info(f"⚠ Faltan archivos obligatorios: {', '.join(faltantes)}")

    def iniciar_programacion(self):
        """Iniciar proceso de programación de horarios"""
        self.ejecutar.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.log_info("\n" + "=" * 60)
        self.log_info("🚀 INICIANDO GENERACIÓN DE HORARIOS - OPTIM")
        self.log_info("=" * 60)

        # Verificar credenciales para web scraping
        email = self.lineEdit_email.text().strip()
        password = self.lineEdit_password.text().strip()

        web_scraping_enabled = self.check_web_scraping.isChecked()

        if web_scraping_enabled and (not email or not password):
            self.log_info("⚠ Web scraping activado pero faltan credenciales UPM")
            self.log_info("  Procesando solo con archivos locales...")
            web_scraping_enabled = False

        # Configurar parámetros
        parametros = {
            'email': email if web_scraping_enabled else '',
            'password': password if web_scraping_enabled else '',
            'semestre': self.combo_semestre.currentText(),
            'capacidad_maxima': self.spin_capacidad.value(),
            'grupos_pares': self.check_grupos_pares.isChecked(),
            'web_scraping': web_scraping_enabled,
            'optimizacion_avanzada': self.check_optimizacion.isChecked()
        }

        # Simular proceso (aquí irá el motor real)
        try:
            # AQUÍ IRÁ EL MOTOR REAL
            # from horarios_labs import programar_laboratorios
            # cod_error, msje_error = programar_laboratorios(...)

            # SIMULACIÓN TEMPORAL
            self.simular_proceso_scheduling(web_scraping_enabled)

        except Exception as e:
            self.mostrar_mensaje(2, f"Error en la programación: {str(e)}")

        finally:
            self.ejecutar.setEnabled(True)
            self.progress_bar.setVisible(False)

    def simular_proceso_scheduling(self, web_scraping_enabled=False):
        """Simulación del proceso de scheduling"""
        import time

        if web_scraping_enabled:
            pasos = [
                (10, "🔐 Validando credenciales UPM..."),
                (15, "🌐 Obteniendo datos de calendario académico..."),
                (25, "📂 Cargando y validando archivo de alumnos..."),
                (40, "🔬 Procesando asignaturas y compatibilidades..."),
                (55, "🏢 Analizando capacidades de laboratorios..."),
                (70, "👨‍🏫 Evaluando disponibilidad de profesores..."),
                (85, "⚖️ Generando grupos equilibrados..."),
                (95, "📅 Asignando horarios sin conflictos..."),
                (100, "💾 Exportando resultados...")
            ]
        else:
            pasos = [
                (15, "📂 Cargando y validando archivo de alumnos..."),
                (30, "🔬 Procesando asignaturas y compatibilidades..."),
                (50, "🏢 Analizando capacidades de laboratorios..."),
                (65, "👨‍🏫 Evaluando disponibilidad de profesores..."),
                (80, "⚖️ Generando grupos equilibrados..."),
                (95, "📅 Asignando horarios sin conflictos..."),
                (100, "💾 Exportando resultados...")
            ]

        for progreso, mensaje in pasos:
            self.log_info(mensaje)
            self.progress_bar.setValue(progreso)
            time.sleep(0.4)
            QtCore.QCoreApplication.processEvents()

        # Resultado simulado
        self.log_info("\n" + "=" * 60)
        self.log_info("✅ HORARIOS GENERADOS EXITOSAMENTE")
        self.log_info("=" * 60)
        self.log_info("📁 Archivo guardado: horarios_laboratorios.xlsx")
        self.log_info("\n📊 Estadísticas del resultado:")
        self.log_info("• Total de grupos generados: 8")
        self.log_info("• Grupos con horario asignado: 8 (100%)")
        self.log_info("• Conflictos detectados: 0")
        self.log_info("• Laboratorios utilizados: 6/8")
        self.log_info("• Grupos equilibrados: 100%")
        if web_scraping_enabled:
            self.log_info("• Datos web integrados: Sí")
        self.log_info("• Tiempo de ejecución: 4.2 segundos")

        self.mostrar_mensaje(0,
                             "¡Horarios generados correctamente!\n\nSistema OPTIM by SoftVier\nArchivo guardado: horarios_laboratorios.xlsx\n\n¿Deseas ver los resultados ahora?",
                             show_results_button=True)

    # ========= MÉTODOS PARA ABRIR INTERFACES =========

    def abrir_configurar_calendario(self):
        """Abrir ventana de configuración de calendario"""
        if not INTERFACES_DISPONIBLES:
            self.mostrar_mensaje(1,
                                 "Las interfaces de configuración no están disponibles.\nVerifica la instalación del módulo 'interfaces'.")
            return

        try:
            if self.ventana_calendario is None:
                self.ventana_calendario = ConfigurarCalendario(parent=self)

            self.ventana_calendario.show()
            self.ventana_calendario.raise_()
            self.ventana_calendario.activateWindow()

            self.log_info("📅 Abriendo configuración de calendario académico...")

        except Exception as e:
            self.mostrar_mensaje(2, f"Error abriendo configuración de calendario:\n{str(e)}")

    def abrir_configurar_horarios(self):
        """Abrir ventana de configuración de horarios"""
        if not INTERFACES_DISPONIBLES:
            self.mostrar_mensaje(1,
                                 "Las interfaces de configuración no están disponibles.\nVerifica la instalación del módulo 'interfaces'.")
            return

        try:
            if self.ventana_horarios is None:
                self.ventana_horarios = ConfigurarHorarios(parent=self)

            self.ventana_horarios.show()
            self.ventana_horarios.raise_()
            self.ventana_horarios.activateWindow()

            self.log_info("⏰ Abriendo configuración de horarios semanales...")

        except Exception as e:
            self.mostrar_mensaje(2, f"Error abriendo configuración de horarios:\n{str(e)}")

    def abrir_ver_resultados(self):
        """Abrir ventana de visualización de resultados"""
        if not INTERFACES_DISPONIBLES:
            self.mostrar_mensaje(1,
                                 "Las interfaces de visualización no están disponibles.\nVerifica la instalación del módulo 'interfaces'.")
            return

        try:
            if self.ventana_resultados is None:
                self.ventana_resultados = VerResultados(parent=self)

            self.ventana_resultados.show()
            self.ventana_resultados.raise_()
            self.ventana_resultados.activateWindow()

            self.log_info("📊 Abriendo visualización de resultados...")

        except Exception as e:
            self.mostrar_mensaje(2, f"Error abriendo visualización de resultados:\n{str(e)}")

    def mostrar_acerca_de(self):
        """Mostrar información sobre OPTIM"""
        mensaje = """
OPTIM by SoftVier - Sistema de Programación de Laboratorios

Versión: 1.0.0
Desarrollado para: ETSIDI (UPM)

Stack Tecnológico:
• Python + PyQt6
• Pandas + NumPy + OpenPyXL
• Algoritmos de optimización personalizados

Características:
• Programación automática de horarios
• Grupos equilibrados de estudiantes
• Gestión de restricciones de profesores
• Optimización de recursos de laboratorio
• Exportación múltiple de resultados

Desarrollado por SoftVier (2024)
        """

        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle("Acerca de OPTIM")
        msg_box.setText(mensaje)
        msg_box.setIcon(QtWidgets.QMessageBox.Icon.Information)
        msg_box.exec()

    def salir_aplicacion(self):
        """Confirmar y salir de la aplicación"""
        reply = QtWidgets.QMessageBox.question(
            None,
            'Confirmar Salida',
            '¿Estás seguro de que quieres salir de OPTIM?',
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            QtWidgets.QApplication.quit()

    def mostrar_mensaje(self, cod_error, mensaje, show_results_button=False):
        """Mostrar mensaje de resultado"""
        tipos_mensaje = {0: 'Información', 1: 'Aviso', 2: 'Error'}
        iconos = {
            'Información': QtWidgets.QMessageBox.Icon.Information,
            'Aviso': QtWidgets.QMessageBox.Icon.Warning,
            'Error': QtWidgets.QMessageBox.Icon.Critical
        }

        msg_box = QtWidgets.QMessageBox()
        msg_box.setText(mensaje)
        msg_box.setWindowTitle(f"OPTIM - {tipos_mensaje[cod_error]}")
        msg_box.setIcon(iconos[tipos_mensaje[cod_error]])

        if show_results_button and INTERFACES_DISPONIBLES:
            msg_box.addButton("📊 Ver Resultados", QtWidgets.QMessageBox.ButtonRole.ActionRole)
            msg_box.addButton("✅ Cerrar", QtWidgets.QMessageBox.ButtonRole.AcceptRole)

            resultado = msg_box.exec()
            if resultado == 0:  # Ver Resultados
                self.abrir_ver_resultados()
        else:
            msg_box.exec()

    def apply_dark_theme_tfg(self):
        """Aplicar tema oscuro idéntico al TFG original"""
        # Aplicar estilos CSS para tema oscuro
        self.centralwidget.setStyleSheet("""
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
                padding: 5px;
                font-size: 10px;
            }

            QPushButton:hover {
                background-color: rgb(66,66,66);
            }

            QPushButton:disabled {
                background-color: rgb(60,60,60);
                color: rgb(140,140,140);
            }

            QLineEdit {
                background-color: rgb(42,42,42);
                color: white;
                border: 1px solid rgb(127,127,127);
                padding: 5px;
                font-size: 11px;
            }

            QLineEdit:focus {
                border: 1px solid rgb(42,130,218);
            }

            QComboBox {
                background-color: rgb(42,42,42);
                color: white;
                border: 1px solid rgb(127,127,127);
                padding: 5px;
            }

            QComboBox::drop-down {
                background-color: rgb(53,53,53);
                border: none;
            }

            QComboBox QAbstractItemView {
                background-color: rgb(42,42,42);
                color: white;
                selection-background-color: rgb(42,130,218);
            }

            QSpinBox {
                background-color: rgb(42,42,42);
                color: white;
                border: 1px solid rgb(127,127,127);
                padding: 5px;
            }

            QTextEdit {
                background-color: rgb(42,42,42);
                color: white;
                border: 1px solid rgb(127,127,127);
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 10px;
            }

            QProgressBar {
                background-color: rgb(42,42,42);
                border: 1px solid rgb(127,127,127);
                text-align: center;
                color: white;
                border-radius: 5px;
            }

            QProgressBar::chunk {
                background-color: rgb(42,130,218);
                border-radius: 3px;
            }

            QMenuBar {
                background-color: rgb(53,53,53);
                color: white;
                border-bottom: 1px solid rgb(127,127,127);
            }

            QMenuBar::item {
                background-color: transparent;
                padding: 8px 12px;
            }

            QMenuBar::item:selected {
                background-color: rgb(42,130,218);
            }

            QMenu {
                background-color: rgb(42,42,42);
                color: white;
                border: 1px solid rgb(127,127,127);
            }

            QMenu::item {
                padding: 8px 20px;
            }

            QMenu::item:selected {
                background-color: rgb(42,130,218);
            }
        """)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Configurar aplicación con tema oscuro como TFG
    app.setApplicationName("OPTIM by SoftVier - ETSIDI")
    app.setStyle('Fusion')

    # Aplicar paleta de colores oscura idéntica al TFG
    paleta_colores = QtGui.QPalette()
    paleta_colores.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(53, 53, 53))
    paleta_colores.setColor(QtGui.QPalette.ColorRole.WindowText, QtGui.QColor(QtGui.QColorConstants.White))
    paleta_colores.setColor(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.WindowText,
                            QtGui.QColor(127, 127, 127))
    paleta_colores.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(42, 42, 42))
    paleta_colores.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(66, 66, 66))
    paleta_colores.setColor(QtGui.QPalette.ColorRole.ToolTipBase, QtGui.QColor(QtGui.QColorConstants.White))
    paleta_colores.setColor(QtGui.QPalette.ColorRole.ToolTipText, QtGui.QColor(QtGui.QColorConstants.White))
    paleta_colores.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor(QtGui.QColorConstants.White))
    paleta_colores.setColor(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Text,
                            QtGui.QColor(127, 127, 127))
    paleta_colores.setColor(QtGui.QPalette.ColorRole.Dark, QtGui.QColor(35, 35, 35))
    paleta_colores.setColor(QtGui.QPalette.ColorRole.Shadow, QtGui.QColor(20, 20, 20))
    paleta_colores.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor(53, 53, 53))
    paleta_colores.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor(QtGui.QColorConstants.White))
    paleta_colores.setColor(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Button,
                            QtGui.QColor(60, 60, 60))
    paleta_colores.setColor(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.ButtonText,
                            QtGui.QColor(140, 140, 140))
    paleta_colores.setColor(QtGui.QPalette.ColorRole.BrightText, QtGui.QColor(QtGui.QColorConstants.Red))
    paleta_colores.setColor(QtGui.QPalette.ColorRole.Link, QtGui.QColor(42, 130, 218))
    paleta_colores.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(42, 130, 218))
    paleta_colores.setColor(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Highlight,
                            QtGui.QColor(80, 80, 80))
    paleta_colores.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor(QtGui.QColorConstants.White))
    paleta_colores.setColor(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.HighlightedText,
                            QtGui.QColor(127, 127, 127))
    app.setPalette(paleta_colores)

    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())