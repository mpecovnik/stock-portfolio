# stock-portfolio

Orodje za generacijo XML poročila za direkten uvoz v `eDavki`. V tem trenutku je podprto le poročilo `Doh-Div`.

[![build workflow](https://github.com/mpecovnik/stock-portfolio/actions/workflows/build.yml/badge.svg)](https://github.com/mpecovnik/stock-portfolio/actions/workflows/build.yml/badge.svg)
[![codecov](https://codecov.io/gh/mpecovnik/stock-portfolio/branch/main/graph/badge.svg?token=2WKDFIW8JD)](https://codecov.io/gh/mpecovnik/stock-portfolio)

![](https://codecov.io/gh/mpecovnik/stock-portfolio/branch/main/graphs/sunburst.svg?token=2WKDFIW8JD)

**DISCLAIMER**: Za morebitne napake pri vnosu odgovarjate sami. Preverite izvožena poročila preden jih oddate.

## Inštalacija

Pred uporabo je potrebno aplikacijo inštalirati. Na vašem sistemu je od prej potreben le Python. Sledite spodnjim korakom:
1. (Opcijsko) Naredite virtual environment po vaši želji, da vam inštalacija ne pokvari morebitnih dependencyjev.
2. (Opcijsko) Aktivirajte virtual environment.
3. Z githuba potegnete repositorij z `git clone https://github.com/mpecovnik/stock-portfolio`,
4. Poženete `cd stock-portfolio && pip install .`,
5. Da preverite, če je inštalacija uspešna lahko poženete `sp --help`.

## Uporaba

Orodje pričakuje dva vhodna podatka:
- Informacije o plačitelju davka. Ta vhodni podatek je podan v JSON obliki. Na primer:

```JSON
{
    "base_info": {
        "tax_number": "Test",
        "tax_payer_type": "Test",
        "name": "Test",
        "address": "Test",
        "city": "Test",
        "post_number": "1111",
        "birth_date": "1994-01-01"
    },
    "doh_div_info": {
        "period": "2022",
        "email_address": "test.test@test.com",
        "phone_number": "000000000",
        "resident_country": "Test"
    }
}
```

- Izvoženi podatki v CSV obliki. Vse CSV datoteke, ki so relevantne za vaše poročilo naj bodo znotraj istega direktorija. Trenutno je podprta le oblika, kot jo izvozi Trading212, vendar lahko podpremo tudi druge, če nastane potreba. Primer te oblike je:

| Action     | Time                | ISIN         | Ticker   | Name                                            |   No. of shares |   Price / share | Currency (Price / share)   |   Exchange rate |   Total (EUR) |   Withholding tax |   Currency (Withholding tax) |   Charge amount (EUR) | Notes         | ID                                   |   Currency conversion fee (EUR) |
|:-----------|:--------------------|:-------------|:---------|:------------------------------------------------|----------------:|----------------:|:---------------------------|----------------:|--------------:|------------------:|-----------------------------:|----------------------:|:--------------|:-------------------------------------|--------------------------------:|
| Deposit    | 2022-01-18 07:38:57 | nan          | nan      | nan                                             |     nan         |          nan    | nan                        |       nan       |       1000    |               nan |                          nan |                  1000 | Bank Transfer | 3e4d15d1-7ed3-4d0a-9a95-529ff4ef5cb4 |                          nan    |
| Market buy | 2022-01-18 09:29:26 | IE00BJ0KDR00 | XD9U     | Xtrackers MSCI USA (Acc)                        |       0.56129   |          114.01 | EUR                        |         1       |         63.99 |               nan |                          nan |                   nan | nan           | EOF1752695162                        |                          nan    |
| Market buy | 2022-01-18 09:29:28 | IE00BFXR5S54 | LGGL     | L&G Global Equity (Acc)                         |      10.6887    |           14.3  | EUR                        |         1       |        152.87 |               nan |                          nan |                   nan | nan           | EOF1752695166                        |                          nan    |
| Market buy | 2022-01-18 09:29:28 | LU0290357846 | DBXG     | Xtrackers II Eurozone Government Bond 25+ (Acc) |       0.3039    |          429.45 | EUR                        |         1       |        130.51 |               nan |                          nan |                   nan | nan           | EOF1752695169                        |                          nan    |
| Market buy | 2022-01-18 09:29:35 | IE00BZ163G84 | VECP     | Vanguard EUR Corporate Bond (Dist)              |       1.26254   |           53.42 | EUR                        |         1       |         67.45 |               nan |                          nan |                   nan | nan           | EOF1752695177                        |                          nan    |

Za generacijo XML poročila lahko uporabite CLI ukaz `sp div-doh xml-report --taxpayer-info <config-path> --data-path <data-path> --xml-path <xml-output-path> --create-csv`, kjer je:
- `<config-path>` pot do JSONa z vašimi podatki,
- `<data-path>` pot do mape z vašimi CSV podatki,
- `<xml-path>` pot kamor se izvozi vaše poročilo.

V istem direktoriju kot je specificirana XML pot, se naredi tudi datoteka `report.csv`. Le-ta služi kot orodje za preverbo XML datoteke, saj je na podlagi te CSV datoteke zgeneriran XML.