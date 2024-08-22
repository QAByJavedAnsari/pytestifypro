import subprocess
import time

import pytest
import logging
import os
from pytestify.client.api_client import APIClient
from pytestify.utils.check_docker import check_docker


@pytest.fixture(scope="session", autouse=True)
def start_wiremock():
    """Start and stop WireMock server using Docker for tests."""
    # Start WireMock using Docker
    try:
        subprocess.run(["docker-compose", "up", "-d"], cwd="./", check=True)
        print("WireMock server started.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to start WireMock server: {e}")
        pytest.fail("Failed to start WireMock server")

    # Wait for WireMock to be fully started
    time.sleep(10)  # Adjust the sleep time if necessary

    yield

    # Stop WireMock after tests
    try:
        subprocess.run(["docker-compose", "down"], cwd="./", check=True)
        print("WireMock server stopped.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to stop WireMock server: {e}")
        pytest.fail("Failed to stop WireMock server")


@pytest.fixture(scope='session', autouse=True)
def docker_check():
    with open("/tmp/docker_check.log", "a") as log_file:
        log_file.write("Starting Docker check...\n")

        # Skip the Docker check if running inside a Docker container
        if os.path.exists('/.dockerenv') or os.path.exists('/proc/1/cgroup'):
            log_file.write("Inside Docker container, skipping Docker check.\n")
            return

        if not check_docker():
            log_file.write("Docker check failed, exiting pytest.\n")
            pytest.exit("Docker is required to run these tests. Please start Docker and try again.")

        log_file.write("Docker check passed.\n")


@pytest.fixture(scope="session")
def docker_setup():
    # Setup code for Docker environment
    yield
    # Teardown code for Docker environment

@pytest.fixture(scope='session')
def api_client():
    """
    Fixture to provide a reusable API client.
    """
    client = APIClient(config_file='src/pytestify/config/config.yaml')
    yield client
    client.close()

@pytest.fixture(scope='session', autouse=True)
def configure_logging():
    """
    Fixture to configure logging settings for all tests.
    """
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow to run"
    )
