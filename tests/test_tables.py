from snowboard.tables import SnowTable, SnowTableData


def test_table_data_no_fields():
    data = SnowTableData(name="fubar")
    assert data.name == "fubar"
    assert data.default_fields is None


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
    assert len(table.data.default_fields) == 9


def test_catalog_items_table():
    table = SnowTable.CATALOG_ITEMS
    assert isinstance(table.data, SnowTableData)
    assert table.data.name == "sc_cat_item"
    assert table.data.default_fields is None
