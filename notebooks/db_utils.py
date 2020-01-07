from sqlalchemy import create_engine


def connection():
    """ Creates a new connection to database
    :return: database engine
    """
    db_user = 'bc0e0e4f733dda'
    db_password = '00f61efe'
    db_name = 'heroku_8149febc614deb5'
    db_host = 'eu-cdbr-west-02.cleardb.net'

    return create_engine('mysql+pymysql://{}:{}@{}/{}'.format(db_user,
                                                              db_password,
                                                              db_host,
                                                              db_name))
