How to publish a new release?
=============================

1. Bump version (run `poetry version minor` or similar and do not forget to update `pw/__init__.py`).
2. Make sure that you are not uploading a development release!
3. `poetry build`
4. `poetry publish`
