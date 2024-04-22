from flask import Flask,render_template,request,flash,redirect,url_for, send_from_directory,redirect
from flask_sqlalchemy import SQLAlchemy
from flask import session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'senhafintech'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/banco'
db = SQLAlchemy(app)

receitas = []
despesas = []
class Usuario(db.Model):
    # Define a tabela 'usuario' no banco de dados
    __tablename__ = 'usuario'

    # Define as colunas da tabela 'usuario'
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_usuario = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True)
    senha = db.Column(db.String(255))

class Poupanca(db.Model):
    # Define a tabela 'poupanca' no banco de dados
    __tablename__ = 'poupanca'

    # Define as colunas da tabela 'poupanca'
    id_poupanca = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao = db.Column(db.String(100))
    valor = db.Column(db.Float(10.2))

    # Define uma relação com a tabela 'usuario'
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))


class Receita(db.Model):
    # Define a tabela 'receita' no banco de dados
    __tablename__ = 'receitas'

    # Define as colunas da tabela 'receita'
    id_receitas = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao = db.Column(db.String(100))
    valor = db.Column(db.Float(10.2))
    datas = db.Column(db.Date)

    # Define uma relação com a tabela 'usuario'
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))


class Despesa(db.Model):
    # Define a tabela 'despesa' no banco de dados
    __tablename__ = 'despesas'

    # Define as colunas da tabela 'despesa'
    id_despesas = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao = db.Column(db.String(100))
    valor = db.Column(db.Float(10.2))
    datas = db.Column(db.Date)

    # Define uma relação com a tabela 'usuario'
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))


@app.route("/")
def index():
   return render_template("Home.html")


@app.route('/login')
def login_form():
  return render_template('Login.html')


@app.route('/login', methods=['POST'])
def login_post():
  email = request.form.get('username')
  senha = request.form.get('password')


  user = Usuario.query.filter_by(email=email).first()

  if user and senha == user.senha:
      session['id'] = user.id_usuario
      if 'next' in session:
          next_route = session.pop('next')
          return redirect(url_for(next_route))
      return redirect(url_for('home'))
  else:
      flash(f'Nome ou senha incorretos', 'error')
      return redirect(url_for('login_form'))


@app.route('/novo_user')
def novo_user():
  return render_template('Cadastro.html', titulo='Novo Usuário')


@app.route('/criar_usuario', methods=['POST'])
def criar_usuario():
   nome_usuario = request.form['nome_usuario']
   email = request.form['email']
   senha = request.form['senha']


   user = Usuario.query.filter_by(email=email).first()
   if user:
       flash('Usuário já existe', 'error')
       return redirect(url_for('novo_user'))
   else:
       novo_usuario = Usuario(email=email, senha=senha, nome_usuario=nome_usuario)
       db.session.add(novo_usuario)
       db.session.commit()
       flash('Usuário cadastrado com sucesso', 'success')
       return redirect(url_for('novo_user'))

@app.route('/inicio')
def home():
    total_receita = 0
    total_despesa = 0
    total_poupanca = 0
    id_usuario = session['id']

    selecao_receita = Receita.query.filter_by(id_usuario=id_usuario).all()
    selecao_despesa = Despesa.query.filter_by(id_usuario=id_usuario).all()
    selecao_poupanca = Poupanca.query.filter_by(id_usuario=id_usuario).all()

    for re in selecao_receita:
        total_receita += re.valor

    for re in selecao_despesa:
        total_despesa += re.valor

    for re in selecao_poupanca:
        total_poupanca += re.valor


    return render_template('Inicio.html',
                           total_receita=total_receita,
                           total_despesa=total_despesa,
                           total_poupanca=total_poupanca,
                           selecao_receita=selecao_receita,
                           selecao_despesa=selecao_despesa,
                           selecao_poupanca=selecao_poupanca)


@app.route('/poupanca')
def poupanca():
    total = 0
    id_usuario = session['id']
    selecao_poupanca = Poupanca.query.filter_by(id_usuario=id_usuario).all()

    for re in selecao_poupanca:
        total += re.valor

    return render_template('poupanca.html', poupanca=selecao_poupanca, total=total)

@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar():
    id_usuario = session['id']

    if request.method == 'GET':
        return render_template('adicionar.html')

    elif request.method == 'POST':
        valor = request.form['valor']
        descricao = request.form['descricao']
        categoria = request.form['categoria']
        datas = request.form['datas']

        if categoria == "poupanca":
            nova_poupanca = Poupanca(valor=valor, descricao=descricao, id_usuario=id_usuario)
            db.session.add(nova_poupanca)
            db.session.commit()
            flash('Poupança cadastrada com sucesso', 'success')
            return redirect(url_for('poupanca'))

        elif categoria == "receita":
            nova_receita = Receita(valor=valor, descricao=descricao, id_usuario=id_usuario, datas=datas)
            db.session.add(nova_receita)
            db.session.commit()
            flash('Receita cadastrada com sucesso', 'success')
            return redirect(url_for('receita'))

        else:
            nova_despesa = Despesa(valor=valor, descricao=descricao, id_usuario=id_usuario, datas=datas)
            db.session.add(nova_despesa)
            db.session.commit()
            flash('Despesa cadastrada com sucesso', 'success')
            return redirect(url_for('despesa'))


@app.route('/receitas')
def receita():
    total = 0
    id_usuario = session['id']
    selecao_receita = Receita.query.filter_by(id_usuario=id_usuario).all()

    for re in selecao_receita:
        total += re.valor

    return render_template('receitas.html', receitas=selecao_receita, total=total)

@app.route('/despesas')
def despesa():
    total = 0
    id_usuario = session['id']
    selecao_despesa = Despesa.query.filter_by(id_usuario=id_usuario).all()

    for re in selecao_despesa:
        total += re.valor

    return render_template('despesas.html', despesas=selecao_despesa, total=total)

if __name__ == "__main__":
   app.run(debug=True)

