from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Database config - reads from environment variable (set in docker-compose)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'mysql+pymysql://root:redhat@localhost:3306/admission_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---- Model ----
class Student(db.Model):
    __tablename__ = 'students'

    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name        = db.Column(db.String(100), nullable=False)
    email       = db.Column(db.String(100), nullable=False, unique=True)
    course      = db.Column(db.String(100), nullable=False)
    education   = db.Column(db.String(100), nullable=False)   # Highest Education
    percentage  = db.Column(db.Float, nullable=False)
    branch      = db.Column(db.String(100), nullable=False)
    mobile      = db.Column(db.String(15), nullable=False)

    def to_dict(self):
        return {
            'id':         self.id,
            'name':       self.name,
            'email':      self.email,
            'course':     self.course,
            'education':  self.education,
            'percentage': self.percentage,
            'branch':     self.branch,
            'mobile':     self.mobile,
        }

# Create tables on startup
with app.app_context():
    db.create_all()

# ---- Routes ----

@app.route('/api/students', methods=['GET'])
def get_all_students():
    students = Student.query.all()
    return jsonify([s.to_dict() for s in students]), 200


@app.route('/api/register', methods=['POST'])
def register_student():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    new_student = Student(
        name       = data['name'],
        email      = data['email'],
        course     = data['course'],
        education  = data['education'],
        percentage = data['percentage'],
        branch     = data['branch'],
        mobile     = data['mobile'],
    )
    db.session.add(new_student)
    db.session.commit()
    return jsonify(new_student.to_dict()), 201


@app.route('/api/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    db.session.delete(student)
    db.session.commit()
    return jsonify({'message': 'Student deleted successfully'}), 200


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
