# What's new in PxWebApi version 2

I have previously worked with SSB's external APIs. I do some work on it in my spare time as a retiree. 
Here is a brief overview of what is new in the new version of PxWebApi v2.

**Most important** is the GET URL support. This makes the API easier to integrate.

**Better masking characters**. You can now mask individual characters with ? , in addition to the existing * for multiple characters. E.g.: 202?M12 - only December numbers for the 2020s. Wildcards work on time as well: `2024*` gives every month of 2024.

**New filters**
- from(value) – retrieve data from and including a starting point
- to(value) – up to and including (inclusive)
- range(from,to) – define a specific interval, e.g. from municipal list
- bottom(n) – opposite of the existing top(n)
- top(n, offset) and bottom(n, offset) – skip the first/last `offset` values, e.g. `top(3,2)` for the three periods before the two most recent

**Note on commas in GET URLs:** a comma separates values in `valueCodes[variable]=a,b,c`, so an expression that itself contains a comma has to be wrapped in square brackets. `valueCodes[Tid]=range(2020,2022)` is split in two and rejected with `400 "Illegal selection expression"`; the correct form is `valueCodes[Tid]=[range(2020,2022)]`. Same for `[top(3,2)]`. A POST body needs no brackets, since each expression is already its own element. Expressions can be combined with plain codes: `2015,top(2)` gives 2015 plus the two most recent periods.

**More flexible data retrieval**
- Fetch predefined datasets without specifying parameters
- More metadata in JSON-stat2, including footnotes (also applies to version 1)
- Metadata in the API can now be shown as JSON-stat2
- Codelists in metadata. Available via Codelists 

**Layout control for CSV and XLSX**
New parameters give full control and flexibility over what goes in rows and columns. This makes CSV and XLSX much more usable.

**View options**
- UseCodes – show only codes
- UseTexts – show only text
- UseCodesAndTexts – show both codes and text
- IncludeTitle – include table title

**Structure control**
- stub – determine which variables should be displayed in the front column
- heading – determine variables in the table header
**Tip**: Place all variables in stub to get a pivot-friendly table

**CSV separator**
- SeparatorTab – tabulator
- SeparatorSpace – space
- SeparatorSemicolon – semicolon
- 
Example:
```
    outputformat=csv
    outputformatparams=separatorsemicolon,usecodesandtexts
    heading=ContentsCode
    stub=VareGrupper2,Tid
```

**HTML output** is new in the API.
Styling tips:
```
	<style type="text/css">
	    th[scope="col"] {
	        text-align: center;
	    }
	    th[scope="row"] {
	        text-align: left;
	    }
	    td {
	        text-align: right;
	    }
	    caption{
	    	font-weight: bold;
	    }
	</style>
```

**Other news**
More metadata in JSON-stat 2, such as footnotes. Also applies to API v1

There is also a new format for using http POST.
Its also good to know that the GET URL is not case sensitive: parameter names, variable codes and value codes are all accepted in any casing (`valuecodes[tid]`, `personer1`, `TOP(1)`). One exception: **codelist IDs are case-sensitive** — `agg_kommfylker` returns `400 "Non-existent codelist"` where `agg_KommFylker` works.

**Known limitations**
**Static URLs**
URLs generated in Statbank are static and do not automatically include future figures. It is necessary to edit it manually to get updated figures. Use e.g. filter from() or top(). In version 1 it was possible to "select all" by eliminating the time variable. This is not possible in v2. A converter for static-to-dynamic time is in this repository: [forenkle_url.html](forenkle_url.html), also hosted at https://nesa.no/ssb/forenkle_url.html

**URL length limitation**
Maximum length of URL: ~2100 characters. Measured 2026-09-09 on table 07459: 400 municipality codes (2,092 characters) answer, 410 codes (2,142 characters) do not. Past the limit the API returns **404**, not 400 — so it looks like the table does not exist. This can be problematic for short-term statistics with long time series. For monthly statistics, the limit goes a little before the Financial Crisis, if they are not corrected. Use `*`, `?`, `from()`/`to()`/`[range()]` or a codelist instead of long value lists — or POST, which has no length limit.

**A repeated value code returns 500**
Give the same value code twice for one variable and the API answers **500** with an empty body, rather than a 400 with an explanation. `valueCodes[Region]=0301,0301` is enough to trigger it. This applies to both GET and POST, and was verified on 2026-09-09 at Statistics Norway, Statistics Sweden and the Latvian CSP. Overlap between an expression and a plain code is fine: `valueCodes[Tid]=2026,top(1)` answers even though `top(1)` is also 2026. If you build selections programmatically, deduplicate the list first.

---

Statistics Norways R-package [PxWebApiData](https://cran.r-project.org/package=PxWebApiData) is also updated to handle V2 URLs

See also [Statistics Norway's user guide for the API](https://www.ssb.no/en/api/pxwebapiv2) and the shared [PxWebApi 2 User Guide](https://www.pxtools.net/PxWebApi/documentation/user-guide/) from PxTools.

The details above, and more, are built into the AI skills in this repository — see the [README](README.md) and each skill's changelog for what was verified against the live API, and when.