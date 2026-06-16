# Monkeypatch BaseContext.__copy__ to support Python 3.14 copy compatibility
try:
    from django.template.context import BaseContext
    import copy

    def base_context_copy(self):
        duplicate = object.__new__(self.__class__)
        duplicate.__dict__.update(self.__dict__)
        duplicate.dicts = self.dicts[:]
        return duplicate

    BaseContext.__copy__ = base_context_copy
except ImportError:
    pass
