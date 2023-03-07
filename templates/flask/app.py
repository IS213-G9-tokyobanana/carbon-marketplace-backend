from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@db:5432/postgres"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
CORS(app)
class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)

    def __init__(self, id, title):
        self.id = id
        self.title = title

    def json(self):
        return {"id": self.id, "title": self.title}

@app.route('/project')
def get_all():
    project_list = Project.query.all()
    if len(project_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "project": [project.json() for project in project_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no projects."
        }
    ), 404

@app.route("/project/<int:id>")
def get_by_id(id):
    project = Project.query.filter_by(id=id).first()
    if project:
        return jsonify(
            {
                "code": 200,
                "data": project.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Project not found."
        }
    ), 404

@app.route("/project/<int:id>", methods=['POST'])
def create_project(id):
    if (Project.query.filter_by(id=id).first()):
        return jsonify(
            {
                "code": 400,
                "data": {
                    "id": id
                },
                "message": "Project already exists."
            }
        ), 400

    data = request.get_json()
    project = Project(id, **data)

    try:
        db.session.add(project)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "id": id
                },
                "message": "An error occurred creating the project."
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": project.json()
        }
    ), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
