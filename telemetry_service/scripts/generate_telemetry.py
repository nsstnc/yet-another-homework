import argparse
import asyncio
import random
import time
from collections import Counter
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import httpx


EVENTS_URL = "http://localhost:8001/events"

PAGES = [
    "/",
    "/catalog",
    "/catalog/electronics",
    "/catalog/clothes",
    "/catalog/books",
    "/cart",
    "/profile",
    "/orders",
    "/favorites",
]

SEARCH_QUERIES = [
    "iphone",
    "ноутбук",
    "наушники",
    "python книга",
    "кроссовки",
    "монитор",
    "клавиатура",
    "кофемашина",
    "рюкзак",
    "зарядка usb c",
]

BUTTONS = [
    "buy",
    "add_to_cart",
    "checkout",
    "login",
    "search",
    "next_page",
    "add_to_favorites",
    "apply_filter",
]

DEVICES = [
    "desktop",
    "mobile",
    "tablet",
]

BROWSERS = [
    "chrome",
    "firefox",
    "safari",
    "edge",
]

OS_LIST = [
    "windows",
    "linux",
    "macos",
    "android",
    "ios",
]

COUNTRIES = [
    "RU",
    "DE",
    "US",
    "NL",
    "PL",
    "FR",
]

PRODUCT_IDS = [
    f"product-{i:04d}"
    for i in range(1, 501)
]


def weighted_event_type() -> str:
    """
    События специально распределены неравномерно:
    page_view/click встречаются часто,
    purchase/error/logout — значительно реже.
    """
    return random.choices(
        population=[
            "page_view",
            "button_click",
            "search",
            "product_view",
            "add_to_cart",
            "remove_from_cart",
            "filter_applied",
            "scroll",
            "checkout_started",
            "purchase",
            "login",
            "logout",
            "favorite_added",
            "api_error",
        ],
        weights=[
            25,
            20,
            8,
            14,
            7,
            2,
            5,
            8,
            3,
            1,
            2,
            1,
            2,
            0.5,
        ],
        k=1,
    )[0]


def common_properties() -> dict:
    return {
        "device": random.choice(DEVICES),
        "browser": random.choice(BROWSERS),
        "os": random.choice(OS_LIST),
        "country": random.choice(COUNTRIES),
    }


def properties_for_event(event_type: str) -> dict:
    properties = common_properties()

    match event_type:
        case "page_view":
            properties.update(
                {
                    "page": random.choice(PAGES),
                    "referrer": random.choice(
                        [
                            None,
                            "google",
                            "yandex",
                            "direct",
                            "email",
                            "telegram",
                        ]
                    ),
                    "duration_ms": random.randint(300, 120_000),
                }
            )

        case "button_click":
            properties.update(
                {
                    "button": random.choice(BUTTONS),
                    "page": random.choice(PAGES),
                    "x": random.randint(0, 1920),
                    "y": random.randint(0, 1080),
                }
            )

        case "search":
            query = random.choice(SEARCH_QUERIES)

            properties.update(
                {
                    "query": query,
                    "results_count": random.randint(0, 250),
                    "page": "/catalog",
                }
            )

        case "product_view":
            properties.update(
                {
                    "product_id": random.choice(PRODUCT_IDS),
                    "price": round(random.uniform(100, 150_000), 2),
                    "currency": "RUB",
                }
            )

        case "add_to_cart" | "remove_from_cart":
            properties.update(
                {
                    "product_id": random.choice(PRODUCT_IDS),
                    "quantity": random.randint(1, 4),
                    "price": round(random.uniform(100, 50_000), 2),
                    "currency": "RUB",
                }
            )

        case "filter_applied":
            properties.update(
                {
                    "category": random.choice(
                        ["electronics", "books", "clothes"]
                    ),
                    "min_price": random.randint(0, 10_000),
                    "max_price": random.randint(10_001, 200_000),
                    "in_stock": random.choice([True, False]),
                }
            )

        case "scroll":
            properties.update(
                {
                    "page": random.choice(PAGES),
                    "scroll_percent": random.randint(1, 100),
                }
            )

        case "checkout_started":
            properties.update(
                {
                    "items_count": random.randint(1, 8),
                    "total": round(random.uniform(500, 200_000), 2),
                    "currency": "RUB",
                }
            )

        case "purchase":
            properties.update(
                {
                    "order_id": str(uuid4()),
                    "items_count": random.randint(1, 8),
                    "total": round(random.uniform(500, 200_000), 2),
                    "currency": "RUB",
                    "payment_method": random.choice(
                        [
                            "card",
                            "sbp",
                            "cash",
                        ]
                    ),
                }
            )

        case "login":
            properties.update(
                {
                    "method": random.choice(
                        ["password", "refresh_token"]
                    )
                }
            )

        case "logout":
            properties.update(
                {
                    "reason": random.choice(
                        [
                            "user_action",
                            "session_expired",
                            "logout_all",
                        ]
                    )
                }
            )

        case "favorite_added":
            properties.update(
                {
                    "product_id": random.choice(PRODUCT_IDS),
                }
            )

        case "api_error":
            properties.update(
                {
                    "endpoint": random.choice(
                        [
                            "/api/products",
                            "/api/cart",
                            "/api/orders",
                            "/api/profile",
                        ]
                    ),
                    "status_code": random.choice(
                        [400, 401, 404, 409, 500, 503]
                    ),
                    "duration_ms": random.randint(20, 10_000),
                }
            )

    return properties


