#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento de los métodos de farmacia
"""

from models.farmacia import Medicamento

def test_medicamentos_por_vencer():
    """Prueba el método obtener_por_vencer"""
    print("=== PRUEBA: Medicamentos Próximos a Vencer ===")
    try:
        medicamentos = Medicamento.obtener_por_vencer(dias=30, limite=5)
        print(f"✅ Éxito: {len(medicamentos)} medicamentos encontrados")
        for med in medicamentos:
            print(f"  - {med.get('nombre', 'N/A')}: vence en {med.get('dias_para_vencer', 'N/A')} días")
        return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_medicamentos_stock_bajo():
    """Prueba el método obtener_stock_bajo"""
    print("\n=== PRUEBA: Medicamentos con Stock Bajo ===")
    try:
        medicamentos = Medicamento.obtener_stock_bajo(umbral=10)
        print(f"✅ Éxito: {len(medicamentos)} medicamentos con stock bajo encontrados")
        for med in medicamentos:
            print(f"  - {med.get('nombre', 'N/A')}: stock = {med.get('stock', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_medicamentos_vencidos():
    """Prueba el método obtener_vencidos"""
    print("\n=== PRUEBA: Medicamentos Vencidos ===")
    try:
        medicamentos = Medicamento.obtener_vencidos()
        print(f"✅ Éxito: {len(medicamentos)} medicamentos vencidos encontrados")
        for med in medicamentos:
            print(f"  - {med.get('nombre', 'N/A')}: vencido hace {med.get('dias_vencido', 'N/A')} días")
        return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_listar_medicamentos():
    """Prueba el método listar para verificar conexión"""
    print("\n=== PRUEBA: Listar Medicamentos (verificación de conexión) ===")
    try:
        medicamentos = Medicamento.listar()
        print(f"✅ Éxito: {len(medicamentos)} medicamentos totales en la base de datos")
        if medicamentos:
            print(f"  Primer medicamento: {medicamentos[0].get('nombre', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de funcionalidad de farmacia...\n")

    tests = [
        test_listar_medicamentos,
        test_medicamentos_por_vencer,
        test_medicamentos_stock_bajo,
        test_medicamentos_vencidos
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n📊 RESUMEN DE PRUEBAS:")
    print(f"✅ Pruebas exitosas: {sum(results)}/{len(results)}")

    if all(results):
        print("🎉 Todas las pruebas pasaron correctamente!")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
