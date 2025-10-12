# GS1 messages

Let us move away from consumer products.

The GS1 organization has specified a comprehensive system of Application
Identifiers (AI) covering most industry use cases.

It is helpful to get the terminology straight here, as we use it
throughout the Biip API:

- An _application identifier_ (AI) is a number with 2-4 digits that
  specifies a data field's format and use.
- An AI prefix, together with its data field, is called an _element
  string_.
- Multiple element strings read from a single barcode is called a
  _message_.

AI element strings can be encoded using several different barcode types,
but the linear barcode format GS1-128 is the most common.

## Serial Shipping Container Code (SSCC)

If we scan a GS1-128 barcode on a pallet, we might get the data string
`00157035381410375177`:

```python
>>> result = biip.parse("00157035381410375177")
>>> print(result.gs1_message)
GS1Message(
    value='00157035381410375177',
    element_strings=[
        GS1ElementString(
            ai=GS1ApplicationIdentifier(
                ai='00',
                description='Serial Shipping Container Code (SSCC)',
                data_title='SSCC',
                separator_required=False,
                format='N2+N18'
            ),
            value='157035381410375177',
            pattern_groups=['157035381410375177'],
            sscc=Sscc(
                value='157035381410375177',
                prefix=GS1Prefix(value='570', usage='GS1 Denmark'),
                company_prefix=GS1CompanyPrefix(value='5703538'),
                extension_digit=1,
                payload='15703538141037517',
                check_digit=7
            )
        )
    ]
)
```

From the above result, we can see that the data is a message that
contains a single element string. The element string has the AI `00`,
which is the code for Serial Shipping Container Code, or SSCC for short.

Biip extracts the SSCC payload and validates its check digit. The result
is an [`Sscc`][biip.sscc.Sscc] instance, with fields like
[`prefix`][biip.sscc.Sscc.prefix] and
[`extension_digit`][biip.sscc.Sscc.extension_digit].

You can extract the element string using
[`GS1Message.element_strings.get()`][biip.gs1_element_strings.GS1ElementStrings.get]
and
[`GS1Message.element_strings.filter()`][biip.gs1_element_strings.GS1ElementStrings.filter]:

```python
>>> element_string = result.gs1_message.element_strings.(ai="00")
>>> element_string.ai.data_title
'SSCC'
>>> element_string.sscc.prefix.usage
'GS1 Denmark'
>>> element_string.sscc.as_hri()
'1 5703538 141037517 7'
```

In case SSCCs are what you are primarily working with, the
[`Sscc`][biip.sscc.Sscc] instance is also available directly from
[`ParseResult`][biip.ParseResult]:

```python
>>> result.sscc == element_string.sscc
True
>>> print(result.sscc)
Sscc(
    value='157035381410375177',
    prefix=GS1Prefix(value='570', usage='GS1 Denmark'),
    company_prefix=GS1CompanyPrefix(value='5703538'),
    extension_digit=1,
    payload='15703538141037517',
    check_digit=7
)
```

If you need to display the barcode data in a more human readable way,
e.g. to print below a barcode, you can use
[`GS1Message.as_hri()`][biip.gs1_messages.GS1Message.as_hri]:

```python
>>> result.gs1_message.as_hri()
'(00)157035381410375177'
```

## Product IDs, expiration dates, and lot numbers

If we unpack the pallet and scan the GS1-128 barcode on a logistic unit,
containing multiple trade units, we might get the data string
`010703206980498815210526100329`:

```python
>>> result = biip.parse("010703206980498815210526100329")
```

We can have a quick look at the human-readable interpretation (HRI) to get a
feel for how the data groups into three element strings:

```python
>>> result.gs1_message.as_hri()
'(01)07032069804988(15)210526(10)0329'
```

And we can dig into the parsed element strings to get all the details:

```python hl_lines="13-21 26 33 38 43"
>>> print(result.gs1_message.element_strings)
[
    GS1ElementString(
        ai=GS1ApplicationIdentifier(
            ai='01',
            description='Global Trade Item Number (GTIN)',
            data_title='GTIN',
            separator_required=False,
            format='N2+N14'
        ),
        value='07032069804988',
        pattern_groups=['07032069804988'],
        gtin=Gtin(
            value='07032069804988',
            format=GtinFormat.GTIN_13,
            prefix=GS1Prefix(value='703', usage='GS1 Norway'),
            company_prefix=GS1CompanyPrefix(value='703206'),
            item_reference='980498',
            payload='703206980498',
            check_digit=8
        )
    ),
    GS1ElementString(
        ai=GS1ApplicationIdentifier(
            ai='15',
            description='Best before date (YYMMDD)',
            data_title='BEST BEFORE or BEST BY',
            separator_required=False,
            format='N2+N6'
        ),
        value='210526',
        pattern_groups=['210526'],
        date=datetime.date(2021, 5, 26)
    ),
    GS1ElementString(
        ai=GS1ApplicationIdentifier(
            ai='10',
            description='Batch or lot number',
            data_title='BATCH/LOT',
            separator_required=True,
            format='N2+X..20'
        ),
        value='0329',
        pattern_groups=['0329']
    )
]
```

