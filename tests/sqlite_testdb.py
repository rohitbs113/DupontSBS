import json
import os

from flask_testing import TestCase

FILE_PATH = os.path.dirname(os.path.abspath(__file__))


class SqliteTest(TestCase):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(FILE_PATH, "test_sbs.db")

    def create_app(self):
        SqliteTest.export_env_vars()

        from sbs import app
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = self.SQLALCHEMY_DATABASE_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ECHO'] = False

        from sbs.database_utility import db
        db.init_app(app)
        self.assertEqual(app.debug, False)

        return app

    def setUp(self):
        """
        Creates a new database for the unit test to use
        """
        from sbs.database_utility import db
        db.drop_all()
        print('====== Creating test database tables ======')
        import sbs.models.models
        db.create_all()
        SqliteTest.populate_db(db)

    @staticmethod
    def populate_db(db):
        """
        populates Sqlite DB with test data
        """
        fd = open(os.path.join(FILE_PATH, 'unit_test_data.sql'), 'r')
        sqlFile = fd.read()
        fd.close()

        sqlCommands = sqlFile.split(';')
        for command in sqlCommands:
            try:
                db.engine.execute(command)
            except Exception as e:
                print("Command skipped: ", e)

    def tearDown(self):
        """
        Ensures that the database is emptied for next unit test
        """
        from sbs.database_utility import db
        db.session.remove()
        db.drop_all()

    @staticmethod
    def export_env_vars():
        os.environ['REQUIRE_TOKEN'] = 'False'
        os.environ['REQUIRE_ROLE'] = 'False'


def expected_response_json(filename):
    data = {}
    try:
        file_path = os.path.join(FILE_PATH, "test_response", filename)
        with open(file_path) as f:
            data = json.load(f)
    except Exception as e:
        print("Error while reading expected test json file: ", e)

    return data
