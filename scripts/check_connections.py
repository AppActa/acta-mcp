from acta_mcp.core.config import get_settings
from acta_mcp.server import create_container


def main() -> None:
    container = create_container(get_settings())
    container.postgres_pool.open(wait=True)
    try:
        print(
            {
                "postgres": container.postgres.ping(),
                "mongodb": container.mongo.ping(),
            }
        )
    finally:
        container.close()


if __name__ == "__main__":
    main()

