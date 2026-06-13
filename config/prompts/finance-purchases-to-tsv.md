Convert the data into a purchases table (csv) with tab-separated values. For example:

```text
Мороженое ванильное Vanilla Dream Monterra	Food	494 ₽
Лимонад «Река» абрикос-апельсин-пихта	Food	199 ₽
Мыло жидкое	Household Goods	165 ₽
Наполнитель для кошки	Pet Care	165 ₽
```

Do not add item quantity to the table. Include the ruble sign.
In the second column, assign the product type from these categories:

```text
Appliances
Books
Clothing
Food
Household Goods
IT
Pet Care
Sports
Stationery
Toys
```

If the data looks like this:

```text
Сливки 20% «Домик в деревне» стерилизованные
2 шт
518 ₽
259 ₽/шт
```

then the purchase total is 518 rubles, not 259 rubles, because 2 items are indicated.

If the data looks like this:

```text
Сливки Домик в деревне стерилизованные 20% 480г	4 шт	389.00 ₽
259.90 ₽	1 039.60 ₽
```

then the purchase total is 1039.60 rubles, not 1 ruble — numbers over 1000 may contain a space in the source. In the output table write 1039.60 ₽, not 1 039.60 ₽.

Data to convert:

```text
{{RAW_DATA}}
```

Return only table rows (no headers and no markdown wrappers).
