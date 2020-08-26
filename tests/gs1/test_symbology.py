from biip.gs1 import GS1Symbology


def test_gs1_symbology_enum() -> None:
    assert GS1Symbology("C1") == GS1Symbology.GS1_128


def test_gs1_symbology_with_ai_element_strings() -> None:
    assert GS1Symbology.EAN_13 not in GS1Symbology.with_ai_element_strings()
    assert GS1Symbology.GS1_128 in GS1Symbology.with_ai_element_strings()


def test_gs1_symbology_with_gtin() -> None:
    assert GS1Symbology.EAN_13 in GS1Symbology.with_gtin()

    # Even though GS1-128 can contain a GTIN,
    # it cannot be parsed with a pure GTIN parser.
    assert GS1Symbology.GS1_128 not in GS1Symbology.with_gtin()
