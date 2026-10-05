import os
from itertools import groupby

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "arriendos.settings")
django.setup()

from django.db import connection

CONSULTA = """
    SELECT c.nombre AS comuna, i.nombre, i.descripcion
    FROM inmuebles_inmueble AS i
    INNER JOIN inmuebles_comuna AS c ON c.id = i.comuna_id
    WHERE i.disponible = TRUE
    ORDER BY c.nombre, i.nombre;
"""

ARCHIVO = os.path.join("reportes", "inmuebles_por_comuna.txt")


def obtener_inmuebles():
    with connection.cursor() as cursor:
        cursor.execute(CONSULTA)
        return cursor.fetchall()


def generar_reporte(filas):
    lineas = ["LISTADO DE INMUEBLES PARA ARRIENDO POR COMUNA", "=" * 60, ""]
    for comuna, inmuebles in groupby(filas, key=lambda fila: fila[0]):
        inmuebles = list(inmuebles)
        lineas.append(f"Comuna: {comuna} ({len(inmuebles)})")
        lineas.append("-" * 60)
        for _, nombre, descripcion in inmuebles:
            lineas.append(f"  Nombre: {nombre}")
            lineas.append(f"  Descripción: {descripcion}")
            lineas.append("")
        lineas.append("")
    lineas.append(f"Total de inmuebles disponibles: {len(filas)}")
    return "\n".join(lineas)


if __name__ == "__main__":
    filas = obtener_inmuebles()
    os.makedirs("reportes", exist_ok=True)
    with open(ARCHIVO, "w", encoding="utf-8") as archivo:
        archivo.write(generar_reporte(filas))
    print(f"Reporte generado en {ARCHIVO} ({len(filas)} inmuebles)")