The first element string is the GTIN of the trade item inside the
logistic unit. As with SSCC's, this is also available directly from the
[`ParseResult`][biip.ParseResult] instance:

```python
>>> result.gtin == result.gs1_message.element_strings[0].gtin
True
>>> print(result.gtin)
Gtin(
    value='07032069804988',
    format=GtinFormat.GTIN_13,
    prefix=GS1Prefix(value='703', usage='GS1 Norway'),
    company_prefix=GS1CompanyPrefix(value='703206'),
    payload='703206980498',
    check_digit=8
)
```

The second element string is the expiration date of the contained trade
items. To save you from interpreting the date value correctly yourself,
Biip does the job for you and exposes a
[`datetime.date`][datetime.date] instance:

```python
>>> element_string = result.gs1_message.element_strings.get(data_title="BEST BY")
>>> element_string.date
datetime.date(2021, 5, 26)
```

The last element string is the batch or lot number of the items:

```python
>>> element_string = result.gs1_message.element_strings.get(ai="10")
>>> element_string.value
'0329'
```

## Variable-length fields

About a third of the specified AIs don't have a fixed length. How do we
then know where the element strings ends, and the next one starts?

Let's look closer at the batch/lot number in the example in the previous
section. It has the following AI definition:

```python hl_lines="6"
GS1ApplicationIdentifier(
    ai='10',
    description='Batch or lot number',
    data_title='BATCH/LOT',
    separator_required=True,
    format='N2+X..20'
)
```

The batch/lot number, with AI `10`, is a variable-length field.
You can see this from the
[`format`][biip.gs1_application_identifiers.GS1ApplicationIdentifier.format],
`N2+X...20`, which indicates a two-digit AI prefix followed by a payload of up
to 20 alphanumeric characters.

In the last example, we didn't need to do anything to handle the variable-length
data field because the batch/lot number element string (AI `10`) was the last
one in the message:

```python
>>> result = biip.parse("010703206980498815210526100329")
>>> result.gs1_message.as_hri()
'(01)07032069804988(15)210526(10)0329'
```

Let's try to reorder the expiration date (AI `15`) and batch/lot number (AI
`10`), so that the batch/lot number comes in the middle of the message:

```python
>>> result = biip.parse("010703206980498810032915210525")
>>> result.gs1_message.as_hri()
'(01)07032069804988(10)032915210525'
```

As we can see, the batch/lot number didn't know where to stop, so it
consumed the remainder of the data, including the full expiration date.

GS1-128 barcodes mark the end of variable-length element strings with a
_Function Code 1_ (FNC1) symbol. When the barcode scanner converts the
barcode to a string of text, it substitutes the FNC1 symbol with
something else, often with the "Group Separator" (GS) ASCII
character. The GS ASCII character has a decimal value of 29 or
hexadecimal value of `0x1D`.

If we insert a byte with value `0x1D`, after the end of the batch/lot
number, we get the following result:

```python
>>> result = biip.parse("0107032069804988100329\x1d15210525")
>>> result.gs1_message.as_hri()
'(01)07032069804988(10)0329(15)210525'
```

Once again, we've correctly detected all three element strings.

## Barcode scanner configuration

To make variable-length fields work correctly, you might need to reconfigure
your barcode scanner hardware to use another separator character if:

- your barcode scanner doesn't insert the GS character, or
- some part of your scanning data pipeline cannot maintain the
  character as-is.

A reasonable choice for an alternative separator character might be the
pipe character, `|`, as this character cannot legally be a part of the
payload in element strings.

If we configure the barcode scanner to use an alternative separator character,
we also need to tell Biip what character to expect by creating a
[`ParseConfig`][biip.ParseConfig] object with the
[`separator_chars`][biip.ParseConfig.separator_chars] option, and then call the
[`parse()`][biip.parse] function with the config:

```python
>>> config = biip.ParseConfig(separator_chars=["|"])
>>> result = biip.parse("0107032069804988100329|15210525", config=config)
>>> result.gs1_message.as_hri()
'(01)07032069804988(10)0329(15)210525'
```

Once again, all three element strings was successfully extracted.

/// note | Learn more
To learn more about GS1 messages, see the
[`biip.gs1_messages`](../reference/gs1_messages.md) reference documentation.
///
