from biip.gtin import Gtin, Rcn


def test_parse_returns_rcn_instance() -> None:
    rcn = Gtin.parse("2088060112343")

    assert isinstance(rcn, Rcn)
