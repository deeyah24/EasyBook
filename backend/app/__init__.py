import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()


def create_app(config=None):
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 'postgresql://easybook_user:easybook_pass@localhost:5432/easybook'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # For simplicity; set proper expiry in prod

    if config:
        app.config.update(config)

    # Extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.services import services_bp
    from app.routes.appointments import appointments_bp
    from app.routes.providers import providers_bp
    from app.routes.reviews import reviews_bp
    from app.routes.categories import categories_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(services_bp, url_prefix='/api/services')
    app.register_blueprint(appointments_bp, url_prefix='/api/appointments')
    app.register_blueprint(providers_bp, url_prefix='/api/providers')
    app.register_blueprint(reviews_bp, url_prefix='/api/reviews')
    app.register_blueprint(categories_bp, url_prefix='/api/categories')

    # Health check
    @app.route('/api/health')
    def health():
        return {'status': 'ok', 'message': 'EasyBook API is running'}

    with app.app_context():
        db.create_all()
        _seed_categories()

    return app


def _seed_categories():
    from app.models.category import Category
    if Category.query.count() == 0:
        categories = [
            Category(name='Medical', description='Healthcare and medical consultations', icon='🏥', color='#2E86AB'),
            Category(name='Salon & Beauty', description='Hair, nails, and beauty treatments', icon='✂️', color='#E84855'),
            Category(name='Fitness', description='Personal training and fitness coaching', icon='💪', color='#F18F01'),
            Category(name='Dental', description='Dental check-ups and treatments', icon='🦷', color='#3BB273'),
            Category(name='Legal', description='Legal consultations and advice', icon='⚖️', color='#7B2D8B'),
            Category(name='Spa & Wellness', description='Massages and relaxation', icon='🧖', color='#3CBBB1'),
        ]
        for cat in categories:
            db.session.add(cat)
        db.session.commit()
