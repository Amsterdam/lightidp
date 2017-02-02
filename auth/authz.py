"""
    auth.authz
    ~~~~~~~~~~

    This module provides an implementation of our authorization model.
"""
import collections.abc
import contextlib
import logging
import psycopg2

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

LEVEL_CITIZEN = 0b0
LEVEL_EMPLOYEE = 0b1
LEVEL_EMPLOYEE_PLUS = 0b11

_levels = {
    LEVEL_EMPLOYEE,
    LEVEL_EMPLOYEE_PLUS
}


class _AuthzMap(collections.abc.MutableMapping):
    """ A MutableMapping for username -> authorization level backed by Postgres.
    """

    q_crt_user_authz = """
        CREATE TABLE user_authz (
            username text PRIMARY KEY,
            authz_level integer DEFAULT 0
        );"""
    q_crt_user_authz_auditlog = """
        CREATE TABLE user_authz_audit (
            username text,
            authz_level integer,
            ts timestamp without time zone DEFAULT (now() at time zone 'utc'),
            active boolean
        );"""
    q_upd_authz_level = "UPDATE user_authz SET authz_level=%s WHERE username=%s"
    q_ins_user = "INSERT INTO user_authz (username, authz_level) VALUES(%s, %s)"
    q_sel_authz_level = "SELECT authz_level from user_authz WHERE username=%s"
    q_sel_all = "SELECT username FROM user_authz"
    q_del_user = "DELETE FROM user_authz WHERE username=%s"
    q_cnt_all = "SELECT COUNT(*) FROM user_authz"
    q_log_change = "INSERT INTO user_authz_audit (username, authz_level, active) VALUES(%s, %s, %s)"

    def __init__(self, *args, **kwargs):
        self._conn = psycopg2.connect(*args, **kwargs)

    @contextlib.contextmanager
    def _transaction(self):
        """ Convenience contextmanager for transactions.
        """
        with self._conn:
            with self._conn.cursor() as cur:
                yield cur

    def create(self):
        """ Create the tables for authz.
        """
        with self._transaction() as cur:
            cur.execute(self.q_crt_user_authz)
            cur.execute(self.q_crt_user_authz_auditlog)
        _logger.warn("Authz tables created")

    def __setitem__(self, username, authz_level):
        """ Assign the given permission to the given user and log the action in
        the audit log.
        """
        if authz_level not in _levels:
            raise ValueError()
        try:
            cur_authz_level = self[username]
            if authz_level == cur_authz_level:
                return
            q = (self.q_upd_authz_level, (authz_level, username))
        except KeyError:
            q = (self.q_ins_user, (username, authz_level))
        with self._transaction() as cur:
            cur.execute(*q)
            cur.execute(self.q_log_change, (username, authz_level, True))

    def __getitem__(self, username):
        """ Get the current authorization level for the given username.
        """
        with self._conn.cursor() as cur:
            cur.execute(self.q_sel_authz_level, (username,))
            result = cur.fetchone()
        if not result:
            raise KeyError()
        return result[0]

    def __delitem__(self, username):
        """ Remove the given user from the authz table and log the action in
        the audit log.
        """
        cur_authz_level = self[username]
        with self._transaction() as cur:
            cur.execute(self.q_del_user, (username,))
            cur.execute(self.q_log_change, (username, cur_authz_level, False))

    def __iter__(self):
        """ Iterate over all username => authz_levels currently in the table.
        """
        with self._conn.cursor() as cur:
            cur.execute(self.q_sel_all)
            for username in cur:
                yield username[0]

    def __len__(self):
        """ Number of usernames in the authz table.
        """
        with self._conn.cursor() as cur:
            cur.execute(self.q_cnt_all)
            return cur.fetchone()[0]

# singleton instance
_udb = None


def authz_getter(psycopg2conf):
    global _udb
    if not _udb:
        _udb = _AuthzMap(**psycopg2conf)

    def getter(username):
        return _udb.get(username, LEVEL_CITIZEN)

    return getter


def is_authorized(granted, needed):
    return needed & granted == needed


if __name__ == '__main__':
    udb = _AuthzMap(**{
        'host': 'localhost',
        'port': 5432,
        'dbname': 'authz',
        'user': 'authuser',
        'password': 'authpassword'})
    try:
        udb.create()
    except psycopg2.ProgrammingError:
        pass
    udb['evert'] = LEVEL_EMPLOYEE
    udb['pieter'] = LEVEL_EMPLOYEE_PLUS
    udb['evert'] = LEVEL_EMPLOYEE_PLUS
    udb['pieter'] = LEVEL_EMPLOYEE
    udb['pieter'] = LEVEL_EMPLOYEE
    try:
        udb['evert'] = LEVEL_CITIZEN
        raise AssertionError('Expected ValueError')
    except ValueError:
        pass
    for u in udb:
        assert udb[u]
    assert len(udb) == 2
    del udb['pieter']
    assert len(udb) == 1
    del udb['evert']
    assert len(udb) == 0
