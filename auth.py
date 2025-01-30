
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True,
                         nullable = False)
    password = db.Column(db.string(250),
                         nullable=False)