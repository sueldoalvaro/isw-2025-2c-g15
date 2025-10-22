"""
═══════════════════════════════════════════════════════════════════════
    ADMINISTRADOR DE BASE DE DATOS - EcoHarmony Park
═══════════════════════════════════════════════════════════════════════

Herramienta completa para administrar la base de datos del sistema.
Permite consultar, limpiar y gestionar todos los registros.

FUNCIONES DISPONIBLES:
  • Consultar todos los registros (usuarios, compras, entradas)
  • Ver estadísticas y resúmenes
  • Limpiar compras y entradas (mantener usuarios)
  • Limpiar todo (incluyendo usuarios)
  • Borrar registros específicos por ID
  • Resetear IDs de autoincremento

USO:
  python db_admin.py                    # Menú interactivo
  python db_admin.py consultar          # Ver todos los registros
  python db_admin.py stats              # Ver estadísticas
  python db_admin.py limpiar            # Limpiar compras/entradas
  python db_admin.py limpiar-todo       # Limpiar TODO
  python db_admin.py borrar-compra 5    # Borrar compra con ID 5

Autor: Sistema EcoHarmony Park
Fecha: Octubre 2025
═══════════════════════════════════════════════════════════════════════
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════

DB_PATH = Path(__file__).parent.parent / 'instance' / 'development.db'


# ═══════════════════════════════════════════════════════════════════════
# FUNCIONES DE CONSULTA
# ═══════════════════════════════════════════════════════════════════════

def consultar_todo():
    """Muestra todos los registros de la base de datos."""
    print("\n" + "="*70)
    print("📋 CONSULTA COMPLETA DE LA BASE DE DATOS")
    print("="*70)
    
    if not DB_PATH.exists():
        print("❌ La base de datos no existe")
        return
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            
            # USUARIOS
            print("\n" + "="*70)
            print("👥 USUARIOS")
            print("="*70)
            cur.execute("SELECT * FROM usuarios ORDER BY id")
            usuarios = cur.fetchall()
            
            if usuarios:
                for usuario in usuarios:
                    print(f"\n  ID: {usuario['id']}")
                    print(f"  Email: {usuario['email']}")
                    print(f"  Nombre: {usuario['nombre']}")
                    print("  " + "-"*60)
            else:
                print("  ⚠️  Sin registros")
            
            # COMPRAS
            print("\n" + "="*70)
            print("🛒 COMPRAS")
            print("="*70)
            cur.execute("""
                SELECT c.*, u.email, u.nombre
                FROM compras c
                JOIN usuarios u ON c.id_usuario = u.id
                ORDER BY c.id DESC
            """)
            compras = cur.fetchall()
            
            if compras:
                for compra in compras:
                    print(f"\n  ID Compra: {compra['id']}")
                    print(f"  Usuario: {compra['nombre']} ({compra['email']})")
                    print(f"  Fecha visita: {compra['fecha_visita']}")
                    print(f"  Cantidad: {compra['cantidad']}")
                    print(f"  Medio de pago: {compra['medio_pago']}")
                    print(f"  Fecha y hora: {compra['fecha_compra']}")
                    # Buscar entradas de esta compra
                    cur.execute("""
                        SELECT * FROM entradas 
                        WHERE id_compra = ? 
                        ORDER BY id
                    """, (compra['id'],))
                    entradas = cur.fetchall()
                    
                    total = 0
                    print(f"  Entradas:")
                    for entrada in entradas:
                        precio = 5000 if entrada['tipo_entrada'] == 'REGULAR' else 10000
                        total += precio
                        print(f"    • Edad {entrada['edad']} años - {entrada['tipo_entrada']} (${precio:,})")
                    print(f"  TOTAL: ${total:,}")
                    print("  " + "-"*60)
            else:
                print("  ⚠️  Sin registros")
            
            print("\n" + "="*70 + "\n")
            
    except sqlite3.Error as e:
        print(f"❌ Error: {e}")


def ver_estadisticas():
    """Muestra estadísticas resumidas de la base de datos."""
    print("\n" + "="*70)
    print("📊 ESTADÍSTICAS DE LA BASE DE DATOS")
    print("="*70)
    
    if not DB_PATH.exists():
        print("❌ La base de datos no existe")
        return
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            
            # Usuarios
            cur.execute("SELECT COUNT(*) FROM usuarios")
            total_usuarios = cur.fetchone()[0]
            
            # Compras
            cur.execute("SELECT COUNT(*) FROM compras")
            total_compras = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM compras WHERE medio_pago = 'EFECTIVO'")
            compras_efectivo = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM compras WHERE medio_pago = 'TARJETA'")
            compras_tarjeta = cur.fetchone()[0]
            
            # Entradas
            cur.execute("SELECT COUNT(*) FROM entradas")
            total_entradas = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM entradas WHERE tipo_entrada = 'REGULAR'")
            entradas_regular = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM entradas WHERE tipo_entrada = 'VIP'")
            entradas_vip = cur.fetchone()[0]
            
            # Total recaudado
            cur.execute("""
                SELECT SUM(
                    CASE 
                        WHEN tipo_entrada = 'REGULAR' THEN 5000 
                        WHEN tipo_entrada = 'VIP' THEN 10000 
                    END
                ) FROM entradas
            """)
            total_recaudado = cur.fetchone()[0] or 0
            
            # Promedio de entradas por compra
            promedio = total_entradas / total_compras if total_compras > 0 else 0
            
            # Compra más reciente
            cur.execute("""
                SELECT c.fecha_visita, u.nombre 
                FROM compras c 
                JOIN usuarios u ON c.id_usuario = u.id 
                ORDER BY c.id DESC 
                LIMIT 1
            """)
            ultima_compra = cur.fetchone()
            
            print(f"\n📈 RESUMEN GENERAL:")
            print(f"   • Total de usuarios: {total_usuarios}")
            print(f"   • Total de compras: {total_compras}")
            print(f"   • Total de entradas: {total_entradas}")
            print(f"   • Promedio entradas/compra: {promedio:.1f}")
            
            print(f"\n💳 MEDIOS DE PAGO:")
            print(f"   • Efectivo: {compras_efectivo} ({compras_efectivo/total_compras*100 if total_compras > 0 else 0:.1f}%)")
            print(f"   • Tarjeta: {compras_tarjeta} ({compras_tarjeta/total_compras*100 if total_compras > 0 else 0:.1f}%)")
            
            print(f"\n🎫 TIPOS DE ENTRADAS:")
            print(f"   • Regular: {entradas_regular} (${entradas_regular * 5000:,})")
            print(f"   • VIP: {entradas_vip} (${entradas_vip * 10000:,})")
            
            print(f"\n💰 RECAUDACIÓN:")
            print(f"   • Total: ${total_recaudado:,}")
            print(f"   • Promedio por compra: ${total_recaudado/total_compras if total_compras > 0 else 0:,.0f}")
            
            if ultima_compra:
                print(f"\n📅 ÚLTIMA COMPRA:")
                print(f"   • Usuario: {ultima_compra[1]}")
                print(f"   • Fecha visita: {ultima_compra[0]}")
            
            print("\n" + "="*70 + "\n")
            
    except sqlite3.Error as e:
        print(f"❌ Error: {e}")


def buscar_compra(compra_id):
    """Busca y muestra una compra específica por ID."""
    if not DB_PATH.exists():
        print("❌ La base de datos no existe")
        return
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            
            cur.execute("""
                SELECT c.*, u.email, u.nombre
                FROM compras c
                JOIN usuarios u ON c.id_usuario = u.id
                WHERE c.id = ?
            """, (compra_id,))
            
            compra = cur.fetchone()
            
            if not compra:
                print(f"❌ No se encontró la compra con ID {compra_id}")
                return
            
            print("\n" + "="*70)
            print(f"🔍 DETALLE DE COMPRA #{compra['id']}")
            print("="*70)
            print(f"\n👤 Usuario: {compra['nombre']} ({compra['email']})")
            print(f"📅 Fecha de visita: {compra['fecha_visita']}")
            print(f"💳 Medio de pago: {compra['medio_pago']}")
            print(f"📦 Cantidad de entradas: {compra['cantidad']}")
            
            # Entradas
            cur.execute("""
                SELECT * FROM entradas 
                WHERE id_compra = ? 
                ORDER BY id
            """, (compra_id,))
            entradas = cur.fetchall()
            
            print(f"\n🎫 ENTRADAS:")
            total = 0
            for i, entrada in enumerate(entradas, 1):
                precio = 5000 if entrada['tipo_entrada'] == 'REGULAR' else 10000
                total += precio
                print(f"   {i}. Visitante de {entrada['edad']} años")
                print(f"      Tipo: {entrada['tipo_entrada']}")
                print(f"      Precio: ${precio:,}")
            
            print(f"\n💰 TOTAL: ${total:,}")
            print("="*70 + "\n")
            
    except sqlite3.Error as e:
        print(f"❌ Error: {e}")


# ═══════════════════════════════════════════════════════════════════════
# FUNCIONES DE LIMPIEZA
# ═══════════════════════════════════════════════════════════════════════

def limpiar_compras_entradas():
    """Elimina todas las compras y entradas, mantiene usuarios."""
    print("\n" + "="*70)
    print("🗑️  LIMPIAR COMPRAS Y ENTRADAS")
    print("="*70)
    
    if not DB_PATH.exists():
        print("❌ La base de datos no existe")
        return
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            
            # Contar registros
            cur.execute("SELECT COUNT(*) FROM entradas")
            total_entradas = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM compras")
            total_compras = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM usuarios")
            total_usuarios = cur.fetchone()[0]
            
            print(f"\n📊 Estado actual:")
            print(f"   • Usuarios: {total_usuarios} (se mantendrán)")
            print(f"   • Compras: {total_compras} (se eliminarán)")
            print(f"   • Entradas: {total_entradas} (se eliminarán)")
            
            if total_compras == 0 and total_entradas == 0:
                print("\n✅ La base de datos ya está limpia")
                return
            
            print("\n⚠️  ATENCIÓN: Esta acción eliminará TODAS las compras y entradas")
            confirmacion = input("¿Estás seguro? (escribe 'SI' para confirmar): ")
            
            if confirmacion.upper() != 'SI':
                print("❌ Operación cancelada")
                return
            
            # Eliminar
            cur.execute("DELETE FROM entradas")
            cur.execute("DELETE FROM compras")
            
            # Resetear autoincrement
            cur.execute("DELETE FROM sqlite_sequence WHERE name IN ('compras', 'entradas')")
            
            conn.commit()
            
            print(f"\n✅ Limpieza completada:")
            print(f"   • {total_compras} compras eliminadas")
            print(f"   • {total_entradas} entradas eliminadas")
            print(f"   • {total_usuarios} usuarios conservados")
            print(f"   • IDs reseteados a 1")
            print()
            
    except sqlite3.Error as e:
        print(f"❌ Error: {e}")


def limpiar_todo():
    """Elimina TODOS los registros incluyendo usuarios."""
    print("\n" + "="*70)
    print("🗑️  LIMPIAR TODA LA BASE DE DATOS")
    print("="*70)
    
    if not DB_PATH.exists():
        print("❌ La base de datos no existe")
        return
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            
            # Contar registros
            cur.execute("SELECT COUNT(*) FROM entradas")
            total_entradas = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM compras")
            total_compras = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM usuarios")
            total_usuarios = cur.fetchone()[0]
            
            print(f"\n📊 Estado actual:")
            print(f"   • Usuarios: {total_usuarios}")
            print(f"   • Compras: {total_compras}")
            print(f"   • Entradas: {total_entradas}")
            
            print("\n⚠️⚠️⚠️  ATENCIÓN: SE ELIMINARÁN TODOS LOS DATOS ⚠️⚠️⚠️")
            print("Esto incluye usuarios, compras y entradas")
            confirmacion = input("¿Estás COMPLETAMENTE seguro? (escribe 'SI BORRAR TODO'): ")
            
            if confirmacion != 'SI BORRAR TODO':
                print("❌ Operación cancelada")
                return
            
            # Eliminar todo
            cur.execute("DELETE FROM entradas")
            cur.execute("DELETE FROM compras")
            cur.execute("DELETE FROM usuarios")
            cur.execute("DELETE FROM sqlite_sequence")
            
            conn.commit()
            
            print(f"\n✅ Base de datos completamente limpiada:")
            print(f"   • Todas las tablas vacías")
            print(f"   • IDs reseteados a 1")
            print()
            
    except sqlite3.Error as e:
        print(f"❌ Error: {e}")


# ═══════════════════════════════════════════════════════════════════════
# FUNCIONES DE BORRADO SELECTIVO
# ═══════════════════════════════════════════════════════════════════════

def borrar_compra(compra_id):
    """Elimina una compra específica y sus entradas asociadas."""
    if not DB_PATH.exists():
        print("❌ La base de datos no existe")
        return
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            
            # Verificar que existe
            cur.execute("SELECT * FROM compras WHERE id = ?", (compra_id,))
            compra = cur.fetchone()
            
            if not compra:
                print(f"❌ No existe una compra con ID {compra_id}")
                return
            
            # Contar entradas
            cur.execute("SELECT COUNT(*) FROM entradas WHERE id_compra = ?", (compra_id,))
            num_entradas = cur.fetchone()[0]
            
            print(f"\n⚠️  Se eliminará:")
            print(f"   • Compra #{compra_id}")
            print(f"   • {num_entradas} entrada(s) asociada(s)")
            
            confirmacion = input("\n¿Continuar? (S/N): ")
            
            if confirmacion.upper() != 'S':
                print("❌ Operación cancelada")
                return
            
            # Eliminar
            cur.execute("DELETE FROM entradas WHERE id_compra = ?", (compra_id,))
            cur.execute("DELETE FROM compras WHERE id = ?", (compra_id,))
            
            conn.commit()
            
            print(f"\n✅ Compra #{compra_id} eliminada correctamente")
            print(f"   • {num_entradas} entrada(s) eliminada(s)\n")
            
    except sqlite3.Error as e:
        print(f"❌ Error: {e}")


def borrar_usuario(usuario_id):
    """Elimina un usuario y todas sus compras asociadas."""
    if not DB_PATH.exists():
        print("❌ La base de datos no existe")
        return
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            
            # Verificar que existe
            cur.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
            usuario = cur.fetchone()
            
            if not usuario:
                print(f"❌ No existe un usuario con ID {usuario_id}")
                return
            
            # Contar compras
            cur.execute("SELECT COUNT(*) FROM compras WHERE id_usuario = ?", (usuario_id,))
            num_compras = cur.fetchone()[0]
            
            # Contar entradas
            cur.execute("""
                SELECT COUNT(*) FROM entradas 
                WHERE id_compra IN (
                    SELECT id FROM compras WHERE id_usuario = ?
                )
            """, (usuario_id,))
            num_entradas = cur.fetchone()[0]
            
            print(f"\n⚠️  Se eliminará:")
            print(f"   • Usuario: {usuario['nombre']} ({usuario['email']})")
            print(f"   • {num_compras} compra(s)")
            print(f"   • {num_entradas} entrada(s)")
            
            confirmacion = input("\n¿Continuar? (S/N): ")
            
            if confirmacion.upper() != 'S':
                print("❌ Operación cancelada")
                return
            
            # Eliminar (las entradas se eliminan por CASCADE)
            cur.execute("""
                DELETE FROM entradas 
                WHERE id_compra IN (
                    SELECT id FROM compras WHERE id_usuario = ?
                )
            """, (usuario_id,))
            cur.execute("DELETE FROM compras WHERE id_usuario = ?", (usuario_id,))
            cur.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
            
            conn.commit()
            
            print(f"\n✅ Usuario #{usuario_id} eliminado correctamente")
            print(f"   • {num_compras} compra(s) eliminada(s)")
            print(f"   • {num_entradas} entrada(s) eliminada(s)\n")
            
    except sqlite3.Error as e:
        print(f"❌ Error: {e}")


# ═══════════════════════════════════════════════════════════════════════
# MENÚ INTERACTIVO
# ═══════════════════════════════════════════════════════════════════════

def mostrar_menu():
    """Muestra el menú principal."""
    print("\n" + "="*70)
    print("🗃️  ADMINISTRADOR DE BASE DE DATOS - EcoHarmony Park")
    print("="*70)
    print("\n📋 CONSULTAS:")
    print("  1. Ver todos los registros")
    print("  2. Ver estadísticas")
    print("  3. Buscar compra por ID")
    
    print("\n🗑️  LIMPIEZA:")
    print("  4. Limpiar compras y entradas (mantener usuarios)")
    print("  5. Limpiar TODO (incluyendo usuarios)")
    
    print("\n❌ BORRADO SELECTIVO:")
    print("  6. Borrar una compra específica")
    print("  7. Borrar un usuario específico")
    
    print("\n  0. Salir")
    print("="*70)


def menu_interactivo():
    """Ejecuta el menú interactivo."""
    while True:
        mostrar_menu()
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion == '1':
            consultar_todo()
        elif opcion == '2':
            ver_estadisticas()
        elif opcion == '3':
            try:
                compra_id = int(input("Ingresa el ID de la compra: "))
                buscar_compra(compra_id)
            except ValueError:
                print("❌ ID inválido")
        elif opcion == '4':
            limpiar_compras_entradas()
        elif opcion == '5':
            limpiar_todo()
        elif opcion == '6':
            try:
                compra_id = int(input("Ingresa el ID de la compra a borrar: "))
                borrar_compra(compra_id)
            except ValueError:
                print("❌ ID inválido")
        elif opcion == '7':
            try:
                usuario_id = int(input("Ingresa el ID del usuario a borrar: "))
                borrar_usuario(usuario_id)
            except ValueError:
                print("❌ ID inválido")
        elif opcion == '0':
            print("\n👋 ¡Hasta luego!\n")
            break
        else:
            print("❌ Opción inválida")
        
        input("\nPresiona Enter para continuar...")


# ═══════════════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ═══════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    if len(sys.argv) > 1:
        comando = sys.argv[1].lower()
        
        if comando == 'consultar':
            consultar_todo()
        elif comando == 'stats':
            ver_estadisticas()
        elif comando == 'limpiar':
            limpiar_compras_entradas()
        elif comando == 'limpiar-todo':
            limpiar_todo()
        elif comando == 'borrar-compra' and len(sys.argv) > 2:
            try:
                compra_id = int(sys.argv[2])
                borrar_compra(compra_id)
            except ValueError:
                print("❌ ID inválido")
        elif comando == 'borrar-usuario' and len(sys.argv) > 2:
            try:
                usuario_id = int(sys.argv[2])
                borrar_usuario(usuario_id)
            except ValueError:
                print("❌ ID inválido")
        elif comando == 'buscar' and len(sys.argv) > 2:
            try:
                compra_id = int(sys.argv[2])
                buscar_compra(compra_id)
            except ValueError:
                print("❌ ID inválido")
        elif comando == 'help' or comando == '-h':
            print(__doc__)
        else:
            print(f"❌ Comando desconocido: {comando}")
            print("\nUso: python db_admin.py [comando] [argumentos]")
            print("\nComandos disponibles:")
            print("  consultar              - Ver todos los registros")
            print("  stats                  - Ver estadísticas")
            print("  buscar <id>            - Buscar compra por ID")
            print("  limpiar                - Limpiar compras/entradas")
            print("  limpiar-todo           - Limpiar TODO")
            print("  borrar-compra <id>     - Borrar compra específica")
            print("  borrar-usuario <id>    - Borrar usuario específico")
            print("  help                   - Mostrar ayuda")
    else:
        menu_interactivo()
