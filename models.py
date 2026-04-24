from database import get_db

MINUTOS_CATEGORIA = {
    'benjamin': 50,
    'alevin': 60,
    'infantil': 70,
    'cadete': 80,
    'juvenil': 90,
}

def get_minutos_partido(categoria):
    return MINUTOS_CATEGORIA.get(categoria.lower(), 60)

def get_stats_jugadores(equipo_id):
    conn = get_db()
    c = conn.cursor()

    equipo = c.execute('SELECT * FROM equipos WHERE id=?', (equipo_id,)).fetchone()
    mins_partido = get_minutos_partido(equipo['categoria'])

    num_partidos = c.execute(
        'SELECT COUNT(*) as n FROM partidos WHERE equipo_id=?', (equipo_id,)
    ).fetchone()['n']

    mins_posibles = num_partidos * mins_partido

    jugadores = c.execute(
        'SELECT * FROM jugadores WHERE equipo_id=?', (equipo_id,)
    ).fetchall()

    stats = []
    for j in jugadores:
        total = c.execute(
            'SELECT COALESCE(SUM(minutos),0) as t FROM minutos WHERE jugador_id=?',
            (j['id'],)
        ).fetchone()['t']
        pct = round((total / mins_posibles * 100), 1) if mins_posibles > 0 else 0
        stats.append({
            'id': j['id'],
            'nombre': j['nombre'],
            'minutos_totales': total,
            'minutos_posibles': mins_posibles,
            'porcentaje': pct,
        })

    conn.close()
    return stats, num_partidos, mins_partido