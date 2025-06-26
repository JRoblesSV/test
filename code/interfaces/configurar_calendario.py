import sys
import json
import os
from PyQt6 import QtCore, QtGui, QtWidgets
from datetime import datetime


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
            'dias_especiales': [],
            'dias_sin_clase': [],
            'fecha_creacion': datetime.now().isoformat()
        }

        self.setupUi()
        self.connect_signals_safely()
        self.cargar_configuracion_segura()

    def setupUi(self):
        """Configurar interfaz con mejor legibilidad"""
        # ========= VENTANA MÁS GRANDE =========
        self.setObjectName("ConfigurarCalendario")
        self.resize(1400, 880)  # Aumentado de 900x600 a 1400x800
        self.setMinimumSize(QtCore.QSize(1400, 880))
        self.setWindowTitle("OPTIM - Configurar Calendario Académico")

        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        # ========= TÍTULO MÁS GRANDE =========
        self.titulo = QtWidgets.QLabel(self.centralwidget)
        self.titulo.setGeometry(QtCore.QRect(50, 10, 1300, 50))  # Más ancho y alto
        self.titulo.setText(f"Configuración de Calendario Académico {self.year_actual}-{self.year_actual + 1}")
        self.titulo.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # ========= CONFIGURACIÓN CON MEJOR ESPACIADO =========
        self.setup_selector_year()
        self.setup_cuatrimestres()
        self.setup_dias_sin_clase()
        self.setup_dias_especiales()
        self.setup_vista_previa()
        self.setup_botones()
        self.apply_dark_theme_legible()

    def setup_selector_year(self):
        """Selector de año académico con mejor tamaño"""
        # Más separación del título
        y_start = 80

        self.label_year = QtWidgets.QLabel(self.centralwidget)
        self.label_year.setGeometry(QtCore.QRect(50, y_start, 150, 30))  # Más ancho y alto
        self.label_year.setText("Año Académico:")

        self.spin_year = QtWidgets.QSpinBox(self.centralwidget)
        self.spin_year.setGeometry(QtCore.QRect(220, y_start, 100, 35))  # Más grande
        self.spin_year.setMinimum(2020)
        self.spin_year.setMaximum(2030)
        self.spin_year.setValue(self.year_actual)

        self.label_year_display = QtWidgets.QLabel(self.centralwidget)
        self.label_year_display.setGeometry(QtCore.QRect(340, y_start, 150, 35))  # Más espacio
        self.label_year_display.setText(f"{self.year_actual}-{self.year_actual + 1}")

    def setup_cuatrimestres(self):
        """Configuración de cuatrimestres con mejor espaciado"""
        y_start = 140

        self.label_cuatrimestres = QtWidgets.QLabel(self.centralwidget)
        self.label_cuatrimestres.setGeometry(QtCore.QRect(50, y_start, 600, 35))  # Más ancho
        self.label_cuatrimestres.setText("Configuración de Períodos Académicos:")

        # Más separación entre cuatrimestres
        self.setup_cuatrimestre_simple(1, y_start + 50)
        self.setup_cuatrimestre_simple(2, y_start + 110)

    def setup_cuatrimestre_simple(self, numero, y_pos):
        """Configurar cuatrimestre con mejor espaciado"""
        # Etiqueta del cuatrimestre
        label = QtWidgets.QLabel(self.centralwidget)
        label.setGeometry(QtCore.QRect(50, y_pos, 150, 32))  # Más ancho
        label.setText(f"{numero}º Cuatrimestre:")

        # Inicio
        label_inicio = QtWidgets.QLabel(self.centralwidget)
        label_inicio.setGeometry(QtCore.QRect(220, y_pos, 70, 32))
        label_inicio.setText("Inicio:")

        line_inicio = QtWidgets.QLineEdit(self.centralwidget)
        line_inicio.setGeometry(QtCore.QRect(300, y_pos, 120, 32))  # Más ancho
        line_inicio.setPlaceholderText("YYYY-MM-DD")

        # Fin
        label_fin = QtWidgets.QLabel(self.centralwidget)
        label_fin.setGeometry(QtCore.QRect(440, y_pos, 70, 32))
        label_fin.setText("Fin:")

        line_fin = QtWidgets.QLineEdit(self.centralwidget)
        line_fin.setGeometry(QtCore.QRect(510, y_pos, 120, 32))  # Más ancho
        line_fin.setPlaceholderText("YYYY-MM-DD")

        # Botón establecer
        btn_establecer = QtWidgets.QPushButton(self.centralwidget)
        btn_establecer.setGeometry(QtCore.QRect(650, y_pos, 100, 32))  # Más ancho
        btn_establecer.setText("Establecer")

        # Guardar referencias
        if numero == 1:
            self.line_inicio_1 = line_inicio
            self.line_fin_1 = line_fin
            self.btn_establecer_1 = btn_establecer
        else:
            self.line_inicio_2 = line_inicio
            self.line_fin_2 = line_fin
            self.btn_establecer_2 = btn_establecer

    def setup_dias_sin_clase(self):
        """Configuración de días sin clase - MEJORADO"""
        x_start = 50
        y_start = 320

        self.label_dias = QtWidgets.QLabel(self.centralwidget)
        self.label_dias.setGeometry(QtCore.QRect(x_start, y_start, 200, 35))
        self.label_dias.setText("Días Sin Clase:")

        # Controles para añadir - MÁS ESPACIADO
        y_controls = y_start + 45
        self.label_nuevo_dia = QtWidgets.QLabel(self.centralwidget)
        self.label_nuevo_dia.setGeometry(QtCore.QRect(x_start, y_controls, 60, 30))
        self.label_nuevo_dia.setText("Fecha:")

        # ✅ QDateEdit MÁS ANCHO para que se vea el icono
        self.date_nuevo_dia = QtWidgets.QDateEdit(self.centralwidget)
        self.date_nuevo_dia.setGeometry(QtCore.QRect(x_start+60, y_controls, 100, 32))  # modifico 140 y no se hace mas pequeño
        self.date_nuevo_dia.setCalendarPopup(True)
        self.date_nuevo_dia.setDate(QtCore.QDate.currentDate())
        self.date_nuevo_dia.setDisplayFormat("yyyy-MM-dd")

        # ✅ Botón añadir CON MÁS ESPACIO
        self.btn_add_dia = QtWidgets.QPushButton(self.centralwidget)
        self.btn_add_dia.setGeometry(QtCore.QRect(x_start + 210, y_controls + 3, 90, 32))  # ✅ Más ancho y separado
        self.btn_add_dia.setText("Añadir")

        # Lista de días sin clase
        y_list = y_controls + 50  # ✅ Más separación
        self.lista_dias_sin_clase = QtWidgets.QListWidget(self.centralwidget)
        self.lista_dias_sin_clase.setGeometry(QtCore.QRect(x_start, y_list, 300, 120))

        # Botón eliminar debajo
        y_btn_eliminar = y_list + 130
        self.btn_remove_dia = QtWidgets.QPushButton(self.centralwidget)
        self.btn_remove_dia.setGeometry(QtCore.QRect(x_start, y_btn_eliminar, 120, 35))  # ✅ Más ancho
        self.btn_remove_dia.setText("🗑️ Eliminar")

    def setup_dias_especiales(self):
        """Configuración de días especiales - REORGANIZADO SIN DESCRIPCIÓN"""
        x_start = 400
        y_start = 320

        self.label_especiales = QtWidgets.QLabel(self.centralwidget)
        self.label_especiales.setGeometry(QtCore.QRect(x_start, y_start, 350, 35))
        self.label_especiales.setText("Días Especiales (horario de otro día):")

        # ✅ NUEVA ORGANIZACIÓN: Fecha en línea 1
        y_controls = y_start + 45

        self.label_fecha_especial = QtWidgets.QLabel(self.centralwidget)
        self.label_fecha_especial.setGeometry(QtCore.QRect(x_start, y_controls, 60, 30))
        self.label_fecha_especial.setText("Fecha:")

        # ✅ QDateEdit MÁS ANCHO para mostrar icono calendario
        self.date_fecha_especial = QtWidgets.QDateEdit(self.centralwidget)
        self.date_fecha_especial.setGeometry(QtCore.QRect(x_start + 105, y_controls, 100, 32))  # ✅ Más ancho
        self.date_fecha_especial.setCalendarPopup(True)
        self.date_fecha_especial.setDate(QtCore.QDate.currentDate())
        self.date_fecha_especial.setDisplayFormat("yyyy-MM-dd")

        # ✅ NUEVA LÍNEA 2: Horario de + Combo + Botón (SIN DESCRIPCIÓN)
        y_controls2 = y_controls + 45  # ✅ Más separación

        self.label_simula = QtWidgets.QLabel(self.centralwidget)
        self.label_simula.setGeometry(QtCore.QRect(x_start, y_controls2, 100, 30))
        self.label_simula.setText("Horario de:")

        # ✅ Combo MÁS ANCHO y mejor posicionado
        self.combo_dia_simula = QtWidgets.QComboBox(self.centralwidget)
        self.combo_dia_simula.setGeometry(QtCore.QRect(x_start + 105, y_controls2, 100, 32))  # ✅ Más ancho
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        self.combo_dia_simula.addItems(dias_semana)

        # ✅ Botón añadir CON BUEN ESPACIO
        self.btn_add_especial = QtWidgets.QPushButton(self.centralwidget)
        self.btn_add_especial.setGeometry(QtCore.QRect(x_start + 260, y_controls2, 90, 32))  # ✅ Mejor posición
        self.btn_add_especial.setText("Añadir")

        # ✅ Lista con MÁS SEPARACIÓN
        y_list_especial = y_controls2 + 50  # ✅ Más espacio
        self.lista_dias_especiales = QtWidgets.QListWidget(self.centralwidget)
        self.lista_dias_especiales.setGeometry(QtCore.QRect(x_start, y_list_especial, 350, 120))  # ✅ Más ancha

        # Botón eliminar debajo
        y_btn_eliminar_especial = y_list_especial + 130
        self.btn_remove_especial = QtWidgets.QPushButton(self.centralwidget)
        self.btn_remove_especial.setGeometry(QtCore.QRect(x_start, y_btn_eliminar_especial, 130, 35))  # ✅ Más ancho
        self.btn_remove_especial.setText("🗑️ Eliminar")

    def setup_vista_previa(self):
        """Vista previa más grande y legible"""
        x_preview = 800  # Más a la derecha
        y_preview = 140

        self.label_vista = QtWidgets.QLabel(self.centralwidget)
        self.label_vista.setGeometry(QtCore.QRect(x_preview, y_preview, 550, 30))
        self.label_vista.setText("Vista Previa de Configuración:")

        # Área de vista previa más grande
        self.vista_previa = QtWidgets.QTextEdit(self.centralwidget)
        self.vista_previa.setGeometry(QtCore.QRect(x_preview, y_preview + 40, 550, 400))  # Mucho más grande
        self.vista_previa.setReadOnly(True)

    def setup_botones(self):
        """Botones principales más grandes"""
        y_buttons = 780  # Más abajo
        x_center = 600   # Centrados

        self.btn_guardar = QtWidgets.QPushButton(self.centralwidget)
        self.btn_guardar.setGeometry(QtCore.QRect(x_center, y_buttons, 120, 45))  # Más grandes
        self.btn_guardar.setText("💾 Guardar")

        self.btn_cargar = QtWidgets.QPushButton(self.centralwidget)
        self.btn_cargar.setGeometry(QtCore.QRect(x_center + 140, y_buttons, 120, 45))
        self.btn_cargar.setText("📂 Cargar")

        self.btn_cerrar = QtWidgets.QPushButton(self.centralwidget)
        self.btn_cerrar.setGeometry(QtCore.QRect(x_center + 280, y_buttons, 120, 45))
        self.btn_cerrar.setText("✅ Cerrar")

    def connect_signals_safely(self):
        """Conectar todas las señales de forma segura"""
        try:
            self.spin_year.valueChanged.connect(self.on_year_changed)
            self.btn_establecer_1.clicked.connect(lambda: self.establecer_cuatrimestre(1))
            self.btn_establecer_2.clicked.connect(lambda: self.establecer_cuatrimestre(2))
            self.btn_add_dia.clicked.connect(self.add_dia_sin_clase)
            self.btn_remove_dia.clicked.connect(self.remove_dia_sin_clase)
            self.btn_guardar.clicked.connect(self.guardar_configuracion)
            self.btn_cargar.clicked.connect(self.cargar_configuracion)
            self.btn_cerrar.clicked.connect(self.close)
            self.btn_add_especial.clicked.connect(self.add_dia_especial)
            self.btn_remove_especial.clicked.connect(self.remove_dia_especial)
        except Exception as e:
            print(f"Error conectando señales: {e}")

    # ========= MÉTODOS FUNCIONALES =========

    def on_year_changed(self, year):
        """Cambiar año del calendario"""
        try:
            self.year_actual = year
            self.calendario_data['year'] = year
            self.label_year_display.setText(f"{year}-{year + 1}")
            self.titulo.setText(f"Configuración de Calendario Académico {year}-{year + 1}")
            self.actualizar_vista_previa()
        except Exception as e:
            print(f"Error cambiando año: {e}")

    def establecer_cuatrimestre(self, numero):
        """Establecer fechas de cuatrimestre"""
        try:
            if numero == 1:
                inicio = self.line_inicio_1.text().strip()
                fin = self.line_fin_1.text().strip()
                if self.validar_fecha(inicio) and self.validar_fecha(fin):
                    self.calendario_data['cuatrimestre_1'] = {'inicio': inicio, 'fin': fin}
                    self.mostrar_mensaje("✅ Éxito", f"1º Cuatrimestre configurado: {inicio} → {fin}")
                else:
                    self.mostrar_mensaje("❌ Error", "Formato de fecha inválido. Use YYYY-MM-DD")
                    return
            else:
                inicio = self.line_inicio_2.text().strip()
                fin = self.line_fin_2.text().strip()
                if self.validar_fecha(inicio) and self.validar_fecha(fin):
                    self.calendario_data['cuatrimestre_2'] = {'inicio': inicio, 'fin': fin}
                    self.mostrar_mensaje("✅ Éxito", f"2º Cuatrimestre configurado: {inicio} → {fin}")
                else:
                    self.mostrar_mensaje("❌ Error", "Formato de fecha inválido. Use YYYY-MM-DD")
                    return

            self.actualizar_vista_previa()
        except Exception as e:
            print(f"Error estableciendo cuatrimestre: {e}")
            self.mostrar_mensaje("❌ Error", f"Error configurando cuatrimestre: {str(e)}")

    def add_dia_sin_clase(self):
        """Añadir día sin clase"""
        try:
            fecha_qdate = self.date_nuevo_dia.date()
            fecha = fecha_qdate.toString("yyyy-MM-dd")
            if not fecha:
                self.mostrar_mensaje("⚠️ Aviso", "Introduzca una fecha")
                return

            if not self.validar_fecha(fecha):
                self.mostrar_mensaje("❌ Error", "Formato de fecha inválido. Use YYYY-MM-DD")
                return

            if fecha not in self.calendario_data['dias_sin_clase']:
                self.calendario_data['dias_sin_clase'].append(fecha)
                self.calendario_data['dias_sin_clase'].sort()
                self.actualizar_lista_dias_sin_clase()
                self.actualizar_vista_previa()
                self.date_nuevo_dia.setDate(QtCore.QDate.currentDate())
                self.mostrar_mensaje("✅ Éxito", f"Día sin clase añadido: {fecha}")
            else:
                self.mostrar_mensaje("⚠️ Aviso", "Esta fecha ya está en la lista")
        except Exception as e:
            print(f"Error añadiendo día: {e}")

    def remove_dia_sin_clase(self):
        """Eliminar día sin clase seleccionado"""
        try:
            item_actual = self.lista_dias_sin_clase.currentItem()
            if item_actual:
                fecha = item_actual.text()
                if fecha in self.calendario_data['dias_sin_clase']:
                    self.calendario_data['dias_sin_clase'].remove(fecha)
                    self.actualizar_lista_dias_sin_clase()
                    self.actualizar_vista_previa()
                    self.mostrar_mensaje("✅ Éxito", f"Día eliminado: {fecha}")
            else:
                self.mostrar_mensaje("⚠️ Aviso", "Seleccione un día de la lista para eliminar")
        except Exception as e:
            print(f"Error eliminando día: {e}")

    def actualizar_lista_dias_sin_clase(self):
        """Actualizar lista visual de días sin clase"""
        try:
            self.lista_dias_sin_clase.clear()
            for fecha in sorted(self.calendario_data['dias_sin_clase']):
                self.lista_dias_sin_clase.addItem(fecha)
        except Exception as e:
            print(f"Error actualizando lista: {e}")

    def validar_fecha(self, fecha_str):
        """Validar formato de fecha YYYY-MM-DD"""
        try:
            datetime.strptime(fecha_str, '%Y-%m-%d')
            return True
        except:
            return False

    # ========= MÉTODOS PARA DÍAS ESPECIALES =========

    def add_dia_especial(self):
        """Añadir día especial (SIN campo descripción)"""
        try:
            fecha_qdate = self.date_fecha_especial.date()
            fecha = fecha_qdate.toString("yyyy-MM-dd")
            dia_simula = self.combo_dia_simula.currentText()
            # ✅ ELIMINADO: descripcion = self.line_desc_especial.text().strip()

            if not fecha:
                self.mostrar_mensaje("⚠️ Aviso", "Introduzca una fecha")
                return

            if not self.validar_fecha(fecha):
                self.mostrar_mensaje("❌ Error", "Formato de fecha inválido. Use YYYY-MM-DD")
                return

            # Verificar que no esté duplicado
            for especial in self.calendario_data['dias_especiales']:
                if especial['fecha'] == fecha:
                    self.mostrar_mensaje("⚠️ Aviso", "Esta fecha ya está configurada como día especial")
                    return

            # Verificar que no esté en días sin clase
            if fecha in self.calendario_data['dias_sin_clase']:
                self.mostrar_mensaje("⚠️ Aviso", "Esta fecha está marcada como día sin clase. Elimínela primero.")
                return

            # ✅ Añadir día especial SIN descripción personalizada
            nuevo_especial = {
                'fecha': fecha,
                'tipo_dia': dia_simula.lower(),
                'descripcion': f"Horario de {dia_simula}"  # ✅ Descripción automática
            }

            self.calendario_data['dias_especiales'].append(nuevo_especial)
            self.actualizar_lista_dias_especiales()
            self.actualizar_vista_previa()

            # ✅ Limpiar campos (SIN line_desc_especial)
            self.date_fecha_especial.setDate(QtCore.QDate.currentDate())
            # ✅ ELIMINADO: self.line_desc_especial.clear()

            self.mostrar_mensaje("✅ Éxito", f"Día especial añadido: {fecha} → Horario de {dia_simula}")

        except Exception as e:
            print(f"Error añadiendo día especial: {e}")
            self.mostrar_mensaje("❌ Error", f"Error añadiendo día especial: {str(e)}")

    def remove_dia_especial(self):
        """Eliminar día especial seleccionado"""
        try:
            item_actual = self.lista_dias_especiales.currentItem()
            if item_actual:
                # El texto del item es "YYYY-MM-DD → Horario de Lunes (Descripción)"
                texto_item = item_actual.text()
                fecha = texto_item.split(' →')[0]

                # Buscar y eliminar
                for i, especial in enumerate(self.calendario_data['dias_especiales']):
                    if especial['fecha'] == fecha:
                        del self.calendario_data['dias_especiales'][i]
                        break

                self.actualizar_lista_dias_especiales()
                self.actualizar_vista_previa()
                self.mostrar_mensaje("✅ Éxito", f"Día especial eliminado: {fecha}")
            else:
                self.mostrar_mensaje("⚠️ Aviso", "Seleccione un día especial de la lista para eliminar")
        except Exception as e:
            print(f"Error eliminando día especial: {e}")

    def actualizar_lista_dias_especiales(self):
        """Actualizar lista visual de días especiales"""
        try:
            self.lista_dias_especiales.clear()
            for especial in sorted(self.calendario_data['dias_especiales'], key=lambda x: x['fecha']):
                fecha = especial['fecha']
                tipo_dia = especial['tipo_dia'].capitalize()
                descripcion = especial.get('descripcion', '')

                # Formato: "2025-10-12 → Horario de Lunes (Día del Pilar)"
                texto = f"{fecha} → Horario de {tipo_dia}"
                if descripcion and descripcion != f"Horario de {tipo_dia}":
                    texto += f" ({descripcion})"

                self.lista_dias_especiales.addItem(texto)
        except Exception as e:
            print(f"Error actualizando lista días especiales: {e}")

    # ========= OTROS MÉTODOS =========

    def actualizar_vista_previa(self):
        """Actualizar vista previa"""
        try:
            preview = f"CONFIGURACIÓN CALENDARIO ACADÉMICO {self.calendario_data['year']}-{self.calendario_data['year'] + 1}\n"
            preview += "=" * 60 + "\n\n"

            # Períodos académicos (igual)
            preview += "📅 PERÍODOS ACADÉMICOS:\n"
            if self.calendario_data['cuatrimestre_1']['inicio']:
                preview += f"  1º Cuatrimestre: {self.calendario_data['cuatrimestre_1']['inicio']} → {self.calendario_data['cuatrimestre_1']['fin']}\n"
            else:
                preview += "  1º Cuatrimestre: Sin configurar\n"

            if self.calendario_data['cuatrimestre_2']['inicio']:
                preview += f"  2º Cuatrimestre: {self.calendario_data['cuatrimestre_2']['inicio']} → {self.calendario_data['cuatrimestre_2']['fin']}\n"
            else:
                preview += "  2º Cuatrimestre: Sin configurar\n"

            # 🆕 DÍAS ESPECIALES
            preview += f"\n🟨 DÍAS ESPECIALES ({len(self.calendario_data['dias_especiales'])}):\n"
            if self.calendario_data['dias_especiales']:
                for especial in sorted(self.calendario_data['dias_especiales'], key=lambda x: x['fecha']):
                    tipo_display = especial['tipo_dia'].capitalize()
                    desc = f" - {especial['descripcion']}" if especial.get('descripcion') else ""
                    preview += f"  • {especial['fecha']} → Horario de {tipo_display}{desc}\n"
            else:
                preview += "  (Ninguno configurado)\n"

            # Días sin clase
            preview += f"\n🟥 DÍAS SIN CLASE ({len(self.calendario_data['dias_sin_clase'])}):\n"
            if self.calendario_data['dias_sin_clase']:
                for fecha in sorted(self.calendario_data['dias_sin_clase']):
                    preview += f"  • {fecha}\n"
            else:
                preview += "  (Ninguno configurado)\n"

            # Estadísticas actualizadas
            cuatrimestres_config = sum(
                1 for c in [self.calendario_data['cuatrimestre_1'], self.calendario_data['cuatrimestre_2']] if
                c['inicio'])

            total_dias_especiales = len(self.calendario_data['dias_especiales']) + len(
                self.calendario_data['dias_sin_clase'])

            preview += f"\n📊 ESTADÍSTICAS:\n"
            preview += f"  • Cuatrimestres configurados: {cuatrimestres_config}/2\n"
            preview += f"  • Días especiales: {len(self.calendario_data['dias_especiales'])}\n"
            preview += f"  • Días sin clase: {len(self.calendario_data['dias_sin_clase'])}\n"
            preview += f"  • Total días no estándar: {total_dias_especiales}\n"

            self.vista_previa.setText(preview)
        except Exception as e:
            print(f"Error actualizando vista previa: {e}")
            self.vista_previa.setText("Error generando vista previa")

    def guardar_configuracion(self):
        """Guardar configuración"""
        try:
            os.makedirs("config", exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.calendario_data, f, indent=2, ensure_ascii=False)
            self.mostrar_mensaje("✅ Éxito", f"Configuración guardada en:\n{self.config_path}")
        except Exception as e:
            print(f"Error guardando: {e}")
            self.mostrar_mensaje("❌ Error", f"Error guardando:\n{str(e)}")

    def cargar_configuracion(self):
        """Cargar configuración"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.calendario_data = json.load(f)

                if self.calendario_data['cuatrimestre_1']['inicio']:
                    self.line_inicio_1.setText(self.calendario_data['cuatrimestre_1']['inicio'])
                    self.line_fin_1.setText(self.calendario_data['cuatrimestre_1']['fin'])

                if self.calendario_data['cuatrimestre_2']['inicio']:
                    self.line_inicio_2.setText(self.calendario_data['cuatrimestre_2']['inicio'])
                    self.line_fin_2.setText(self.calendario_data['cuatrimestre_2']['fin'])

                self.actualizar_lista_dias_sin_clase()
                self.actualizar_lista_dias_especiales()
                self.actualizar_vista_previa()
                self.mostrar_mensaje("✅ Éxito", "Configuración cargada")
            else:
                self.cargar_configuracion_defecto()
        except Exception as e:
            print(f"Error cargando: {e}")
            self.mostrar_mensaje("❌ Error", f"Error cargando:\n{str(e)}")
            self.cargar_configuracion_defecto()

    def cargar_configuracion_segura(self):
        """Cargar configuración con manejo de errores"""
        try:
            self.cargar_configuracion_defecto()
        except Exception as e:
            print(f"Error en configuración segura: {e}")

    def cargar_configuracion_defecto(self):
        """ACTUALIZAR configuración por defecto para incluir días especiales"""
        try:
            year = self.year_actual
            self.calendario_data = {
                'year': year,
                'cuatrimestre_1': {
                    'inicio': f"{year}-09-16",
                    'fin': f"{year + 1}-01-20"
                },
                'cuatrimestre_2': {
                    'inicio': f"{year + 1}-02-03",
                    'fin': f"{year + 1}-06-06"
                },
                # 🆕 DÍAS ESPECIALES CON EJEMPLOS
                'dias_especiales': [
                    {
                        'fecha': f"{year}-10-12",
                        'tipo_dia': 'lunes',
                        'descripcion': 'Día del Pilar'
                    },
                    {
                        'fecha': f"{year}-12-06",
                        'tipo_dia': 'martes',
                        'descripcion': 'Día de la Constitución'
                    }
                ],
                'dias_sin_clase': [
                    f"{year}-11-01",  # Todos los Santos
                    f"{year}-12-25",  # Navidad
                    f"{year + 1}-01-01"  # Año Nuevo
                ],
                'fecha_creacion': datetime.now().isoformat()
            }

            # Actualizar campos si existen
            if hasattr(self, 'line_inicio_1'):
                self.line_inicio_1.setText(f"{year}-09-16")
                self.line_fin_1.setText(f"{year + 1}-01-20")
                self.line_inicio_2.setText(f"{year + 1}-02-03")
                self.line_fin_2.setText(f"{year + 1}-06-06")

                self.actualizar_lista_dias_sin_clase()
                # 🆕 ACTUALIZAR LISTA DÍAS ESPECIALES
                if hasattr(self, 'lista_dias_especiales'):
                    self.actualizar_lista_dias_especiales()
                self.actualizar_vista_previa()
        except Exception as e:
            print(f"Error configuración defecto: {e}")

    def mostrar_mensaje(self, titulo, mensaje):
        """Mostrar mensaje"""
        try:
            msg_box = QtWidgets.QMessageBox(self)
            msg_box.setWindowTitle(titulo)
            msg_box.setText(mensaje)
            msg_box.exec()
        except Exception as e:
            print(f"Error mostrando mensaje: {e}")

    def apply_dark_theme_legible(self):
        """Aplicar tema oscuro con fuentes más grandes y legibles"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: rgb(53,53,53);
                color: white;
            }
            QWidget {
                background-color: rgb(53,53,53);
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;  /* Aumentado de 11px */
            }
            QLabel {
                color: white;
                font-size: 13px;  /* Aumentado de 11px */
                font-weight: bold;
            }
            QPushButton {
                background-color: rgb(53,53,53);
                color: white;
                border: 1px solid rgb(127,127,127);
                padding: 10px;  /* Aumentado de 8px */
                font-size: 12px;  /* Aumentado de 10px */
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgb(66,66,66);
                border: 1px solid rgb(42,130,218);
            }
            QLineEdit {
                background-color: rgb(42,42,42);
                color: white;
                border: 1px solid rgb(127,127,127);
                padding: 8px;  /* Aumentado de 5px */
                font-size: 12px;  /* Aumentado de 11px */
                border-radius: 3px;
            }
            QLineEdit:focus {
                border: 2px solid rgb(42,130,218);
            }
            QSpinBox {
                background-color: rgb(42,42,42);
                color: white;
                border: 1px solid rgb(127,127,127);
                padding: 8px;  /* Aumentado de 5px */
                font-size: 12px;
                border-radius: 3px;
            }
            QSpinBox:focus {
                border: 2px solid rgb(42,130,218);
            }
            
            /* ✅ AÑADIR ESTOS ESTILOS PARA QDateEdit */
            QDateEdit {
                background-color: rgb(42,42,42);
                color: white;
                border: 1px solid rgb(127,127,127);
                padding: 8px 25px 8px 8px;  /* ✅ Más padding a la derecha para el icono */
                font-size: 12px;
                border-radius: 3px;
                min-width: 100px;  /* ✅ Más ancho */
                min-height: 20px;
            }
            QDateEdit:focus {
                border: 2px solid rgb(42,130,218);
            }
            QDateEdit::drop-down {
                background-color: rgb(53,53,53);
                border: 1px solid rgb(127,127,127);
                border-radius: 3px;
                width: 25px;  /* ✅ Más ancho para el botón */
                height: 20px;
                subcontrol-position: right;
                subcontrol-origin: padding;
            }
            QDateEdit::drop-down:hover {
                background-color: rgb(42,130,218);
                border: 1px solid rgb(42,130,218);
            }
            QDateEdit::down-arrow {
                width: 12px;
                height: 12px;
                background-color: rgb(200,200,200);  /* ✅ Color visible para la flecha */
                border: none;
            }
            QDateEdit::down-arrow:hover {
                background-color: white;  /* ✅ Más visible al hover */
            }
            /* ✅ ESTILOS PARA EL CALENDARIO POPUP */
            QCalendarWidget {
                background-color: rgb(42,42,42);
                color: white;
                border: 2px solid rgb(42,130,218);
                border-radius: 8px;  /* ✅ Más redondeado */
                font-size: 11px;
                min-width: 300px;  /* ✅ Calendario más grande */
                min-height: 200px;
            }
            QCalendarWidget QToolButton {
                background-color: rgb(53,53,53);
                color: white;
                border: 1px solid rgb(127,127,127);
                border-radius: 4px;
                padding: 5px;  /* ✅ Más padding */
                font-size: 12px;  /* ✅ Texto más grande */
                font-weight: bold;
                min-width: 30px;
                min-height: 25px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: rgb(42,130,218);
                color: white;
            }
            QCalendarWidget QMenu {
                background-color: rgb(42,42,42);
                color: white;
                border: 1px solid rgb(127,127,127);
                font-size: 11px;
            }
            QCalendarWidget QSpinBox {
                background-color: rgb(42,42,42);
                color: white;
                border: 1px solid rgb(127,127,127);
                font-size: 12px;  /* ✅ Más grande */
                padding: 3px;
                selection-background-color: rgb(42,130,218);
            }
            QCalendarWidget QAbstractItemView {
                background-color: rgb(42,42,42);
                color: white;
                selection-background-color: rgb(42,130,218);
                selection-color: white;
                font-size: 11px;
                gridline-color: rgb(60,60,60);
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: white;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: rgb(35,35,35);
                border-bottom: 1px solid rgb(127,127,127);
            }
            QCalendarWidget QAbstractItemView:item {
                padding: 5px;  /* ✅ Más espacio en cada día */
            }
            QCalendarWidget QAbstractItemView:item:selected {
                background-color: rgb(42,130,218);
                color: white;
                border-radius: 3px;
            }
            /* ✅ AÑADIR ESTILOS COMBOBOX SI NO ESTÁN */
            QComboBox {
                background-color: rgb(42,42,42);
                color: white;
                border: 1px solid rgb(127,127,127);
                padding: 8px 25px 8px 8px;  /* ✅ Más padding para el icono dropdown */
                font-size: 12px;
                border-radius: 3px;
                min-width: 100px;
                min-height: 20px;
            }
            QComboBox:focus {
                border: 2px solid rgb(42,130,218);
            }
            QComboBox::drop-down {
                background-color: rgb(53,53,53);
                border: 1px solid rgb(127,127,127);
                border-radius: 3px;
                width: 25px;  /* ✅ Más ancho */
                height: 20px;
                subcontrol-position: right;
                subcontrol-origin: padding;
            }
            QComboBox::drop-down:hover {
                background-color: rgb(42,130,218);
                border: 1px solid rgb(42,130,218);
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
                background-color: rgb(200,200,200);  /* ✅ Flecha visible */
                border: none;
            }
            QComboBox::down-arrow:hover {
                background-color: white;  /* ✅ Más visible al hover */
            }
            QComboBox QAbstractItemView {
                background-color: rgb(42,42,42);
                color: white;
                border: 1px solid rgb(127,127,127);
                selection-background-color: rgb(42,130,218);
                selection-color: white;
                font-size: 12px;
                padding: 5px;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px;  /* ✅ Más espacio entre opciones */
                border-bottom: 1px solid rgb(60,60,60);
                min-height: 20px;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: rgb(42,130,218);
                color: white;
            }
            QTextEdit {
                background-color: rgb(42,42,42);
                color: white;
                border: 1px solid rgb(127,127,127);
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;  /* Aumentado de 10px */
                line-height: 1.4;
                padding: 10px;
                border-radius: 3px;
            }
            QListWidget {
                background-color: rgb(42,42,42);
                color: white;
                border: 1px solid rgb(127,127,127);
                font-size: 12px;  /* Aumentado */
                selection-background-color: rgb(42,130,218);
                padding: 5px;
                border-radius: 3px;
            }
            QListWidget::item {
                padding: 8px;  /* Más espacio entre items */
                border-bottom: 1px solid rgb(60,60,60);
            }
            QListWidget::item:selected {
                background-color: rgb(42,130,218);
                color: white;
            }
            QMessageBox {
                background-color: rgb(53,53,53);
                color: white;
                font-size: 12px;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 12px;
            }
            QMessageBox QPushButton {
                min-width: 80px;
                min-height: 30px;
                font-size: 11px;
            }
        """)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')

    window = ConfigurarCalendario()
    window.show()
    sys.exit(app.exec())