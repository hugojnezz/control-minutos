from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from database import init_db, get_db
from models import get_stats_jugadores, get_minutos_partido
import hashlib

app = Flask(__name__, static_folder='static')
app.secret_key = 'clave_secreta_control_minutos_2025'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

CATEGORIAS = ['benjamin', 'alevin', 'infantil', 'cadete', 'juvenil']


class Usuario(UserMixin):
    def __init__(self, id, nombre, email):
        self.id = id
        self.nombre = nombre
        self.email = email


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    u = conn.execute(
        'SELECT * FROM usuarios WHERE id=?',
        (user_id,)
    ).fetchone()
    conn.close()

    if u:
        return Usuario(u['id'], u['nombre'], u['email'])
    return None


@app.route('/')
@login_required
def index():
    conn = get_db()
    equipos = conn.execute(
        'SELECT * FROM equipos WHERE usuario_id=? ORDER BY club',
        (current_user.id,)
    ).fetchall()
    conn.close()
    return render_template('index.html', equipos=equipos)


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']

        if not nombre or not email or not password:
            flash('Todos los campos son obligatorios.')
            return render_template('registro.html')

        conn = get_db()
        try:
            conn.execute(
                'INSERT INTO usuarios (nombre, email, password) VALUES (?,?,?)',
                (nombre, email, hash_password(password))
            )
            conn.commit()
            flash('Cuenta creada correctamente. Ya puedes iniciar sesión.')
            return redirect(url_for('login'))
        except Exception:
            flash('Ese email ya está registrado.')
        finally:
            conn.close()

    return render_template('registro.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = hash_password(request.form['password'])

        conn = get_db()
        u = conn.execute(
            'SELECT * FROM usuarios WHERE email=? AND password=?',
            (email, password)
        ).fetchone()
        conn.close()

        if u:
            usuario = Usuario(u['id'], u['nombre'], u['email'])
            login_user(usuario)
            flash('Bienvenido, {}'.format(u['nombre']))
            return redirect(url_for('index'))
        else:
            flash('Email o contraseña incorrectos.')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/equipo/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_equipo():
    if request.method == 'POST':
        club = request.form['club'].strip()
        categoria = request.form['categoria']
        letra = request.form['letra'].strip()

        if not club or not categoria or not letra:
            flash('Debes completar todos los campos del equipo.')
            return render_template('nuevo_equipo.html', categorias=CATEGORIAS)

        conn = get_db()
        conn.execute(
            'INSERT INTO equipos (usuario_id, club, categoria, letra) VALUES (?,?,?,?)',
            (current_user.id, club, categoria, letra)
        )
        conn.commit()
        conn.close()

        flash('Equipo creado correctamente.')
        return redirect(url_for('index'))

    return render_template('nuevo_equipo.html', categorias=CATEGORIAS)


@app.route('/equipo/<int:equipo_id>')
@login_required
def equipo(equipo_id):
    conn = get_db()

    eq = conn.execute(
        'SELECT * FROM equipos WHERE id=? AND usuario_id=?',
        (equipo_id, current_user.id)
    ).fetchone()

    if not eq:
        conn.close()
        flash('Equipo no encontrado.')
        return redirect(url_for('index'))

    partidos = conn.execute(
        'SELECT * FROM partidos WHERE equipo_id=? ORDER BY fecha DESC',
        (equipo_id,)
    ).fetchall()

    conn.close()

    stats, num_partidos, mins_partido = get_stats_jugadores(equipo_id)

    return render_template(
        'equipo.html',
        equipo=eq,
        stats=stats,
        partidos=partidos,
        num_partidos=num_partidos,
        mins_partido=mins_partido
    )


@app.route('/equipo/<int:equipo_id>/jugador/nuevo', methods=['POST'])
@login_required
def nuevo_jugador(equipo_id):
    nombre = request.form['nombre'].strip()

    conn = get_db()
    eq = conn.execute(
        'SELECT * FROM equipos WHERE id=? AND usuario_id=?',
        (equipo_id, current_user.id)
    ).fetchone()

    if not eq:
        conn.close()
        flash('Equipo no encontrado.')
        return redirect(url_for('index'))

    if not nombre:
        conn.close()
        flash('El nombre del jugador es obligatorio.')
        return redirect(url_for('equipo', equipo_id=equipo_id))

    conn.execute(
        'INSERT INTO jugadores (equipo_id, nombre) VALUES (?,?)',
        (equipo_id, nombre)
    )
    conn.commit()
    conn.close()

    flash('Jugador añadido correctamente.')
    return redirect(url_for('equipo', equipo_id=equipo_id))


@app.route('/equipo/<int:equipo_id>/partido/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_partido(equipo_id):
    conn = get_db()

    eq = conn.execute(
        'SELECT * FROM equipos WHERE id=? AND usuario_id=?',
        (equipo_id, current_user.id)
    ).fetchone()

    if not eq:
        conn.close()
        flash('Equipo no encontrado.')
        return redirect(url_for('index'))

    jugadores = conn.execute(
        'SELECT * FROM jugadores WHERE equipo_id=? ORDER BY nombre',
        (equipo_id,)
    ).fetchall()

    if request.method == 'POST':
        rival = request.form['rival'].strip()
        fecha = request.form['fecha']
        mins_partido = get_minutos_partido(eq['categoria'])

        if not rival or not fecha:
            conn.close()
            flash('Debes completar rival y fecha.')
            return redirect(url_for('nuevo_partido', equipo_id=equipo_id))

        cur = conn.execute(
            'INSERT INTO partidos (equipo_id, rival, fecha) VALUES (?,?,?)',
            (equipo_id, rival, fecha)
        )
        partido_id = cur.lastrowid

        for j in jugadores:
            mins = int(request.form.get(f'mins_{j["id"]}', 0))

            if mins < 0:
                mins = 0
            if mins > mins_partido:
                mins = mins_partido

            conn.execute(
                'INSERT INTO minutos (partido_id, jugador_id, minutos) VALUES (?,?,?)',
                (partido_id, j['id'], mins)
            )

        conn.commit()
        conn.close()

        flash('Partido registrado correctamente.')
        return redirect(url_for('equipo', equipo_id=equipo_id))

    conn.close()
    mins_partido = get_minutos_partido(eq['categoria'])

    return render_template(
        'partido.html',
        equipo=eq,
        jugadores=jugadores,
        mins_partido=mins_partido
    )


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', debug=True)