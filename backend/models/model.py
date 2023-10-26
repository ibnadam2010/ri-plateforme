from models.exts import db

"""
Class User:
    id:integer
    username:string
    email:string
    role:string
    password:string
"""
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80),nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    password = db.Column(db.Text(), nullable=False)
    def __repr__(self):
        return '<User %r>' % self.username
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self, username, email, role, password):
        self.username = username
        self.email = email
        self.role = role
        self.password = password
        db.session.commit()
