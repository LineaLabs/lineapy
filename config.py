PROD_ENV = "production"
PROD_DEBUG = False
PROD_TESTING = False
PROD_DATABASE_URI = "sqlite:///local.db"

# persistent tests
DEV_ENV = "development"
DEV_DEBUG = True
DEV_TESTING = False
DEV_DATABASE_URI = "sqlite:///local.db"

# in memory tests
TEST_ENV = "development"
TEST_DEBUG = True
TEST_TESTING = True
TEST_DATABASE_URI = "sqlite:///:memory:"
