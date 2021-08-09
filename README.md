# Plover Number Format

Transforms a previous number in the specified manner. Currently, three actions are supported:

## number_format_insert

Formats the previous number in a similar way that Case CATalyst does. Read their guidelines here:

https://www.stenograph.com/content/files/documents/casecatalyst4%20manual.pdf (page 397)

Example:

```
 "A*PL": "{:number_format_insert:nN:NN} a.m."
 "T*F": "{:number_format_insert:X (XXn) NNN-NNNN}"
 "S*F": "{:number_format_insert:NNN-NN-NNNN}"
 
 248/A*PL
 2:48
 
 1259/A*PL
 12:59
 
 1234567890/T*F
 (123) 456-7890
 
 3333333/T*F
 333-3333
 
 987654321/S*F
 987-65-4321
 ```
 
 ## number_format_roman

Transforms the previous number into a Roman numeral. There are two arguments:

The first argument specifies the method of conversion. 0: standard; 1: additive.

The second argument specifies the letter case. 0: upper; 1: lower.

Example:

```
 "R*PB": "{:number_format_roman:0:0}"
 "R*PBS": "{:number_format_roman:1:0}"
 "SR*PB": "{:number_format_roman:0:1}"
 
 2021/R*PB
 MMXXI
 
 19/R*PB
 XIX
 
 19/R*PBS
 XVIIII
 
 19/SR*PB
 xix
 ```
 
 ## retro_insert_currency

Inserts a currency symbol (or any symbol, really) in front of the previous number.

Unlike Plover's natively supported command, this command ignores any decimal points, comma separators and any letters or words following the number.

Example:

```
 "TKHR*": "{:retro_insert_currency:10:$}"
 "TKHR*BG": "{:retro_insert_currency:10:CAD }"
 "P*PBD": "{:retro_insert_currency:10:£}"
 
 1.9 million/TKHR*
 $1.9 million
 
 2,000,000.00/TKHR*BG
 CAD 2,000,000.00
 
 13B bill/P*PBD
 £13B bill
 ```