from datetime import datetime
from pathlib import Path

import pytest

from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.database import DB_TZ, BarOverview, TickOverview, convert_tz
from vnpy.trader.object import BarData, TickData
from vnpy_sqlite.sqlite_database import SqliteDatabase, path as sqlite_path


_LOAD_START: datetime = datetime(2024, 1, 1)
_LOAD_END: datetime = datetime(2024, 2, 1)


@pytest.fixture(scope="session")
def database() -> SqliteDatabase:
    return SqliteDatabase()


def _make_bars(symbol: str) -> tuple[datetime, datetime, list[BarData]]:
    start: datetime = datetime(2024, 1, 15, 10, 0, tzinfo=DB_TZ)
    end: datetime = datetime(2024, 1, 15, 10, 1, tzinfo=DB_TZ)
    bars: list[BarData] = [
        BarData(
            gateway_name="TEST",
            symbol=symbol,
            exchange=Exchange.SHFE,
            datetime=start,
            interval=Interval.MINUTE,
            volume=12.0,
            open_price=100.0,
            high_price=110.0,
            low_price=90.0,
            close_price=105.0,
        ),
        BarData(
            gateway_name="TEST",
            symbol=symbol,
            exchange=Exchange.SHFE,
            datetime=end,
            interval=Interval.MINUTE,
            volume=8.0,
            open_price=105.0,
            high_price=112.0,
            low_price=101.0,
            close_price=108.0,
        ),
    ]
    return start, end, bars


def _make_ticks(symbol: str) -> tuple[datetime, datetime, list[TickData]]:
    start: datetime = datetime(2024, 1, 16, 10, 0, tzinfo=DB_TZ)
    end: datetime = datetime(2024, 1, 16, 10, 0, 1, tzinfo=DB_TZ)
    ticks: list[TickData] = [
        TickData(
            gateway_name="TEST",
            symbol=symbol,
            exchange=Exchange.SHFE,
            datetime=start,
            last_price=400.5,
            volume=20.0,
        ),
        TickData(
            gateway_name="TEST",
            symbol=symbol,
            exchange=Exchange.SHFE,
            datetime=end,
            last_price=401.0,
            volume=21.0,
        ),
    ]
    return start, end, ticks


def _bar_overview(database: SqliteDatabase, symbol: str) -> BarOverview | None:
    matched: list[BarOverview] = [
        overview
        for overview in database.get_bar_overview()
        if overview.symbol == symbol
    ]
    if not matched:
        return None
    assert len(matched) == 1
    return matched[0]


def _tick_overview(database: SqliteDatabase, symbol: str) -> TickOverview | None:
    matched: list[TickOverview] = [
        overview
        for overview in database.get_tick_overview()
        if overview.symbol == symbol
    ]
    if not matched:
        return None
    assert len(matched) == 1
    return matched[0]


def test_save_and_load_bar_data(database: SqliteDatabase) -> None:
    symbol: str = "rbSqliteBar"
    start, end, bars = _make_bars(symbol)
    assert database.save_bar_data(bars) is True

    loaded: list[BarData] = database.load_bar_data(
        symbol,
        Exchange.SHFE,
        Interval.MINUTE,
        _LOAD_START,
        _LOAD_END,
    )
    assert len(loaded) == 2

    assert loaded[0].symbol == symbol
    assert loaded[0].interval == Interval.MINUTE
    assert loaded[0].datetime == start
    assert loaded[0].open_price == 100.0
    assert loaded[0].high_price == 110.0
    assert loaded[0].low_price == 90.0
    assert loaded[0].close_price == 105.0
    assert loaded[0].volume == 12.0

    assert loaded[1].symbol == symbol
    assert loaded[1].interval == Interval.MINUTE
    assert loaded[1].datetime == end
    assert loaded[1].open_price == 105.0
    assert loaded[1].high_price == 112.0
    assert loaded[1].low_price == 101.0
    assert loaded[1].close_price == 108.0
    assert loaded[1].volume == 8.0


def test_delete_bar_data_then_load_empty(database: SqliteDatabase) -> None:
    symbol: str = "rbSqliteBarDel"
    _start, _end, bars = _make_bars(symbol)
    database.save_bar_data(bars)

    database.delete_bar_data(symbol, Exchange.SHFE, Interval.MINUTE)
    loaded: list[BarData] = database.load_bar_data(
        symbol,
        Exchange.SHFE,
        Interval.MINUTE,
        _LOAD_START,
        _LOAD_END,
    )
    assert loaded == []
    assert _bar_overview(database, symbol) is None


def test_bar_overview_count_and_range(database: SqliteDatabase) -> None:
    symbol: str = "rbSqliteBarOv"
    start, end, bars = _make_bars(symbol)
    database.save_bar_data(bars)

    overview: BarOverview | None = _bar_overview(database, symbol)
    assert overview is not None
    assert overview.count == 2
    assert overview.start == convert_tz(start)
    assert overview.end == convert_tz(end)

    database.delete_bar_data(symbol, Exchange.SHFE, Interval.MINUTE)
    assert _bar_overview(database, symbol) is None


def test_save_and_load_tick_data(database: SqliteDatabase) -> None:
    symbol: str = "auSqliteTick"
    start, end, ticks = _make_ticks(symbol)
    assert database.save_tick_data(ticks) is True

    loaded: list[TickData] = database.load_tick_data(
        symbol,
        Exchange.SHFE,
        _LOAD_START,
        _LOAD_END,
    )
    assert len(loaded) == 2

    assert loaded[0].symbol == symbol
    assert loaded[0].datetime == start
    assert loaded[0].last_price == 400.5
    assert loaded[0].volume == 20.0

    assert loaded[1].symbol == symbol
    assert loaded[1].datetime == end
    assert loaded[1].last_price == 401.0
    assert loaded[1].volume == 21.0


def test_delete_tick_data_then_load_empty(database: SqliteDatabase) -> None:
    symbol: str = "auSqliteTickDel"
    _start, _end, ticks = _make_ticks(symbol)
    database.save_tick_data(ticks)

    database.delete_tick_data(symbol, Exchange.SHFE)
    loaded: list[TickData] = database.load_tick_data(
        symbol,
        Exchange.SHFE,
        _LOAD_START,
        _LOAD_END,
    )
    assert loaded == []
    assert _tick_overview(database, symbol) is None


def test_tick_overview_count_and_range(database: SqliteDatabase) -> None:
    symbol: str = "auSqliteTickOv"
    start, end, ticks = _make_ticks(symbol)
    database.save_tick_data(ticks)

    overview: TickOverview | None = _tick_overview(database, symbol)
    assert overview is not None
    assert overview.count == 2
    assert overview.start == convert_tz(start)
    assert overview.end == convert_tz(end)

    database.delete_tick_data(symbol, Exchange.SHFE)
    assert _tick_overview(database, symbol) is None


def test_sqlite_file_created_under_temp_vntrader(
    database: SqliteDatabase,
    vntrader_dir: Path,
) -> None:
    db_file: Path = Path(sqlite_path)
    assert db_file == vntrader_dir.joinpath("test_sqlite.db")
    assert db_file.is_file()
    assert Path(database.db.database) == db_file
    home_vntrader: Path = Path.home().joinpath(".vntrader")
    assert vntrader_dir != home_vntrader
    assert db_file.parent != home_vntrader
