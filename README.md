# flake8_unused_fixtures
This project searches for all functions 
with prefix "test_" or suffix "_test" 
and searches for all unused fixture names inside the function body.
For now, it does not check if the function is actually marked as fixture.

It is assumed that fixtures that do not need to be directly accessed are
declared using `@pytest.mark.usefixtures`