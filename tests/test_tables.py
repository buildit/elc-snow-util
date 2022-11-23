from snowboard.tables import SnowTable, SnowTableData


def test_table_data_no_fields():
    data = SnowTableData(name="fubar")
    assert data.name == "fubar"
    assert data.default_fields is None


def test_table_data_with_more_fields():
    data = SnowTableData(name="fubar").with_fields("fu", "bar")
    assert data.name == "fubar"
    assert data.default_fields == ["fu", "bar"]


def test_topic_table():
    table = SnowTable.TOPICS
    assert isinstance(table.data, SnowTableData)
    assert table.data.name == "topic"
    assert isinstance(table.data.default_fields, list)
    assert len(table.data.default_fields) == 9


def test_connected_content_table():
    table = SnowTable.CONNECTED_CONTENT
    assert isinstance(table.data, SnowTableData)
    assert table.data.name == "m2m_connected_content"
    assert isinstance(table.data.default_fields, list)
    assert len(table.data.default_fields) == 6


def test_connected_content_table_with_fields():
    table = SnowTable.CONNECTED_CONTENT
    assert isinstance(table.data, SnowTableData)
    table_data = table.with_fields("order", "alphabetical_odrder")
    assert table_data.name == "m2m_connected_content"
    assert isinstance(table_data.default_fields, list)
    assert len(table_data.default_fields) == 8


def test_catalog_items_table():
    table = SnowTable.CATALOG_ITEMS
    assert isinstance(table.data, SnowTableData)
    assert table.data.name == "sc_cat_item"
    assert table.data.default_fields is None