class Session:
    def __init__(self, user_id: UUID | None):
        self.user_id = user_id
        self.session_id = uuid4()

        # Сессия появилась когда-то за последние 24 часа.
        self.timestamp = datetime.now(UTC) - timedelta(
            seconds=random.randint(0, 86_400)
        )

    def next_timestamp(self) -> datetime:
        # Пользователь совершает действия с хаотичными паузами.
        self.timestamp += timedelta(
            seconds=random.uniform(0.2, 90)
        )

        return self.timestamp


def create_sessions(
        users_count: int,
        sessions_count: int,
) -> list[Session]:
    users = [
        uuid4()
        for _ in range(users_count)
    ]

    sessions = []

    for _ in range(sessions_count):
        # Немного анонимного трафика.
        anonymous = random.random() < 0.07

        user_id = (
            None
            if anonymous
            else random.choice(users)
        )

        sessions.append(
            Session(user_id=user_id)
        )

    return sessions


def generate_event(session: Session) -> dict:
    event_type = weighted_event_type()

    return {
        "event_type": event_type,
        "user_id": (
            str(session.user_id)
            if session.user_id
            else None
        ),
        "session_id": str(session.session_id),
        "timestamp": session.next_timestamp().isoformat(),
        "properties": properties_for_event(event_type),
    }


async def send_event(
        client: httpx.AsyncClient,
        semaphore: asyncio.Semaphore,
        payload: dict,
        stats: Counter,
) -> None:
    async with semaphore:
        try:
            response = await client.post(
                EVENTS_URL,
                json=payload,
            )

            stats[f"http_{response.status_code}"] += 1

            if response.is_error:
                print(
                    f"ERROR {response.status_code}: "
                    f"{response.text[:300]}"
                )

        except Exception as exc:
            stats["exceptions"] += 1
            print(f"REQUEST FAILED: {exc}")


async def generate_load(
        events_count: int,
        users_count: int,
        sessions_count: int,
        concurrency: int,
) -> None:
    sessions = create_sessions(
        users_count=users_count,
        sessions_count=sessions_count,
    )

    stats = Counter()
    semaphore = asyncio.Semaphore(concurrency)

    timeout = httpx.Timeout(10.0)

    started_at = time.monotonic()

    async with httpx.AsyncClient(
            timeout=timeout,
    ) as client:
        tasks = []

        for i in range(events_count):
            session = random.choice(sessions)
            payload = generate_event(session)

            task = asyncio.create_task(
                send_event(
                    client=client,
                    semaphore=semaphore,
                    payload=payload,
                    stats=stats,
                )
            )

            tasks.append(task)

            # Иногда делаем короткие всплески,
            # иногда небольшие паузы.
            if i % 1000 == 0 and i != 0:
                print(
                    f"Scheduled {i}/{events_count} events"
                )

            if random.random() < 0.015:
                await asyncio.sleep(
                    random.uniform(0.01, 0.15)
                )

        await asyncio.gather(*tasks)

    elapsed = time.monotonic() - started_at

    print()
    print("Finished")
    print(f"Events:       {events_count}")
    print(f"Elapsed:      {elapsed:.2f} sec")
    print(
        f"Average RPS:  "
        f"{events_count / elapsed:.2f}"
    )

    print()
    print("Responses:")

    for key, value in sorted(stats.items()):
        print(f"  {key}: {value}")


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--events",
        type=int,
        default=20_000,
    )

    parser.add_argument(
        "--users",
        type=int,
        default=500,
    )

    parser.add_argument(
        "--sessions",
        type=int,
        default=1500,
    )

    parser.add_argument(
        "--concurrency",
        type=int,
        default=100,
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    asyncio.run(
        generate_load(
            events_count=args.events,
            users_count=args.users,
            sessions_count=args.sessions,
            concurrency=args.concurrency,
        )
    )


if __name__ == "__main__":
    main()