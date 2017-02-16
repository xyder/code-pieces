"""
This script demonstrates how to patch a psycopg2 cursor in python 2.7.
"""

import unittest
import mock
import psycopg2


def get_db_cursor():
    """ Creates a psycopg2 database cursor. """

    user = 'postgres'
    host = ''
    database = 'postgres'
    password = ''
    conn = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=database,
    )
    cur = conn.cursor()

    return cur


def run_sql_command():
    """ Runs an sql command. """

    cursor = get_db_cursor()
    cursor.execute('a sql command')
    result = []

    while True:
        try:
            # explicitly using this iteration method to expose the issue with `next`.
            row = next(cursor)
        except StopIteration:
            break

        result.append(row)

    return result


class MockIterator(mock.MagicMock):
    """ Class that builds a MagicMock iterator. This is needed because `next` is "special" and MagicMock
        has some issues with that. A different approach would be something like this:

        mock.MagicMock.next = mock.MagicMock()

        or:

        mock.MagicMock.next = lambda self: self

        , but that might be a bad idea down the line. """

    next = mock.MagicMock()


class SqlCommandTestCase(unittest.TestCase):

    @mock.patch('psycopg2.connect')
    def test_run_sql_command(self, mock_connect):
        mock_cursor = MockIterator(**{
            'next.side_effect': [1, 2, 3]
        })

        mock_connect.configure_mock(**{
            'return_value.cursor.return_value': mock_cursor
        })

        self.assertEqual(run_sql_command(), [1, 2, 3])
