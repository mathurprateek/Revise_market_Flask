from market_flask import db, bcrypt, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=100), nullable=False)
    email = db.Column(db.String(length=150), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=50), nullable=False, unique=False)
    budget = db.Column(db.Integer(), nullable=False, default=1000)
    items = db.relationship('Items', backref='owned_user', lazy=True)

    def __repr__(self):
        return f"{self.id}-->{self.username}-->Rs.{self.budget}"

    @property
    def prettier_budget(self):
        if len(str(self.budget)) <= 3:
            return f"₹{str(self.budget)}"
        else:
            lst = [x for x in str(self.budget)]
            lst.insert(-3, ',')
            if len(str(self.budget)) > 4:
                for i in range(-7, -len(lst)- 3, -4):
                    if i+len(lst) != 0:
                        lst.insert(i, ',')
            self.budget = "".join(lst)
            return f"₹{self.budget}"

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    def can_purchase(self, item_price):
        return self.budget > item_price

    def can_sell(self, item_obj):
        return item_obj in self.items


class Items(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=100), unique=True, nullable=False)
    price = db.Column(db.Integer(), nullable=False)
    barcode = db.Column(db.String(length=12), unique=True, nullable=False)
    description = db.Column(db.String(length=1000), nullable=False)
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))

    def __repr__(self):
        return f"{self.name}-->Rs.{self.price}"

    def buy(self, user):
        self.owner = user.id
        user.budget -= self.price
        db.session.commit()

    def sell(self, user):
        self.owner = None
        user.budget += self.price
        db.session.commit()
