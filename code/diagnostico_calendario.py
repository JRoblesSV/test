#!/usr/bin/env python3
"""
Script de diagnóstico para encontrar el problema exacto
"""

import sys
import os
from PyQt6 import QtCore, QtGui, QtWidgets
from datetime import datetime


def test_basico():
    """Prueba básica de PyQt6"""
    print("🧪 FASE 1: Prueba básica PyQt6")
    try:
        app = QtWidgets.QApplication(sys.argv)
        print("✅ QApplication creada")

        window = QtWidgets.QMainWindow()
        print("✅ QMainWindow creada")

        window.setWindowTitle("Prueba Básica")
        window.resize(400, 300)
        print("✅ Configuración básica OK")

        # Solo mostrar si no estamos en modo batch
        if len(sys.argv) == 1:
            window.show()
            print("✅ Ventana mostrada - cerrando en 2 segundos...")
            QtCore.QTimer.singleShot(2000, app.quit)
            app.exec()

        return True
    except Exception as e:
        print(f"❌ Error en prueba básica: {e}")
        return False


def test_widgets_complejos():
    """Probar widgets que pueden causar problemas"""
    print("\n🧪 FASE 2: Probando widgets complejos")

    widgets_problemáticos = []

    try:
        app = QtWidgets.QApplication(sys.argv)
        window = QtWidgets.QMainWindow()
        central = QtWidgets.QWidget()
        window.setCentralWidget(central)

        # Test QCalendarWidget
        try:
            calendar = QtWidgets.QCalendarWidget(central)
            print("✅ QCalendarWidget OK")
        except Exception as e:
            print(f"❌ QCalendarWidget FALLA: {e}")
            widgets_problemáticos.append("QCalendarWidget")

        # Test QDateEdit
        try:
            date_edit = QtWidgets.QDateEdit(central)
            date_edit.setCalendarPopup(True)
            print("✅ QDateEdit con popup OK")
        except Exception as e:
            print(f"❌ QDateEdit FALLA: {e}")
            widgets_problemáticos.append("QDateEdit")

        # Test QSpinBox
        try:
            spin = QtWidgets.QSpinBox(central)
            print("✅ QSpinBox OK")
        except Exception as e:
            print(f"❌ QSpinBox FALLA: {e}")
            widgets_problemáticos.append("QSpinBox")

        return widgets_problemáticos

    except Exception as e:
        print(f"❌ Error general en widgets: {e}")
        return ["ERROR_GENERAL"]


def test_importacion_interfaces():
    """Probar importación de interfaces"""
    print("\n🧪 FASE 3: Probando importación interfaces")

    try:
        # Cambiar al directorio correcto
        if os.path.exists('interfaces'):
            print("✅ Directorio interfaces encontrado")
        else:
            print("❌ Directorio interfaces NO encontrado")
            return False

        # Test importación __init__.py
        try:
            from interfaces import ConfigurarCalendario, ConfigurarHorarios, VerResultados
            print("✅ Importación de interfaces OK")
        except Exception as e:
            print(f"❌ Error importando interfaces: {e}")
            return False

        # Test instanciación básica
        try:
            app = QtWidgets.QApplication(sys.argv)
            window = QtWidgets.QMainWindow()

            # Probar solo ConfigurarHorarios y VerResultados (que funcionan)
            horarios = ConfigurarHorarios(parent=window)
            print("✅ ConfigurarHorarios instanciado OK")

            resultados = VerResultados(parent=window)
            print("✅ VerResultados instanciado OK")

            # Probar ConfigurarCalendario
            calendario = ConfigurarCalendario(parent=window)
            print("✅ ConfigurarCalendario instanciado OK")

        except Exception as e:
            print(f"❌ Error instanciando interfaces: {e}")
            import traceback
            traceback.print_exc()
            return False

        return True

    except Exception as e:
        print(f"❌ Error general en interfaces: {e}")
        return False


def main():
    """Función principal de diagnóstico"""
    print("🔬 DIAGNÓSTICO DE CONFIGURAR CALENDARIO")
    print("=" * 50)

    # Cambiar al directorio code si existe
    if os.path.exists('code'):
        os.chdir('code')
        print("📁 Cambiado a directorio 'code'")

    # Fase 1: PyQt6 básico
    if not test_basico():
        print("\n❌ PROBLEMA FUNDAMENTAL CON PyQt6")
        print("Solución: Reinstalar PyQt6")
        return

    # Fase 2: Widgets complejos
    widgets_problemáticos = test_widgets_complejos()
    if widgets_problemáticos:
        print(f"\n⚠️ WIDGETS PROBLEMÁTICOS: {widgets_problemáticos}")

    # Fase 3: Interfaces
    if not test_importacion_interfaces():
        print("\n❌ PROBLEMA CON INTERFACES")
        return

    print("\n🎯 DIAGNÓSTICO COMPLETADO")
    print("=" * 50)

    if not widgets_problemáticos:
        print("✅ Todo parece estar bien - el problema puede ser específico")
    else:
        print(f"⚠️ Evitar estos widgets: {widgets_problemáticos}")


if __name__ == "__main__":
    main()