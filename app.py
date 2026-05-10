from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
app = Flask(__name__)
app.config['SECRET_KEY'] = 'traveloopsecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_name = db.Column(db.String(100))
    start_date = db.Column(db.String(50))
    end_date = db.Column(db.String(50))
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100))
    activity_name = db.Column(db.String(100))
    cost = db.Column(db.Integer)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'))

class PackingItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100))
    packed = db.Column(db.Boolean, default=False)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        user = User(
            name=name,
            email=email,
            password=password
        )
        db.session.add(user)
        db.session.commit()
        flash('Account Created Successfully')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(
            email=email,
            password=password
        ).first()
        if user:
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid Credentials')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    trips = Trip.query.filter_by(
        user_id=current_user.id
    ).all()
    return render_template(
        'dashboard.html',
        trips=trips
    )

@app.route('/create_trip', methods=['GET', 'POST'])
@login_required
def create_trip():
    if request.method == 'POST':
        trip_name = request.form.get('trip_name')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        description = request.form.get('description')
        trip = Trip(
            trip_name=trip_name,
            start_date=start_date,
            end_date=end_date,
            description=description,
            user_id=current_user.id
        )
        db.session.add(trip)
        db.session.commit()
        flash('Trip Created Successfully')
        return redirect(url_for('dashboard'))
    return render_template('create_trip.html')

@app.route('/my_trips')
@login_required
def my_trips():
    trips = Trip.query.filter_by(
        user_id=current_user.id
    ).all()
    return render_template(
        'my_trips.html',
        trips=trips
    )

@app.route('/itinerary/<int:trip_id>', methods=['GET', 'POST'])
@login_required
def itinerary(trip_id):
    trip = Trip.query.get(trip_id)
    if request.method == 'POST':
        city = request.form.get('city')
        activity_name = request.form.get('activity_name')
        cost = request.form.get('cost')
        activity = Activity(
            city=city,
            activity_name=activity_name,
            cost=cost,
            trip_id=trip_id
        )
        db.session.add(activity)
        db.session.commit()
    activities = Activity.query.filter_by(
        trip_id=trip_id
    ).all()
    total_cost = 0
    for activity in activities:
        total_cost += activity.cost
    return render_template(
        'itinerary.html',
        trip=trip,
        activities=activities,
        total_cost=total_cost
    )

@app.route('/packing/<int:trip_id>', methods=['GET', 'POST'])
@login_required
def packing(trip_id):
    if request.method == 'POST':
        item_name = request.form.get('item_name')
        item = PackingItem(
            item_name=item_name,
            trip_id=trip_id
        )
        db.session.add(item)
        db.session.commit()
    items = PackingItem.query.filter_by(
        trip_id=trip_id
    ).all()
    return render_template(
        'packing.html',
        items=items
    )

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)