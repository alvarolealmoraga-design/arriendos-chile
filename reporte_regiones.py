import os
from itertools import groupby

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "arriendos.settings")
django.setup()

from django.db import connection

CONSULTA = """
    SELECT r.nombre AS region, i.nombre, i.descripcion, c.nombre AS comuna
    FROM inmuebles_inmueble AS i
    INNER JOIN inmuebles_comuna AS c ON c.id = i.comuna_id
    INNER JOIN inmuebles_region AS r ON r.id = c.region_id
    WHERE i.disponible = TRUE
    ORDER BY r.id, c.nombre, i.nombre;
"""

ARCHIVO = os.path.join("reportes", "inmuebles_por_region.txt")


def obtener_inmuebles():
    with connection.cursor() as cursor:
        cursor.execute(CONSULTA)
        return cursor.fetchall()


def generar_reporte(filas):
    lineas = ["LISTADO DE INMUEBLES PARA ARRIENDO POR REGIÓN", "=" * 60, ""]
    for region, inmuebles in groupby(filas, key=lambda fila: fila[0]):
        inmuebles = list(inmuebles)
        lineas.append(f"{region} ({len(inmuebles)})")
        lineas.append("-" * 60)
        for _, nombre, descripcion, comuna in inmuebles:
            lineas.append(f"  Nombre: {nombre}")
            lineas.append(f"  Descripción: {descripcion}")
            lineas.append(f"  Comuna: {comuna}")
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
