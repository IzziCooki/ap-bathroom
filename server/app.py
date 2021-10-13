from flask import Flask, jsonify, request, json, flash, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from time import gmtime, strftime



app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://xlhchzvlqttlfb:bace9ec293b9454e49e580c08f33463f56ee836f664c82e78fbfa8b0e5d94388@ec2-3-221-100-217.compute-1.amazonaws.com:5432/ddtm5qfaum265e"
app.secret_key = "super secret key"
db = SQLAlchemy(app)
print("test")


class log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timein = db.Column(db.DateTime, default=func.now())
    user = db.Column(db.String)
 
    timeout = db.Column(db.DateTime, nullable=True)

    def str(self):
        return f'{self.id}, {self.user}'


def log_serializer(log):
    return {
        "id": log.id,
        "name": log.user
    }

@app.route("/api", methods=["GET"])
def index():
    return jsonify([*map(log_serializer, log.query.all())])

@app.route("/api", methods=["POST"])
def logout():

    logs = log.query.all()
  
    for l in logs:
        if not l.timeout:
            flash("The device is Already Logged Out by " + str(l.user))
            return redirect(url_for("home"))

    user = request.form["user"]
    newLog = log(user=user)
    db.session.add(newLog)
    db.session.commit()

   

    return redirect(url_for("home"))


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        data = request.args.get["email"]
        print(data)
        

    if request.args.get('page_num'):
        page_num =  int(request.args.get("page_num"))

        employees = log.query.order_by(log.id.desc()).paginate(per_page=5, page=page_num, error_out=True)
        
        return render_template('home.html', employees=employees)

    logs = log.query.order_by(log.id.desc()).paginate(per_page=5, page=1, error_out=True)


    return render_template('home.html', employees = logs)




@app.route("/api/<int:id>", methods=["GET"])
def checkout(id):

    updatedLog = log.query.filter_by(id=id).first()
    updatedLog.timeout = func.now()
    db.session.commit()

    return redirect(url_for("home"))


@app.route('/api/delete/<int:id>', methods=["GET"])
def delete_log(id):

    logs = log.query.filter_by(id=id).first()
    db.session.delete(logs)
    db.session.commit()

    return redirect(url_for('home'))



if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
