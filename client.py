import requests
import redis
import cPickle as pickle

from genesis.queryobserver import connection


class QueryObserverClient(object):
    """
    Client for the remote query observer API. This client should be used to interact
    with the query observers from Django.
    """

    def __init__(self):
        """
        Constructs the query observer API client.
        """

        self._redis = redis.StrictRedis(**connection.get_redis_settings())

    def _request(self, command, **kwargs):
        """
        RPC request helper.

        :param command: Command name
        :param **kwargs: Picklable command keyword arguments
        """

        kwargs['command'] = command
        return requests.post(
            'http://%(host)s:%(port)d/' % connection.get_queryobserver_settings(),
            data=pickle.dumps(kwargs),
        ).json()

    def create_observer(self, queryset, subscriber):
        """
        Starts observing a specific query.

        :param query: QuerySet instance to observe
        :param subscriber: Subscriber channel name
        :return: Serialized current query results
        """

        return self._request('create_observer', query=queryset.query, subscriber=subscriber)

    def _notify(self, event, **kwargs):
        """
        Event emission helper.

        :param event: Event name
        :param **kwargs: Picklable event attributes
        """

        kwargs['event'] = event
        self._redis.publish(connection.QUERYOBSERVER_REDIS_CHANNEL, pickle.dumps(kwargs))

    def notify_table_insert(self, table):
        """
        Notifies the query observer that a table instance has been inserted.
        """

        return self._notify('table_insert', table=table)

    def notify_table_update(self, table):
        """
        Notifies the query observer that a table instance has been changed.
        """

        return self._notify('table_update', table=table)

    def notify_table_remove(self, table):
        """
        Notifies the query observer that a table instance has been removed.
        """

        return self._notify('table_remove', table=table)
