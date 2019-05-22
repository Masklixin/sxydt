#encoding:utf-8
from flask import Flask,render_template,request,redirect,url_for,session,g
import config

from models import User,Question,Answer
from exts import db
import pymysql
from decorators import login_required
from sqlalchemy import or_
from functools import wraps
pymysql.install_as_MySQLdb()
app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)
#secret key
app.config['SECRET_KEY']='lixin'


@app.route('/')
def index():
    context={
        'questions':Question.query.order_by(Question.create_time.desc()).all()#拿出所有数据,按时间顺序排列


    }
    return render_template('index.html',**context)

@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template('login.html')
    else:
        usernum=request.form.get('usernum')
        password=request.form.get('password')
        user=User.query.filter(User.usernum==usernum).first()
        print(user.check_password(password))
        if user and user.check_password(password):
            session['user_id']=user.id
            #如果登录一次之后，想在31天内都不需要登录
            session.permanent=True
            return redirect(url_for('index'))
        # elif usernum==None or password==None:
        #     return '用户名或密码不能为空'

        else:
            return "学号或者密码错误"

@app.route('/regist',methods=['GET','POST'])
def regist():
    if request.method=='GET':
        return render_template('regist.html')
    else:
        telephone=request.form.get('telephone')
        usernum=request.form.get('usernum')
        password1=request.form.get('password1')
        password2=request.form.get('password2')

        #手机号码验证
        user=User.query.filter(User.telephone==telephone).first()
        if user:
            return "该手机号码已经被注册，请更换手机号码"
        else:
            #两次密码不相等
            if password1!=password2:
                return "两次密码不相等"
            else:
                user=User(telephone=telephone,usernum=usernum,password=password1)
                db.session.add(user)
                db.session.commit()
                #跳转到登陆页面
                return redirect(url_for('login'))

@app.route('/logout/')
def logout():
    #session.pop('user_id')
    #del session('user id')
    session.clear()
    return redirect(url_for('login'))

@app.route('/question/',methods=['GET','POST'])
@login_required
def question():
    if request.method=='GET':
        return render_template('question.html')
    else:
        title=request.form.get('title')
        content=request.form.get('content')
        question=Question(title=title,content=content)
        # user_id=session.get('user_id')
        # user=User.query.filter(User.id==user_id).first()
        question.author=g.user
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('index'))

@app.route('/detail/<question_id>')
def detail(question_id):
    question_model=Question.query.filter(Question.id==question_id).first()
    return render_template('detail.html',question=question_model)

@app.route('/add_answer/',methods=['POST'])
@login_required
def add_answer():
    content=request.form.get('answer_content')
    question_id=request.form.get('question_id')
    answer=Answer(content=content)
    #user_id=session['user_id']
    #user=User.query.filter(User.id==user_id).first()
    answer.author=g.user
    question=Question.query.filter(Question.id==question_id).first()
    answer.question=question
    db.session.add(answer)
    db.session.commit()
    return redirect(url_for('detail',question_id=question_id))

@app.before_request
def my_before_requstion():
    user_id=session.get('user_id')
    if user_id:
        user=User.query.filter(User.id==user_id).first()
        if user:
            g.user=user
@app.context_processor
def my_context_processor():
    if hasattr(g,'user'):
    # if user_id:
    #     user=User.query.filter(User.id==user_id).first()
        return {'user':g.user}
    return {}#即使错误也得返回一个空回去，不然便会报错

@app.route('/search/')
def search():
    q=request.args.get('q')
    questions=Question.query.filter(or_(Question.title.contains(q),Question.content.contains(q))).order_by(Question.create_time.desc())
    return render_template('index.html',questions=questions)
if __name__ == '__main__':
    app.run(debug=True)
