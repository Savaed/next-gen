from typing import Any, Union

from bson.errors import InvalidId
from bson.objectid import ObjectId
from mongoengine import connect, disconnect
from mongoengine.errors import DoesNotExist, MultipleObjectsReturned

from nextgen.data.dbmodels import EvoResult, User
from nextgen.data.exceptions import DbError, ManyObjectsError, NotFoundError


class MongoDbContext(object):
    def __init__(self, db: str, host: str = "localhost", port: int = 27017) -> None:
        """
        Mongo connection.

        Use this class as context menager to ensure the Mongo connection is properly open and close.

            >>> with MongoDbContext(db="database"):
            >>>     collection = MongoCollection.objects()
        """

        self._host = host
        self._port = port
        self._db = db
        self._connected = False

    def __enter__(self):
        if not self._connected:
            connect(host=self._host, port=self._port, db=self._db)
            self._connected = True

        return self

    def __exit__(self, type, value, traceback) -> None:
        if self._connected:
            disconnect()
            self._connected = False


class UserDbService:
    """Database service to manipulate User objects."""

    def __init__(self) -> None:
        self._context = MongoDbContext(db="nextgen")

    def add(self, user: User) -> ObjectId:
        """
        Add a new user to the database.

        Parameters
        ----------
        user : User
            The User object to add.

        Returns
        -------
        str
            The string version of ObjectId of newly created user.
        """

        with self._context:
            return user.save().id

    def get_by_username(self, username: str) -> User:
        """
        Get user by username. Raise the NotFoundError or ManyObjectsError if there is more then one or any objects.

        Parameters
        ----------
        username : str
            User's username

        Returns
        -------
        User
            User object with matched username

        Raises
        ------
        NotFoundError
            Username with passed username doesnt exist.
        ManyObjectsError
            More than one user returned but only one was expected.
        """

        try:
            with self._context:
                return User.objects().get(username=username)
        except DoesNotExist as ex:
            raise NotFoundError(f"User with '{username=}' not found") from ex
        except MultipleObjectsReturned as ex:
            raise ManyObjectsError(f"More than one users has '{username=}'") from ex

    def get_all(self) -> list[User]:
        """
        Get all users.

        Returns
        -------
        list[EvoResult]
            List of all users.
        """

        with self._context:
            return list(User.objects())


class EvoResultDbService:
    """Database service to manipulate EvoResult objects."""

    def __init__(self) -> None:
        self._context = MongoDbContext(db="nextgen")

    def add(self, result: EvoResult) -> ObjectId:
        """
        Add new result of genetic or evolution algorithm.

        Parameters
        ----------
        result : EvoResult
            The algorithm result.

        Returns
        -------
        ObjectId
            The ObjectId id of added result.
        """

        with self._context:
            return result.save().id

    def delete_by_id(self, result_id: Union[str, ObjectId]) -> None:
        """
        Delete result by id.

        Parameters
        ----------
        id : Union[str, ObjectId]
            The ID of result to be deleted. It may be either string or ObjectId.
            If string passed it will be internally converted to ObjectId.

        Raises
        ------
        ValueError
            Invalid format of ID as string.
        """

        try:
            result_id = ObjectId(result_id) if isinstance(result_id, str) else result_id

            with self._context:
                EvoResult.objects.get(id=result_id).delete()
        except InvalidId as ex:
            raise ValueError(f"Parameter '{result_id=}' has invalid format") from ex

    def delete(self, by: str, filter_value: Any) -> None:
        """
        Delete results filtered by object field value.

        Parameters
        ----------
        by : str
            Name of field used to filter documents.
        filter_value : Any
            Value of filterd field.

        Raises
        ------
        DbError
            Generic Mongo database error.
        """

        try:
            filter_query = {by: filter_value}

            with self._context:
                EvoResult.objects(__raw__=filter_query).delete()
        except Exception as ex:
            raise DbError("Unexpected internal db error") from ex

    def get(self, by: str, filter_value: Any) -> list[EvoResult]:
        """
        Filter and return results that meet the condition.

        If only one document satisfy the filter condition then the one-element list will be return.

        Parameters
        ----------
        by : str
            Name of field used to filter documents.
        filter_value : Any
            Value of filterd field.

        Returns
        -------
        EvoResult
            Filtered results, the one-element list if only one document satisfy the filter condition.

        Raises
        ------
        DbError
            Generic Mongo database error.
        """

        try:
            filter_query = {by: filter_value}

            with self._context:
                return EvoResult.objects(__raw__=filter_query)
        except Exception as ex:
            raise DbError("Unexpected internal db error") from ex

    def get_all(self) -> list[EvoResult]:
        """
        Get all genetic and evolution results.

        Returns
        -------
        list[EvoResult]
            List of all results.
        """

        with self._context:
            return EvoResult.objects()
